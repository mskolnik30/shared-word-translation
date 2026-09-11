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
BASE = 'ca1e05676715f295505039047dbd80f97755d0d4'
COUNTS = {21: 36, 22: 31, 23: 33, 24: 18}
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
    assert len(audits) == 16
    assert sum(a['verses'] for a in audits) == 2304
    assert len(chapter_paths) == 79
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
    assert len(by_ref) == 118
    expected_mapping = {
        f'{c}:{v}': ('Exod 21:37' if v == 1 else f'Exod 22:{v-1}') if c == 22 else f'Exod {c}:{v}'
        for c,n in COUNTS.items() for v in range(1,n+1)
    }
    assert {ref:row['source_reference'] for ref,row in by_ref.items()} == expected_mapping
    annotated_refs = [ref for ref,row in by_ref.items() if '<note' in raw[row['source_reference']]]
    assert {'21:8','22:1','22:5','22:27'} <= set(annotated_refs)
    assert all(f'22:{v}' in annotated_refs for v in range(1,32))
    for ref, row in by_ref.items():
        assert row['source_verse_sha256'] == hashlib.sha256(raw[row['source_reference']].encode()).hexdigest()
    assert all(tag in raw['Exod 21:8'] for tag in ('type="variant"', 'type="x-ketiv"', 'type="x-qere"'))

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

    checks = {'21:2': ['six years', 'seventh year', 'without payment'], '21:4': ['wife and her children belong', 'leave alone'], '21:6': ['before God', 'doorpost', 'awl', 'permanently'], '21:8': ['for himself', 'redeemed', 'foreign people', 'betrayed'], '21:10': ['food', 'clothing', 'marital rights'], '21:13': ['did not lie in wait', 'God let it happen'], '21:14': ['attacks', 'kill', 'deceit', 'altar', 'death'], '21:16': ['kidnaps', 'sold', 'possession'], '21:20': ['male or female slave', 'rod', 'avenged'], '21:21': ['day or two', 'no vengeance', 'his money'], '21:22': ['pregnant woman', 'her children come out', 'no harm', 'husband', 'judges'], '21:23': ['harm occurs', 'life for life'], '21:24': ['eye for eye', 'tooth for tooth', 'hand for hand', 'foot for foot'], '21:25': ['burn for burn', 'wound for wound', 'bruise for bruise'], '21:26': ['male or female slave', 'eye', 'go free'], '21:27': ['tooth', 'go free'], '21:29': ['known to gore', 'warned', 'failed', 'man or woman', 'owner must also'], '21:30': ['If a ransom', 'redeem his life'], '21:32': ['thirty shekels', 'master', 'stoned'], '21:35': ['living ox', 'divide its price', 'divide the dead'], '21:36': ['ox for ox', 'dead animal becomes his'], '22:1': ['five cattle', 'four sheep or goats'], '22:3': ['sun has risen', 'bloodguilt', 'sold'], '22:4': ['alive', 'double'], '22:5': ['best of their own'], '22:9': ['before God', 'double'], '22:11': ['oath before the LORD', 'owner must accept', 'need not'], '22:12': ['stolen', 'make restitution'], '22:14': ['owner is absent', 'full restitution'], '22:15': ['owner is present', 'no restitution', 'hired'], '22:16': ['virgin', 'not pledged', 'bride-price'], '22:17': ['father', 'refuses', 'still pay'], '22:18': ['sorceress', 'live'], '22:20': ['devoted to destruction'], '22:24': ['I will kill', 'wives', 'widows', 'fatherless'], '22:25': ['poor', 'Do not charge them interest'], '22:26': ['before the sun sets'], '22:27': ['skin', 'sleep', 'I will hear'], '22:29': ['firstborn of your sons'], '22:30': ['seven days', 'eighth day'], '22:31': ['holy', 'torn apart', 'dogs'], '23:3': ['Do not favor a poor person'], '23:5': ['hates you', 'help'], '23:6': ['Do not deny a poor person'], '23:11': ['seventh year', 'poor', 'wild animals', 'vineyard', 'olive grove'], '23:12': ['six days', 'seventh day', 'ox and donkey', 'son of your female slave', 'foreigner'], '23:15': ['seven days', 'Abib', 'Egypt', 'empty-handed'], '23:16': ['Harvest', 'Ingathering', 'year’s end'], '23:17': ['Three times', 'all your males', 'Lord GOD'], '23:18': ['blood', 'leavened', 'fat', 'morning'], '23:19': ['young goat', 'mother’s milk'], '23:21': ['not pardon', 'my name is within him'], '23:23': ['Amorites, Hittites, Perizzites, Canaanites, Hivites, and Jebusites', 'wipe them out'], '23:25': ['he will bless', 'I will remove'], '23:28': ['hornet', 'Hivites, Canaanites, and Hittites'], '23:29': ['single year', 'desolate', 'wild animals'], '23:30': ['Little by little'], '23:31': ['Sea of Reeds', 'sea of the Philistines', 'wilderness', 'River', 'drive them out'], '24:1': ['Aaron, Nadab, Abihu', 'seventy', 'distance'], '24:2': ['Moses alone', 'others must not', 'people must not'], '24:3': ['all the rulings', 'one voice'], '24:4': ['twelve pillars', 'twelve tribes'], '24:5': ['young Israelite men', 'bulls', 'burnt offerings', 'peace offerings'], '24:6': ['half', 'basins', 'altar'], '24:7': ['covenant document', 'read it aloud', 'we will obey'], '24:8': ['splashed it on the people', 'blood of the covenant'], '24:9': ['Aaron, Nadab, Abihu', 'seventy'], '24:10': ['saw the God of Israel', 'his feet', 'something like'], '24:11': ['did not lay his hand', 'beheld God', 'ate and drank'], '24:12': ['stone tablets', 'I have written', 'teach the people'], '24:13': ['Joshua'], '24:14': ['Aaron and Hur', 'dispute'], '24:16': ['six days', 'seventh day'], '24:18': ['forty days and forty nights']}
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref,term)
    assert 'miscarriage' not in by_ref['21:22']['after'].lower()
    assert 'premature' not in by_ref['21:22']['after'].lower()
    for left,right in [('21:5','21:6'),('21:18','21:19'),('21:23','21:24'),('21:24','21:25'),('21:33','21:34'),('22:10','22:11'),('22:26','22:27')]:
        assert by_ref[left]['after'].endswith((',', '’')) and by_ref[right]['after'][0].islower()
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=24}
    assert len(exodus_refs)==len(set(exodus_refs))==663 and set(exodus_refs)==expected
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

    overlap = {'scope': 'Exodus 21–24 only; 118 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 21–24; 118 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 79, 'verses': 2304},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_hashed_in_full': annotated_refs,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read all 118 pinned Hebrew records including annotations, composed the English from Hebrew, consulted NET lexical/grammatical notes (21–22 before drafting, 23–24 after drafting), read every TSW comparator after drafting, and reread the assembled English. Focused checks address legal conditions and exceptions, enslaved people and real harm, birth/harm ambiguity, monetary and calendar numbers, named peoples, divine agency, covenant blood, direct seeing of God, and the public/Hebrew numbering shift. Peace-offering terminology was aligned to 20:24. This is an authoring self-check, not independent scholarly review.',
        'exodus_source_references_unique_through_24': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 79, 'verses': 2304, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
