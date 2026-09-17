#!/usr/bin/env python3
"""Verify Ephesians 6 and Philippians 1–4 draft checkpoint.

Structural and source-binding QA only. This script does not grant editorial or
publication approval and does not represent independent scholarly review.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[3]
SCOPES = [
 ('2026-09-17-ephesians-6','ephesians','ephesians-pinned-greek.txt'),
 ('2026-09-17-philippians-1-4','philippians','philippians-pinned-greek.txt'),
]
PARENT = 'ccb3985e87fad907698c1574db897dd67dca6904'
sha = lambda b: hashlib.sha256(b).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def old(path):
    return subprocess.check_output(['git', 'show', PARENT + ':' + path], cwd=R)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-directory', required=True, type=Path)
    ap.add_argument('--bind-focused-records', action='store_true')
    args = ap.parse_args()
    source_dir = args.source_directory.resolve()
    sys.path.insert(0, str(R / 'tools'))
    from audit_fluent_revision import audit

    queue_path = 'audit/fluent-revision/WORK_QUEUE.json'
    q = json.loads((R / queue_path).read_text())
    oq = json.loads(old(queue_path))
    assert q['completed_draft_scopes'][:len(oq['completed_draft_scopes'])] == oq['completed_draft_scopes']
    assert len(q['completed_draft_scopes']) == len(oq['completed_draft_scopes']) + 2
    assert q['next_work'][3:] == oq['next_work'][1:]
    assert [x['scope'] for x in q['next_work'][1:3]] == ['Whole-book Ephesians consistency review','Whole-book Philippians consistency review']
    assert q['completed_fifty_chapter_blocks'] == oq['completed_fifty_chapter_blocks']

    prior_paths = set()
    prior_verses = 0
    for scope in oq['completed_draft_scopes']:
        ledger_path = scope['ledger']
        assert (R / ledger_path).read_bytes() == old(ledger_path), ledger_path
        ledger = json.loads((R / ledger_path).read_text())
        for chapter in ledger['chapters']:
            path = chapter['path']
            assert path not in prior_paths
            prior_paths.add(path)
            prior_verses += chapter['verse_count']
            assert (R / path).read_bytes() == old(path), path
            assert sha((R / path).read_bytes()) == chapter['after_sha256']
            assert sha((R / chapter['tsw_comparator_path']).read_bytes()) == chapter['tsw_comparator_sha256']
    assert (len(oq['completed_draft_scopes']), len(prior_paths), prior_verses) == (127, 1107, 29426)

    ledgers = []
    unique_source_records = 0
    focus_count = 0
    source_audits = []
    allowed = {
        queue_path,
        'tools/audit_fluent_revision.py',
        'tools/build_fluent_mark_checkpoint.py',
        'tools/package_fluent_checkpoint.py',
    }
    for dirname, slug, source_name in SCOPES:
        directory = R / 'audit/fluent-revision' / dirname
        cfg = json.loads((directory / 'config.json').read_text())
        ledger_path = directory / (slug + '-verse-review.json')
        ledger = json.loads(ledger_path.read_text())
        source_bytes = (source_dir / source_name).read_bytes()
        assert sha(source_bytes) == ledger['source']['sha256'] == cfg['source']['sha256']
        blob = hashlib.sha1(b'blob ' + str(len(source_bytes)).encode() + b'\0' + source_bytes).hexdigest()
        assert blob == ledger['source']['git_blob_sha'] == cfg['source']['git_blob_sha']
        errors = audit(R, ledger, source_bytes)
        assert not errors, (slug, errors)
        ledgers.append(ledger)
        source_rows = {line.split('\t', 1)[0]: line.split('\t', 1)[1]
                       for line in source_bytes.decode().splitlines() if '\t' in line}
        scoped_refs = {v['source_reference'] for v in ledger['verses']}
        unique_source_records += len(scoped_refs)
        assert scoped_refs.issubset(source_rows)
        f3 = set(cfg['f3'])
        focus = [{**v, 'exact_source_record': source_rows[v['source_reference']]}
                 for v in ledger['verses'] if v['reference'].split()[-1] in f3]
        assert len(focus) == len(f3)
        reread = directory / 'authoring-reread.md'
        record = {
            'status': 'AUTHORING_REREAD_COMPLETED',
            'review_type': 'Drafting-assistant bilingual self-reread; not human or independent scholarly review',
            'authoring_record_sha256': sha(reread.read_bytes()),
            'rows': focus,
        }
        focused_path = directory / 'focused-comparisons.json'
        if args.bind_focused_records:
            dump(focused_path, record)
        else:
            assert json.loads(focused_path.read_text()) == record
        focus_count += len(focus)
        source_audits.append({'ledger': str(ledger_path.relative_to(R)), 'status': 'PASSED',
                              'public_verses': len(ledger['verses']), 'unique_source_records': len(scoped_refs)})
        allowed.update(str(p.relative_to(R)) for p in directory.rglob('*') if p.is_file())
        for chapter in ledger['chapters']:
            assert chapter['path'] not in prior_paths
            allowed.add(chapter['path'])
            review = f'audit/exegetical-core/fluent-production/{slug}/' + Path(chapter['path']).name.replace('.md', '_review.json')
            allowed.add(review)
            review_data = json.loads((R / review).read_text())
            assert review_data['chapter_binding'] == chapter
            assert review_data['publication_allowed'] is False and review_data['status'] == 'REVIEW_PENDING'
            text = (R / chapter['path']).read_text()
            assert text.count('## Notes\n') == 1 and text.count('## Vocabulary\n') == 1
            body = text.split('## Notes')[0]
            opened = False
            for line in body.splitlines():
                if line == '<p>':
                    assert not opened
                    opened = True
                elif line == '</p>':
                    assert opened
                    opened = False
                elif re.match(r'^v\d+:', line):
                    assert opened, (chapter['path'], line)
            assert not opened
            maximum = chapter['verse_count'] + len(chapter.get('source_omitted_public_labels', []))
            for label in re.findall(r'^v([\d,–\- ]+):', text.split('## Notes')[1], re.M):
                assert all(1 <= int(number) <= maximum for number in re.findall(r'\d+', label))
        for filename in cfg['book_record_files']:
            path = f'audit/exegetical-core/fluent-production/{slug}/{filename}'
            allowed.add(path)
            current = json.loads((R / path).read_text())
            previous = json.loads(old(path))
            assert current['publication_allowed'] is False and current['status'] == 'REVIEW_PENDING'
            assert current['revision_batches'][:-1] == previous.get('revision_batches', [])
            assert current['source'] == previous['source']
            if 'entries' in previous:
                assert len(current['entries'])==len(previous['entries'])
                for entry,prior in zip(current['entries'],previous['entries']):
                    if prior['chapter'] in cfg['chapters']:
                        assert all(entry[k]==v for k,v in prior.items())
                        assert entry['status']=='SUPERSEDED'
                    else: assert entry==prior
            if 'bindings' in previous:
                assert current['bindings'] == previous['bindings']

    earlier=['audit/fluent-revision/2026-09-17-ephesians-1-5/ephesians-verse-review.json']
    for path in earlier:
        assert not audit(R,json.loads((R/path).read_text()),(source_dir/'ephesians-pinned-greek.txt').read_bytes())
    assert sum(len(l['chapters']) for l in ledgers)==5
    assert sum(len(l['verses']) for l in ledgers)==unique_source_records==128
    assert focus_count==98
    assert all(l['status']=='REVIEW_PENDING' and not l['publication_allowed'] and l['qa_scope']=='structural' for l in ledgers)
    rows={v['reference']:v for l in ledgers for v in l['verses']}
    after={r:v['after'] for r,v in rows.items()}
    checks={
      'slavery_and_threats': all(x in after['Ephesians 6:5'] for x in ['Slaves','masters','fear and trembling']) and 'stop threatening' in after['Ephesians 6:9'],
      'nonhuman_opponents': 'not against flesh and blood' in after['Ephesians 6:12'],
      'standing_and_peace': all('stand' in after['Ephesians 6:'+str(v)].lower() for v in [11,13,14]) and 'peace' in after['Ephesians 6:15'],
      'messenger': 'Tychicus' in after['Ephesians 6:21'],
      'senders': all(x in after['Philippians 1:1'] for x in ['Paul','Timothy','slaves','Philippi','overseers','deacons']),
      'life_and_death': all(x in after['Philippians 1:20'] for x in ['life','death','body']),
      'form_and_equality': all(x in after['Philippians 2:6'] for x in ['form of God','equality with God']),
      'emptying_and_slave': 'emptied himself' in after['Philippians 2:7'] and 'form of a slave' in after['Philippians 2:7'],
      'three_regions': all(x in after['Philippians 2:10'] for x in ['heaven','on earth','beneath the earth']),
      'willing_and_doing': all(x in after['Philippians 2:13'] for x in ['God','your willing','your doing']),
      'specific_father': 'father' in after['Philippians 2:22'],
      'epaphroditus_roles': all(x in after['Philippians 2:25'] for x in ['Epaphroditus','brother','fellow worker','fellow soldier','messenger','minister']),
      'eighth_day_and_tribe': all(x in after['Philippians 3:5'] for x in ['eighth day','Israel','Benjamin','Hebrew','Pharisee']),
      'faithfulness_and_faith': "Christ's faithfulness" in after['Philippians 3:9'] and 'basis of faith' in after['Philippians 3:9'],
      'source_short_name': 'Jesus' not in after['Philippians 3:12'],
      'source_short_3_16': 'rule' not in after['Philippians 3:16'],
      'civic_connection': 'citizens' in after['Philippians 1:27'] and 'citizenship' in after['Philippians 3:20'],
      'equal_women_appeals': after['Philippians 4:2'].count('I appeal')==2 and all(x in after['Philippians 4:2'] for x in ['Euodia','Syntyche']),
      'women_workers': 'these women' in after['Philippians 4:3'] and 'struggled beside me' in after['Philippians 4:3'] and 'Clement' in after['Philippians 4:3'],
      'source_short_4_13': 'Christ' not in after['Philippians 4:13'],
      'places': 'Macedonia' in after['Philippians 4:15'] and 'Thessalonica' in after['Philippians 4:16'],
      'caesar_household': "Caesar's household" in after['Philippians 4:22'],
      'short_closing': 'Amen' not in after['Philippians 4:23'],
    }
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    chapters=[c for scope in q['completed_draft_scopes'] for c in json.loads((R/scope['ledger']).read_text())['chapters']]
    assert len(q['completed_draft_scopes'])==129
    assert len({c['path'] for c in chapters})==len(chapters)==1112
    assert sum(c['verse_count'] for c in chapters)==29554
    block=q['active_fifty_chapter_block']
    assert (block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==(5,45,128)
    assert block['remaining_scope'].startswith('Colossians 1–4;')

    changed = (subprocess.check_output(['git', 'diff', '--name-only', PARENT], cwd=R).decode().splitlines()
               + subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=R).decode().splitlines())
    for path in changed:
        if path == '.fluent-revision-writer.lock':
            continue
        assert path in allowed or any(path.startswith(f'audit/fluent-revision/{name}/') for name, _, _ in SCOPES), path
    assert not subprocess.check_output(['git', 'diff', PARENT, '--', 'books', 'companions'], cwd=R).strip()
    subprocess.run(['git', 'diff', '--check', PARENT], cwd=R, check=True)
    family = subprocess.check_output([sys.executable, 'tools/audit_translation_family.py'], cwd=R).decode()

    result = {
        'status': 'PASSED',
        'qa_scope': 'structural',
        'parent_commit': PARENT,
        'new_chapters': 5,
        'new_verses': 128,
        'unique_original_source_records': 128,
        'cumulative_coverage': {'ledgers': 129, 'chapters': 1112, 'verses': 29554},
        'prior_preservation': {'ledgers_byte_identical': 127, 'chapters_byte_identical': 1107,
                               'verses': 29426, 'tsw_and_companion_unchanged': True},
        'source_binding_audits': source_audits,
        'additional_affected_ledgers': earlier,
        'source_sensitive_checks': checks,
        'focused_authoring_reread_count': focus_count,
        'translation_family': family,
        'active_fifty_chapter_block': block,
        'independent_editorial_review': 'REVIEW_PENDING',
        'whole_book_reviews': 'PENDING; Ephesians and Philippians newly queued',
        'reader_testing': 'PENDING',
        'companion_reconciliation': 'PENDING; no quotations or bindings changed',
        'publication_allowed': False,
    }
    dump(Path(__file__).with_name('verification.json'), result)
    print(json.dumps({key: result[key] for key in ['status', 'new_chapters', 'new_verses', 'unique_original_source_records', 'cumulative_coverage']}))


if __name__ == '__main__':
    main()
