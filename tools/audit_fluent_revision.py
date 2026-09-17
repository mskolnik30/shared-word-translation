#!/usr/bin/env python3
"""Verify a source-bound Fluent revision ledger; does not approve translation choices."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

from audit_translation_overlap import verse_texts


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit(root, ledger, source_bytes):
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    source = ledger['source']
    check(sha(source_bytes) == source['sha256'], 'source SHA-256 mismatch')
    blob = hashlib.sha1(b'blob ' + str(len(source_bytes)).encode() + b'\0' + source_bytes).hexdigest()
    check(blob == source['git_blob_sha'], 'source Git blob mismatch')
    source_verses = {}
    if source.get('format', 'tab_separated') == 'osis_xml':
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(source_bytes)
        records = re.findall(r'<verse\b[^>]*>.*?</verse>', source_bytes.decode(), re.S)
        check(len(records) == len(tree.findall('.//{*}verse')), 'XML record extraction differs')
        check(len(records) == source['book_verse_count'], 'source book count differs')
        scope = source['scope_chapters']
        extra_references = set(source.get('extra_source_references', []))
        excluded_references = set(source.get('excluded_source_references', []))
        check(scope == sorted(set(scope)) and bool(scope), 'invalid source chapter scope')
        check(scope == [c['chapter'] for c in ledger['chapters']], 'chapter/source scope differs')
        for record in records:
            element = ET.fromstring(record)
            book, chapter, verse = element.attrib['osisID'].split('.')
            source_reference = f'{book} {chapter}:{verse}'
            if book == source['osis_book_id'] and (
                (int(chapter) in scope and source_reference not in excluded_references)
                or source_reference in extra_references
            ):
                reference = source_reference
                check(reference not in source_verses, f'duplicate source reference: {reference}')
                source_verses[reference] = record
    else:
        all_source_verses = {}
        for line in source_bytes.decode().splitlines():
            match = re.match(r'([^\t]+)\t(.*)', line)
            if match:
                check(match[1] not in all_source_verses, f'duplicate source reference: {match[1]}')
                all_source_verses[match[1]] = match[2]
        if 'scope_chapters' in source:
            scope = source['scope_chapters']
            check(scope == sorted(set(scope)) and bool(scope), 'invalid source chapter scope')
            check(scope == [c['chapter'] for c in ledger['chapters']], 'chapter/source scope differs')
            check(len(all_source_verses) == source['book_verse_count'], 'source book count differs')
            for ref, value in all_source_verses.items():
                parsed = re.fullmatch(r'(.+) (\d+):(\d+)', ref)
                check(bool(parsed), f'invalid source reference: {ref}')
                if parsed:
                    check(parsed[1] == source['osis_book_id'], f'unexpected source book: {ref}')
                    if parsed[1] == source['osis_book_id'] and int(parsed[2]) in scope:
                        source_verses[ref] = value
        else:
            source_verses = all_source_verses
    # A public verse can contain several complete source records (e.g. Num 26:1).
    # Keep each original record and hash separately; never hash normalized joins.
    references = []
    for verse in ledger['verses']:
        if 'source_segments' in verse:
            segments = verse['source_segments']
            valid = (isinstance(segments, list) and len(segments) >= 2
                     and all(isinstance(s, dict)
                             and isinstance(s.get('source_reference'), str)
                             and isinstance(s.get('source_verse_sha256'), str)
                             for s in segments))
            check(valid, f"invalid source segments: {verse['reference']}")
            if not valid:
                continue
            check(any(s['source_reference'] == verse['source_reference']
                      and s['source_verse_sha256'] == verse['source_verse_sha256']
                      for s in segments), f"primary source missing from segments: {verse['reference']}")
            positions = {ref: i for i, ref in enumerate(source_verses)}
            indices = [positions.get(s['source_reference'], -1) for s in segments]
            check(all(i >= 0 for i in indices) and indices == sorted(indices),
                  f"source segment order differs: {verse['reference']}")
            for segment in segments:
                ref = segment['source_reference']
                references.append(ref)
                check(ref in source_verses, f"unknown source segment: {ref}")
                check(sha(source_verses.get(ref, '').encode()) == segment['source_verse_sha256'],
                      f"source segment hash mismatch: {verse['reference']} / {ref}")
        else:
            references.append(verse['source_reference'])
    # A source record can span public verses (e.g. Hebrew Ps 13:6 or Greek
    # 2Cor 13:12). Such a split must partition every word/token exactly once,
    # in public order. Every part still binds the complete original record;
    # these ranges never replace the full-record hash.
    partitions = {}
    for verse in ledger['verses']:
        if 'source_partition' in verse:
            ref = verse['source_reference']
            part = verse['source_partition']
            xml_partition = (source.get('format') == 'osis_xml'
                             and type(part.get('word_start')) is int
                             and type(part.get('word_end')) is int
                             and 1 <= part['word_start'] <= part['word_end'])
            tab_partition = (source.get('format') == 'tab_separated'
                             and type(part.get('token_start')) is int
                             and type(part.get('token_end')) is int
                             and 1 <= part['token_start'] <= part['token_end'])
            valid = ('source_segments' not in verse and isinstance(part, dict)
                     and (xml_partition or tab_partition)
                     and isinstance(part.get('reason'), str)
                     and bool(part['reason'].strip()))
            check(valid, f"invalid source partition: {verse['reference']}")
            if valid:
                partitions.setdefault(ref, []).append(part)
    counts = Counter(references)
    for ref, count in counts.items():
        if count > 1 or ref in partitions:
            parts = partitions.get(ref, [])
            check(count > 1 and len(parts) == count,
                  f'duplicate ledger reference without complete partitions: {ref}')
            if parts and ref in source_verses:
                if source.get('format') == 'osis_xml':
                    import xml.etree.ElementTree as ET
                    words = [e for e in ET.fromstring(source_verses[ref])
                             if e.tag.split('}')[-1] == 'w']
                    positions = [i for p in parts
                                 for i in range(p['word_start'], p['word_end'] + 1)]
                else:
                    words = source_verses[ref].split()
                    positions = [i for p in parts
                                 for i in range(p['token_start'], p['token_end'] + 1)]
                check(positions == list(range(1, len(words) + 1)),
                      f'source partition gap, overlap, or order mismatch: {ref}')
    check(set(references) == set(source_verses), 'ledger/source coverage differs')
    check(ledger['publication_allowed'] is False, 'draft publication must remain blocked')
    check(ledger['status'] == 'REVIEW_PENDING', 'draft editorial status changed')
    chapters = {}
    for chapter in ledger['chapters']:
        current = (root / chapter['path']).read_bytes()
        check(sha(current) == chapter['after_sha256'], f"current hash mismatch: {chapter['path']}")
        before = subprocess.check_output(['git', 'show', f"{ledger['base_commit']}:{chapter['path']}"], cwd=root)
        check(sha(before) == chapter['before_sha256'], f"base hash mismatch: {chapter['path']}")
        comparator = (root / chapter['tsw_comparator_path']).read_bytes()
        check(sha(comparator) == chapter['tsw_comparator_sha256'], f"TSW hash mismatch: {chapter['path']}")
        text = current.decode()
        check('editorial_status: REVIEW_PENDING\n' in text and 'publication_allowed: false\n' in text,
              f"missing draft metadata: {chapter['path']}")
        body = text.split('## Notes')[0]
        opened = False
        for line in body.splitlines():
            if line == '<p>':
                check(not opened, f"nested paragraph: {chapter['path']}")
                opened = True
            elif line == '</p>':
                check(opened, f"unmatched paragraph close: {chapter['path']}")
                opened = False
            elif re.match(r'^v\d+:', line):
                check(opened, f"verse outside paragraph: {chapter['path']}")
        check(not opened, f"unclosed paragraph: {chapter['path']}")
        check(text.count('## Notes\n') == 1 and text.count('## Vocabulary\n') == 1,
              f"apparatus heading count: {chapter['path']}")
        after, old, tsw = map(verse_texts, (text, before.decode(), comparator.decode()))
        # Some pinned sources omit a public verse present in the comparator.
        # Accept only a declared, explained gap already present in the exact
        # parent text. Full source-record coverage is independently required above.
        omitted = chapter.get('source_omitted_public_labels', [])
        valid_omission = (isinstance(omitted, list)
                          and all(isinstance(v, int) and v > 0 for v in omitted)
                          and omitted == sorted(set(omitted)))
        check(valid_omission, f"invalid omitted labels: {chapter['path']}")
        if not valid_omission:
            omitted = []
        maximum = chapter['verse_count'] + len(omitted)
        check(all(v <= maximum for v in omitted), f"omitted label out of range: {chapter['path']}")
        if omitted:
            check(bool(chapter.get('source_omission_reason', '').strip()),
                  f"missing omission explanation: {chapter['path']}")
        expected = [f'{v:02}' for v in range(1, maximum + 1) if v not in omitted]
        check(list(after) == expected, f"verse sequence mismatch: {chapter['path']}")
        if 'tsw_public_labels' in chapter:
            declared = chapter['tsw_public_labels']
            unmatched = chapter.get('tsw_unmatched_source_labels', [])
            additional = chapter.get('tsw_additional_public_labels', [])
            valid_alignment = (isinstance(declared, list) and declared == sorted(set(declared))
                               and all(type(v) is int and v > 0 for v in declared)
                               and isinstance(unmatched, list) and unmatched == sorted(set(unmatched))
                               and all(type(v) is int and f'{v:02}' in after for v in unmatched)
                               and isinstance(additional, list) and additional == sorted(set(additional))
                               and all(type(v) is int and v > 0 for v in additional)
                               and set(unmatched).isdisjoint(additional)
                               and set(declared) == (set(map(int, after)) - set(unmatched)) | set(additional)
                               and bool(chapter.get('tsw_alignment_reason', '').strip()))
            check(valid_alignment, f'invalid explicit comparator alignment: {chapter["path"]}')
            comparator_expected = [f'{v:02}' for v in declared] if valid_alignment else []
        else:
            unmatched = []
            comparator_omitted = chapter.get('tsw_omitted_public_labels', [])
            valid_comparator_omission = (isinstance(comparator_omitted, list)
                                        and all(type(v) is int for v in comparator_omitted)
                                        and comparator_omitted == sorted(set(comparator_omitted))
                                        and set(comparator_omitted).issubset(omitted))
            check(valid_comparator_omission, f'invalid comparator omitted labels: {chapter["path"]}')
            if not valid_comparator_omission:
                comparator_omitted = []
            if comparator_omitted:
                check(bool(chapter.get('tsw_omission_reason', '').strip()),
                      f'missing comparator omission explanation: {chapter["path"]}')
            comparator_expected = [f'{v:02}' for v in range(1, maximum + 1)
                                   if v not in comparator_omitted]
        # Legacy ledgers predate this explicit field and only allowed source
        # omissions already absent from their parent Fluent. New ledgers bind
        # the field even when empty, permitting a declared source correction
        # to remove a parent-only public label.
        parent_omitted = chapter.get('parent_omitted_public_labels', omitted)
        valid_parent_omission = (isinstance(parent_omitted, list)
                                 and all(type(v) is int for v in parent_omitted)
                                 and parent_omitted == sorted(set(parent_omitted))
                                 and set(parent_omitted).issubset(omitted))
        check(valid_parent_omission, f'invalid parent omitted labels: {chapter["path"]}')
        if not valid_parent_omission:
            parent_omitted = []
        if parent_omitted and 'parent_omitted_public_labels' in chapter:
            check(bool(chapter.get('parent_omission_reason', '').strip()),
                  f'missing parent omission explanation: {chapter["path"]}')
        parent_expected = [f'{v:02}' for v in range(1, maximum + 1)
                           if v not in parent_omitted]
        check(list(old) == parent_expected and list(tsw) == comparator_expected,
              f"verse alignment mismatch: {chapter['path']}")
        chapters[chapter['chapter']] = (after, old, tsw)
    seen = Counter()
    for verse in ledger['verses']:
        public_match = re.search(r'(\d+):(\d+)$', verse['reference'])
        check(bool(public_match), f"invalid public reference: {verse['reference']}")
        if not public_match:
            continue
        chapter, label = map(int, public_match.groups())
        after, old, tsw = chapters[chapter]
        key = f'{label:02}'
        seen[chapter] += 1
        comparator = tsw.get(key, '')
        check(after[key] == verse['after'] and old[key] == verse['before'] and comparator == verse['tsw_comparator'],
              f"ledger text mismatch: {verse['reference']}")
        if label in set(next(c for c in ledger['chapters'] if c['chapter'] == chapter).get('tsw_unmatched_source_labels', [])):
            check(verse.get('tsw_comparator_status') == 'UNAVAILABLE_PUBLIC_LABEL'
                  and bool(verse.get('tsw_comparator_reason', '').strip()),
                  f"missing unmatched comparator metadata: {verse['reference']}")
        check(verse['delta'] in ('F0', 'F1', 'F2', 'F3') and bool(verse['rationale'].strip()),
              f"missing/invalid decision: {verse['reference']}")
        check(verse['editorial_status'] == 'REVIEW_PENDING', f"unexpected approval: {verse['reference']}")
        raw = source_verses.get(verse['source_reference'], '')
        check(sha(raw.encode()) == verse['source_verse_sha256'], f"source verse hash mismatch: {verse['reference']}")
    check(dict(seen) == {c['chapter']: c['verse_count'] for c in ledger['chapters']}, 'chapter/ledger counts differ')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    parser.add_argument('--source-text', type=Path, required=True)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text())
    errors = audit(args.repo_root, ledger, args.source_text.read_bytes())
    print(json.dumps({'status': 'FAILED' if errors else 'PASSED',
                      'chapters': len(ledger['chapters']), 'verses': len(ledger['verses']),
                      'scope': 'source identity, byte bindings, coverage, format, ledger consistency; no human approval',
                      'errors': errors}, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
