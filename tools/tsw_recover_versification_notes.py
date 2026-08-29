#!/usr/bin/env python3

from pathlib import Path
import importlib.util
import subprocess
import sys
import re

SOURCE = "81bcb9f75c59a375e72d2d27f68671eb0259ce1b"

# Only chapters whose versification shift has been established by
# high-confidence exact-text matching. Ezekiel 21 is intentionally
# excluded because its historical notes contain inconsistent internal
# verse labels and should be reviewed separately.
OFFSETS = {
    "books/NT/philippians/Philippians_02.md": -1,
    "books/OT/1chronicles/1Chronicles_06.md": 15,
    "books/OT/1kings/1Kings_05.md": -14,
    "books/OT/psalms/Psalm_038.md": -1,
    "books/OT/psalms/Psalm_039.md": -1,
    "books/OT/psalms/Psalm_054.md": -2,
    "books/OT/psalms/Psalm_055.md": -1,
    "books/OT/psalms/Psalm_059.md": -1,
    "books/OT/psalms/Psalm_061.md": -1,
    "books/OT/psalms/Psalm_063.md": -1,
    "books/OT/psalms/Psalm_065.md": -1,
    "books/OT/psalms/Psalm_075.md": -1,
}

APPLY = "--apply" in sys.argv

spec = importlib.util.spec_from_file_location(
    "recover", "tools/tsw_recover_notes.py"
)
recover = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = recover
spec.loader.exec_module(recover)

INLINE_REF_RE = re.compile(
    r"\bv(\d{1,3})(?:\s*[–-]\s*(\d{1,3}))?\b",
    re.I
)


def map_ref(ref, offset):
    nums = recover.ref_numbers(ref)
    if not nums:
        return None

    mapped = [n + offset for n in nums]
    if any(n < 1 for n in mapped):
        return None

    if len(mapped) == 1:
        return f"v{mapped[0]:02}"

    return f"v{mapped[0]:02}–{mapped[-1]:02}"


def remap_inline_refs(text, offset):
    def repl(match):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else None

        new_start = start + offset
        if new_start < 1:
            return match.group(0)

        if end is None:
            return f"v{new_start:02}"

        new_end = end + offset
        if new_end < 1:
            return match.group(0)

        return f"v{new_start:02}–{new_end:02}"

    return INLINE_REF_RE.sub(repl, text)


def clean_duplicate_leading_ref(body, old_ref):
    # Some historical apparatus entries were malformed like:
    #   v16: - v16: “After the ark came to rest” ...
    # Remove only a duplicate copy of the entry's own leading reference.
    escaped = re.escape(old_ref)
    return re.sub(
        rf"^\s*-\s*{escaped}\s*:\s*",
        "",
        body,
        count=1,
        flags=re.I
    )


def remap_entry(entry, new_ref, offset):
    block = list(entry.block)
    if not block:
        return None

    first = block[0]
    m = recover.NOTE_ENTRY_RE.match(first.strip())
    if not m:
        return None

    indent = first[:len(first) - len(first.lstrip())]
    body = m.group(2)

    body = clean_duplicate_leading_ref(body, entry.ref)
    body = remap_inline_refs(body, offset)

    block[0] = f"{indent}{new_ref}: {body}"

    # Remap verse references in continuation lines too.
    for i in range(1, len(block)):
        block[i] = remap_inline_refs(block[i], offset)

    return recover.NoteEntry(new_ref, block)


def exact_text_match(old_verses, new_verses, old_ref, new_ref):
    old_nums = recover.ref_numbers(old_ref)
    new_nums = recover.ref_numbers(new_ref)

    if not old_nums or not new_nums or len(old_nums) != len(new_nums):
        return False

    try:
        old_text = " ".join(old_verses[n] for n in old_nums)
        new_text = " ".join(new_verses[n] for n in new_nums)
    except KeyError:
        return False

    return (
        recover.normalize_verse_text(old_text)
        == recover.normalize_verse_text(new_text)
    )


total = 0
changed_files = 0

for rel, offset in OFFSETS.items():
    path = Path(rel)
    current = path.read_text()

    historical = subprocess.check_output(
        ["git", "show", f"{SOURCE}:{rel}"],
        text=True
    )

    old_verses = recover.extract_verses(historical)
    new_verses = recover.extract_verses(current)

    current_entries = recover.parse_note_entries(current)
    historical_entries = recover.parse_note_entries(historical)

    current_bodies = {
        recover.normalize_note_body(e)
        for e in current_entries
    }

    additions = []

    for note in historical_entries:
        body = recover.normalize_note_body(note)

        if body in current_bodies:
            continue

        new_ref = map_ref(note.ref, offset)
        if not new_ref:
            continue

        if not exact_text_match(
            old_verses,
            new_verses,
            note.ref,
            new_ref
        ):
            continue

        mapped = remap_entry(note, new_ref, offset)
        if mapped:
            additions.append(mapped)
            current_bodies.add(body)

    if not additions:
        continue

    print(f"{rel}: {len(additions)} notes")
    for note in additions:
        print(f"  {note.ref}: {recover.normalize_note_body(note)[:90]}")

    total += len(additions)

    if APPLY:
        merged = current_entries + additions

        def sort_key(entry):
            nums = recover.ref_numbers(entry.ref)
            return nums[0] if nums else 9999

        merged.sort(key=sort_key)

        new_text = recover.replace_notes_section(current, merged)

        # Safety invariant: nothing outside Notes may change.
        def without_notes(text):
            lines = text.splitlines()
            bounds = recover.section_bounds(lines, "Notes")
            if not bounds:
                return "\n".join(lines).rstrip()
            a, z = bounds
            return "\n".join(lines[:a] + lines[z:]).rstrip()

        if without_notes(current) != without_notes(new_text):
            raise RuntimeError(
                f"Safety invariant failed for {rel}"
            )

        path.write_text(new_text)
        changed_files += 1

print()
print(f"Recoverable remapped notes: {total}")

if APPLY:
    print(f"Files changed: {changed_files}")
    print("Mode: APPLY")
else:
    print("Mode: DRY RUN")
