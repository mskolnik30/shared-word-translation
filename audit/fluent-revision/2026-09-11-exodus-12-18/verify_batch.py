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
BASE = '33011221029a62782ebeee731bdced92cd74cedf'
COUNTS = {12: 51, 13: 22, 14: 31, 15: 27, 16: 36, 17: 16, 18: 27}
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
    assert len(audits) == 14
    assert sum(a['verses'] for a in audits) == 2135
    assert len(chapter_paths) == 73
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
    assert len(by_ref) == 210
    annotated_refs = [ref for ref in by_ref if '<note' in raw['Exod '+ref]]
    assert {'14:25','14:29','16:2','16:7'} <= set(annotated_refs)
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

    checks = {'12:3': ['tenth', 'each man', 'household'], '12:5': ['year-old male', 'no defect', 'sheep', 'goats'], '12:6': ['fourteenth', 'twilight'], '12:7': ['both doorposts', 'lintel'], '12:8': ['fire', 'unleavened bread', 'bitter herbs'], '12:9': ['raw', 'boiled', 'head, legs, and internal organs'], '12:11': ['belt', 'sandals', 'staff', 'haste', 'Passover'], '12:12': ['every firstborn', 'people and livestock', 'all the gods'], '12:15': ['seven days', 'cut off'], '12:18': ['fourteenth', 'twenty-first'], '12:19': ['resident foreigner', 'native'], '12:23': ['destroyer', 'will not let'], '12:29': ['midnight', 'Pharaoh', 'captive', 'livestock'], '12:30': ['no house without someone dead'], '12:37': ['six hundred thousand men', 'children', 'Rameses', 'Succoth'], '12:40': ['four hundred thirty', 'Egypt'], '12:41': ['four hundred thirty'], '12:44': ['slave', 'bought', 'circumcised'], '12:46': ['one house', 'bones'], '12:48': ['every male', 'No uncircumcised male'], '13:2': ['opens the womb'], '13:5': ['Canaanites, Hittites, Amorites, Hivites, and Jebusites', 'milk and honey'], '13:8': ['son', 'for me'], '13:9': ['hand', 'between your eyes', 'mouth'], '13:13': ['donkey', 'break its neck', 'firstborn son'], '13:15': ['LORD killed', 'redeem'], '13:18': ['Sea of Reeds', 'equipped for battle'], '13:19': ['Joseph’s bones', 'God will surely come to your aid'], '13:20': ['Etham'], '13:21': ['cloud by day', 'fire by night'], '14:2': ['Pi-hahiroth', 'Migdol', 'Baal-zephon'], '14:4': ['I will harden'], '14:7': ['six hundred chosen chariots'], '14:8': ['LORD hardened', 'raised hand'], '14:17': ['harden the Egyptians’ hearts'], '14:20': ['cloud and darkness', 'lit up the night'], '14:21': ['All night', 'east wind', 'dry ground'], '14:22': ['right', 'left'], '14:25': ['took off', 'wheels'], '14:27': ['fled toward', 'shook'], '14:28': ['Not one'], '14:30': ['dead on the seashore'], '15:1': ['horse and rider'], '15:2': ['Yah', 'salvation', 'father’s God'], '15:3': ['warrior'], '15:5': ['stone'], '15:6': ['Your right hand, LORD', 'your right hand, LORD'], '15:8': ['nostrils', 'heap', 'congealed', 'heart'], '15:10': ['lead'], '15:11': ['among the gods'], '15:12': ['earth swallowed'], '15:13': ['faithful love', 'redeemed'], '15:15': ['Edom', 'Moab', 'Canaan'], '15:16': ['until your people', 'until the people'], '15:17': ['plant', 'inheritance', 'LORD', 'Lord'], '15:20': ['Miriam the prophetess', 'Aaron’s sister', 'all the women'], '15:22': ['Shur', 'three days'], '15:27': ['twelve springs', 'seventy palm'], '16:1': ['fifteenth', 'second month', 'Sin', 'Sinai'], '16:4': ['rain bread', 'test'], '16:12': ['twilight'], '16:16': ['omer for each person'], '16:18': ['nothing left over', 'no shortage'], '16:20': ['worms', 'stank'], '16:22': ['two omers'], '16:24': ['did not stink', 'no worms'], '16:25': ['today'], '16:28': ['you all'], '16:29': ['bread for two days', 'sixth day'], '16:31': ['coriander', 'white', 'honey'], '16:34': ['testimony'], '16:35': ['forty years', 'edge of Canaan'], '16:36': ['one-tenth', 'ephah'], '17:3': ['us', 'me, my children, and my livestock'], '17:5': ['you struck the Nile'], '17:6': ['Horeb', 'elders'], '17:7': ['Massah', 'Meribah'], '17:12': ['Aaron and Hur', 'one on each side', 'sunset'], '17:13': ['edge of the sword'], '17:14': ['blot out the memory of Amalek'], '17:16': ['Yah’s throne', 'generation to generation'], '18:2': ['Zipporah', 'sent away'], '18:3': ['two sons', 'Gershom'], '18:4': ['Eliezer', 'father’s God'], '18:11': ['greater than all the gods'], '18:12': ['Jethro', 'burnt offering', 'Aaron', 'elders'], '18:21': ['capable men', 'fear God', 'trustworthy', 'dishonest gain', 'thousands, hundreds, fifties, and tens'], '18:23': ['God commands'], '18:25': ['thousands, hundreds, fifties, and tens'], '18:26': ['difficult', 'minor']}
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref,term)
    assert by_ref['15:1']['after'].split('horse and rider')[1] == by_ref['15:21']['after'].split('horse and rider')[1].rstrip('”')
    assert by_ref['16:25']['after'].lower().count('today') == 3
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=18}
    assert len(exodus_refs)==len(set(exodus_refs))==494 and set(exodus_refs)==expected
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

    overlap = {'scope': 'Exodus 12–18 only; 210 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 12–18; 210 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 73, 'verses': 2135},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_hashed_in_full': annotated_refs,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every pinned Hebrew verse, drafted each verse independently, consulted supplemental grammatical notes, read all TSW comparators, and reread the assembled English. Focused checks address Passover dates and participants, firstborn harm, source-specific wheel removal, repeated hand and song imagery, written/read forms, manna quantities and Sabbath exception, ambiguous throne clause and judicial selection. This is not independent editorial review.',
        'exodus_source_references_unique_through_18': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 73, 'verses': 2135, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
