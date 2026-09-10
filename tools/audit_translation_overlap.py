#!/usr/bin/env python3
"""Measure English overlap for editorial triage, never as a translation-quality gate."""
from __future__ import annotations

import argparse
from collections import defaultdict
from difflib import SequenceMatcher
import html
import json
from pathlib import Path
import re
import subprocess
import unicodedata

from audit_translation_family import load_corpus, main_text


def verse_texts(text):
    """Keep continuation lines; exclude headings, markup, and apparatus."""
    verses = {}
    current = None
    for line in main_text(text).splitlines():
        match = re.match(r'^\s*v(\d{1,3}[a-z]?(?:[–-]\d{1,3}[a-z]?)?):\s*(.*)', line)
        if match:
            current = match[1]
            if current in verses:
                raise ValueError(f'duplicate verse label {current}')
            verses[current] = match[2]
        elif line.lstrip().startswith('#'):
            current = None
        elif current and line.strip():
            verses[current] += ' ' + line.strip()
    return {k: ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', v)).split())
            for k, v in verses.items()}


def words(text):
    text = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
    return re.findall(r"[^\W_]+(?:'[^\W_]+)*", text)


def audit(root):
    registry = json.loads((root / 'translations/registry.json').read_text())
    definitions = {d['id']: d for d in registry['translations']}
    problems = []
    corpora = {key: load_corpus(root, definitions[key], problems) for key in ('tsw', 'fluent')}
    rows = []
    unmatched = []
    totals = defaultdict(lambda: {'matched_verses': 0, 'identical_words': 0, 'near_identical': 0, 'word_similarity_sum': 0})
    for key in sorted(set(corpora['tsw']) | set(corpora['fluent'])):
        if any(key not in c for c in corpora.values()):
            unmatched.append({'chapter': key.display(), 'reason': 'missing chapter'})
            continue
        pair = {t: verse_texts(corpora[t][key].path.read_text()) for t in corpora}
        for label in sorted(set(pair['tsw']) | set(pair['fluent'])):
            if any(label not in p for p in pair.values()):
                unmatched.append({'chapter': key.display(), 'verse': label,
                                  'present_in': [t for t, p in pair.items() if label in p]})
                continue
            a, b = words(pair['tsw'][label]), words(pair['fluent'][label])
            same = a == b
            similarity = SequenceMatcher(None, a, b, autojunk=False).ratio()
            near = not same and similarity >= .9
            for scope in ('ALL', key.book_slug):
                total = totals[scope]
                total['matched_verses'] += 1
                total['identical_words'] += int(same)
                total['near_identical'] += int(near)
                total['word_similarity_sum'] += similarity
            if same or near:
                rows.append({'chapter': key.display(), 'verse': label,
                             'kind': 'identical_words' if same else 'near_identical',
                             'word_similarity': round(similarity, 6),
                             'minimum_word_count': min(len(a), len(b))})
    for total in totals.values():
        n = total['matched_verses']
        total['identical_percent'] = round(100 * total['identical_words'] / n, 2)
        total['mean_word_similarity'] = round(total.pop('word_similarity_sum') / n, 6)
    return {'schema_version': 1,
            'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
            'scope': 'working tree; chapter and verse labels aligned; Scripture only',
            'method': 'NFKC/casefold; ignore punctuation and markup; preserve words and continuation lines. Near-identical means nonidentical token SequenceMatcher ratio >= 0.90. Unmatched verse labels are excluded, not silently aligned.',
            'interpretation': 'Editorial triage only. Short sayings, quotations, names, and technical terms can legitimately overlap. No minimum difference quota; this does not prove source fidelity or independent translation.',
            'totals': dict(totals), 'overlap_locations': rows,
            'unmatched': unmatched, 'structural_problems': problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json-output', type=Path, required=True)
    parser.add_argument('--include-locations', action='store_true',
                        help='include all exact/near-exact verse locations (large report)')
    args = parser.parse_args()
    report = audit(args.repo_root.resolve())
    report['overlap_location_count'] = len(report['overlap_locations'])
    if not args.include_locations:
        del report['overlap_locations']
        report['locations_note'] = 'Use --include-locations to regenerate every flagged verse; omitted here to keep the saved comparison reviewable.'
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'all': report['totals']['ALL'], 'james': report['totals']['james'],
                      'unmatched': len(report['unmatched']), 'problems': report['structural_problems']}, indent=2))
    return int(bool(report['structural_problems']))


if __name__ == '__main__':
    raise SystemExit(main())
