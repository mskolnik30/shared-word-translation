#!/usr/bin/env python3
"""Audit the checksum-bound, unpublished Biblical profile-image candidates."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "resources/biblical-world/profiles/plan.json"
MANIFEST_PATH = ROOT / "resources/biblical-world/profiles/candidates/manifest.json"
CANDIDATE_DIR = MANIFEST_PATH.parent

EXPECTED_FILES = {
    "profile-person-abraham-v1.png",
    "profile-person-sarah-v1.png",
    "profile-person-moses-v1.png",
    "profile-person-ruth-v1.png",
    "profile-person-david-v1.png",
    "profile-person-mary-nazareth-v1.png",
    "profile-person-mary-magdalene-v1.png",
    "profile-person-peter-v1.png",
    "profile-person-paul-v1.png",
    "profile-person-jesus-v1.png",
    "profile-book-genesis-v1.png",
    "profile-book-isaiah-v1.png",
    "profile-books-gospels-v1.png",
    "profile-book-hebrews-v1.png",
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("not a PNG with an IHDR header")
    return struct.unpack(">II", header[16:24])


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    plan_ids = {entry["id"] for entry in plan["entries"]}
    entries = manifest.get("entries", [])

    if manifest.get("candidate_count") != len(entries):
        errors.append("manifest candidate_count does not match entries")
    if len(entries) != 14:
        errors.append(f"expected 14 pilot candidates, found {len(entries)}")
    files = {entry.get("file") for entry in entries}
    if files != EXPECTED_FILES:
        errors.append(f"candidate file set mismatch: missing={sorted(EXPECTED_FILES-files)} extra={sorted(files-EXPECTED_FILES)}")
    if len({entry.get("id") for entry in entries}) != len(entries):
        errors.append("candidate IDs are not unique")
    if len({entry.get("sha256") for entry in entries}) != len(entries):
        errors.append("candidate hashes are not unique; possible duplicate images")

    covered_plan_ids: set[str] = set()
    for entry in entries:
        label = entry.get("id", "<missing-id>")
        path = CANDIDATE_DIR / str(entry.get("file", ""))
        if not path.is_file():
            errors.append(f"{label}: file is missing")
            continue
        if file_hash(path) != entry.get("sha256"):
            errors.append(f"{label}: SHA-256 mismatch")
        if path.stat().st_size != entry.get("bytes"):
            errors.append(f"{label}: byte-size mismatch")
        try:
            width, height = png_dimensions(path)
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
            continue
        if (width, height) != (entry.get("width"), entry.get("height")):
            errors.append(f"{label}: manifest dimensions do not match file")
        if entry.get("format") != "PNG":
            errors.append(f"{label}: manifest format must be PNG")
        if width != height or width < 1200:
            errors.append(f"{label}: expected square image at least 1200 px, found {width}x{height}")

        refs = set(entry.get("plan_entry_ids", []))
        covered_plan_ids.update(refs)
        unknown = refs - plan_ids
        if unknown:
            errors.append(f"{label}: unknown profile-plan IDs {sorted(unknown)}")
        for field in ("prompt", "alt_text", "caption", "candidate_type", "period_region", "sources", "red_team_notes"):
            if not entry.get(field):
                errors.append(f"{label}: missing {field}")
        for field in ("publication_status",):
            if entry.get(field) != "blocked":
                errors.append(f"{label}: {field} must be blocked")
        for field in ("human_scholarly_review", "human_visual_review", "rights_review"):
            if entry.get(field) != "required":
                errors.append(f"{label}: {field} must be required")
        if "not" not in entry.get("caption", "").lower():
            warnings.append(f"{label}: caption may lack an explicit non-reconstruction limitation")

    if manifest.get("covered_plan_entry_count") != len(covered_plan_ids):
        errors.append("covered_plan_entry_count does not match candidate references")
    if len(covered_plan_ids) != 17:
        errors.append(f"expected 17 covered profile-plan entries, found {len(covered_plan_ids)}")
    for field, required in (
        ("publication_status", "blocked"),
        ("human_scholarly_review", "required"),
        ("human_visual_review", "required"),
        ("rights_review", "required"),
    ):
        if manifest.get(field) != required:
            errors.append(f"manifest {field} must be {required}")

    by_id = {entry["id"]: entry for entry in entries}
    jesus_text = " ".join(
        str(by_id["profile-candidate-person-jesus-v1"].get(field, ""))
        for field in ("prompt", "caption", "red_team_notes")
    ).lower()
    for phrase in ("shroud", "not a facial reconstruction", "ordinary", "west asian", "not beautiful"):
        if phrase not in jesus_text:
            errors.append(f"Jesus candidate controls do not include {phrase!r}")

    isaiah = by_id["profile-candidate-book-isaiah-v1"]
    isaiah_text = " ".join((isaiah["prompt"], isaiah["caption"], " ".join(isaiah["red_team_notes"]))).lower()
    for phrase in ("three panels", "not a claim", "exilic", "postexilic"):
        if phrase not in isaiah_text:
            errors.append(f"Isaiah candidate controls do not include {phrase!r}")

    gospels = by_id["profile-candidate-books-gospels-v1"]
    expected_gospel_ids = {
        "profile-book-matthew",
        "profile-book-mark",
        "profile-book-luke",
        "profile-book-john",
    }
    if set(gospels["plan_entry_ids"]) != expected_gospel_ids:
        errors.append("Gospel editorial does not bind exactly the four Gospel plan records")

    disk_pngs = {path.name for path in CANDIDATE_DIR.glob("*.png")}
    if disk_pngs != EXPECTED_FILES:
        errors.append(f"unmanifested PNGs present: {sorted(disk_pngs-EXPECTED_FILES)}")

    print("=== BIBLICAL PROFILE-CANDIDATE AUDIT ===")
    print(f"Candidates: {len(entries)}")
    print(f"Covered profile-plan entries: {len(covered_plan_ids)}/76")
    print(f"Unique image hashes: {len({entry.get('sha256') for entry in entries})}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    if errors:
        print("FAILED: profile candidates are not internally consistent")
        return 1
    print("PASSED: files, hashes, plan bindings, disclosures, and publication controls are internally consistent")
    print("NOTE: likeness, material culture, aesthetics, rights, and publication remain human scholarly/visual gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
