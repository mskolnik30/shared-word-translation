#!/usr/bin/env python3
"""Audit unpublished Fluent Companion chapter candidates.

This audit checks structure, exact source binding, placeholders, duplicated prose,
and a small set of unsafe deterministic phrases. It cannot approve content.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "companions" / "fluent"
CHAPTER_ROOTS = [CONTENT_ROOT / "chapters", CONTENT_ROOT / "calibration"]
BOOK_ROOT = CONTENT_ROOT / "books"

REQUIRED_HEADINGS = [
    "## Before You Read",
    "### Where You Are",
    "### Chapter Path",
    "### Watch For",
    "## Read the Chapter",
    "## After You Read",
    "### Tell It in Your Own Words",
    "### Threads Through Scripture",
    "### Questions for Conversation",
    "### Prayer and Practice",
    "## Go Deeper",
]

REQUIRED_QUESTION_LABELS = ["Notice", "Understand", "Connect", "Respond"]
PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
    r"lorem ipsum",
    r"\{\{.+?\}\}",
    r"\[insert .+?\]",
    r"<\/?p>",
    r"(?m)^v\d{2}:",
]
SAFETY_PATTERNS = [
    r"God will heal (?:you|them) if",
    r"you must forgive and reconcile",
    r"suffering means God",
    r"mental illness is (?:a |the )?demon",
    r"your faith was not strong enough",
]


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError:
        return {}
    result = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chapter_files() -> list[Path]:
    paths = []
    for root in CHAPTER_ROOTS:
        if root.exists():
            paths.extend(root.rglob("*.md"))
    return sorted(paths)


def normalized_paragraphs(text: str) -> list[str]:
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", body):
        paragraph = paragraph.strip()
        if paragraph.startswith("#") or paragraph.startswith("-"):
            continue
        normalized = re.sub(r"[^a-z0-9 ]", "", paragraph.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        if len(normalized.split()) >= 20:
            paragraphs.append(normalized)
    return paragraphs


def main() -> int:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    records = []
    paragraph_owners: dict[str, list[str]] = defaultdict(list)

    batch_manifests = []
    record_manifests = []
    for manifest_path in sorted((CONTENT_ROOT / "manifests").glob("*.json")):
        candidate = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "books" in candidate:
            batch_manifests.append(candidate)
        if "records" in candidate:
            record_manifests.append(candidate)
    calibration_manifest = json.loads((CONTENT_ROOT / "manifests" / "calibration.json").read_text(encoding="utf-8"))
    source_locks = json.loads((CONTENT_ROOT / "manifests" / "source-locks.json").read_text(encoding="utf-8"))["sources"]
    manifest_chapters = {
        chapter
        for manifest in batch_manifests
        for book in manifest["books"]
        for chapter in book["chapters"]
    } | {
        chapter
        for manifest in record_manifests
        for chapter in manifest["records"]
    }
    discovered_chapters = {path.relative_to(ROOT).as_posix() for path in chapter_files()}
    if manifest_chapters != discovered_chapters:
        missing = sorted(discovered_chapters - manifest_chapters)
        extra = sorted(manifest_chapters - discovered_chapters)
        errors.append({
            "file": "companions/fluent/manifests",
            "check": "manifest-scope",
            "message": f"Unlisted files={missing}; missing files={extra}",
        })

    introduction_records = []
    introduction_manifests = batch_manifests + [{"books": [
        {"book": item["book"], "introduction": item["file"]}
        for item in calibration_manifest.get("introductions", [])
    ]}]
    for manifest in introduction_manifests:
      for book in manifest["books"]:
          intro_rel = book["introduction"]
          intro = ROOT / intro_rel
          if not intro.is_file():
              errors.append({"file": intro_rel, "check": "introduction", "message": "Missing book introduction"})
              continue
          intro_text = intro.read_text(encoding="utf-8")
          intro_meta = frontmatter(intro_text)
          if intro_meta.get("publication_status") != "unpublished":
              errors.append({"file": intro_rel, "check": "publication", "message": "Introduction must remain unpublished"})
          if intro_meta.get("book") != book["book"]:
              errors.append({"file": intro_rel, "check": "introduction", "message": "Book name does not match manifest"})
          required_intro_groups = (
              ("## Begin Here",),
              ("## At a Glance", "### At a Glance"),
              ("## What Is Going On?", "## The World Behind the Book"),
              ("## The Book's Movement", "## How the Book Moves"),
              ("## Watch For", "## Themes to Follow"),
              ("## A Thread to Carry", "## An Invitation to Begin"),
          )
          for alternatives in required_intro_groups:
              if not any(heading in intro_text for heading in alternatives):
                  errors.append({"file": intro_rel, "check": "introduction", "message": f"Missing one of {alternatives}"})
          introduction_records.append({
              "file": intro_rel,
              "book": intro_meta.get("book"),
              "sha256": sha256(intro),
              "status": intro_meta.get("companion_status"),
          })

    for path in chapter_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        meta = frontmatter(text)
        source_rel = meta.get("source", "")
        source = ROOT / source_rel

        if not meta:
            errors.append({"file": rel, "check": "frontmatter", "message": "Missing front matter"})
        for key in ("book", "chapter", "source", "source_status", "companion_status", "publication_status"):
            if not meta.get(key):
                errors.append({"file": rel, "check": "metadata", "message": f"Missing {key}"})
        if meta.get("publication_status") != "unpublished":
            errors.append({"file": rel, "check": "publication", "message": "Candidate must remain unpublished"})
        if not source.is_file():
            errors.append({"file": rel, "check": "binding", "message": f"Missing source {source_rel}"})
            source_hash = None
        else:
            source_text = source.read_text(encoding="utf-8")
            if "status: QA_PASSED" not in source_text:
                errors.append({"file": rel, "check": "binding", "message": "Source is not QA_PASSED"})
            source_hash = sha256(source)
            locked_hash = source_locks.get(source_rel)
            if locked_hash is None:
                errors.append({"file": rel, "check": "source-lock", "message": "Source is not present in source-locks.json"})
            elif locked_hash != source_hash:
                errors.append({"file": rel, "check": "source-lock", "message": "Source hash differs from approved candidate lock"})

        expected_h1 = f"# {meta.get('book', '')} {meta.get('chapter', '')}"
        if expected_h1 not in text:
            errors.append({"file": rel, "check": "title", "message": f"Missing {expected_h1}"})
        for heading in REQUIRED_HEADINGS:
            if heading not in text:
                errors.append({"file": rel, "check": "structure", "message": f"Missing {heading}"})
        if "### The Chapter in Brief" not in text and "### The Psalm in Brief" not in text:
            errors.append({"file": rel, "check": "structure", "message": "Missing brief summary heading"})
        if "### Follow the Story" not in text and "### Follow the Movement" not in text:
            errors.append({"file": rel, "check": "structure", "message": "Missing story/movement heading"})
        chapter_path = text.split("### Chapter Path", 1)[-1].split("### Watch For", 1)[0]
        source_verses = [int(number) for number in re.findall(r"(?m)^v(\d{2,3}):", source.read_text(encoding="utf-8"))] if source.is_file() else []
        max_verse = max(source_verses, default=0)
        for cited_chapter, start, end in re.findall(r"(\d+):(\d+)(?:[–-](\d+))?", chapter_path):
            if int(cited_chapter) != int(meta.get("chapter", "0")):
                errors.append({"file": rel, "check": "chapter-path", "message": f"Unexpected chapter citation {cited_chapter}:{start}"})
            if max(int(start), int(end or start)) > max_verse:
                errors.append({"file": rel, "check": "chapter-path", "message": f"Citation exceeds source verse count {max_verse}"})
        for label in REQUIRED_QUESTION_LABELS:
            if f"**{label}:**" not in text and f"#### {label}" not in text:
                errors.append({"file": rel, "check": "questions", "message": f"Missing {label} question"})

        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, text, flags=re.I):
                errors.append({"file": rel, "check": "placeholder", "message": f"Matched {pattern}"})
        for pattern in SAFETY_PATTERNS:
            if re.search(pattern, text, flags=re.I):
                errors.append({"file": rel, "check": "safety", "message": f"Matched {pattern}"})

        words = len(re.findall(r"\b[\w’'-]+\b", re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)))
        if not 500 <= words <= 1800:
            warnings.append({"file": rel, "check": "length", "message": f"Word count {words} outside 500–1800"})

        for paragraph in normalized_paragraphs(text):
            paragraph_owners[paragraph].append(rel)

        records.append({
            "file": rel,
            "book": meta.get("book"),
            "chapter": meta.get("chapter"),
            "source": source_rel,
            "source_sha256": source_hash,
            "word_count": words,
            "status": meta.get("companion_status"),
        })

    for paragraph, owners in paragraph_owners.items():
        if len(owners) > 1:
            errors.append({
                "file": ", ".join(owners),
                "check": "duplication",
                "message": f"Exact repeated prose paragraph: {paragraph[:120]}…",
            })

    bound_sources = {record["source"] for record in records}
    unbound_locks = sorted(set(source_locks) - bound_sources)
    if unbound_locks:
        errors.append({
            "file": "companions/fluent/manifests/source-locks.json",
            "check": "source-lock",
            "message": f"Locked sources have no companion record: {unbound_locks}",
        })

    report = {
        "audit": "fluent-companion-content",
        "result": "PASS" if not errors else "FAIL",
        "record_count": len(records),
        "introduction_count": len(introduction_records),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "records": records,
        "introductions": introduction_records,
        "human_approval": "NOT_PERFORMED",
        "publication_status": "blocked",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
