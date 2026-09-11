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
BASE = 'edf306f499fd56e328c803b41a418606b8a7a0b3'
COUNTS = {7: 25, 8: 32}
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
    assert len(audits) == 12
    assert sum(a['verses'] for a in audits) == 1851
    assert len(chapter_paths) == 63
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
    assert len(by_ref) == 57
    for ref in ('7:10',):
        assert '<note' in raw['Exod ' + ref] and 'Leningrad Codex' in raw['Exod ' + ref]
        assert by_ref[ref]['source_verse_sha256'] == hashlib.sha256(raw['Exod ' + ref].encode()).hexdigest()

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
        '7:1':['like God to Pharaoh','your prophet'], '7:3':['I will harden Pharaoh’s heart','signs and wonders'],
        '7:4':['my hand','my companies','my people','judgment'], '7:7':['eighty years','eighty-three'],
        '7:9':['your staff','serpent'], '7:10':['Aaron threw his staff'], '7:12':['Aaron’s staff swallowed their staffs'],
        '7:13':['heart grew hard'], '7:14':['heart is unyielding'], '7:15':['morning','snake'],
        '7:16':['Let my people go','serve me','not listened'], '7:17':['staff in my hand','blood'],
        '7:18':['fish','die','stink','struggle'], '7:19':['rivers, canals, ponds','wood and stone'],
        '7:20':['He raised','before the eyes','All the water'], '7:21':['could not drink'],
        '7:22':['heart remained hard'], '7:23':['take even this to heart'], '7:24':['dug'],
        '7:25':['Seven full days','LORD struck'], '8:3':['teem','bedroom','bed','ovens','kneading bowls'],
        '8:4':['onto you','your people','all your servants'], '8:5':['Aaron','staff'],
        '8:6':['Aaron stretched'], '8:7':['magicians','brought frogs'], '8:9':['only in the Nile'],
        '8:10':['Tomorrow','Pharaoh answered'], '8:11':['only in the Nile'],
        '8:13':['houses, courtyards, and fields'], '8:14':['heaps upon heaps','stank'],
        '8:15':['he hardened his heart'], '8:16':['dust of the ground','gnats'],
        '8:17':['people and animals','all the dust'], '8:18':['could not','people and animals'],
        '8:19':['finger of God','heart remained hard'], '8:22':['Goshen','No swarms','midst of the land'],
        '8:23':['redeeming','set them apart','tomorrow'], '8:24':['land was being ruined'],
        '8:25':['here in the land'], '8:26':['abomination','stone us'], '8:27':['three days'],
        '8:28':['not go far at all','Plead for me'], '8:29':['Pharaoh must not deceive us again'],
        '8:31':['Not one remained'], '8:32':['Pharaoh hardened his heart'],
    }
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    mapped = set()
    for row in ledger['verses']:
        c,v=map(int,row['reference'].replace('Exodus ','').split(':'))
        sc,sv=(c,v) if c==7 else ((7,v+25) if v<=4 else (8,v-4))
        assert row['source_reference']==f'Exod {sc}:{sv}'
        mapped.add(row['source_reference'])
        if c==8:
            assert f'KJV:Exod.8.{v}' in raw[row['source_reference']]
    expected = {f'Exod 7:{v}' for v in range(1,30)} | {f'Exod 8:{v}' for v in range(1,29)}
    assert mapped==expected and len(mapped)==57
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    assert len(exodus_refs)==len(set(exodus_refs))==210
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

    overlap = {'scope': 'Exodus 7–8 only; 57 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 7–8; 57 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 63, 'verses': 1851},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotation_7_10_and_versification_notes_hashed_in_full': True,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every Hebrew verse, drafted from that source with supplemental grammatical notes, read all TSW comparators, and reread the assembled English. Focused checks cover explicit and unstated hardening agents, staff ownership and unnamed performer, creatures, water and animal harm, timing, the redemption noun, and public/source numbering. This is not independent editorial review.',
        'public_hebrew_versification': 'All 57 source records mapped exactly once; public 8:1–4 = Hebrew 7:26–29 and public 8:5–32 = Hebrew 8:1–28. The XML KJV reference notes independently corroborate each chapter 8 mapping.',
        'exodus_source_references_unique_through_8': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 63, 'verses': 1851, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
