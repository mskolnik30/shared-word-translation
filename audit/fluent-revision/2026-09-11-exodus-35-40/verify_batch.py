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
BASE = '93c7c67682f88a08ef36bd3c016ec5b3c3aec34f'
COUNTS = {35:35, 36:38, 37:29, 38:31, 39:43, 40:38}
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
    assert len(audits) == 20
    assert sum(a['verses'] for a in audits) == 2854
    assert len(chapter_paths) == 95
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
    assert len(by_ref) == 214
    expected_mapping = {f'{c}:{v}': f'Exod {c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
    assert {ref:row['source_reference'] for ref,row in by_ref.items()} == expected_mapping
    annotated_refs = [ref for ref,row in by_ref.items() if '<note' in raw[row['source_reference']]]
    assert set(annotated_refs) == {'35:7','35:11','36:2','37:8','39:4','39:33'}
    for ref, row in by_ref.items():
        assert row['source_verse_sha256'] == hashlib.sha256(raw[row['source_reference']].encode()).hexdigest()
    assert all(tag in raw['Exod 37:8'] for tag in ('type="variant"', 'type="x-ketiv"', 'type="x-qere"'))

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

    checks = {
        '35:2':['put to death'], '35:25':['woman','her own hands'],
        '35:26':['women','skill','goat hair'], '35:30':['Bezalel','Uri','Hur','Judah'],
        '35:34':['teach','Oholiab','Ahisamach','Dan'],
        '36:6':['No man or woman'], '36:8':['ten curtains','The craftsman'],
        '37:1':['two and a half','a cubit and a half'],
        '37:25':['a cubit long','a cubit wide','two cubits high'],
        '38:8':['mirrors','women','served'],
        '38:24':['twenty-nine talents','seven hundred thirty'],
        '38:25':['a hundred talents','one thousand seven hundred seventy-five'],
        '38:26':['beka','half a shekel','twenty years','six hundred three thousand five hundred fifty'],
        '38:27':['a hundred bases','one talent per base'],
        '38:28':['one thousand seven hundred seventy-five'],
        '38:29':['seventy talents','two thousand four hundred'],
        '39:30':['Holy to the LORD'], '39:43':['Moses blessed them'],
        '40:17':['first day','first month','second year'],
        '40:22':['north','outside the dividing curtain'], '40:24':['opposite the table','south'],
        '40:31':['Moses, Aaron, and Aaron’s sons','would wash','hands and feet'],
        '40:33':['Moses finished the work'], '40:35':['Moses could not enter'],
        '40:37':['would not set out until'], '40:38':['by day','in it by night','whole house of Israel']
    }
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    # Arithmetic of the stated silver inventory, not historical validation of the census.
    assert 603550 / 2 == 100 * 3000 + 1775
    # Preserve exact repeated fulfillment formula and the alternation around the hem.
    refrain='just as the LORD had commanded Moses'
    for c, verses in {39:[1,5,7,21,26,29,31,32,42],40:[19,21,23,25,27,29,32]}.items():
        found=[v for v in range(1,COUNTS[c]+1) if refrain in by_ref[f'{c}:{v}']['after']]
        assert found == verses, (c,found)
    assert by_ref['39:25']['after'].count('between the pomegranates') == 2
    assert by_ref['39:26']['after'].lower().count('a bell and a pomegranate') == 2
    assert 'linen' not in by_ref['39:24']['after']
    for c in (34,35):
        assert 'glory filled the tabernacle' in by_ref[f'40:{c}']['after']
    # Provisional stone names must agree with the corresponding command, in the same rows.
    prior_28=(ROOT/'translations/fluent/OT/exodus/Exodus_28.md').read_text()
    for old_v,new_v,stones in [(17,10,['carnelian','topaz','emerald']),(18,11,['turquoise','sapphire','moonstone']),(19,12,['jacinth','agate','amethyst']),(20,13,['beryl','onyx','jasper'])]:
        old_line=re.search(rf'^v{old_v:02}: (.*)$',prior_28,re.M)[1]
        assert all(stone in old_line and stone in by_ref[f'39:{new_v}']['after'] for stone in stones)
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=40}
    assert len(exodus_refs)==len(set(exodus_refs))==1213 and set(exodus_refs)==expected
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

    overlap = {'scope': 'Exodus 35–40 only; 214 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 35–40; 214 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 95, 'verses': 2854},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_hashed_in_full': annotated_refs,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read all 214 pinned Hebrew records including annotations, drafted independently, then read all TSW comparators and consulted supplemental NET notes for chapters 35, 38, 39 and 40. It reread the assembled English and checked command/fulfillment terminology, measurements, materials, inventories, names and gemstone rows against chapters 25–31. Focused risks include women’s skilled labor, unnamed singular/plural artisan shifts, uncertain skins and textile terms, metal totals, exact repetitions, Moses among habitual washing users, and Moses unable to enter the glory-filled tabernacle. This is an authoring self-check, not independent scholarly review.',
        'exodus_source_references_unique_through_40': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 95, 'verses': 2854, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
