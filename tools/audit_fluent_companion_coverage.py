#!/usr/bin/env python3
"""Verify complete chapter-by-chapter Fluent Companion coverage."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLUENT = ROOT / "translations" / "fluent"
COMPANION = ROOT / "companions" / "fluent"


def metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    raw = text.split("---\n", 2)[1]
    result: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def canonical_books(chapters: set[str]) -> set[str]:
    books: set[str] = set()
    for relative in chapters:
        text = (ROOT / relative).read_text(encoding="utf-8")
        match = re.search(r"(?m)^book:\s*(.+)$", text)
        if match:
            books.add(match.group(1).strip())
    return books


def companion_records() -> list[Path]:
    records = list((COMPANION / "chapters").rglob("*.md"))
    records.extend((COMPANION / "calibration").glob("*.md"))
    return sorted(records)


def missing_summary(paths: set[str]) -> list[str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for relative in sorted(paths):
        path = Path(relative)
        grouped[path.parent.name].append(path.stem)
    lines = []
    for book, chapters in sorted(grouped.items()):
        preview = ", ".join(chapters[:8])
        if len(chapters) > 8:
            preview += ", ..."
        lines.append(f"  - {book}: {len(chapters)} missing ({preview})")
    return lines


def main() -> int:
    canonical_chapters = {
        str(path.relative_to(ROOT)) for path in FLUENT.rglob("*.md")
    }
    canonical = canonical_books(canonical_chapters)

    by_source: dict[str, list[str]] = defaultdict(list)
    missing_source_metadata: list[str] = []
    for path in companion_records():
        source = metadata(path).get("source")
        relative = str(path.relative_to(ROOT))
        if not source:
            missing_source_metadata.append(relative)
            continue
        by_source[source].append(relative)

    covered_sources = set(by_source)
    missing_chapters = canonical_chapters - covered_sources
    unexpected_sources = covered_sources - canonical_chapters
    duplicate_sources = {
        source: records for source, records in by_source.items() if len(records) > 1
    }

    introduction_books = {
        metadata(path).get("book")
        for path in (COMPANION / "books").rglob("introduction.md")
    }
    introduction_books.discard(None)
    missing_introductions = canonical - introduction_books
    extra_introductions = introduction_books - canonical

    ot_chapters = {path for path in canonical_chapters if "/OT/" in path}
    nt_chapters = {path for path in canonical_chapters if "/NT/" in path}
    ot_covered = len(ot_chapters & covered_sources)
    nt_covered = len(nt_chapters & covered_sources)

    print("=== FLUENT COMPANION COMPLETE-CORPUS COVERAGE AUDIT ===")
    print(f"Canonical chapter files: {len(canonical_chapters)}")
    print(f"Old Testament coverage: {ot_covered}/{len(ot_chapters)}")
    print(f"New Testament coverage: {nt_covered}/{len(nt_chapters)}")
    print(f"Total chapter coverage: {len(canonical_chapters & covered_sources)}/{len(canonical_chapters)}")
    print(f"Remaining chapter companions: {len(missing_chapters)}")
    print(f"Canonical book introductions: {len(canonical & introduction_books)}/{len(canonical)}")

    if missing_chapters:
        print("Missing coverage by book:")
        print("\n".join(missing_summary(missing_chapters)))
    if unexpected_sources:
        print("Unexpected source paths:")
        for source in sorted(unexpected_sources):
            print(f"  - {source}")
    if duplicate_sources:
        print("Duplicate chapter bindings:")
        for source, records in sorted(duplicate_sources.items()):
            print(f"  - {source}: {', '.join(records)}")
    if missing_source_metadata:
        print("Companion records without source metadata:")
        for record in missing_source_metadata:
            print(f"  - {record}")
    if missing_introductions:
        print("Missing introductions: " + ", ".join(sorted(missing_introductions)))
    if extra_introductions:
        print("Unexpected introduction labels: " + ", ".join(sorted(extra_introductions)))

    failed = any(
        (
            missing_chapters,
            unexpected_sources,
            duplicate_sources,
            missing_source_metadata,
            missing_introductions,
            extra_introductions,
        )
    )
    if failed:
        print("INCOMPLETE: complete chapter-by-chapter coverage remains open")
        return 1

    print("PASSED: every Fluent chapter has exactly one Companion record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
