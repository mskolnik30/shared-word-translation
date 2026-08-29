#!/usr/bin/env python3
"""Recover historical TSW ##Vocabulary entries without altering Scripture or Notes."""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
import subprocess
import sys
import tarfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

HEADING_RE = re.compile(r"^##\s*(Notes|Vocabulary)\s*$", re.I)
VOCAB_ENTRY_RE = re.compile(
    r"^(v\d{1,3}(?:\s*[–—-]\s*\d{1,3})?)\s*:\s*(.*)$",
    re.I,
)
VERSE_RE = re.compile(r"^v(\d{1,3})\s*:?\s+(.*)$", re.I)
YAML_FIELD_RE = re.compile(
    r"^(book|testament|chapter|translation):\s*(.*?)\s*$",
    re.I,
)


def git(*args: str, check: bool = True) -> str:
    p = subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and p.returncode:
        raise RuntimeError(
            p.stderr.strip() or f"git {' '.join(args)} failed"
        )
    return p.stdout.strip()


def valid_ref(ref: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def parse_identity(text: str) -> tuple[str, str, int] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    data: dict[str, str] = {}

    for line in lines[1:30]:
        if line.strip() == "---":
            break

        m = YAML_FIELD_RE.match(line.strip())
        if m:
            data[m.group(1).lower()] = m.group(2).strip()

    try:
        return (
            data["book"].casefold(),
            data["testament"].upper(),
            int(data["chapter"]),
        )
    except Exception:
        return None


def section_bounds(
    lines: list[str],
    name: str,
) -> tuple[int, int] | None:
    start_heading = None

    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if m and m.group(1).lower() == name.lower():
            start_heading = i
            break

    if start_heading is None:
        return None

    end = len(lines)

    for i in range(start_heading + 1, len(lines)):
        if lines[i].startswith("##"):
            end = i
            break

    return start_heading, end


@dataclass
class VocabEntry:
    ref: str
    block: list[str]

    @property
    def normalized_ref(self) -> str:
        s = (
            self.ref.lower()
            .replace("—", "-")
            .replace("–", "-")
        )
        return re.sub(r"\s+", "", s)

    @property
    def text(self) -> str:
        return "\n".join(self.block)


def parse_vocab_entries(text: str) -> list[VocabEntry]:
    lines = text.splitlines()
    bounds = section_bounds(lines, "Vocabulary")

    if not bounds:
        return []

    start = bounds[0] + 1
    end = bounds[1]

    entries: list[VocabEntry] = []
    current: VocabEntry | None = None

    for line in lines[start:end]:
        m = VOCAB_ENTRY_RE.match(line.strip())

        if m:
            if current:
                while current.block and current.block[-1] == "":
                    current.block.pop()
                entries.append(current)

            current = VocabEntry(m.group(1), [line])

        elif current:
            current.block.append(line)

    if current:
        while current.block and current.block[-1] == "":
            current.block.pop()
        entries.append(current)

    return entries


def normalize_vocab_body(entry: VocabEntry) -> str:
    """Normalize vocabulary content without its verse-reference prefix."""
    if not entry.block:
        return ""

    first = entry.block[0].strip()
    m = VOCAB_ENTRY_RE.match(first)

    parts = [
        m.group(2) if m else first,
        *entry.block[1:],
    ]

    text = " ".join(
        part.strip()
        for part in parts
        if part.strip()
    )

    return re.sub(r"\s+", " ", text).casefold().strip()


def extract_verses(text: str) -> dict[int, str]:
    """Read Scripture body only, before Notes/Vocabulary."""
    lines = text.splitlines()
    cut = len(lines)

    for name in ("Notes", "Vocabulary"):
        bounds = section_bounds(lines, name)
        if bounds:
            cut = min(cut, bounds[0])

    verses: dict[int, list[str]] = {}
    current: int | None = None

    for line in lines[:cut]:
        m = VERSE_RE.match(line.strip())

        if m:
            current = int(m.group(1))
            verses[current] = [m.group(2)]

        elif current is not None:
            s = line.strip()

            if s.startswith("##") or s in {"<p>", "</p>"}:
                continue

            if s:
                verses[current].append(s)

    return {
        k: " ".join(v)
        for k, v in verses.items()
    }


def ref_numbers(ref: str) -> list[int]:
    nums = [int(x) for x in re.findall(r"\d+", ref)]

    if not nums:
        return []

    if len(nums) == 1:
        return nums

    a, b = nums[0], nums[1]

    if b < a or b - a > 100:
        return nums[:2]

    return list(range(a, b + 1))


def normalize_verse_text(s: str) -> str:
    s = s.casefold()
    s = re.sub(
        r"[^\w\s]",
        " ",
        s,
        flags=re.UNICODE,
    )
    return " ".join(s.split())


def verse_similarity(
    ref: str,
    old: dict[int, str],
    current: dict[int, str],
) -> float | None:
    nums = ref_numbers(ref)

    if not nums:
        return None

    old_parts: list[str] = []
    current_parts: list[str] = []

    for n in nums:
        if n not in old or n not in current:
            return None

        old_parts.append(old[n])
        current_parts.append(current[n])

    a = normalize_verse_text(" ".join(old_parts))
    b = normalize_verse_text(" ".join(current_parts))

    if not a or not b:
        return None

    return difflib.SequenceMatcher(None, a, b).ratio()


def load_source_tree(
    ref: str,
) -> tuple[
    dict[str, str],
    dict[tuple[str, str, int], tuple[str, str]],
]:
    by_path: dict[str, str] = {}
    by_id: dict[
        tuple[str, str, int],
        tuple[str, str],
    ] = {}

    proc = subprocess.Popen(
        ["git", "archive", "--format=tar", ref, "books"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.stdout is not None

    with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
        for member in tf:
            if (
                not member.isfile()
                or not member.name.lower().endswith(".md")
            ):
                continue

            fh = tf.extractfile(member)

            if not fh:
                continue

            text = fh.read().decode(
                "utf-8",
                errors="replace",
            )

            path = member.name.replace("\\", "/")
            by_path[path] = text

            ident = parse_identity(text)

            if ident:
                by_id[ident] = (path, text)

    _, err = proc.communicate()

    if proc.returncode:
        raise RuntimeError(
            err.decode(errors="replace").strip()
        )

    return by_path, by_id


def determine_source_ref(explicit: str | None) -> str:
    if explicit and explicit != "auto":
        if not valid_ref(explicit):
            raise RuntimeError(
                f"Source ref does not exist: {explicit}"
            )
        return git("rev-parse", explicit)

    # Richest known pre-normalization apparatus snapshot.
    if valid_ref("c1ced84"):
        return git("rev-parse", "c1ced84")

    raise RuntimeError(
        "Could not auto-detect c1ced84. "
        "Pass --source-ref explicitly."
    )


def replace_vocabulary_section(
    current_text: str,
    merged_entries: list[VocabEntry],
) -> str:
    lines = current_text.splitlines()
    bounds = section_bounds(lines, "Vocabulary")

    # Preserve the current heading spelling/spacing when it exists.
    heading = "##Vocabulary"

    if bounds:
        heading = lines[bounds[0]]
    vocab_lines = [heading]

    if merged_entries:
        vocab_lines.append("")

    for i, entry in enumerate(merged_entries):
        vocab_lines.extend(entry.block)

        if i != len(merged_entries) - 1:
            vocab_lines.append("")

    if bounds:
        start, end = bounds
        new_lines = (
            lines[:start]
            + vocab_lines
            + lines[end:]
        )
    else:
        prefix = list(lines)

        while prefix and prefix[-1] == "":
            prefix.pop()

        new_lines = (
            prefix
            + [""]
            + vocab_lines
        )

    return "\n".join(new_lines).rstrip() + "\n"


@dataclass
class FileResult:
    path: str
    source_path: str | None
    current_vocab: int
    source_vocab: int
    restored: int
    conflicts: int
    skipped_text_changed: int
    status: str


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Restore lost historical TSW Vocabulary while "
            "preserving current Scripture and Notes."
        )
    )

    ap.add_argument(
        "--source-ref",
        default="auto",
        help=(
            "Historical Git ref. Default: auto "
            "(prefers c1ced84 when present)."
        ),
    )

    ap.add_argument(
        "--threshold",
        type=float,
        default=0.88,
        help=(
            "Minimum relevant-verse text similarity for "
            "automatic restoration (default .88)."
        ),
    )

    ap.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Actually modify files. Without this flag, "
            "performs a dry run."
        ),
    )

    ap.add_argument(
        "--allow-text-changed",
        action="store_true",
        help=(
            "Restore even when relevant verse text similarity "
            "is below threshold. Use only after review."
        ),
    )

    ap.add_argument(
        "--books",
        default="books",
        help="Current Scripture root or book path.",
    )

    ap.add_argument(
        "--report-dir",
        default="audit/vocabulary_recovery",
        help="Report directory.",
    )

    args = ap.parse_args()

    try:
        root = Path(
            git("rev-parse", "--show-toplevel")
        )
        source_ref = determine_source_ref(
            args.source_ref
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    current_root = root / args.books

    if not current_root.exists():
        print(
            f"ERROR: {current_root} does not exist",
            file=sys.stderr,
        )
        return 2

    source_by_path, source_by_id = load_source_tree(
        source_ref
    )

    print(f"Source ref: {source_ref}")
    print(
        f"Mode: {'APPLY' if args.apply else 'DRY RUN'}"
    )

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    report_dir = root / args.report_dir
    report_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    backup_root = (
        root
        / "audit"
        / "vocabulary_recovery_backups"
        / stamp
    )

    results: list[FileResult] = []

    total_restored = 0
    total_conflicts = 0
    total_skipped = 0

    for path in sorted(current_root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()

        current = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        old = source_by_path.get(rel)
        source_path = rel if old is not None else None

        if old is None:
            ident = parse_identity(current)

            if ident and ident in source_by_id:
                source_path, old = source_by_id[ident]

        if old is None:
            results.append(
                FileResult(
                    rel,
                    None,
                    len(parse_vocab_entries(current)),
                    0,
                    0,
                    0,
                    0,
                    "NO_SOURCE_FILE",
                )
            )
            continue

        current_entries = parse_vocab_entries(current)
        source_entries = parse_vocab_entries(old)

        if not source_entries:
            results.append(
                FileResult(
                    rel,
                    source_path,
                    len(current_entries),
                    0,
                    0,
                    0,
                    0,
                    "SOURCE_HAS_NO_VOCABULARY",
                )
            )
            continue

        cur_by_ref: dict[
            str,
            list[VocabEntry],
        ] = {}

        for entry in current_entries:
            cur_by_ref.setdefault(
                entry.normalized_ref,
                [],
            ).append(entry)

        source_by_ref: dict[
            str,
            list[VocabEntry],
        ] = {}

        for entry in source_entries:
            source_by_ref.setdefault(
                entry.normalized_ref,
                [],
            ).append(entry)

        old_verses = extract_verses(old)
        cur_verses = extract_verses(current)

        conflicts = 0
        skipped = 0
        restored_count = 0

        merged_by_ref: dict[
            str,
            list[VocabEntry],
        ] = {}

        def safe_to_restore(ref: str) -> bool:
            nonlocal skipped

            sim = verse_similarity(
                ref,
                old_verses,
                cur_verses,
            )

            if sim is None or sim < args.threshold:
                if not args.allow_text_changed:
                    skipped += 1
                    return False

            return True

        for key, old_group in source_by_ref.items():
            cur_group = cur_by_ref.get(key, [])

            cur_bodies = [
                normalize_vocab_body(entry)
                for entry in cur_group
            ]

            used_cur: set[int] = set()
            out_group: list[VocabEntry] = []

            for old_entry in old_group:
                old_body = normalize_vocab_body(
                    old_entry
                )

                # 1. Exact entry already survives.
                exact = next(
                    (
                        i
                        for i, body in enumerate(cur_bodies)
                        if (
                            i not in used_cur
                            and body == old_body
                        )
                    ),
                    None,
                )

                if exact is not None:
                    out_group.append(cur_group[exact])
                    used_cur.add(exact)
                    continue

                # 2. Current entry is fuller than historical.
                current_fuller = next(
                    (
                        i
                        for i, body in enumerate(cur_bodies)
                        if (
                            i not in used_cur
                            and old_body
                            and old_body in body
                        )
                    ),
                    None,
                )

                if current_fuller is not None:
                    out_group.append(
                        cur_group[current_fuller]
                    )
                    used_cur.add(current_fuller)
                    continue

                # 3. Historical entry is fuller than a
                # surviving truncated current entry.
                historical_fuller = [
                    i
                    for i, body in enumerate(cur_bodies)
                    if (
                        i not in used_cur
                        and body
                        and body in old_body
                    )
                ]

                if historical_fuller:
                    if safe_to_restore(old_entry.ref):
                        out_group.append(old_entry)
                        restored_count += 1
                        used_cur.update(
                            historical_fuller
                        )
                    continue

                # 4. Very close rewrite: preserve current
                # and report rather than duplicate.
                close = []

                for i, body in enumerate(cur_bodies):
                    if (
                        i in used_cur
                        or not body
                        or not old_body
                    ):
                        continue

                    ratio = difflib.SequenceMatcher(
                        None,
                        old_body,
                        body,
                    ).ratio()

                    if ratio >= 0.90:
                        close.append(i)

                if close:
                    conflicts += 1
                    continue

                # 5. Distinct historical vocabulary entry:
                # restore if underlying verse remains stable.
                if safe_to_restore(old_entry.ref):
                    out_group.append(old_entry)
                    restored_count += 1

            # Keep current-only entries.
            for i, cur_entry in enumerate(cur_group):
                if i not in used_cur:
                    out_group.append(cur_entry)

            merged_by_ref[key] = out_group

        if not restored_count:
            if conflicts:
                status = "CONFLICTS_ONLY"
            elif skipped:
                status = "TEXT_CHANGED_SKIPS"
            else:
                status = "NO_LOST_VOCABULARY"

            results.append(
                FileResult(
                    rel,
                    source_path,
                    len(current_entries),
                    len(source_entries),
                    0,
                    conflicts,
                    skipped,
                    status,
                )
            )

            total_conflicts += conflicts
            total_skipped += skipped
            continue

        # Rebuild in historical reference order, then append
        # current-only references.
        merged: list[VocabEntry] = []
        emitted: set[str] = set()

        for entry in source_entries:
            key = entry.normalized_ref

            if key in emitted:
                continue

            merged.extend(
                merged_by_ref.get(key, [])
            )
            emitted.add(key)

        for entry in current_entries:
            key = entry.normalized_ref

            if key not in emitted:
                merged.extend(cur_by_ref[key])
                emitted.add(key)

        new_text = replace_vocabulary_section(
            current,
            merged,
        )

        # Safety invariant: everything except Vocabulary
        # must remain equivalent.
        def without_vocab(text: str) -> str:
            lines = text.splitlines()
            bounds = section_bounds(
                lines,
                "Vocabulary",
            )

            if not bounds:
                return "\n".join(lines).rstrip()

            start, end = bounds

            return "\n".join(
                lines[:start] + lines[end:]
            ).rstrip()

        if without_vocab(current) != without_vocab(
            new_text
        ):
            raise RuntimeError(
                "Safety invariant failed: recovery "
                f"would alter non-Vocabulary content in {rel}"
            )

        if args.apply:
            backup = backup_root / rel
            backup.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            shutil.copy2(path, backup)
            path.write_text(
                new_text,
                encoding="utf-8",
            )

        results.append(
            FileResult(
                rel,
                source_path,
                len(current_entries),
                len(source_entries),
                restored_count,
                conflicts,
                skipped,
                "RESTORED",
            )
        )

        total_restored += restored_count
        total_conflicts += conflicts
        total_skipped += skipped

    json_path = (
        report_dir
        / f"vocabulary_recovery_{stamp}.json"
    )
    csv_path = (
        report_dir
        / f"vocabulary_recovery_{stamp}.csv"
    )

    payload = {
        "source_ref": source_ref,
        "mode": (
            "apply" if args.apply else "dry-run"
        ),
        "threshold": args.threshold,
        "allow_text_changed": (
            args.allow_text_changed
        ),
        "summary": {
            "files_scanned": len(results),
            "vocabulary_restored": total_restored,
            "same_reference_conflicts": (
                total_conflicts
            ),
            "vocabulary_skipped_for_text_change": (
                total_skipped
            ),
        },
        "files": [
            asdict(result)
            for result in results
        ],
    }

    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    fieldnames = (
        list(asdict(results[0]).keys())
        if results
        else list(
            FileResult.__dataclass_fields__
        )
    )

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for result in results:
            writer.writerow(asdict(result))

    print("\nSummary")
    print(f"Files scanned: {len(results)}")
    print(
        "Historical vocabulary eligible/restored: "
        f"{total_restored}"
    )
    print(
        "Same-reference conflicts retained as current: "
        f"{total_conflicts}"
    )
    print(
        "Historical vocabulary skipped because verse "
        f"text changed: {total_skipped}"
    )

    if args.apply and total_restored:
        print(
            "Backups: "
            f"{backup_root.relative_to(root)}"
        )

    print(
        "JSON report: "
        f"{json_path.relative_to(root)}"
    )
    print(
        "CSV report:  "
        f"{csv_path.relative_to(root)}"
    )

    if not args.apply:
        print(
            "\nDry run only. Re-run with --apply "
            "after the totals look reasonable."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
