"""Verify source bindings, preservation boundaries, and this batch's focused risks.

Run from the repository with --genesis-source and --james-source pointing to
exact original source files. These checks cannot establish editorial fidelity.
"""
from pathlib import Path
from difflib import SequenceMatcher
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).resolve().parent
BASE = '0e79100131d031eae2486981c986e2402f00eb0b'
COUNTS = {42: 38, 43: 34, 44: 34, 45: 28}
sys.path.insert(0, str(ROOT / 'tools'))
from audit_translation_overlap import words

def run(*args):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()

def put_json(name, value):
    (BATCH / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--genesis-source', required=True, type=Path)
    parser.add_argument('--james-source', required=True, type=Path)
    args = parser.parse_args()
    queue = json.loads((ROOT / 'audit/fluent-revision/WORK_QUEUE.json').read_text())
    audits = []
    chapter_paths = set()
    all_genesis_sources = set()
    for scope in queue['completed_draft_scopes']:
        ledger_path = ROOT / scope['ledger']
        ledger = json.loads(ledger_path.read_text())
        source_path = args.james_source if scope['scope'].startswith('James') else args.genesis_source
        result = json.loads(run(sys.executable, 'tools/audit_fluent_revision.py', scope['ledger'], '--source-text', str(source_path.resolve())))
        audits.append({'ledger': scope['ledger'], **result})
        for chapter in ledger['chapters']:
            assert chapter['path'] not in chapter_paths
            chapter_paths.add(chapter['path'])
        if scope['scope'].startswith('Genesis'):
            references = {v['source_reference'] for v in ledger['verses']}
            assert not all_genesis_sources.intersection(references)
            all_genesis_sources.update(references)
    assert len(audits) == 8
    assert sum(a['verses'] for a in audits) == 1495
    assert len(chapter_paths) == 50
    assert len(all_genesis_sources) == 1387

    text = args.genesis_source.read_text()
    raw = {f'Gen {int(c)}:{int(v)}': verse for verse in re.findall(r'<verse\b[^>]*>.*?</verse>', text, re.S)
           for c, v in [re.search(r'osisID="Gen\.(\d+)\.(\d+)"', verse).groups()]}
    assert len(raw) == 1533
    assert 'type="x-qere"' in raw['Gen 43:28']
    ledger = json.loads((BATCH / 'genesis-verse-review.json').read_text())
    by_ref = {v['reference'].replace('Genesis ', ''): v for v in ledger['verses']}
    assert len(by_ref) == 134
    assert by_ref['43:28']['source_verse_sha256'] == hashlib.sha256(raw['Gen 43:28'].encode()).hexdigest()

    for chapter, count in COUNTS.items():
        chapter_text = (ROOT / f'translations/fluent/OT/genesis/Genesis_{chapter:02}.md').read_text()
        main_text = chapter_text.split('## Notes', 1)[0]
        assert re.findall(r'^v(\d\d):', main_text, re.M) == [f'{v:02}' for v in range(1, count + 1)]
        assert main_text.count('<p>') == main_text.count('</p>')
        assert main_text.count('“') == main_text.count('”')
        for required in ('qa_scope: structural', 'editorial_status: REVIEW_PENDING', 'publication_allowed: false'):
            assert required in chapter_text
        # No sentence is broken by a new heading or paragraph marker.
        for prior, following in zip(main_text.split('</p>')[:-1], main_text.split('</p>')[1:]):
            end = prior.rstrip()
            assert not end.endswith((',', '—', ':')), (chapter, end[-100:])

    checks = {
        '42:3': ['ten'], '42:13': ['twelve', 'no longer with us'],
        '42:17': ['three days'], '42:21': ['anguish', 'pleaded', 'would not listen'],
        '42:24': ['Simeon', 'bound him', 'wept'],
        '42:37': ['two sons to death'], '42:38': ['Sheol', 'gray head'],
        '43:11': ['balm', 'honey', 'gum', 'resin', 'pistachios', 'almonds'],
        '43:12': ['twice', 'return'], '43:14': ['compassion', 'bereaved'],
        '43:23': ['Peace', 'Simeon'], '43:30': ['compassion', 'wept'],
        '43:32': ['separately', 'abomination'], '43:34': ['five times', 'became drunk'],
        '44:2': ['Put my cup', 'youngest'], '44:5': ['divination'],
        '44:9': ['die', 'slaves'], '44:10': ['my slave', 'free of blame'],
        '44:15': ['divination'], '44:20': ['full brother is dead'],
        '44:22': ['his father will die'], '44:30': ['father’s life is bound'],
        '44:33': ['my lord’s slave', 'in the young man’s place'],
        '45:4': ['whom you sold'], '45:5': ['God sent me', 'preserve life'],
        '45:6': ['two years', 'five more', 'plowing', 'harvest'],
        '45:7': ['remnant', 'deliverance'], '45:8': ['father to Pharaoh'],
        '45:10': ['Goshen', 'grandchildren', 'flocks', 'herds'],
        '45:22': ['three hundred', 'five changes'],
        '45:23': ['ten male donkeys', 'ten female donkeys', 'grain, bread'],
        '45:28': ['Israel', 'before I die'],
    }
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    assert by_ref['43:3']['after'].split('‘')[1].split('’')[0] == by_ref['43:5']['after'].split('‘')[1].split('’')[0]
    assert 'live and not die' in by_ref['42:2']['after'] and 'live and not die' in by_ref['43:8']['after']
    assert 'all my life' in by_ref['43:9']['after'] and 'all my life' in by_ref['44:32']['after']

    reviewdir = 'audit/exegetical-core/fluent-production/genesis/'
    allowed = {'audit/fluent-revision/WORK_QUEUE.json'}
    allowed.update(f'translations/fluent/OT/genesis/Genesis_{c:02}.md' for c in COUNTS)
    allowed.update(reviewdir + f'Genesis_{c:02}_review.json' for c in COUNTS)
    allowed.update(reviewdir + n for n in ('APPROVE_QA.json', 'BOOK_VERSE_REVIEW_LEDGER.json', 'GENESIS_FLUENT_BOOK_QA.json'))
    batch_prefix = str(BATCH.relative_to(ROOT)) + '/'
    changed = run('git', 'diff', '--name-only', BASE).splitlines()
    untracked = run('git', 'ls-files', '--others', '--exclude-standard').splitlines()
    assert all(p in allowed or p.startswith(batch_prefix) for p in changed + untracked)
    for name in ('APPROVE_QA.json', 'BOOK_VERSE_REVIEW_LEDGER.json', 'GENESIS_FLUENT_BOOK_QA.json'):
        old = json.loads(run('git', 'show', BASE + ':' + reviewdir + name))
        new = json.loads((ROOT / reviewdir / name).read_text())
        assert new['revision_batches'][:-1] == old['revision_batches']
        assert new['publication_allowed'] is False
        if 'entries' in old:
            for previous, current in zip(old['entries'], new['entries']):
                if previous['chapter'] not in COUNTS:
                    assert previous == current

    overlap = {'scope': 'Genesis 42–45 only; 134 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
    for stage in ('before', 'after'):
        rows = []
        for row in ledger['verses']:
            a, b = words(row[stage]), words(row['tsw_comparator'])
            rows.append({'reference': row['reference'], 'identical': a == b, 'similarity': round(SequenceMatcher(None, a, b, autojunk=False).ratio(), 6)})
        overlap['stages'][stage] = {'identical_verses': sum(r['identical'] for r in rows), 'near_identical_verses': sum(not r['identical'] and r['similarity'] >= .9 for r in rows), 'mean_similarity': round(sum(r['similarity'] for r in rows) / len(rows), 6), 'verses': rows}
    put_json('overlap-before-after.json', overlap)
    family = run(sys.executable, 'tools/audit_translation_family.py')
    diff = run('git', 'diff', '--check')
    put_json('verification.json', {
        'status': 'PASSED', 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'base_commit': BASE, 'scope': 'Genesis 42–45; 134 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 50, 'verses': 1495},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_45': len(all_genesis_sources),
        'focused_assertions': checks,
        'written_read_record_43_28_hashed_in_full': True,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_later_Genesis_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every Hebrew verse before drafting, then read TSW comparators and reread the assembled English. Local corrections clarified kinship, preserved completed footwashing, and avoided equating Joseph’s rank with Pharaoh’s. This is not independent editorial review.',
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 50, 'verses': 1495, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
