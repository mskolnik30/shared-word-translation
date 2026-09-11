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
BASE = '261f9177666af1d8abf9c3f5723327a0f8057d60'
COUNTS = {9: 35, 10: 29, 11: 10}
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
    assert len(audits) == 13
    assert sum(a['verses'] for a in audits) == 1925
    assert len(chapter_paths) == 66
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
    assert len(by_ref) == 74
    for ref in ('10:1','11:8'):
        assert '<note' in raw['Exod ' + ref]
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
        '9:3':['LORD’s hand','in the fields','horses, donkeys, camels, cattle, sheep, and goats'],
        '9:4':['Not one animal'], '9:5':['Tomorrow'], '9:6':['All Egypt’s livestock died','not one animal'],
        '9:8':['soot from a kiln','Moses is to throw'], '9:9':['people and animals'],
        '9:11':['could not stand','all the Egyptians'], '9:12':['LORD hardened'],
        '9:14':['your very heart','your servants','your people'], '9:15':['could have','wiping you'],
        '9:16':['kept you standing','my power','my name'], '9:17':['set yourself above'],
        '9:18':['About this time tomorrow'], '9:19':['shelter','Every person or animal','die'],
        '9:20':['feared','slaves and livestock'], '9:21':['did not take','slaves and livestock'],
        '9:23':['thunder and hail','fire'], '9:25':['people and animals','every plant','every tree'],
        '9:26':['Goshen'], '9:27':['This time I have sinned','righteous'], '9:28':['God’s thunder'],
        '9:29':['spread out my hands','earth belongs to the LORD'], '9:30':['not yet fear'],
        '9:31':['flax and barley','barley was in the ear','flax was in bud'],
        '9:32':['wheat and spelt','not struck down','ripen later'],
        '9:34':['he sinned again','He and his servants hardened their hearts'], '9:35':['heart remained hard'],
        '10:1':['I have hardened','his servants’ hearts'], '10:2':['son and your grandson','mockery','you all'],
        '10:5':['hail left'], '10:6':['fathers nor their fathers'], '10:7':['snare','Let the men go'],
        '10:9':['young and old','sons and daughters','flocks and herds'], '10:10':['little ones','evil lies ahead'],
        '10:11':['You men','driven out'], '10:13':['east wind','all that day and all night','Morning'],
        '10:15':['Nothing green remained'], '10:17':['forgive my sin','just this once','only this death'],
        '10:19':['west wind','Sea of Reeds','Not one locust'], '10:20':['LORD hardened'],
        '10:21':['darkness that can be felt'], '10:22':['three days'], '10:23':['three days','all the Israelites had light'],
        '10:24':['flocks and herds must stay','little ones may go'], '10:25':['You yourself','burnt offerings'],
        '10:26':['Not a hoof','will not know','until we get there'], '10:27':['LORD hardened','Pharaoh was unwilling'],
        '10:28':['see my face','you will die'], '10:29':['not see your face again'],
        '11:1':['one more plague','drive you out completely'], '11:2':['silver and gold','each man','each woman'],
        '11:4':['About midnight'], '11:5':['Every firstborn','slave woman','mill','animals'],
        '11:6':['great cry'], '11:7':['dog','person or an animal','you all'],
        '11:8':['bow before me','Moses left Pharaoh in fierce anger'], '11:10':['LORD hardened'],
    }
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    assert by_ref['9:2']['after'].endswith(',') and by_ref['9:3']['after'].startswith('the LORD')
    assert by_ref['10:1']['after'].endswith(',') and by_ref['10:2']['after'].startswith('and so')
    for v in range(1,11):
        assert not re.match(r'^\d+\s', by_ref[f'11:{v}']['after'])
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=11}
    assert len(exodus_refs)==len(set(exodus_refs))==284 and set(exodus_refs)==expected
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

    overlap = {'scope': 'Exodus 9–11 only; 74 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 9–11; 74 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 66, 'verses': 1925},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_10_1_and_11_8_hashed_in_full': True,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every Hebrew verse, drafted from that source with supplemental grammatical notes, read all TSW comparators, and reread the assembled English. Final corrections restored the height image in 9:17 and the fathers/fathers repetition in 10:6. Focused checks cover animal and crop scope, wind directions, intervals, explicit hardening agents, restricted household departure, firstborn harm, and the transition at 11:1–8. This is not independent editorial review.',
        'exodus_source_references_unique_through_11': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 66, 'verses': 1925, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
