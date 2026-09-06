#!/usr/bin/env python3
"""Create source-bound draft Companion records for every uncovered Fluent chapter.

The generator preserves existing hand-shaped records. New records derive their
chapter path, reading prompts, contextual observations, and deeper-reading cues
from each QA-passed Fluent chapter's own structure and apparatus. Generated
records remain unpublished and require human review.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLUENT = ROOT / "translations" / "fluent"
COMPANION = ROOT / "companions" / "fluent"
MANIFEST_ROOT = COMPANION / "manifests"


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    raw = text.split("---\n", 2)[1]
    result: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_inline(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("TSW", "the translation")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def source_sections(text: str) -> list[dict[str, object]]:
    body = text.split("## Notes", 1)[0]
    matches = list(re.finditer(r"(?m)^## (.+?)\s*$", body))
    sections: list[dict[str, object]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[start:end]
        verses = [int(item) for item in re.findall(r"(?m)^v(\d{2,3}):", content)]
        if not verses:
            continue
        sections.append(
            {
                "title": clean_inline(match.group(1)),
                "start": min(verses),
                "end": max(verses),
            }
        )
    if not sections:
        verses = [int(item) for item in re.findall(r"(?m)^v(\d{2,3}):", body)]
        if verses:
            sections.append(
                {
                    "title": "The Chapter's Complete Movement",
                    "start": min(verses),
                    "end": max(verses),
                }
            )
    return sections


def source_notes(text: str) -> list[tuple[str, str]]:
    if "## Notes" not in text:
        return []
    raw = text.split("## Notes", 1)[1].split("## Vocabulary", 1)[0]
    notes: list[tuple[str, str]] = []
    seen: set[str] = set()
    for block in re.split(r"\n\s*\n", raw):
        block = block.strip()
        match = re.match(r"v([0-9–-]+):\s*(.+)", block, flags=re.S)
        if not match:
            continue
        label = match.group(1)
        body = clean_inline(match.group(2))
        if body and body not in seen:
            seen.add(body)
            notes.append((label, body))
    return notes


def source_vocabulary(text: str) -> list[tuple[str, str, str]]:
    if "## Vocabulary" not in text:
        return []
    raw = text.split("## Vocabulary", 1)[1]
    blocks = [item.strip() for item in re.split(r"\n\s*\n", raw) if item.strip()]
    entries: list[tuple[str, str, str]] = []
    index = 0
    while index < len(blocks):
        match = re.match(r"v([0-9–-]+):\s*(.+)", blocks[index], flags=re.S)
        if not match:
            index += 1
            continue
        label = match.group(1)
        term = clean_inline(match.group(2))
        explanation = ""
        if index + 1 < len(blocks) and not re.match(r"v[0-9–-]+:", blocks[index + 1]):
            explanation = clean_inline(blocks[index + 1])
            index += 1
        entries.append((label, term, explanation))
        index += 1
    return entries


def sentence_case_heading(title: str) -> str:
    return title.rstrip(".?!")


def join_movement(titles: list[str]) -> str:
    if len(titles) == 1:
        return titles[0]
    if len(titles) == 2:
        return f"{titles[0]} and then {titles[1]}"
    return f"{', '.join(titles[:-1])}, and finally {titles[-1]}"


def chapter_path(sections: list[dict[str, object]], chapter: int) -> str:
    lines = []
    for section in sections:
        start = int(section["start"])
        end = int(section["end"])
        reference = f"{chapter}:{start}" if start == end else f"{chapter}:{start}–{end}"
        lines.append(f"- **{reference}:** {section['title']}.")
    return "\n".join(lines)


def position_text(book: str, chapter: int, total: int) -> str:
    if total == 1:
        return f"This is the only chapter of {book}."
    if chapter == 1:
        return f"This opening chapter begins {book}'s {total}-chapter movement."
    if chapter == total:
        return f"This final chapter completes {book}'s {total}-chapter movement."
    return f"This is chapter {chapter} of {book}'s {total}-chapter movement."


def neighbor_text(book: str, chapter: int, total: int) -> str:
    if total == 1:
        return f"Read the {book} book guide before returning to this chapter as a whole."
    if chapter == 1:
        return f"Read {book} {chapter + 1} afterward to see how the opening movement continues."
    if chapter == total:
        return f"Read {book} {chapter - 1} again to see what the closing movement receives and resolves—or leaves unresolved."
    return f"Read {book} {chapter - 1} and {book} {chapter + 1} to keep this chapter inside its immediate literary setting."


def genre_guidance(testament: str, book: str) -> str:
    poetry = {"Psalms", "Job", "Proverbs", "Ecclesiastes", "Song of Songs", "Lamentations"}
    prophets = {
        "Isaiah", "Jeremiah", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
        "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi",
    }
    gospels = {"Matthew", "Mark", "Luke", "John"}
    letters = {
        "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
        "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
        "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
    }
    if book in poetry:
        return "Attend to image, repetition, parallel lines, changes of speaker, and emotional movement; poetic language should not be reduced to a flat proposition."
    if book in prophets:
        return "Keep the prophecy's first historical horizon visible before tracing later echoes, and do not turn judgment or restoration imagery into a timetable for current events."
    if book in gospels:
        return "Follow the narrative sequence and the responses of different characters before combining this Gospel's presentation with parallel accounts."
    if book in letters:
        return "Follow the argument across the whole letter, remembering that a sentence addresses a particular community and should not be isolated from its surrounding appeal."
    if book == "Revelation":
        return "Receive the chapter's symbols through their scriptural echoes and pastoral purpose rather than converting them into a speculative calendar."
    if book == "Acts":
        return "Distinguish what the narrative reports from what it commands, and notice how the Spirit leads real communities through conflict and change."
    if testament == "OT":
        return "Keep the chapter within Israel's narrated covenant life, allowing its legal, historical, and theological tensions to remain visible."
    return "Read the chapter within its own literary setting before drawing broader theological conclusions."


def render_record(source: Path, output: Path, total: int) -> str:
    text = source.read_text(encoding="utf-8")
    meta = frontmatter(text)
    book = meta["book"]
    chapter = int(meta["chapter"])
    testament = meta["testament"]
    sections = source_sections(text)
    if not sections:
        raise ValueError(f"No verse-bearing sections in {source}")
    notes = source_notes(text)
    vocabulary = source_vocabulary(text)

    titles = [sentence_case_heading(str(item["title"])) for item in sections]
    movement = join_movement(titles)
    first = titles[0]
    last = titles[-1]
    middle = titles[len(titles) // 2]
    selected_notes = notes[:3]

    watch = (
        f"In {book} {chapter}, watch how the movement from “{first}” toward “{last}” changes the chapter's emphasis. "
        f"Do not let one verse erase the sequence created by the whole chapter."
    )
    if selected_notes:
        watch += f" The source apparatus especially marks verse {selected_notes[0][0]} for careful attention."

    note_paragraphs = []
    for label, body in selected_notes[1:3]:
        note_paragraphs.append(f"At verse {label}, the source notes preserve this detail: {body}")
    if not note_paragraphs:
        note_paragraphs.append(
            f"The section sequence in {book} {chapter}—from {first} to {last}—supplies the primary context. Where the text remains compressed, the Companion should preserve that restraint rather than inventing a missing explanation."
        )

    vocabulary_text = ""
    if vocabulary:
        label, term, explanation = vocabulary[0]
        vocabulary_text = (
            f" One vocabulary entry at verse {label} identifies {term}."
            + (f" {explanation}" if explanation else "")
        )

    source_rel = source.relative_to(ROOT).as_posix()
    output_rel = output.relative_to(ROOT).as_posix()
    study = neighbor_text(book, chapter, total)
    brief_sections = "; then ".join(titles[:4])
    if len(titles) > 4:
        brief_sections += f"; and the remaining movement leads to {last}"

    return f"""---
resource: fluent-companion
record_type: chapter-companion
book: {book}
chapter: {chapter}
source: {source_rel}
source_status: QA_PASSED
companion_status: GENERATED_REVIEW_REQUIRED
publication_status: unpublished
template_version: 1.0
---

# {book} {chapter}

## Before You Read

### Where You Are

{position_text(book, chapter, total)} The chapter is organized around {movement}. Read it as one movement before separating individual lines for closer study.

### Chapter Path

{chapter_path(sections, chapter)}

### Watch For

{watch}

## Read the Chapter

Read {book} {chapter} in the Fluent Translation. Follow the section changes, repeated words, contrasts, speakers, and responses before consulting the Companion.

## After You Read

### Tell It in Your Own Words

How does {book} {chapter} move from {first} through {middle} to {last}, and what changes—or remains unresolved—along the way?

### The Chapter in Brief

{book} {chapter} moves through {brief_sections}. These headings provide the chapter's visible architecture. The details within them show how the chapter develops its claims rather than presenting a collection of detached sayings. The ending at “{last}” should therefore be heard in relation to the opening at “{first}.”

### Follow the Movement

The order of {book} {chapter} matters. Its movement through {movement} controls how isolated details should be heard. A reading that begins with the conclusion but ignores the earlier tension may make the chapter say more—or less—than its complete shape allows.

{' '.join(note_paragraphs)}{vocabulary_text}

For {book} {chapter}, {genre_guidance(testament, book).lower()} The goal is attentive understanding, not premature resolution. Where the source notes identify uncertainty, readers should keep that uncertainty visible.

### Threads Through Scripture

{study} Then use the {book} book guide to trace the chapter's major themes through the rest of the book. Wider biblical connections should deepen attention to this passage rather than replace its own voice.

### Questions for Conversation

- **Notice:** What words, images, people, or actions connect “{first}” with “{last}”?
- **Understand:** Why does the chapter place “{middle}” where it does?
- **Connect:** Where does this chapter challenge a familiar assumption without supplying an easy resolution?
- **Respond:** What is one truthful, non-coercive response invited by the chapter's complete movement?

### Prayer and Practice

Choose one phrase or image from {book} {chapter} and carry it through the day. Before turning it into advice for someone else, ask what it reveals about your own attention, responsibility, hope, or need for mercy.

## Go Deeper

### What Needs Context

This record is bound to `{source_rel}` and remains an unpublished candidate. The source chapter's own headings and apparatus govern its outline.{(' ' + selected_notes[0][1]) if selected_notes else ''}

### Wrestle with This

What becomes harder—or more faithful—when {book} {chapter} is allowed to retain the tension between “{first}” and “{last}”?

### Further Study

{study} Revisit the book introduction before making a whole-book or whole-Bible claim from this chapter.
"""


def introduction_map() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in (COMPANION / "books").rglob("introduction.md"):
        book = frontmatter(path.read_text(encoding="utf-8")).get("book")
        if book:
            result[book] = path
    return result


def existing_records() -> dict[str, Path]:
    records = list((COMPANION / "chapters").rglob("*.md"))
    records.extend((COMPANION / "calibration").glob("*.md"))
    return {
        source: path
        for path in records
        if (source := frontmatter(path.read_text(encoding="utf-8")).get("source"))
    }


def manifested_records(exclude: Path) -> set[str]:
    result: set[str] = set()
    for path in MANIFEST_ROOT.glob("*.json"):
        if path == exclude:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        result.update(data.get("records", []))
        for book in data.get("books", []):
            result.update(book.get("chapters", []))
    return result


def main() -> int:
    introductions = introduction_map()
    if len(introductions) != 66:
        raise SystemExit(f"Expected 66 book introductions; found {len(introductions)}")

    sources = sorted(FLUENT.rglob("*.md"))
    totals: dict[str, int] = defaultdict(int)
    for source in sources:
        totals[frontmatter(source.read_text(encoding="utf-8"))["book"]] += 1

    existing = existing_records()
    created = 0
    preserved = 0
    refreshed = 0
    for source in sources:
        source_rel = source.relative_to(ROOT).as_posix()
        meta = frontmatter(source.read_text(encoding="utf-8"))
        book = meta["book"]
        chapter = int(meta["chapter"])
        number = re.search(r"_(\d+)\.md$", source.name)
        if not number:
            raise ValueError(f"Cannot derive chapter filename from {source}")
        output = existing.get(source_rel)
        if output is not None:
            output_meta = frontmatter(output.read_text(encoding="utf-8"))
            if output_meta.get("companion_status") != "GENERATED_REVIEW_REQUIRED":
                preserved += 1
                continue
            output.write_text(render_record(source, output, totals[book]), encoding="utf-8")
            refreshed += 1
            continue
        output = COMPANION / "chapters" / introductions[book].parent.name / f"{number.group(1)}.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_record(source, output, totals[book]), encoding="utf-8")
        created += 1

    lock_path = MANIFEST_ROOT / "source-locks.json"
    locks = json.loads(lock_path.read_text(encoding="utf-8"))
    locks["sources"] = {
        source.relative_to(ROOT).as_posix(): sha256(source) for source in sources
    }
    lock_path.write_text(json.dumps(locks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    expansion_path = MANIFEST_ROOT / "complete-corpus-expansion.json"
    already_manifested = manifested_records(expansion_path)
    all_records = list((COMPANION / "chapters").rglob("*.md"))
    all_records.extend((COMPANION / "calibration").glob("*.md"))
    expansion_records = sorted(
        path.relative_to(ROOT).as_posix()
        for path in all_records
        if path.relative_to(ROOT).as_posix() not in already_manifested
    )
    expansion = {
        "schema_version": 1,
        "resource": "fluent-companion",
        "batch": "complete-corpus-expansion",
        "status": "GENERATED_REVIEW_REQUIRED",
        "publication_status": "unpublished",
        "template_version": "1.0",
        "canonical_chapter_target": len(sources),
        "records": expansion_records,
        "human_review": "companions/fluent/reviews/complete-corpus-expansion-review.md",
    }
    expansion_path.write_text(json.dumps(expansion, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Preserved existing chapter records: {preserved}")
    print(f"Refreshed generated chapter records: {refreshed}")
    print(f"Created chapter records: {created}")
    print(f"Canonical source locks: {len(locks['sources'])}")
    print(f"Expansion manifest records: {len(expansion_records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
