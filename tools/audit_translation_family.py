#!/usr/bin/env python3
"""Audit structural parity and required metadata across project translations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FRONT_MATTER_RE = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n", re.DOTALL)
FIELD_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):\s*(?P<value>.*)$")
VERSE_RE = re.compile(r"^\s*v(?P<label>\d{1,3}[a-z]?(?:[–-]\d{1,3}[a-z]?)?):", re.MULTILINE)


@dataclass(frozen=True, order=True)
class ChapterKey:
    testament: str
    book_slug: str
    chapter: int

    def display(self) -> str:
        return f"{self.testament}/{self.book_slug}/{self.chapter}"


@dataclass
class ChapterRecord:
    key: ChapterKey
    path: Path
    metadata: dict[str, str]
    verse_labels: list[str]


def parse_front_matter(text: str, path: Path, problems: list[str]) -> dict[str, str]:
    match = FRONT_MATTER_RE.search(text)
    if not match:
        problems.append(f"{path}: missing or malformed front matter")
        return {}

    metadata: dict[str, str] = {}
    for line in match.group("body").splitlines():
        field = FIELD_RE.match(line)
        if field:
            metadata[field.group("key")] = field.group("value").strip()
    return metadata


def main_text(text: str) -> str:
    boundaries = [position for heading in ("\n## Notes", "\n## Vocabulary") if (position := text.find(heading)) >= 0]
    return text[: min(boundaries)] if boundaries else text


def load_corpus(
    repo_root: Path,
    definition: dict[str, Any],
    problems: list[str],
) -> dict[ChapterKey, ChapterRecord]:
    corpus_root = repo_root / definition["root"]
    records: dict[ChapterKey, ChapterRecord] = {}

    if not corpus_root.is_dir():
        problems.append(f"{corpus_root}: translation root does not exist")
        return records

    for path in sorted(corpus_root.glob("*/*/*.md")):
        relative = path.relative_to(corpus_root)
        if len(relative.parts) != 3:
            continue
        testament, book_slug, _filename = relative.parts
        text = path.read_text(encoding="utf-8")
        metadata = parse_front_matter(text, path.relative_to(repo_root), problems)

        try:
            chapter = int(metadata.get("chapter", ""))
        except ValueError:
            problems.append(f"{path.relative_to(repo_root)}: chapter must be an integer")
            continue

        key = ChapterKey(testament, book_slug, chapter)
        if key in records:
            problems.append(
                f"{path.relative_to(repo_root)}: duplicates chapter key {key.display()} "
                f"already provided by {records[key].path.relative_to(repo_root)}"
            )
            continue

        expected_translation = definition["front_matter_id"]
        if metadata.get("translation") != expected_translation:
            problems.append(
                f"{path.relative_to(repo_root)}: translation is "
                f"{metadata.get('translation')!r}; expected {expected_translation!r}"
            )
        if metadata.get("testament") != testament:
            problems.append(
                f"{path.relative_to(repo_root)}: testament is "
                f"{metadata.get('testament')!r}; expected {testament!r}"
            )
        required_status = definition.get("required_status")
        if required_status and metadata.get("status") != required_status:
            problems.append(
                f"{path.relative_to(repo_root)}: status is "
                f"{metadata.get('status')!r}; expected {required_status!r}"
            )

        labels = [match.group("label") for match in VERSE_RE.finditer(main_text(text))]
        if not labels:
            problems.append(f"{path.relative_to(repo_root)}: no public verse labels found")
        if len(labels) != len(set(labels)):
            duplicates = sorted({label for label in labels if labels.count(label) > 1})
            problems.append(
                f"{path.relative_to(repo_root)}: duplicate public verse labels: "
                + ", ".join(duplicates)
            )

        records[key] = ChapterRecord(key, path, metadata, labels)

    return records


def audit(repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    registry_path = repo_root / "translations" / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    definitions = registry.get("translations", [])
    problems: list[str] = []

    if len(definitions) < 2:
        problems.append("translations/registry.json: at least two translations are required")

    ids = [definition.get("id") for definition in definitions]
    if len(ids) != len(set(ids)):
        problems.append("translations/registry.json: translation IDs must be unique")
    if registry.get("site_default") not in ids:
        problems.append("translations/registry.json: site_default is not a registered translation")

    corpora: dict[str, dict[ChapterKey, ChapterRecord]] = {}
    summaries: dict[str, Any] = {}
    for definition in definitions:
        translation_id = definition["id"]
        records = load_corpus(repo_root, definition, problems)
        corpora[translation_id] = records
        books = {(key.testament, key.book_slug) for key in records}
        summary = {
            "books": len(books),
            "chapters": len(records),
            "public_verse_labels": sum(len(record.verse_labels) for record in records.values()),
        }
        summaries[translation_id] = summary

        expected = definition.get("coverage", {})
        for field in ("books", "chapters"):
            if field in expected and summary[field] != expected[field]:
                problems.append(
                    f"{translation_id}: found {summary[field]} {field}; expected {expected[field]}"
                )

    parity: dict[str, Any] = {}
    if definitions:
        baseline_id = definitions[0]["id"]
        baseline = corpora[baseline_id]
        for definition in definitions[1:]:
            translation_id = definition["id"]
            candidate = corpora[translation_id]
            missing = sorted(set(baseline) - set(candidate))
            extra = sorted(set(candidate) - set(baseline))
            label_mismatches: list[dict[str, Any]] = []
            documented_exceptions: list[dict[str, Any]] = []
            exception_map: dict[ChapterKey, dict[str, Any]] = {}

            for exception in definition.get("verse_label_exceptions", []):
                if exception.get("relative_to") != baseline_id:
                    problems.append(
                        f"{translation_id}: verse-label exception must be relative to {baseline_id}"
                    )
                    continue
                key = ChapterKey(
                    exception["testament"],
                    exception["book"],
                    int(exception["chapter"]),
                )
                if key in exception_map:
                    problems.append(
                        f"{translation_id}: duplicate verse-label exception for {key.display()}"
                    )
                    continue
                exception_map[key] = exception

            for key in sorted(set(baseline) & set(candidate)):
                left = baseline[key].verse_labels
                right = candidate[key].verse_labels
                if left == right:
                    if key in exception_map:
                        problems.append(
                            f"{translation_id}: stale verse-label exception for {key.display()}"
                        )
                    continue

                actual_missing = [label for label in left if label not in right]
                actual_additional = [label for label in right if label not in left]
                shared_left = [label for label in left if label in right]
                shared_right = [label for label in right if label in left]
                exception = exception_map.get(key)
                expected_missing = exception.get("missing", []) if exception else []
                expected_additional = exception.get("additional", []) if exception else []

                if (
                    exception
                    and actual_missing == expected_missing
                    and actual_additional == expected_additional
                    and shared_left == shared_right
                    and exception.get("reason")
                ):
                    documented_exceptions.append(
                        {
                            "chapter": key.display(),
                            "missing": actual_missing,
                            "additional": actual_additional,
                            "reason": exception["reason"],
                        }
                    )
                else:
                    label_mismatches.append(
                        {
                            "chapter": key.display(),
                            baseline_id: left,
                            translation_id: right,
                        }
                    )

            parity[translation_id] = {
                "baseline": baseline_id,
                "missing_chapters": [key.display() for key in missing],
                "extra_chapters": [key.display() for key in extra],
                "documented_verse_label_exceptions": documented_exceptions,
                "verse_label_mismatches": label_mismatches,
            }
            if missing:
                problems.append(
                    f"{translation_id}: {len(missing)} chapter(s) missing relative to {baseline_id}"
                )
            if extra:
                problems.append(
                    f"{translation_id}: {len(extra)} extra chapter(s) relative to {baseline_id}"
                )
            if label_mismatches:
                problems.append(
                    f"{translation_id}: {len(label_mismatches)} chapter(s) have public verse-label mismatches"
                )

    report = {
        "schema_version": 1,
        "status": "passed" if not problems else "failed",
        "registry": str(registry_path.relative_to(repo_root)),
        "translations": summaries,
        "parity": parity,
        "problems": problems,
    }
    return report, problems


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: inferred from this script)",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="optional path for the complete JSON report",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    try:
        report, problems = audit(repo_root)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"AUDIT ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("=== TRANSLATION FAMILY AUDIT ===")
    for translation_id, summary in report["translations"].items():
        print(
            f"{translation_id}: {summary['books']} books; {summary['chapters']} chapters; "
            f"{summary['public_verse_labels']} public verse labels"
        )

    if problems:
        print(f"\nFAILED: {len(problems)} problem(s)")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("\nPASSED: registered translations have structural parity and only documented verse-label exceptions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
