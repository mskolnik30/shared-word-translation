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
BASE = '0e762160f4b24f6dbb1deb2b4c1657019652d3ae'
COUNTS = {25: 40, 26: 37, 27: 21}
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
    assert len(audits) == 17
    assert sum(a['verses'] for a in audits) == 2402
    assert len(chapter_paths) == 82
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
    assert len(by_ref) == 98
    expected_mapping = {f'{c}:{v}': f'Exod {c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
    assert {ref:row['source_reference'] for ref,row in by_ref.items()} == expected_mapping
    annotated_refs = [ref for ref,row in by_ref.items() if '<note' in raw[row['source_reference']]]
    assert set(annotated_refs) == {'26:6','27:11','27:15'}
    for ref, row in by_ref.items():
        assert row['source_verse_sha256'] == hashlib.sha256(raw[row['source_reference']].encode()).hexdigest()
    assert all(tag in raw['Exod 27:11'] for tag in ('type="variant"', 'type="x-ketiv"', 'type="x-qere"'))

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

    checks = {'25:2': ['heart', 'contribution'], '25:3': ['gold, silver, and bronze'], '25:4': ['blue, purple, and scarlet', 'fine linen', 'goat hair'], '25:5': ['rams’ skins dyed red', 'taḥash', 'acacia'], '25:6': ['light', 'anointing oil', 'incense'], '25:7': ['onyx', 'ephod', 'breastpiece'], '25:8': ['dwell among them'], '25:9': ['pattern'], '25:10': ['two and a half cubits long', 'a cubit and a half wide', 'a cubit and a half high'], '25:11': ['pure gold', 'inside and out'], '25:12': ['four gold rings', 'four feet', 'two rings', 'two on the other'], '25:15': ['must remain', 'do not remove'], '25:16': ['testimony'], '25:17': ['atonement cover', 'two and a half cubits long', 'a cubit and a half wide'], '25:18': ['two gold cherubim', 'hammering'], '25:19': ['one piece', 'two ends'], '25:20': ['wings upward', 'face one another', 'toward the cover'], '25:21': ['on top', 'inside'], '25:22': ['meet with you', 'above', 'between the two', 'I will speak', 'Israelites'], '25:23': ['two cubits long', 'one cubit wide', 'a cubit and a half high'], '25:25': ['handbreadth'], '25:26': ['four gold rings', 'four corners', 'four legs'], '25:29': ['dishes', 'ladles', 'pitchers', 'bowls', 'pure gold'], '25:30': ['bread of the Presence', 'before me always'], '25:31': ['base, shaft, cups, buds, and flowers', 'one piece'], '25:32': ['Six branches', 'three from one side', 'three from the other'], '25:33': ['three cups', 'all six branches'], '25:34': ['four cups', 'almond blossoms'], '25:35': ['first pair', 'next pair', 'last pair', 'six branches'], '25:36': ['single piece', 'pure gold'], '25:37': ['seven lamps', 'in front'], '25:38': ['tongs', 'firepans'], '25:39': ['one talent', 'all these utensils'], '25:40': ['pattern', 'mountain'], '26:1': ['ten curtains', 'cherubim'], '26:2': ['twenty-eight cubits long', 'four cubits wide', 'same dimensions'], '26:3': ['five curtains', 'other five'], '26:5': ['fifty loops', 'face one another'], '26:6': ['fifty gold clasps', 'one whole'], '26:7': ['goat hair', 'eleven'], '26:8': ['thirty cubits long', 'four cubits wide', 'All eleven'], '26:9': ['five curtains', 'six into another', 'sixth curtain double', 'front'], '26:10': ['fifty loops'], '26:11': ['fifty bronze clasps', 'one whole'], '26:12': ['half-curtain', 'back'], '26:13': ['cubit on each side'], '26:14': ['rams’ skins dyed red', 'taḥash skins on top'], '26:15': ['upright', 'acacia'], '26:16': ['ten cubits long', 'a cubit and a half wide'], '26:17': ['two tenons'], '26:18': ['twenty', 'south'], '26:19': ['forty silver bases', 'twenty frames'], '26:20': ['north', 'twenty frames'], '26:21': ['forty silver bases'], '26:22': ['west', 'six frames'], '26:23': ['two more frames', 'corners'], '26:24': ['bottom', 'top', 'one ring', 'both corner frames'], '26:25': ['eight frames', 'sixteen silver bases'], '26:26': ['acacia wood', 'five'], '26:27': ['five', 'other side', 'rear', 'west'], '26:28': ['middle', 'end to end'], '26:29': ['frames with gold', 'gold rings', 'crossbars with gold'], '26:30': ['design', 'mountain'], '26:31': ['blue, purple, and scarlet', 'linen', 'cherubim'], '26:32': ['four acacia pillars', 'gold hooks', 'four silver bases'], '26:33': ['beneath the clasps', 'behind the curtain', 'Holy Place', 'Most Holy Place'], '26:34': ['atonement cover', 'Most Holy Place'], '26:35': ['table outside', 'lampstand opposite', 'south', 'table on the north'], '26:36': ['screen', 'entrance', 'embroidery'], '26:37': ['five acacia pillars', 'gold', 'five bronze bases'], '27:1': ['five cubits long', 'five cubits wide', 'square', 'three cubits high'], '27:2': ['four corners', 'one piece', 'bronze'], '27:3': ['pots', 'shovels', 'basins', 'forks', 'firepans', 'bronze'], '27:4': ['net', 'four bronze rings', 'four corners'], '27:5': ['beneath', 'midpoint'], '27:6': ['acacia', 'bronze'], '27:7': ['two sides'], '27:8': ['hollow', 'boards', 'mountain'], '27:9': ['south', 'hundred cubits'], '27:10': ['twenty pillars', 'twenty bronze bases', 'silver'], '27:11': ['north', 'hundred cubits', 'twenty pillars', 'twenty bronze bases', 'silver'], '27:12': ['west', 'fifty cubits', 'ten pillars', 'ten bases'], '27:13': ['east', 'sunrise', 'fifty cubits'], '27:14': ['fifteen cubits', 'three pillars', 'three bases'], '27:15': ['fifteen cubits', 'three pillars', 'three bases'], '27:16': ['twenty cubits', 'four pillars', 'four bases', 'embroidery'], '27:17': ['silver bands', 'silver hooks', 'bronze bases'], '27:18': ['hundred cubits long', 'fifty cubits wide', 'five cubits high'], '27:19': ['tent pegs', 'courtyard’s pegs', 'bronze'], '27:20': ['pure oil', 'beaten olives', 'regularly'], '27:21': ['tent of meeting', 'outside the curtain', 'Aaron and his sons', 'evening until morning', 'generations']}
    for ref, terms in checks.items():
        for term in terms:
            assert term.lower() in by_ref[ref]['after'].lower(), (ref,term)
    assert by_ref['25:33']['after'].count('three cups') == 2
    assert by_ref['25:35']['after'].count('a bud beneath') == 3
    for ref in ('26:5','26:10'):
        assert by_ref[ref]['after'].count('fifty loops') == 2
    assert by_ref['26:27']['after'].count('five') == 2
    for left,right in [('26:20','26:21'),('26:26','26:27'),('27:9','27:10'),('27:14','27:15')]:
        assert by_ref[left]['after'].endswith(',') and by_ref[right]['after'][0].islower()
    assert all(by_ref[f'25:{v}']['after'].endswith(';') for v in range(3,7))
    exodus_refs=[]
    for scope in queue['completed_draft_scopes']:
        if scope['scope'].startswith('Exodus'):
            exodus_refs.extend(v['source_reference'] for v in json.loads((ROOT/scope['ledger']).read_text())['verses'])
    expected={ref for ref in raw if int(ref.split()[1].split(':')[0])<=27}
    assert len(exodus_refs)==len(set(exodus_refs))==761 and set(exodus_refs)==expected
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

    overlap = {'scope': 'Exodus 25–27 only; 98 verses', 'method': 'Case-folded word tokens and SequenceMatcher; near-identical means nonidentical similarity >= 0.90. Triage only, not fidelity or originality evidence.', 'stages': {}}
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
        'base_commit': BASE, 'scope': 'Exodus 25–27; 98 verses',
        'revision_audits': audits, 'cumulative_coverage': {'chapters': 82, 'verses': 2402},
        'source_record_count': len(raw), 'genesis_source_references_unique_through_50': len(all_genesis_sources),
        'focused_assertions': checks,
        'source_annotations_hashed_in_full': annotated_refs,
        'prior_batches_and_unaffected_approvals_preserved': True,
        'TSW_prior_revisions_and_Companion_unchanged': True,
        'translation_family_audit': family, 'git_diff_check': diff,
        'editorial_self_check': 'The authoring model read every one of the 98 pinned Hebrew records including annotations, drafted from Hebrew, consulted supplemental NET notes, read every TSW comparator, and reread the assembled English. A table-vessel clause was clarified and an over-specific direction of altar-grating extension was removed. Focused checks preserve materials, dimensions, repeated counts, inner/outer curtain distinctions, sanctuary spatial relationships, uncertain technical words, and named lamp attendants. This is an authoring self-check, not independent scholarly review.',
        'exodus_source_references_unique_through_27': len(exodus_refs),
        'independent_editorial_review': 'REVIEW_PENDING', 'publication_allowed': False,
    })
    print(json.dumps({'status': 'PASSED', 'ledgers': len(audits), 'chapters': 82, 'verses': 2402, 'overlap': {k: {x:v for x,v in val.items() if x != 'verses'} for k,val in overlap['stages'].items()}}, indent=2))

if __name__ == '__main__':
    main()
