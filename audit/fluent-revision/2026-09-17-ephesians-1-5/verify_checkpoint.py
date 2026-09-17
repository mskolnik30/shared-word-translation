#!/usr/bin/env python3
"""Verify the Romans 16–Ephesians 5 draft batch and completed block boundary.

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
    ('2026-09-17-romans-16', 'romans', 'romans-pinned-greek.txt'),
    ('2026-09-17-1corinthians-1-16', '1corinthians', '1corinthians-pinned-greek.txt'),
    ('2026-09-17-2corinthians-1-13', '2corinthians', '2corinthians-pinned-greek.txt'),
    ('2026-09-17-galatians-1-6', 'galatians', 'galatians-pinned-greek.txt'),
    ('2026-09-17-ephesians-1-5', 'ephesians', 'ephesians-pinned-greek.txt'),
]
PARENT = '601ddbd8612ac0c74e0184544e9402c861937e54'
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
    assert q['completed_draft_scopes'][len(oq['completed_draft_scopes']):] == [
        {'scope': 'Romans 16', 'verses': 24, 'ledger': 'audit/fluent-revision/2026-09-17-romans-16/romans-verse-review.json'},
        {'scope': '1 Corinthians 1–16', 'verses': 437, 'ledger': 'audit/fluent-revision/2026-09-17-1corinthians-1-16/1corinthians-verse-review.json'},
        {'scope': '2 Corinthians 1–13', 'verses': 257, 'ledger': 'audit/fluent-revision/2026-09-17-2corinthians-1-13/2corinthians-verse-review.json'},
        {'scope': 'Galatians 1–6', 'verses': 149, 'ledger': 'audit/fluent-revision/2026-09-17-galatians-1-6/galatians-verse-review.json'},
        {'scope': 'Ephesians 1–5', 'verses': 131, 'ledger': 'audit/fluent-revision/2026-09-17-ephesians-1-5/ephesians-verse-review.json'},
    ]
    assert q['next_work'][1:4] == oq['next_work'][1:4]
    assert q['next_work'][8:] == oq['next_work'][4:]

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
    assert (len(oq['completed_draft_scopes']), len(prior_paths), prior_verses) == (122, 1066, 28428)

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
            if 'bindings' in previous:
                assert current['bindings'] == previous['bindings']

    # Re-audit every earlier Romans ledger against the same exact full-book source.
    romans_source = (source_dir / 'romans-pinned-greek.txt').read_bytes()
    earlier_romans = [s['ledger'] for s in oq['completed_draft_scopes'] if s['scope'] in ('Romans 1–6', 'Romans 7–15')]
    assert len(earlier_romans) == 2
    for path in earlier_romans:
        errors = audit(R, json.loads((R / path).read_text()), romans_source)
        assert not errors, (path, errors)

    assert sum(len(l['chapters']) for l in ledgers) == 41
    assert sum(len(l['verses']) for l in ledgers) == 998
    assert unique_source_records == 997
    assert all(l['status'] == 'REVIEW_PENDING' and l['publication_allowed'] is False
               and l['qa_scope'] == 'structural' and l['automated_qa'] == 'PASSED' for l in ledgers)

    rows = {v['reference']: v for ledger in ledgers for v in ledger['verses']}
    after = {ref: value['after'] for ref, value in rows.items()}
    checks = {
        'romans_names_and_roles': all(name in after['Romans 16:1'] + after['Romans 16:2'] + after['Romans 16:7']
                                      for name in ['Phoebe', 'Junia']) and 'deacon' in after['Romans 16:1'],
        'romans_versification': rows['Romans 16:24']['tsw_comparator_status'] == 'UNAVAILABLE_PUBLIC_LABEL'
                               and not any(ref in rows for ref in ['Romans 16:25', 'Romans 16:26', 'Romans 16:27']),
        'first_corinthians_numbers': 'twenty-three thousand' in after['1Corinthians 10:8']
                                     and 'the twelve' in after['1Corinthians 15:5'].lower()
                                     and 'more than five hundred' in after['1Corinthians 15:6'].lower(),
        'first_corinthians_variants': 'broken' not in after['1Corinthians 11:24'].lower()
                                      and 'not all fall asleep' in after['1Corinthians 15:51'].lower()
                                      and 'death' in after['1Corinthians 15:55'].lower(),
        'first_corinthians_social_status': all(term in after['1Corinthians 12:13'].lower()
                                               for term in ['enslaved', 'free']),
        'second_corinthians_harm_counts': all(term in after['2Corinthians 11:24'].lower()
                                              for term in ['five', 'forty lashes minus one'])
                                           and all(term in after['2Corinthians 11:25'].lower()
                                                   for term in ['three times', 'once', 'three times']),
        'second_corinthians_vision_count': 'fourteen years' in after['2Corinthians 12:2'],
        'second_corinthians_public_mapping': rows['2Corinthians 13:12']['source_reference'] == '2Cor 13:12'
                                             and rows['2Corinthians 13:13']['source_reference'] == '2Cor 13:12'
                                             and rows['2Corinthians 13:14']['source_reference'] == '2Cor 13:13'
                                             and rows['2Corinthians 13:12']['source_partition']['token_end'] == 5
                                             and rows['2Corinthians 13:13']['source_partition']['token_start'] == 6,
        'galatians_names_and_chronology': 'Cephas' in after['Galatians 1:18']
                                          and 'fifteen days' in after['Galatians 1:18']
                                          and 'fourteen years' in after['Galatians 2:1'],
        'galatians_numbers_and_body': 'four hundred thirty years' in after['Galatians 3:17']
                                      and 'castrate' in after['Galatians 5:12'].lower(),
        'galatians_status_and_gender': all(term in after['Galatians 3:28'].lower()
                                           for term in ['enslaved', 'free', 'male', 'female']),
        'galatians_faithfulness': 'faithfulness of Jesus Christ' in after['Galatians 2:16']
                                  and 'believed in Christ Jesus' in after['Galatians 2:16'],
        'ephesians_bracketed_place': '[in Ephesus]' in after['Ephesians 1:1'],
        'ephesians_reconciliation': all(term in after['Ephesians 2:14'].lower()
                                        for term in ['two', 'one', 'dividing wall', 'hostility']),
        'ephesians_co_compounds': all(term in after['Ephesians 3:6'].lower()
                                      for term in ['coheirs', 'same body', 'copartners']),
        'ephesians_captive_image': 'captivity captive' in after['Ephesians 4:8'],
        'ephesians_household_frame': 'one another' in after['Ephesians 5:21']
                                     and 'submit' in after['Ephesians 5:22']
                                     and 'gave himself' in after['Ephesians 5:25'],
    }
    assert all(checks.values()), [name for name, passed in checks.items() if not passed]

    chapters = [chapter for scope in q['completed_draft_scopes']
                for chapter in json.loads((R / scope['ledger']).read_text())['chapters']]
    assert len(q['completed_draft_scopes']) == 127
    assert len({chapter['path'] for chapter in chapters}) == len(chapters) == 1107
    assert sum(chapter['verse_count'] for chapter in chapters) == 29426
    completed = q['completed_fifty_chapter_blocks'][-1]
    assert (completed['status'], completed['chapters'], completed['verses']) == ('DRAFT_COMPLETED', 50, 1243)
    block = q['active_fifty_chapter_block']
    assert (block['status'], block['completed_chapters'], block['remaining_chapters'], block['completed_verses']) == ('IN_PROGRESS', 0, 50, 0)
    assert block['scope'].startswith('Ephesians 6;') and block['remaining_scope'] == block['scope']

    changed = (subprocess.check_output(['git', 'diff', '--name-only', PARENT], cwd=R).decode().splitlines()
               + subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=R).decode().splitlines())
    for path in changed:
        if path == '.fluent-revision-writer.lock':
            continue
        assert path in allowed or any(path.startswith(f'audit/fluent-revision/{name}/') for name, _, _ in SCOPES), path
    assert not subprocess.check_output(['git', 'diff', PARENT, '--', 'books', 'companions'], cwd=R).strip()
    subprocess.run(['git', 'diff', '--check', PARENT], cwd=R, check=True)
    family = subprocess.check_output([sys.executable, 'tools/audit_translation_family.py'], cwd=R).decode()

    boundary = {
        'status': 'PASSED',
        'scope': 'Romans 7–16; 1 Corinthians 1–16; 2 Corinthians 1–13; Galatians 1–6; Ephesians 1–5',
        'chapters': 50,
        'verses': 1243,
        'newly_completed_in_this_batch': {
            'scope': 'Romans 16; 1 Corinthians 1–16; 2 Corinthians 1–13; Galatians 1–6; Ephesians 1–5',
            'chapters': 41,
            'verses': 998,
        },
        'completed_before_next_block_started': True,
        'next_block_started_with': None,
        'qualification': 'Draft coverage and structural QA complete; independent editorial and whole-book review pending.',
        'publication_allowed': False,
    }
    dump(R / 'audit/fluent-revision/2026-09-17-ephesians-1-5/block-boundary-verification.json', boundary)
    result = {
        'status': 'PASSED',
        'qa_scope': 'structural',
        'parent_commit': PARENT,
        'new_chapters': 41,
        'new_verses': 998,
        'unique_original_source_records': 997,
        'cumulative_coverage': {'ledgers': 127, 'chapters': 1107, 'verses': 29426},
        'prior_preservation': {'ledgers_byte_identical': 122, 'chapters_byte_identical': 1066,
                               'verses': 28428, 'tsw_and_companion_unchanged': True},
        'source_binding_audits': source_audits,
        'additional_affected_ledgers': earlier_romans,
        'source_sensitive_checks': checks,
        'focused_authoring_reread_count': focus_count,
        'translation_family': family,
        'completed_fifty_chapter_block': completed,
        'active_fifty_chapter_block': block,
        'independent_editorial_review': 'REVIEW_PENDING',
        'whole_book_reviews': 'PENDING; Romans, 1 Corinthians, 2 Corinthians, and Galatians newly queued',
        'reader_testing': 'PENDING',
        'companion_reconciliation': 'PENDING; no quotations or bindings changed',
        'publication_allowed': False,
    }
    dump(R / 'audit/fluent-revision/2026-09-17-ephesians-1-5/verification.json', result)
    print(json.dumps({key: result[key] for key in ['status', 'new_chapters', 'new_verses', 'unique_original_source_records', 'cumulative_coverage']}))


if __name__ == '__main__':
    main()
