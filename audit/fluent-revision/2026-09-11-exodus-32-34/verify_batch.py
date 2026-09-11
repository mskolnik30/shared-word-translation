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
BASE = 'e7fb160695a2c6d05689ea86fe548f49c5a40c9e'
COUNTS = {32: 35, 33: 23, 34: 35}
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
    assert len(audits) == 19
    assert sum(a['verses'] for a in audits) == 2640
    assert len(chapter_paths) == 89
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
    assert len(by_ref) == 93
    expected_mapping = {f'{c}:{v}': f'Exod {c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
    assert {ref:row['source_reference'] for ref,row in by_ref.items()} == expected_mapping
    annotated_refs = [ref for ref,row in by_ref.items() if '<note' in raw[row['source_reference']]]
    assert set(annotated_refs) == {'32:17','32:19','33:10','33:16','34:6'}
    for ref, row in by_ref.items():
        assert row['source_verse_sha256'] == hashlib.sha256(raw[row['source_reference']].encode()).hexdigest()
    assert all(tag in raw['Exod 32:19'] for tag in ('type="variant"', 'type="x-ketiv"', 'type="x-qere"'))

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

    checks = {'32:1': ['gods to go ahead', 'this Moses', 'we do not know'], '32:2': ['wives, sons, and daughters'], '32:4': ['engraving tool', 'cast-metal calf', 'These are your gods'], '32:5': ['festival to the LORD'], '32:6': ['burnt offerings', 'peace offerings', 'eat and drink', 'revel'], '32:7': ['Your people, whom you brought up'], '32:8': ['bowed down', 'sacrificed', 'These are your gods'], '32:10': ['leave me alone', 'consume them', 'make you into a great nation'], '32:11': ['your people, whom you brought out', 'strong hand'], '32:12': ['kill them in the mountains', 'Relent'], '32:13': ['Abraham, Isaac, and Israel', 'by your own self', 'offspring', 'stars', 'inherit it forever'], '32:14': ['LORD relented', 'his people'], '32:15': ['two tablets', 'in his hand', 'both sides, front and back'], '32:16': ['God’s work', 'God’s writing'], '32:18': ['sound of victory', 'sound of defeat', 'sound of singing'], '32:19': ['his anger burned', 'from his hands', 'shattered'], '32:20': ['burned', 'ground it to powder', 'scattered', 'made the Israelites drink'], '32:24': ['I threw it into the fire', 'out came this calf'], '32:25': ['out of control', 'Aaron had let them loose'], '32:27': ['LORD, the God of Israel, says', 'sword', 'kill his brother, his friend, and his neighbor'], '32:28': ['about three thousand men', 'fell that day'], '32:29': ['Consecrate yourselves', 'son and his brother', 'blessing'], '32:30': ['Perhaps', 'atonement'], '32:32': ['if you will forgive their sin— But if not', 'erase me', 'book'], '32:35': ['plague', 'they had made the calf', 'Aaron made'], '33:1': ['Abraham, Isaac, and Jacob'], '33:2': ['Canaanites, Amorites, Hittites, Perizzites, Hivites, and Jebusites'], '33:3': ['milk and honey', 'will not go up among you', 'consume you'], '33:5': ['even a moment', 'consume you', 'take off your ornaments'], '33:6': ['Horeb'], '33:7': ['used to', 'far away from the camp', 'Anyone seeking'], '33:11': ['face to face', 'friend', 'young assistant Joshua son of Nun'], '33:14': ['My presence will go', 'give you rest'], '33:15': ['do not bring us up'], '33:18': ['show me your glory'], '33:19': ['all my goodness', 'I will be gracious to whom I will be gracious', 'I will show compassion to whom I will show compassion'], '33:20': ['cannot see my face', 'no human can see me and live'], '33:22': ['cleft', 'hand', 'until I have passed'], '33:23': ['take away my hand', 'see my back', 'my face must not be seen'], '34:1': ['Cut two stone tablets', 'I will write', 'which you shattered'], '34:3': ['No one', 'flocks and herds'], '34:6': ['The LORD, the LORD', 'compassionate and gracious', 'slow to anger', 'faithful love and faithfulness'], '34:7': ['thousands', 'guilt, rebellion, and sin', 'not clearing the guilty', 'fathers’ guilt', 'children and grandchildren', 'third and fourth'], '34:9': ['Though', 'forgive our guilt and sin', 'your inheritance'], '34:11': ['Amorites, Canaanites, Hittites, Perizzites, Hivites, and Jebusites'], '34:13': ['Tear down', 'shatter', 'cut down', 'Asherah poles'], '34:14': ['whose name is Jealous', 'jealous God'], '34:16': ['daughters as wives for your sons', 'prostitute themselves'], '34:18': ['seven days', 'Abib'], '34:19': ['opens the womb', 'firstborn male'], '34:20': ['sheep or goat', 'break its neck', 'every firstborn son'], '34:21': ['six days', 'seventh', 'plowing and harvest'], '34:22': ['Weeks', 'wheat harvest', 'Ingathering'], '34:23': ['Three times a year', 'all your males', 'Lord GOD'], '34:24': ['dispossess nations', 'enlarge your territory', 'covet your land', 'three times a year'], '34:26': ['firstfruits', 'Do not boil a young goat in its mother’s milk'], '34:28': ['forty days and forty nights', 'no bread', 'no water', 'he wrote', 'Ten Words'], '34:29': ['two tablets', 'did not know', 'skin of his face shone'], '34:33': ['finished speaking', 'put a veil'], '34:34': ['take off the veil', 'tell the Israelites'], '34:35': ['would see Moses’ face', 'put the veil back', 'speak with the LORD again']}
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    assert by_ref['33:16']['after'].count('I and your people') == 2
    assert by_ref['34:16']['after'].count('prostitute themselves') == 2
    assert 'those who hate me' not in by_ref['34:7']['after']
    assert 'thousands of generations' not in by_ref['34:7']['after']
    assert 'book of life' not in by_ref['32:32']['after']
    assert by_ref['34:6']['after'].endswith(',') and by_ref['34:7']['after'].startswith('keeping')
    for c,v in [(32,18),(34,6),(34,7)]:
        chapter_text = (ROOT / f'translations/fluent/OT/exodus/Exodus_{c:02}.md').read_text().split('## Notes')[0]
        record = re.search(rf'^v{v:02}: (.*?)(?=^v\d\d:|^</p>)', chapter_text, re.M | re.S)[1].strip()
        assert '\n' in record
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=34}
    assert len(exodus_refs)==len(set(exodus_refs))==999 and set(exodus_refs)==expected
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

    overlap = {'scope': 'Exodus 32–34 only; 93 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 32–34; 93 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 89, 'verses': 2640},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_hashed_in_full': annotated_refs,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read all 93 pinned Hebrew records including annotations, drafted independently, then consulted supplemental NET notes and read all TSW comparators. It reread the assembled English, preserved lineated speech and proclamation within verse paragraphs, and checked repeated language against Exodus 13, 20, 23 and 28–31. Review clarified conversation referents and aligned Lord GOD and intergenerational-guilt language with prior chapters while preserving differences. Focused checks cover plural gods with a single calf, Aaron’s account versus narration, kinship killing, approximate death count, unfinished plea, relenting, presence/face images, writing-subject ambiguity, and veil sequence. This is an authoring self-check, not independent scholarly review.',
        'exodus_source_references_unique_through_34': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 89, 'verses': 2640, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
