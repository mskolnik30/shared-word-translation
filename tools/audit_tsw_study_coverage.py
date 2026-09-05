#!/usr/bin/env python3
"""Verify that the TSW Study Companion completion set covers all 66 books."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "companions/tsw-study/manifests"
ROADMAP = ROOT / "companions/tsw-study/roadmap.json"
WORLD = ROOT / "resources/biblical-world/registry.json"


def main() -> int:
    errors: list[str] = []
    manifests = []
    dossiers = []
    for path in sorted(MANIFEST_DIR.glob("batch*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        manifests.append(data)
        dossiers.extend(data.get("dossiers", []))

    expected_books = {
        path.name
        for testament in (ROOT / "books").iterdir()
        if testament.is_dir()
        for path in testament.iterdir()
        if path.is_dir()
    }
    covered = Counter(Path(item["tsw_source"]).parent.name for item in dossiers)
    covered_books = set(covered)

    if len(manifests) != 7:
        errors.append(f"expected 7 batches; found {len(manifests)}")
    if len(dossiers) != 70:
        errors.append(f"expected 70 dossiers; found {len(dossiers)}")
    if len(expected_books) != 66:
        errors.append(f"repository canon should contain 66 books; found {len(expected_books)}")
    missing = expected_books - covered_books
    unknown = covered_books - expected_books
    if missing:
        errors.append(f"books without a dossier: {sorted(missing)}")
    if unknown:
        errors.append(f"unknown covered book directories: {sorted(unknown)}")
    if sum(count - 1 for count in covered.values()) != 4:
        errors.append("completion set must contain exactly four additional high-stakes dossiers")

    roadmap = json.loads(ROADMAP.read_text(encoding="utf-8"))
    if roadmap.get("canonical_books") != 66 or roadmap.get("target_dossiers") != 70:
        errors.append("roadmap completion counts do not match the audit contract")

    world = json.loads(WORLD.read_text(encoding="utf-8"))
    completion_visual_ids = set(roadmap.get("completion_visual_ids", []))
    if len(completion_visual_ids) != 50:
        errors.append(f"roadmap should identify 50 completion visual requests; found {len(completion_visual_ids)}")
    visuals = {item["id"]: item for item in world.get("visual_requests", [])}
    for visual_id in completion_visual_ids:
        visual = visuals.get(visual_id)
        if not visual:
            errors.append(f"missing completion visual request: {visual_id}")
        elif visual.get("publication_status") != "blocked" or visual.get("rights_status") != "not-acquired":
            errors.append(f"unfinished visual must remain blocked with rights not acquired: {visual_id}")

    print("=== TSW STUDY COMPANION COVERAGE AUDIT ===")
    print(f"Batches: {len(manifests)}/7")
    print(f"Dossiers: {len(dossiers)}/70")
    print(f"Canonical books represented: {len(covered_books)}/66")
    print(f"Additional high-stakes dossiers: {sum(count - 1 for count in covered.values())}/4")
    print(f"Completion visuals blocked: {len(completion_visual_ids)}/{len(completion_visual_ids)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    statuses = {manifest.get("status") for manifest in manifests}
    if statuses == {"APPROVED_FOR_PUBLICATION"}:
        print("PASSED: complete approved text coverage; unfinished visuals remain blocked")
    else:
        print("PASSED: complete draft coverage with publication gates intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
