#!/usr/bin/env python3
"""Report first-edition Fluent Companion canonical-book coverage."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLUENT = ROOT / "translations" / "fluent"
COMPANION = ROOT / "companions" / "fluent"


def metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    raw = text.split("---\n", 2)[1]
    result = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def canonical_books() -> set[str]:
    books = set()
    for path in FLUENT.rglob("*.md"):
        match = re.search(r"(?m)^book:\s*(.+)$", path.read_text(encoding="utf-8"))
        if match:
            books.add(match.group(1).strip())
    return books


def main() -> int:
    canonical = canonical_books()
    chapter_books = {metadata(path).get("book") for path in (COMPANION / "chapters").rglob("*.md")}
    chapter_books |= {metadata(path).get("book") for path in (COMPANION / "calibration").glob("*.md")}
    introduction_books = {metadata(path).get("book") for path in (COMPANION / "books").rglob("introduction.md")}
    chapter_books.discard(None)
    introduction_books.discard(None)
    if "Psalm" in chapter_books:
        chapter_books.remove("Psalm")
        chapter_books.add("Psalms")

    missing_chapters = sorted(canonical - chapter_books)
    missing_introductions = sorted(canonical - introduction_books)
    extra_chapters = sorted(chapter_books - canonical)
    extra_introductions = sorted(introduction_books - canonical)

    print("=== FLUENT COMPANION COVERAGE AUDIT ===")
    print(f"Canonical books with chapter companions: {len(canonical - set(missing_chapters))}/66")
    print(f"Canonical books with introductions: {len(canonical - set(missing_introductions))}/66")
    print(f"Total chapter companions: {sum(1 for _ in (COMPANION / 'chapters').rglob('*.md')) + sum(1 for _ in (COMPANION / 'calibration').glob('*.md'))}")
    if missing_chapters:
        print("Missing chapter coverage: " + ", ".join(missing_chapters))
    if missing_introductions:
        print("Missing introductions: " + ", ".join(missing_introductions))
    if extra_chapters or extra_introductions:
        print("Unexpected book labels: " + ", ".join(sorted(set(extra_chapters + extra_introductions))))
    if missing_chapters or missing_introductions or extra_chapters or extra_introductions:
        print("INCOMPLETE: first-edition candidate coverage remains open")
        return 1
    print("PASSED: all 66 books have an introduction and at least one chapter companion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
