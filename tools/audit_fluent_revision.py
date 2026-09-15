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
        for line in source_bytes.decode().splitlines():
            match = re.match(r'([^\t]+)\t(.*)', line)
            if match:
                check(match[1] not in source_verses, f'duplicate source reference: {match[1]}')
                source_verses[match[1]] = match[2]
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
    check(len(references) == len(set(references)), 'duplicate ledger reference')
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
        comparator_expected = [f'{v:02}' for v in range(1, maximum + 1)]
        check(list(old) == list(after) and list(tsw) == comparator_expected,
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
        check(after[key] == verse['after'] and old[key] == verse['before'] and tsw[key] == verse['tsw_comparator'],
              f"ledger text mismatch: {verse['reference']}")
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
