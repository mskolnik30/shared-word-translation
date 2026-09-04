#!/usr/bin/env python3
"""Validate a TSW Study Companion batch before human review or release."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "companions/tsw-study/manifests/batch01.json"
SHARED_REGISTRY = REPO_ROOT / "resources/biblical-world/registry.json"
REQUIRED_FRONT_MATTER = {
    "id",
    "title",
    "passage",
    "translation",
    "status",
    "batch",
    "shared_world",
}
DISALLOWED_PUBLIC_PHRASES = (
    "facilitator should",
    "ask the group",
    "tell participants",
    "instructor note",
    "teacher only",
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    try:
        block = text.split("---\n", 2)[1]
    except IndexError:
        return {}
    values: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def parse_inline_list(value: str) -> list[str]:
    if not value.startswith("[") or not value.endswith("]"):
        return []
    return [part.strip().strip("'\"") for part in value[1:-1].split(",") if part.strip()]


def resolve_repo_path(value: str) -> Path:
    path = (REPO_ROOT / value).resolve()
    if REPO_ROOT not in path.parents and path != REPO_ROOT:
        raise ValueError(f"path escapes repository: {value}")
    return path


def audit(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_json(manifest_path)
    dossiers = manifest.get("dossiers", [])
    required_sections = manifest.get("required_sections", [])

    if manifest.get("status") != "DRAFTED_REVIEW_REQUIRED":
        errors.append("manifest status must be DRAFTED_REVIEW_REQUIRED")
    if manifest.get("dossier_count") != len(dossiers):
        errors.append("dossier_count does not match dossier entries")
    if len(dossiers) != 10:
        errors.append(f"batch must contain 10 dossiers; found {len(dossiers)}")

    shared = load_json(SHARED_REGISTRY)
    shared_ids = {record.get("id") for record in shared.get("records", [])}
    seen_ids: set[str] = set()
    seen_passages: set[str] = set()

    for entry in dossiers:
        dossier_id = entry.get("id", "<missing-id>")
        if dossier_id in seen_ids:
            errors.append(f"duplicate dossier id: {dossier_id}")
        seen_ids.add(dossier_id)
        passage = entry.get("passage", "")
        if passage in seen_passages:
            errors.append(f"duplicate passage: {passage}")
        seen_passages.add(passage)

        try:
            dossier_path = resolve_repo_path(entry["file"])
            tsw_source = resolve_repo_path(entry["tsw_source"])
        except (KeyError, ValueError) as exc:
            errors.append(f"{dossier_id}: invalid path: {exc}")
            continue
        if not dossier_path.is_file():
            errors.append(f"{dossier_id}: missing dossier file {entry.get('file')}")
            continue
        if not tsw_source.is_file():
            errors.append(f"{dossier_id}: missing TSW source {entry.get('tsw_source')}")

        text = dossier_path.read_text(encoding="utf-8")
        front = parse_front_matter(text)
        missing_keys = REQUIRED_FRONT_MATTER - front.keys()
        if missing_keys:
            errors.append(f"{dossier_id}: missing front matter {sorted(missing_keys)}")
        if front.get("id") != dossier_id:
            errors.append(f"{dossier_id}: front-matter id mismatch")
        if front.get("passage") != passage:
            errors.append(f"{dossier_id}: passage mismatch")
        if front.get("translation") != "tsw":
            errors.append(f"{dossier_id}: translation must be tsw")
        if front.get("status") != "DRAFTED_REVIEW_REQUIRED":
            errors.append(f"{dossier_id}: status must require review")
        if front.get("batch") != "1":
            errors.append(f"{dossier_id}: batch must be 1")

        for section in required_sections:
            if f"## {section}" not in text:
                errors.append(f"{dossier_id}: missing section {section}")
        if "**Questions for public reflection**" not in text:
            errors.append(f"{dossier_id}: missing public question callout")
        if len(re.findall(r"^> - ", text, flags=re.MULTILINE)) < 4:
            errors.append(f"{dossier_id}: needs at least four public questions")
        if len(re.findall(r"https://", text)) < 3:
            errors.append(f"{dossier_id}: source ledger needs at least three links")

        lower = text.lower()
        for phrase in DISALLOWED_PUBLIC_PHRASES:
            if phrase in lower:
                errors.append(f"{dossier_id}: contains facilitator-only phrase: {phrase}")

        refs = parse_inline_list(front.get("shared_world", ""))
        if not refs:
            errors.append(f"{dossier_id}: no shared-world references")
        for ref in refs:
            if ref not in shared_ids:
                errors.append(f"{dossier_id}: unknown shared-world id {ref}")
            if f"`{ref}`" not in text:
                errors.append(f"{dossier_id}: shared-world id not exposed in public section: {ref}")

    review_path_value = manifest.get("review_manifest")
    if not review_path_value:
        errors.append("manifest is missing review_manifest")
    else:
        review_path = resolve_repo_path(review_path_value)
        if not review_path.is_file():
            errors.append(f"missing review manifest: {review_path_value}")
        else:
            review = load_json(review_path)
            if review.get("publication_state") != "BLOCKED_PENDING_HUMAN_REVIEW":
                errors.append("review manifest must block publication pending human review")
            gates = review.get("human_gates", [])
            if not gates or any(gate.get("status") != "pending" for gate in gates):
                errors.append("all initial human review gates must be pending")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()
    try:
        errors = audit(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAILED: {exc}")
        return 1

    print("=== TSW STUDY COMPANION BATCH AUDIT ===")
    print(f"Manifest: {manifest_path.relative_to(REPO_ROOT)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    count = len(load_json(manifest_path)["dossiers"])
    print(f"Dossiers: {count}")
    print("Shared-world references: valid")
    print("Public section structure: valid")
    print("Publication gate: blocked pending human review")
    print("PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
