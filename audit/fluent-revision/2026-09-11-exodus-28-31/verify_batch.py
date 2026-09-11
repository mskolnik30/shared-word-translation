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
BASE = 'c36696ef18c62bd6a332852f2f4a84c860e304e9'
COUNTS = {28: 43, 29: 46, 30: 38, 31: 18}
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
    assert len(audits) == 18
    assert sum(a['verses'] for a in audits) == 2547
    assert len(chapter_paths) == 86
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
    assert len(by_ref) == 145
    expected_mapping = {f'{c}:{v}': f'Exod {c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
    assert {ref:row['source_reference'] for ref,row in by_ref.items()} == expected_mapping
    annotated_refs = [ref for ref,row in by_ref.items() if '<note' in raw[row['source_reference']]]
    assert set(annotated_refs) == {'28:28','30:12'}
    for ref, row in by_ref.items():
        assert row['source_verse_sha256'] == hashlib.sha256(raw[row['source_reference']].encode()).hexdigest()
    assert all(tag in raw['Exod 28:28'] for tag in ('type="variant"', 'type="x-ketiv"', 'type="x-qere"'))

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

    checks = {'28:1': ['Aaron', 'Nadab, Abihu, Eleazar, and Ithamar'], '28:2': ['honor and beauty'], '28:40': ['honor and beauty'], '28:10': ['six names', 'six remaining names', 'birth order'], '28:12': ['their names', 'two shoulders', 'memorial'], '28:16': ['square', 'folded double', 'a span long', 'a span wide'], '28:17': ['carnelian, topaz, and emerald'], '28:18': ['turquoise, sapphire, and moonstone'], '28:19': ['jacinth, agate, and amethyst'], '28:20': ['beryl, onyx, and jasper'], '28:21': ['twelve stones', 'twelve tribes'], '28:28': ['breastpiece’s rings', 'ephod’s rings', 'blue cord', 'above the waistband', 'does not come loose'], '28:29': ['names', 'heart', 'memorial'], '28:30': ['Urim and Thummim', 'Israel’s judgment'], '28:35': ['sound', 'enters', 'leaves', 'so he will not die'], '28:36': ['pure gold', 'Holy to the LORD'], '28:38': ['forehead', 'bear the guilt', 'accepted'], '28:42': ['linen', 'waist', 'thighs'], '28:43': ['guilt and die'], '29:1': ['one young bull', 'two rams without blemish'], '29:2': ['unleavened bread', 'cakes mixed with oil', 'wafers brushed with oil', 'wheat flour'], '29:12': ['finger', 'horns', 'remaining blood', 'base'], '29:14': ['meat, hide, and dung', 'outside the camp', 'sin offering'], '29:20': ['right earlobes', 'right thumbs', 'right big toes', 'Splash'], '29:21': ['sprinkle', 'Aaron and his garments', 'his sons and their garments'], '29:22': ['fat tail', 'both kidneys', 'right thigh'], '29:24': ['palms', 'wave offering'], '29:26': ['your portion'], '29:30': ['son who succeeds', 'seven days'], '29:34': ['morning', 'burn'], '29:36': ['Each day', 'bull', 'Purify the altar', 'atonement'], '29:37': ['seven days', 'whatever touches it will become holy'], '29:38': ['two lambs a year old each day'], '29:40': ['tenth of an ephah', 'quarter of a hin of beaten oil', 'quarter of a hin of wine'], '29:42': ['meet with you all', 'speak with you, Moses'], '29:46': ['brought them out of Egypt', 'dwell among them'], '30:2': ['a cubit long', 'a cubit wide', 'two cubits high'], '30:4': ['two gold rings', 'two opposite sides'], '30:9': ['unauthorized incense', 'burnt offering', 'grain offering', 'drink offering'], '30:12': ['each man', 'ransom for his life', 'plague'], '30:13': ['twenty gerahs'], '30:14': ['twenty years old or older'], '30:15': ['rich must not give more', 'poor must not give less'], '30:18': ['bronze basin', 'bronze stand', 'between the tent of meeting and the altar'], '30:20': ['so they do not die'], '30:21': ['hands and feet', 'so they do not die'], '30:23': ['five hundred shekels', 'two hundred fifty', 'cinnamon', 'fragrant cane'], '30:24': ['five hundred of cassia', 'sanctuary shekel', 'a hin of olive oil'], '30:32': ['human flesh', 'same proportions'], '30:34': ['stacte, onycha, and galbanum', 'frankincense', 'equal quantities'], '30:35': ['seasoned with salt'], '30:38': ['enjoy its fragrance', 'cut off'], '31:2': ['Bezalel', 'Uri', 'Hur', 'Judah'], '31:3': ['Spirit of God', 'wisdom, understanding, knowledge'], '31:6': ['Oholiab son of Ahisamach', 'Dan', 'every skilled worker'], '31:14': ['put to death', 'cut off'], '31:15': ['six days', 'seventh day', 'put to death'], '31:16': ['lasting covenant'], '31:17': ['six days', 'seventh day', 'stopped and caught his breath'], '31:18': ['Mount Sinai', 'two tablets', 'stone tablets', 'finger of God']}
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref, term)
    assert by_ref['28:34']['after'].lower().count('a gold bell and a pomegranate') == 2
    assert by_ref['30:10']['after'].lower().count('once a year') == 2
    assert by_ref['30:13']['after'].count('half a shekel') == 2
    assert by_ref['30:23']['after'].count('two hundred fifty') == 2
    for left,right in [('28:9','28:10'),('28:13','28:14'),('29:1','29:2'),('30:23','30:24'),('30:26','30:27'),('30:27','30:28'),('31:3','31:4'),('31:4','31:5')]:
        assert by_ref[left]['after'].endswith(',') and by_ref[right]['after'][0].islower()
    assert all(by_ref[f'31:{v}']['after'].endswith(';') for v in range(7,11))
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=31}
    assert len(exodus_refs)==len(set(exodus_refs))==906 and set(exodus_refs)==expected
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

    overlap = {'scope': 'Exodus 28–31 only; 145 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 28–31; 145 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 86, 'verses': 2547},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_hashed_in_full': annotated_refs,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read all 145 pinned Hebrew records including annotations, drafted each chapter from Hebrew, consulted supplemental NET notes and NRSVUE gemstone comparisons, read every TSW comparator, and reread the assembled English. The self-check corrected a note that overstated a spelling variant as a singular/plural difference and clarified the list of ram portions. Focused checks preserve named priests and craftspeople, gemstone ordering with provisional identifications, measurements, blood actions, offering quantities, equal census payments, death and exclusion sanctions, and divine bodily imagery. This is an authoring self-check, not independent scholarly review.',
        'exodus_source_references_unique_through_31': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 86, 'verses': 2547, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
