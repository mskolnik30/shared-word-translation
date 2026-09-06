#!/usr/bin/env python3
"""Flag identity lists that could be read as exhaustive.

This is a narrow editorial guardrail, not a substitute for human review. It
examines prose paragraphs in companion dossiers and requires an explicit
non-exhaustive or universal signal when three or more identity dimensions
appear together.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOSSIERS = ROOT / "companions" / "tsw-study" / "dossiers"

CATEGORIES = {
    "race or ethnicity": re.compile(r"\b(?:race|racial|ethnicity|ethnic)\b", re.I),
    "sex": re.compile(r"\bsex(?:es)?\b", re.I),
    "sexual orientation": re.compile(r"\bsexual orientation\b|\bqueer\b|\bLGBTQIA?\+?\b", re.I),
    "gender": re.compile(r"\bgender(?: identity| expression)?\b|\btransgender\b|\bnonbinary\b", re.I),
    "disability": re.compile(r"\b(?:disability|disabilities|disabled|capacity)\b", re.I),
    "nationality or citizenship": re.compile(r"\b(?:nationality|national origin|citizenship|immigration status)\b", re.I),
    "economic or social standing": re.compile(r"\b(?:wealth|poverty|economic status|social standing|social class|class status|usefulness)\b", re.I),
    "religion": re.compile(r"\b(?:religious identity|religious power|religion|faith tradition)\b", re.I),
    "age": re.compile(r"\b(?:age|young|old|elderly)\b", re.I),
}

NON_EXHAUSTIVE = re.compile(
    r"\b(?:including|not limited to|not restricted to|among the many|among other|such as|for example|"
    r"any other|every other|other status|whatever (?:their|a person's)|no (?:identity|status|"
    r"body|history|circumstance|difference)|none (?:limits|places|excludes))\b",
    re.I,
)

UNIVERSAL_SCOPE = re.compile(
    r"\b(?:human(?:ity|kind| beings?)?|people|persons?|dignity|worth|belonging|protection|"
    r"safety|exclude[ds]?|den(?:y|ies|ied)|rank(?:s|ed|ing)?|grad(?:e|es|ed|ing))\b",
    re.I,
)


def prose_paragraphs(text: str):
    if text.startswith("---"):
        parts = text.split("---", 2)
        text = parts[2] if len(parts) == 3 else text
    for number, paragraph in enumerate(re.split(r"\n\s*\n", text), start=1):
        paragraph = " ".join(line.strip() for line in paragraph.splitlines())
        if not paragraph or paragraph.startswith(("#", "- `", "- Read ", "- Compare ", ">")):
            continue
        yield number, paragraph


def main() -> int:
    failures = []
    reviewed = 0
    for path in sorted(DOSSIERS.glob("*.md")):
        for paragraph_number, paragraph in prose_paragraphs(path.read_text(encoding="utf-8")):
            present = [name for name, pattern in CATEGORIES.items() if pattern.search(paragraph)]
            if len(present) < 3 or "," not in paragraph or not UNIVERSAL_SCOPE.search(paragraph):
                continue
            reviewed += 1
            if re.search(r"\betc\.(?:\s|$)", paragraph, re.I) or not NON_EXHAUSTIVE.search(paragraph):
                failures.append((path.relative_to(ROOT), paragraph_number, present, paragraph[:180]))

    print("=== COMPANION INCLUSIVE-LIST AUDIT ===")
    print(f"Candidate identity-list paragraphs reviewed: {reviewed}")
    if failures:
        for path, paragraph_number, present, excerpt in failures:
            print(f"FAILED: {path} paragraph {paragraph_number}")
            print(f"  dimensions: {', '.join(present)}")
            print(f"  excerpt: {excerpt}")
        print(f"FAILED: {len(failures)} potentially closed identity list(s)")
        return 1

    print("PASSED: identity lists are explicitly non-exhaustive or universally closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
