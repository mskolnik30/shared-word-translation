#!/usr/bin/env python3
"""Audit committed Biblical World SVG candidates and their manifest."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "resources" / "biblical-world" / "registry.json"
MANIFEST = ROOT / "resources" / "biblical-world" / "candidates" / "vectors" / "manifest.json"
RASTER_ONLY = {"visual-jericho-archaeology", "visual-caesarea-philippi", "visual-deuteronomic-law-context"}


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    requests = {item["id"]: item for item in registry["visual_requests"]}
    entries = manifest.get("entries", [])
    errors: list[str] = []
    warnings: list[str] = []

    expected = set(requests) - RASTER_ONLY
    actual_ids = [item.get("visual_id") for item in entries]
    actual = set(actual_ids)
    if expected != actual:
        errors.append(f"manifest coverage mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    duplicates = sorted(item for item, count in Counter(actual_ids).items() if item and count > 1)
    if duplicates:
        errors.append(f"duplicate manifest visual ids: {duplicates}")
    if manifest.get("asset_count") != len(entries):
        errors.append("asset_count does not match entries")
    if manifest.get("publication_status") != "blocked":
        errors.append("candidate set must remain publication-blocked")

    hashes = []
    for entry in entries:
        visual_id = entry.get("visual_id", "<missing-id>")
        request = requests.get(visual_id)
        if not request:
            continue
        if entry.get("record_id") != request.get("record"):
            errors.append(f"{visual_id}: record binding mismatch")
        if entry.get("requested_class") != request.get("class"):
            errors.append(f"{visual_id}: requested class mismatch")
        if entry.get("claim_label") != request.get("claim_label"):
            errors.append(f"{visual_id}: claim label mismatch")
        if entry.get("publication_status") != "blocked":
            errors.append(f"{visual_id}: candidate is not blocked")
        if entry.get("scholarly_review") != "required" or entry.get("accessibility_review") != "required":
            errors.append(f"{visual_id}: missing required human gates")
        if not entry.get("primary_texts"):
            errors.append(f"{visual_id}: missing primary texts")
        if len(entry.get("alt_text", "")) < 80:
            errors.append(f"{visual_id}: alt text is too short")
        for source in entry.get("sources", []):
            if not re.match(r"^https://", source):
                errors.append(f"{visual_id}: non-HTTPS source {source!r}")
        if entry.get("candidate_format") == "schematic-coordinate-map" and not entry.get("sources"):
            errors.append(f"{visual_id}: coordinate map has no external place source")

        rel = entry.get("file", "")
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"{visual_id}: missing file {rel}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append(digest)
        if digest != entry.get("sha256"):
            errors.append(f"{visual_id}: SHA-256 mismatch")
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"{visual_id}: invalid SVG XML: {exc}")
            continue
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            errors.append(f"{visual_id}: root element is not SVG")
        if root.get("role") != "img" or root.get("aria-labelledby") != "title desc":
            errors.append(f"{visual_id}: missing SVG accessibility semantics")
        text = " ".join("".join(root.itertext()).split())
        if "UNPUBLISHED CANDIDATE" not in text and "SCHEMATIC COORDINATE MAP" not in text:
            errors.append(f"{visual_id}: missing visible candidate/schematic disclosure")
        for forbidden in ("low dining table", "Paul describes", "in Paul's account", "God rejects their speech about Job", "heavenly wager"):
            if forbidden.casefold() in text.casefold():
                errors.append(f"{visual_id}: forbidden red-team wording: {forbidden}")

    duplicate_hashes = [digest for digest, count in Counter(hashes).items() if count > 1]
    if duplicate_hashes:
        errors.append(f"duplicate SVG byte content detected: {len(duplicate_hashes)} hashes")

    print("=== BIBLICAL WORLD VECTOR-CANDIDATE AUDIT ===")
    print(f"Expected vector requests: {len(expected)}")
    print(f"Manifest entries: {len(entries)}")
    print(f"Unique files: {len(set(hashes))}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    if errors:
        return 1
    print("PASSED: vector candidates are complete, bound, accessible, and publication-blocked")
    print("NOTE: historical, geographic, theological, and visual approval remain human gates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
