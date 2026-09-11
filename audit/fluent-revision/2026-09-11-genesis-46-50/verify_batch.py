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
BASE = '0f32a7b7b721827cc4ea781c3a230c8904824ade'
COUNTS = {46: 34, 47: 31, 48: 22, 49: 33, 50: 26}
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
    assert len(audits) == 9
    assert sum(a['verses'] for a in audits) == 1641
    assert len(chapter_paths) == 55
    assert len(all_genesis_sources) == 1533

    text = args.genesis_source.read_text()
    raw = {f'Gen {int(c)}:{int(v)}': verse for verse in re.findall(r'<verse\b[^>]*>.*?</verse>', text, re.S)
           for c, v in [re.search(r'osisID="Gen\.(\d+)\.(\d+)"', verse).groups()]}
    assert len(raw) == 1533
    assert all_genesis_sources == set(raw)
    ledger = json.loads((BATCH / 'genesis-verse-review.json').read_text())
    by_ref = {v['reference'].replace('Genesis ', ''): v for v in ledger['verses']}
    assert len(by_ref) == 146
    for ref in ('49:10', '49:11'):
        assert 'type="x-qere"' in raw['Gen ' + ref]
        assert by_ref[ref]['source_verse_sha256'] == hashlib.sha256(raw['Gen ' + ref].encode()).hexdigest()

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
        '46:4': ['I myself', 'close your eyes'],
        '46:9': ['Hanoch, Pallu, Hezron, and Carmi'],
        '46:10': ['Jemuel, Jamin, Ohad, Jachin, Zohar, and Shaul', 'mother was a Canaanite'],
        '46:11': ['Gershon, Kohath, and Merari'],
        '46:12': ['Er, Onan, Shelah, Perez, and Zerah', 'Er and Onan died', 'Hezron and Hamul'],
        '46:13': ['Tola, Puvah, Job, and Shimron'],
        '46:14': ['Sered, Elon, and Jahleel'],
        '46:15': ['Dinah', 'thirty-three'],
        '46:16': ['Ziphion, Haggi, Shuni, Ezbon, Eri, Arodi, and Areli'],
        '46:17': ['Imnah, Ishvah, Ishvi, and Beriah', 'sister was Serah', 'Heber and Malchiel'],
        '46:18': ['Zilpah', 'sixteen'],
        '46:20': ['Manasseh and Ephraim', 'Asenath', 'Potiphera', 'On'],
        '46:21': ['Bela, Becher, Ashbel, Gera, Naaman, Ehi, Rosh, Muppim, Huppim, and Ard'],
        '46:22': ['fourteen'], '46:23': ['Hushim'],
        '46:24': ['Jahzeel, Guni, Jezer, and Shillem'],
        '46:25': ['Bilhah', 'seven'], '46:26': ['sixty-six', 'not counting his sons’ wives'],
        '46:27': ['two sons', 'seventy'], '46:34': ['abomination'],
        '47:2': ['five'], '47:4': ['foreigners', 'no pasture'],
        '47:9': ['hundred and thirty', 'few and hard'],
        '47:12': ['little ones'], '47:17': ['horses, sheep and goats, cattle, and donkeys'],
        '47:19': ['Buy us and our land', 'slaves', 'live and not die'],
        '47:21': ['moved them into cities'], '47:22': ['did not buy', 'priests'],
        '47:23': ['bought you and your land'], '47:24': ['fifth', 'four shares'],
        '47:25': ['kept us alive', 'Pharaoh’s slaves'],
        '47:28': ['seventeen', 'hundred and forty-seven'],
        '47:29': ['under my thigh', 'faithful kindness'], '47:31': ['swore', 'head of his bed'],
        '48:5': ['Ephraim and Manasseh', 'Reuben and Simeon'],
        '48:10': ['Israel kissed'], '48:13': ['Ephraim in his right hand, toward Israel’s left', 'Manasseh in his left hand, toward Israel’s right'],
        '48:14': ['right hand', 'head of Ephraim', 'left hand on Manasseh’s head', 'crossing'],
        '48:15': ['blessed Joseph', 'shepherded'], '48:16': ['angel', 'redeemed'],
        '48:19': ['I know, my son, I know', 'younger brother', 'multitude of nations'],
        '48:21': ['you all'], '48:22': ['one portion more', 'sword and bow'],
        '49:4': ['he went up to my couch'], '49:6': ['killed men', 'hamstrung oxen'],
        '49:7': ['Cursed be their anger'], '49:10': ['Shiloh', 'between his feet', 'obedience of peoples'],
        '49:11': ['young donkey', 'blood of grapes'], '49:12': ['dark with wine', 'white with milk'],
        '49:13': ['Sidon'], '49:14': ['strong-boned donkey', 'saddlebags'],
        '49:15': ['forced laborer'], '49:18': ['salvation, LORD'],
        '49:19': ['raided by raiders'], '49:21': ['beautiful words'],
        '49:22': ['fruitful branch', 'spring', 'wall'], '49:24': ['Stone of Israel'],
        '49:25': ['breasts and womb'], '49:26': ['forebears', 'everlasting hills', 'set apart'],
        '49:28': ['twelve tribes'], '49:30': ['facing Mamre'],
        '49:31': ['Abraham', 'Sarah', 'Isaac', 'Rebekah', 'Leah'],
        '49:33': ['feet', 'gathered to his people'],
        '50:3': ['forty days', 'seventy days'], '50:5': ['dug for myself', 'I will return'],
        '50:10': ['beyond the Jordan', 'seven days'], '50:11': ['Abel-mizraim'],
        '50:13': ['facing Mamre'], '50:17': ['offense and sin', 'Joseph wept'],
        '50:18': ['your slaves'], '50:20': ['You intended harm', 'God intended it for good', 'keeping many people alive'],
        '50:23': ['third generation', 'Machir', 'Joseph’s knees'],
        '50:24': ['Abraham, Isaac, and Jacob'], '50:25': ['carry my bones up'],
        '50:26': ['hundred and ten', 'coffin in Egypt'],
    }
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    assert by_ref['49:22']['after'].count('fruitful branch') == 2
    assert by_ref['49:25']['after'].count('blessings of') == 3
    assert by_ref['49:31']['after'].lower().count('there') == 3
    for ref in ('50:24', '50:25'):
        assert 'God will surely come to your aid' in by_ref[ref]['after']
    # Poetry and continuation lines must remain inside verse paragraphs.
    for c in COUNTS:
        content = (ROOT / f'translations/fluent/OT/genesis/Genesis_{c}.md').read_text().split('---', 2)[2].split('## Notes')[0]
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

    overlap = {'scope': 'Genesis 46–50 only; 146 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Genesis 46–50; 146 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 55, 'verses': 1641},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'written_read_records_49_10_and_49_11_hashed_in_full': True,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every Hebrew verse before drafting, then read TSW comparators and reread the assembled English. Local corrections identified Israel as the one embracing the sons, preserved the young donkey, and aligned facing Mamre with the chapter 23 purchase account. This is not independent editorial review.',
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 55, 'verses': 1641, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
