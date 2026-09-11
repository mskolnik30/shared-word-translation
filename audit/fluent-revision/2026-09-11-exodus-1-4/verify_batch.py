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
BASE = '1fdb00287932df8c2ce39dd799c977a07db9b59d'
COUNTS = {1: 22, 2: 25, 3: 22, 4: 31}
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
    assert len(audits) == 10
    assert sum(a['verses'] for a in audits) == 1741
    assert len(chapter_paths) == 59
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
    assert len(by_ref) == 100
    for ref in ('4:2',):
        assert 'type="x-qere"' in raw['Exod ' + ref]
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
        '1:2':['Reuben, Simeon, Levi, and Judah'], '1:3':['Issachar, Zebulun, and Benjamin'],
        '1:4':['Dan and Naphtali, Gad and Asher'], '1:5':['seventy'],
        '1:7':['fruitful','teemed','multiplied','filled'], '1:11':['Pithom and Rameses','forced-labor'],
        '1:13':['ruthlessly','slaves'], '1:14':['ruthlessly','mortar and brick','fields'],
        '1:15':['Shiphrah','Puah'], '1:16':['boy, kill him','girl, let her live'],
        '1:17':['feared God','kept the boys alive'], '1:21':['households'],
        '1:22':['all his people','every newborn boy','every girl'],
        '2:1':['Levi'], '2:2':['three months'], '2:3':['papyrus','bitumen and pitch','among the reeds'],
        '2:5':['slave woman'], '2:10':['Moses','her son','drew him out'],
        '2:12':['struck the Egyptian dead','hid him'], '2:16':['seven daughters'],
        '2:18':['Reuel'], '2:21':['Zipporah'], '2:22':['Gershom','foreigner in a foreign land'],
        '2:23':['slavery'], '2:24':['God heard','God remembered','covenant','Abraham, Isaac, and Jacob'],
        '2:25':['God saw the Israelites. God knew.'], '3:1':['Jethro','Horeb'],
        '3:2':['angel of the LORD','not being consumed'], '3:4':['Moses! Moses!'],
        '3:5':['God said','holy ground'], '3:6':['your father','God of Abraham','God of Isaac','God of Jacob'],
        '3:7':['indeed seen','heard','know their pain'], '3:8':['come down','bring them up','milk and honey'],
        '3:12':['I will be with you','you all will serve God'], '3:14':['I AM WHO I AM'],
        '3:15':['forever','generation to generation'], '3:16':['surely attended to you'],
        '3:18':['three days’ journey','sacrifice'], '3:19':['strong hand'], '3:20':['stretch out my hand'],
        '3:22':['Each woman','ask','silver and gold','sons and daughters','plunder'],
        '4:6':['white as snow'], '4:8':['voice of the first sign','voice of the second'],
        '4:9':['Nile','dry ground','blood'], '4:10':['mouth and tongue'],
        '4:11':['unable to speak or deaf, sighted or blind'], '4:14':['anger burned','brother Aaron the Levite'],
        '4:15':['your mouth and his','teach you both'], '4:16':['your mouth','as God to him'],
        '4:19':['All the men'], '4:20':['wife and sons','donkey','staff of God'],
        '4:21':['I will harden his heart'], '4:22':['Israel is my son, my firstborn'],
        '4:23':['I will kill your son, your firstborn'], '4:24':['LORD met him and sought to kill him'],
        '4:25':['flint','son’s foreskin','his feet','bridegroom of blood'], '4:26':['he let him alone','circumcision'],
        '4:27':['mountain of God','kissed him'], '4:30':['Aaron spoke','he performed'],
        '4:31':['believed','heard','attended','seen their suffering','bowed down'],
    }
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    for ref in ('3:8','3:17'):
        assert 'Canaanites, Hittites, Amorites, Perizzites, Hivites, and Jebusites' in by_ref[ref]['after']
    assert 'Hebrew' not in by_ref['1:22']['after']
    assert by_ref['2:23']['after'].count('slavery') == 2
    apparatus = (ROOT / 'translations/fluent/OT/exodus/Exodus_04.md').read_text().split('## Notes')[1]
    assert 'ancient Greek reads “rejoiced.”' in apparatus
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

    overlap = {'scope': 'Exodus 1–4 only; 100 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 1–4; 100 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 59, 'verses': 1741},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'written_read_record_4_2_hashed_in_full': True,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every Hebrew verse before drafting, read every TSW comparator afterward, and reread the assembled English. Focused corrections clarified the speaker in 3:5 and corrected the 4:31 textual note from saw to the Greek rejoiced. Selected numerical, name, repetition, agency, and ambiguity checks are recorded above. This is not independent editorial review.',
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 59, 'verses': 1741, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
