#!/usr/bin/env python3
"""Audit TSW apparatus counts across recent Git history without changing files."""
from __future__ import annotations

import argparse
import csv
import io
import re
import subprocess
import sys
import tarfile
from dataclasses import dataclass, asdict
from pathlib import Path

HEADING_RE = re.compile(r"^##\s*(Notes|Vocabulary)\s*$", re.I)
ENTRY_RE = re.compile(r"^v\d{1,3}(?:\s*[–—-]\s*\d{1,3})?\s*:", re.I)


def git(*args: str, check: bool = True) -> str:
    p = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(p.stderr.strip() or f"git {' '.join(args)} failed")
    return p.stdout.strip()


def valid_ref(ref: str) -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def extract_section(text: str, name: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if m and m.group(1).lower() == name.lower():
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith("##"):
            end = i
            break
    return "\n".join(lines[start:end]).strip()


def entry_count(section: str) -> int:
    return sum(1 for line in section.splitlines() if ENTRY_RE.match(line.strip()))


@dataclass
class Snapshot:
    ref: str
    commit: str
    date: str
    subject: str
    chapters: int = 0
    notes_sections: int = 0
    note_entries: int = 0
    vocabulary_sections: int = 0
    vocabulary_entries: int = 0


def snapshot(ref: str) -> Snapshot:
    commit = git("rev-parse", ref)
    date = git("show", "-s", "--format=%cI", ref)
    subject = git("show", "-s", "--format=%s", ref)
    out = Snapshot(ref=ref, commit=commit, date=date, subject=subject)

    proc = subprocess.Popen(["git", "archive", "--format=tar", ref, "books"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
        for member in tf:
            if not member.isfile() or not member.name.lower().endswith(".md"):
                continue
            fh = tf.extractfile(member)
            if not fh:
                continue
            text = fh.read().decode("utf-8", errors="replace")
            out.chapters += 1
            notes = extract_section(text, "Notes")
            vocab = extract_section(text, "Vocabulary")
            if notes:
                out.notes_sections += 1
                out.note_entries += entry_count(notes)
            if vocab:
                out.vocabulary_sections += 1
                out.vocabulary_entries += entry_count(vocab)
    _, err = proc.communicate()
    if proc.returncode:
        raise RuntimeError(err.decode(errors="replace").strip())
    return out


def candidate_refs(recent: int) -> list[str]:
    refs: list[str] = []
    # Known pre/final-audit anchors preserved in the 2026-08-25 terminal record.
    for ref in ("c1ced84", "8009d20", "HEAD"):
        if valid_ref(ref):
            refs.append(ref)

    # Locate commits that first added distinctive final-audit files; include their parents.
    for path in (
        "audit/FINAL_AUDIT.json",
        "audit/FINAL_APPARATUS_STRUCTURE_CHANGES.json",
        "audit/PASS2H_APPARATUS_FINAL.json",
    ):
        log = git("log", "--diff-filter=A", "--format=%H", "--", path, check=False)
        for commit in log.splitlines()[:3]:
            if commit and valid_ref(commit):
                refs.append(commit)
                parent = f"{commit}^"
                if valid_ref(parent):
                    refs.append(parent)

    log = git("log", "--first-parent", f"-n{recent}", "--format=%H")
    refs.extend(x for x in log.splitlines() if x)

    seen = set()
    unique = []
    for ref in refs:
        commit = git("rev-parse", ref) if valid_ref(ref) else None
        if commit and commit not in seen:
            seen.add(commit)
            unique.append(ref)
    return unique


def main() -> int:
    ap = argparse.ArgumentParser(description="Count TSW Notes/Vocabulary across recent Git history.")
    ap.add_argument("--recent", type=int, default=30, help="Number of first-parent commits to inspect (default 30).")
    ap.add_argument("--ref", action="append", default=[], help="Specific ref to inspect; may be repeated.")
    ap.add_argument("--csv", default="audit/NOTES_HISTORY_COUNTS.csv", help="CSV output path.")
    args = ap.parse_args()

    try:
        root = git("rev-parse", "--show-toplevel")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    Path(root).resolve()

    refs = args.ref or candidate_refs(args.recent)
    rows: list[Snapshot] = []
    print(f"Inspecting {len(refs)} unique commits/refs…")
    for i, ref in enumerate(refs, 1):
        try:
            row = snapshot(ref)
            rows.append(row)
            print(f"[{i:>2}/{len(refs)}] {row.commit[:8]}  notes={row.note_entries:>5}  vocab={row.vocabulary_entries:>5}  {row.subject}")
        except Exception as e:
            print(f"WARN {ref}: {e}", file=sys.stderr)

    if not rows:
        print("No snapshots could be inspected.", file=sys.stderr)
        return 1

    # Chronological sort for change analysis.
    chrono = sorted(rows, key=lambda r: r.date)
    biggest_drop = None
    for a, b in zip(chrono, chrono[1:]):
        drop = a.note_entries - b.note_entries
        if drop > 0 and (biggest_drop is None or drop > biggest_drop[0]):
            biggest_drop = (drop, a, b)

    best = max(rows, key=lambda r: r.note_entries)
    print("\nSummary")
    print(f"Highest note count inspected: {best.note_entries} at {best.commit[:12]} ({best.date})")
    if biggest_drop:
        drop, a, b = biggest_drop
        print(f"Largest inspected note drop: {drop} entries")
        print(f"  from {a.commit[:12]} ({a.note_entries}) — {a.subject}")
        print(f"    to {b.commit[:12]} ({b.note_entries}) — {b.subject}")
        print(f"Suggested recovery baseline for that drop: {a.commit}")

    out = Path(args.csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for row in chrono:
            w.writerow(asdict(row))
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
