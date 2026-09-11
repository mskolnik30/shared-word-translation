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
BASE = '084335a96cd6586583cadefbaeb016d9806ec1f8'
COUNTS = {5: 23, 6: 30}
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
    assert len(audits) == 11
    assert sum(a['verses'] for a in audits) == 1794
    assert len(chapter_paths) == 61
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
    assert len(by_ref) == 53
    for ref in ('6:6',):
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
        '5:1':['festival','Let my people go'], '5:2':['listen to his voice','I do not know the LORD'],
        '5:3':['three days','strike us','plague or sword'], '5:6':['taskmasters and foremen'],
        '5:8':['Do not reduce','lazy'], '5:9':['men','lying words'], '5:12':['stubble'],
        '5:14':['Israelite foremen','were beaten','yesterday','today'],
        '5:16':['your own people'], '5:17':['Lazy','lazy'], '5:21':['stink in the eyes','sword','kill us'],
        '5:22':['you brought harm'], '5:23':['he has brought harm','not rescued your people at all'],
        '6:1':['strong hand','let them go','drive them out'], '6:3':['God Almighty','I was not known to them'],
        '6:4':['covenant','foreigners'], '6:5':['I myself','enslaving','remembered my covenant'],
        '6:6':['I will bring','I will rescue','I will redeem','outstretched arm','judgment'],
        '6:7':['my people','your God'], '6:8':['raised my hand in an oath','possession'],
        '6:9':['because','spirits were crushed','labor was harsh'], '6:12':['lips are uncircumcised'],
        '6:14':['Hanoch, Pallu, Hezron, and Carmi'],
        '6:15':['Jemuel, Jamin, Ohad, Jachin, Zohar, and Shaul','mother was a Canaanite'],
        '6:16':['Gershon, Kohath, and Merari','hundred and thirty-seven'],
        '6:17':['Libni and Shimei'], '6:18':['Amram, Izhar, Hebron, and Uzziel','hundred and thirty-three'],
        '6:19':['Mahli and Mushi'], '6:20':['aunt Jochebed','Aaron and Moses','hundred and thirty-seven'],
        '6:21':['Korah, Nepheg, and Zichri'], '6:22':['Mishael, Elzaphan, and Sithri'],
        '6:23':['Elisheba','daughter of Amminadab','sister of Nahshon','Nadab, Abihu, Eleazar, and Ithamar'],
        '6:24':['Assir, Elkanah, and Abiasaph'], '6:25':['one of Putiel’s daughters','Phinehas'],
        '6:26':['Aaron and Moses','companies'], '6:27':['Moses and Aaron'],
        '6:30':['lips are uncircumcised'],
    }
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    assert by_ref['6:1']['after'].lower().count('under a strong hand') == 2
    assert 'fully' not in by_ref['6:3']['after'] and '?' not in by_ref['6:3']['after']
    assert by_ref['6:28']['after'].endswith(',')
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

    overlap = {'scope': 'Exodus 5–6 only; 53 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 5–6; 53 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 61, 'verses': 1794},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotation_6_6_hashed_in_full': True,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every Hebrew verse, drafted from that source with supplemental grammatical notes, read all TSW comparators, and reread the assembled English. The cause of the people’s not listening at 6:9 was made explicit. Names, ages, labor authorities, repeated accusations, kinship, and consequential ambiguities received focused checks. This is not independent editorial review.',
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 61, 'verses': 1794, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
