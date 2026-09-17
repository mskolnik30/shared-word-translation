#!/usr/bin/env python3
"""Audit the 76-image Biblical profile plan before raster generation."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "resources" / "biblical-world" / "profiles" / "plan.json"
BOOKS_DIR = ROOT / "companions" / "fluent" / "books"


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    entries = plan.get("entries", [])
    errors: list[str] = []
    ids = [item.get("id") for item in entries]
    duplicates = sorted(value for value, count in Counter(ids).items() if value and count > 1)
    if duplicates:
        errors.append(f"duplicate profile ids: {duplicates}")
    if len(entries) != 76 or plan.get("total_count") != 76:
        errors.append(f"expected 76 profiles, found {len(entries)}")

    canonical_slugs = {path.parent.name for path in BOOKS_DIR.glob("*/introduction.md")}
    book_entries = [item for item in entries if item.get("kind") == "book-authorial-identity"]
    profile_slugs = {item["id"].removeprefix("profile-book-") for item in book_entries}
    if profile_slugs != canonical_slugs:
        errors.append(f"book-profile coverage mismatch: missing={sorted(canonical_slugs-profile_slugs)} extra={sorted(profile_slugs-canonical_slugs)}")
    if len(book_entries) != 66 or plan.get("book_profile_count") != 66:
        errors.append("book profile count must be 66")
    person_entries = [item for item in entries if item.get("kind") == "named-biblical-person"]
    if len(person_entries) != 10 or plan.get("key_person_count") != 10:
        errors.append("key-person count must be 10")

    for entry in entries:
        profile_id = entry.get("id", "<missing-id>")
        if entry.get("publication_status") != "blocked":
            errors.append(f"{profile_id}: publication must remain blocked")
        if entry.get("human_scholarly_review") != "required" or entry.get("human_visual_review") != "required":
            errors.append(f"{profile_id}: both human gates are required")
        if not entry.get("sources") or not all(str(url).startswith("https://") for url in entry.get("sources", [])):
            errors.append(f"{profile_id}: missing HTTPS scholarly source")
        if "illustrative rather than reconstructed" not in entry.get("portrait_limit", ""):
            errors.append(f"{profile_id}: portrait limitation is incomplete")
        if "never default" not in entry.get("racial_accuracy", "").lower():
            errors.append(f"{profile_id}: racial-accuracy constraint is incomplete")
        status = entry.get("authorship_status", "")
        strategy = entry.get("visual_strategy", "")
        uncertain_status = not status.startswith("named-undisputed") and any(
            token in status for token in ("anonymous", "composite", "layered", "pseudonymous", "disputed")
        )
        if uncertain_status and strategy == "interpretive-named-figure-portrait":
            errors.append(f"{profile_id}: uncertain authorship cannot default to one author portrait")

    jesus = next((item for item in entries if item.get("id") == "profile-person-jesus"), None)
    if not jesus:
        errors.append("Jesus profile is missing")
    else:
        evidence = jesus.get("evidence_note", "").lower()
        for phrase in ("ordinary", "weathered", "non-european", "not idealized", "shroud of turin is excluded"):
            if phrase not in evidence:
                errors.append(f"Jesus profile missing constraint: {phrase}")

    isaiah = next((item for item in entries if item.get("id") == "profile-book-isaiah"), None)
    if not isaiah or isaiah.get("visual_strategy") != "authorship-aware-multi-voice-editorial":
        errors.append("Isaiah must use a multi-voice authorship-aware treatment")

    print("=== BIBLICAL PROFILE PLAN AUDIT ===")
    print(f"Canonical book profiles: {len(book_entries)}/66")
    print(f"Key-person profiles: {len(person_entries)}/10")
    print(f"Total planned images: {len(entries)}/76")
    print(f"Errors: {len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("PASSED: profile plan preserves ethnicity, non-idealization, and authorship uncertainty controls")
    print("NOTE: no planned portrait is a facial reconstruction or publication-approved image")
    return 0


if __name__ == "__main__":
    sys.exit(main())
