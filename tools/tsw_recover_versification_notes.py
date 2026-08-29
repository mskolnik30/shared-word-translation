#!/usr/bin/env python3

from pathlib import Path
import importlib.util
import subprocess
import sys
import re

SOURCE = "81bcb9f75c59a375e72d2d27f68671eb0259ce1b"

# Chapters with a verified systematic versification shift.
# Ezekiel 21 remains intentionally excluded for manual/recreation review.
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

# Individually verified exact-text mappings that do not belong to a
# sufficiently reliable chapter-wide offset. Psalm 53 is intentionally
# excluded because its historical note was judged too generic to retain.
IRREGULAR = {
    "books/NT/luke/Luke_15.md": {
        "source_path": "books/NT/luke/Luke_15.md",
        "refs": {
            "v23–24": "v22–23",
            "v25–27": "v24–26",
            "v28–30": "v27–29",
            "v31": "v30",
            "v32": "v31",
        },
    },
    "books/OT/genesis/Genesis_35.md": {
        "source_path": "books/OT/genesis/Genesis_35.md",
        "refs": {
            "v28–30": "v27–29",
        },
    },
    "books/OT/psalms/Psalm_021.md": {
        "source_path": "books/OT/psalms/Psalm_21.md",
        "refs": {
            "v3": "v02",
            "v6": "v05",
            "v7": "v06",
        },
    },
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


def note_signature(entry):
    """Compare note substance while ignoring verse-label/Markdown cleanup."""
    s = recover.normalize_note_body(entry)
    s = INLINE_REF_RE.sub(" ", s)
    s = re.sub(r'[*_`#>:“”"‘’.,;()\[\]{}—–-]+', " ", s)
    return " ".join(s.split())


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
    escaped = re.escape(old_ref)
    return re.sub(
        rf"^\s*-\s*{escaped}\s*:\s*",
        "",
        body,
        count=1,
        flags=re.I,
    )


def remap_entry(entry, new_ref, offset=None, remap_internal=True):
    block = list(entry.block)
    if not block:
        return None

    first = block[0]
    m = recover.NOTE_ENTRY_RE.match(first.strip())
    if not m:
        return None

    indent = first[:len(first) - len(first.lstrip())]
    body = clean_duplicate_leading_ref(m.group(2), entry.ref)

    if remap_internal and offset is not None:
        body = remap_inline_refs(body, offset)

    block[0] = f"{indent}{new_ref}: {body}"

    if remap_internal and offset is not None:
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


def write_if_needed(rel, current, current_entries, additions):
    if not additions:
        return 0

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
        raise RuntimeError(f"Safety invariant failed for {rel}")

    Path(rel).write_text(new_text)
    return 1


total = 0
changed_files = 0

# 1. Systematic mappings.
for rel, offset in OFFSETS.items():
    path = Path(rel)
    current = path.read_text()

    historical = subprocess.check_output(
        ["git", "show", f"{SOURCE}:{rel}"],
        text=True,
    )

    old_verses = recover.extract_verses(historical)
    new_verses = recover.extract_verses(current)

    current_entries = recover.parse_note_entries(current)
    historical_entries = recover.parse_note_entries(historical)

    current_signatures = {note_signature(e) for e in current_entries}
    additions = []

    for note in historical_entries:
        if note_signature(note) in current_signatures:
            continue

        new_ref = map_ref(note.ref, offset)
        if not new_ref:
            continue

        if not exact_text_match(
            old_verses,
            new_verses,
            note.ref,
            new_ref,
        ):
            continue

        mapped = remap_entry(
            note,
            new_ref,
            offset=offset,
            remap_internal=True,
        )

        if mapped and note_signature(mapped) not in current_signatures:
            additions.append(mapped)
            current_signatures.add(note_signature(mapped))

    if additions:
        print(f"{rel}: {len(additions)} notes")
        for note in additions:
            print(
                f"  {note.ref}: "
                f"{recover.normalize_note_body(note)[:90]}"
            )

        total += len(additions)

        if APPLY:
            changed_files += write_if_needed(
                rel,
                current,
                current_entries,
                additions,
            )


# 2. Explicit irregular mappings.
for rel, config in IRREGULAR.items():
    path = Path(rel)
    current = path.read_text()
    source_rel = config["source_path"]
    mappings = config["refs"]

    historical = subprocess.check_output(
        ["git", "show", f"{SOURCE}:{source_rel}"],
        text=True,
    )

    old_verses = recover.extract_verses(historical)
    new_verses = recover.extract_verses(current)

    current_entries = recover.parse_note_entries(current)
    historical_entries = recover.parse_note_entries(historical)

    current_signatures = {note_signature(e) for e in current_entries}
    additions = []

    for note in historical_entries:
        new_ref = mappings.get(note.ref)
        if not new_ref:
            continue

        if note_signature(note) in current_signatures:
            continue

        if not exact_text_match(
            old_verses,
            new_verses,
            note.ref,
            new_ref,
        ):
            raise RuntimeError(
                f"Approved irregular mapping no longer matches text: "
                f"{rel} {note.ref} -> {new_ref}"
            )

        # These nine approved notes contain no secondary verse references
        # requiring remapping, so only the primary apparatus reference is
        # changed.
        mapped = remap_entry(
            note,
            new_ref,
            offset=None,
            remap_internal=False,
        )

        if mapped and note_signature(mapped) not in current_signatures:
            additions.append(mapped)
            current_signatures.add(note_signature(mapped))

    if additions:
        print(f"{rel}: {len(additions)} irregular notes")
        for note in additions:
            print(
                f"  {note.ref}: "
                f"{recover.normalize_note_body(note)[:90]}"
            )

        total += len(additions)

        if APPLY:
            changed_files += write_if_needed(
                rel,
                current,
                current_entries,
                additions,
            )


print()
print(f"Recoverable remapped notes: {total}")

if APPLY:
    print(f"Files changed: {changed_files}")
    print("Mode: APPLY")
else:
    print("Mode: DRY RUN")
