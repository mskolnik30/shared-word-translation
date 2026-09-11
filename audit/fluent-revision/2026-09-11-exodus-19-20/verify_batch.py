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
BASE = '56be98df7ec092ace1d876a1223597b4f5a5db77'
COUNTS = {19: 25, 20: 26}
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
    parser.add_argument('--exodus-source', required=True, type=Path)
    args = parser.parse_args()
    queue = json.loads((ROOT / 'audit/fluent-revision/WORK_QUEUE.json').read_text())
    audits = []
    chapter_paths = set()
    all_genesis_sources = set()
    for scope in queue['completed_draft_scopes']:
        ledger_path = ROOT / scope['ledger']
        ledger = json.loads(ledger_path.read_text())
        source_path = {'James': args.james_source, 'Genesis': args.genesis_source, 'Exodus': args.exodus_source}[scope['scope'].split()[0]]
        result = json.loads(run(sys.executable, 'tools/audit_fluent_revision.py', scope['ledger'], '--source-text', str(source_path.resolve())))
        audits.append({'ledger': scope['ledger'], **result})
        for chapter in ledger['chapters']:
            assert chapter['path'] not in chapter_paths
            chapter_paths.add(chapter['path'])
        if scope['scope'].startswith('Genesis'):
            references = {v['source_reference'] for v in ledger['verses']}
            assert not all_genesis_sources.intersection(references)
            all_genesis_sources.update(references)
    assert len(audits) == 15
    assert sum(a['verses'] for a in audits) == 2186
    assert len(chapter_paths) == 75
    assert len(all_genesis_sources) == 1533

    text = args.genesis_source.read_text()
    raw = {f'Gen {int(c)}:{int(v)}': verse for verse in re.findall(r'<verse\b[^>]*>.*?</verse>', text, re.S)
           for c, v in [re.search(r'osisID="Gen\.(\d+)\.(\d+)"', verse).groups()]}
    assert len(raw) == 1533
    assert all_genesis_sources == set(raw)
    text = args.exodus_source.read_text()
    raw = {f'Exod {int(c)}:{int(v)}': verse for verse in re.findall(r'<verse\b[^>]*>.*?</verse>', text, re.S)
           for c, v in [re.search(r'osisID="Exod\.(\d+)\.(\d+)"', verse).groups()]}
    assert len(raw) == 1213
    ledger = json.loads((BATCH / 'exodus-verse-review.json').read_text())
    by_ref = {v['reference'].replace('Exodus ', ''): v for v in ledger['verses']}
    assert len(by_ref) == 51
    annotated_refs = [ref for ref in by_ref if '<note' in raw['Exod '+ref]]
    assert {'20:2','20:3','20:4','20:5','20:6','20:8','20:9','20:10','20:13','20:14','20:15'} <= set(annotated_refs)
    for ref in annotated_refs:
        assert by_ref[ref]['source_verse_sha256'] == hashlib.sha256(raw['Exod '+ref].encode()).hexdigest()

    for chapter, count in COUNTS.items():
        chapter_text = (ROOT / f'translations/fluent/OT/exodus/Exodus_{chapter:02}.md').read_text()
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

    checks = {'19:1': ['third month', 'Sinai'], '19:2': ['Rephidim'], '19:3': ['house of Jacob', 'Israelites'], '19:4': ['eagles’ wings', 'to myself'], '19:5': ['if', 'covenant', 'treasured possession', 'whole earth'], '19:6': ['kingdom of priests', 'holy nation'], '19:8': ['All the people', 'everything'], '19:10': ['today and tomorrow', 'wash'], '19:11': ['third day'], '19:12': ['edge', 'put to death'], '19:13': ['No hand', 'stoned or shot', 'animal or human', 'long blast', 'go up'], '19:15': ['third day', 'sexual relations with a woman'], '19:16': ['third day', 'thunder and lightning', 'horn', 'trembled'], '19:18': ['fire', 'kiln', 'whole mountain shook'], '19:19': ['louder and louder', 'voice'], '19:22': ['priests', 'break out'], '19:24': ['Aaron', 'priests and the people'], '20:2': ['house of slavery'], '20:3': ['no other gods before me'], '20:4': ['carved image', 'heavens above', 'earth below', 'waters beneath'], '20:5': ['jealous', 'fathers’ guilt', 'third and fourth', 'hate me'], '20:6': ['faithful love', 'thousands', 'love me'], '20:7': ['misuse', 'guiltless'], '20:8': ['Remember', 'Sabbath', 'holy'], '20:9': ['six days'], '20:10': ['seventh day', 'son or daughter', 'male or female slave', 'livestock', 'foreigner', 'gates'], '20:11': ['six days', 'heavens', 'earth', 'sea', 'rested', 'blessed'], '20:12': ['father', 'mother', 'ground'], '20:13': ['Do not murder'], '20:14': ['adultery'], '20:15': ['steal'], '20:16': ['false testimony', 'neighbor'], '20:17': ['house', 'wife', 'male or female slave', 'ox or donkey'], '20:18': ['thunder', 'horn', 'smoking'], '20:20': ['Do not be afraid', 'fear of him', 'test', 'not sin'], '20:22': ['from heaven'], '20:23': ['silver', 'gold'], '20:24': ['altar of earth', 'burnt offerings', 'peace offerings', 'I cause my name'], '20:25': ['cut stones', 'tool', 'profane'], '20:26': ['steps', 'nakedness']}
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref,term)
    assert by_ref['20:17']['after'].count('Do not covet') == 2
    assert by_ref['20:5']['after'].endswith(',') and by_ref['20:6']['after'].startswith('but')
    assert by_ref['20:9']['after'].endswith(',') and by_ref['20:10']['after'].startswith('but')
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=20}
    assert len(exodus_refs)==len(set(exodus_refs))==545 and set(exodus_refs)==expected
    # Poetry and continuation lines must remain inside verse paragraphs.
    for c in COUNTS:
        content = (ROOT / f'translations/fluent/OT/exodus/Exodus_{c:02}.md').read_text().split('---', 2)[2].split('## Notes')[0]
        inside = False
        for line in content.splitlines():
            if line == '<p>':
                assert not inside
                inside = True
            elif line == '</p>':
                assert inside
                inside = False
            elif line.strip() and not line.startswith('## '):
                assert inside, (c, line)
        assert not inside

    reviewdir = 'audit/exegetical-core/fluent-production/exodus/'
    allowed = {'audit/fluent-revision/WORK_QUEUE.json'}
    allowed.update(f'translations/fluent/OT/exodus/Exodus_{c:02}.md' for c in COUNTS)
    allowed.update(reviewdir + f'Exodus_{c:02}_review.json' for c in COUNTS)
    allowed.update(reviewdir + n for n in ('APPROVE_QA.json', 'BOOK_VERSE_REVIEW_LEDGER.json', 'EXODUS_FLUENT_BOOK_QA.json'))
    batch_prefix = str(BATCH.relative_to(ROOT)) + '/'
    changed = run('git', 'diff', '--name-only', BASE).splitlines()
    untracked = run('git', 'ls-files', '--others', '--exclude-standard').splitlines()
    assert all(p in allowed or p.startswith(batch_prefix) for p in changed + untracked)
    for name in ('APPROVE_QA.json', 'BOOK_VERSE_REVIEW_LEDGER.json', 'EXODUS_FLUENT_BOOK_QA.json'):
        old = json.loads(run('git', 'show', BASE + ':' + reviewdir + name))
        new = json.loads((ROOT / reviewdir / name).read_text())
        assert new['revision_batches'][:-1] == old.get('revision_batches', [])
        assert new['publication_allowed'] is False
        if 'entries' in old:
            for previous, current in zip(old['entries'], new['entries']):
                if previous['chapter'] not in COUNTS:
                    assert previous == current

    overlap = {'scope': 'Exodus 19–20 only; 51 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 19–20; 51 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 75, 'verses': 2186},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_hashed_in_full': annotated_refs,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read all 51 Hebrew verses including the source annotations, drafted from the pinned Hebrew, consulted supplemental lexical and grammatical notes, read all TSW comparators, and reread the assembled English. Focused checks preserve covenant conditions, boundary death sanctions, direct speech, Sabbath household scope, slavery, intergenerational consequences, repeated covet, fear vocabulary and altar restrictions. This is not independent scholarly review.',
        'exodus_source_references_unique_through_20': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 75, 'verses': 2186, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
