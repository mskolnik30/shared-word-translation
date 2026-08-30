#!/usr/bin/env python3
"""Normalize and validate Markdown spacing in TSW apparatus sections."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


HEADINGS = ("## Notes", "## Vocabulary")


def is_entry(line: str) -> bool:
    """Return True for a canonical apparatus line beginning with a verse label."""
    return len(line) >= 4 and line[0] == "v" and line[1:3].isdigit() and line[3] in ":-–"


def normalize(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    section: str | None = None
    skip_blanks_after_heading = False

    for line in lines:
        if line in HEADINGS:
            while output and not output[-1].strip():
                output.pop()
            if output:
                output.append("")
            output.extend((line, ""))
            section = line
            skip_blanks_after_heading = True
            continue

        if skip_blanks_after_heading and not line.strip():
            continue
        skip_blanks_after_heading = False

        if line.startswith("## "):
            section = None

        if section and is_entry(line):
            while len(output) >= 2 and not output[-1].strip() and not output[-2].strip():
                output.pop()
            if output and output[-1].strip():
                output.append("")

        output.append(line)

    while output and not output[-1].strip():
        output.pop()
    return "\n".join(output) + "\n"


def validate(path: Path, text: str) -> list[str]:
    problems: list[str] = []
    lines = text.splitlines()

    for heading in HEADINGS:
        positions = [index for index, line in enumerate(lines) if line == heading]
        if len(positions) != 1:
            problems.append(f"{heading}: expected once, found {len(positions)}")
            continue

        index = positions[0]
        if index == 0 or lines[index - 1].strip():
            problems.append(f"{heading}: missing blank line before heading")
        if index + 1 < len(lines) and lines[index + 1].strip():
            problems.append(f"{heading}: missing blank line after heading")
        if index >= 2 and not lines[index - 2].strip():
            problems.append(f"{heading}: more than one blank line before heading")
        if index + 2 < len(lines) and not lines[index + 2].strip():
            problems.append(f"{heading}: more than one blank line after heading")

    section: str | None = None
    for index, line in enumerate(lines):
        if line in HEADINGS:
            section = line
            continue
        if line.startswith("## "):
            section = None
        if section and is_entry(line) and (index == 0 or lines[index - 1].strip()):
            problems.append(f"line {index + 1}: apparatus entry lacks a separating blank line")

    if normalize(text) != text:
        problems.append("file is not in canonical apparatus-spacing form")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("books"))
    parser.add_argument("--fix", action="store_true", help="rewrite files in canonical form")
    args = parser.parse_args()

    files = sorted(args.root.rglob("*.md"))
    changed = 0
    failures: list[tuple[Path, list[str]]] = []

    for path in files:
        original = path.read_text(encoding="utf-8")
        canonical = normalize(original)
        if args.fix and canonical != original:
            path.write_text(canonical, encoding="utf-8")
            changed += 1
        current = canonical if args.fix else original
        problems = validate(path, current)
        if problems:
            failures.append((path, problems))

    if failures:
        for path, problems in failures[:50]:
            for problem in problems:
                print(f"{path}: {problem}", file=sys.stderr)
        if len(failures) > 50:
            print(f"...and {len(failures) - 50} more files", file=sys.stderr)
        return 1

    action = "normalized" if args.fix else "validated"
    print(f"{action} {len(files)} chapter files; changed {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
