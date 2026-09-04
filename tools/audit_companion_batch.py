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
    "public presentation should",
    "public materials should",
    "a public companion should",
)
ALLOWED_REVIEW_STATUSES = {"pending", "approved"}
DRAFT_STATUS = "DRAFTED_REVIEW_REQUIRED"
APPROVED_STATUS = "APPROVED_FOR_PUBLICATION"
ALLOWED_BATCH_STATUSES = {DRAFT_STATUS, APPROVED_STATUS}
BLOCKED_PUBLICATION = "BLOCKED_PENDING_HUMAN_REVIEW"
APPROVED_PUBLICATION = "APPROVED_FOR_PUBLICATION"
REQUIRED_GATES = {
    "source-language",
    "historical",
    "reception",
    "critical-voices",
    "power-and-harm",
    "public-language",
    "visual-evidence",
}
ALLOWED_VISUAL_CLASSES = {
    "archaeological photograph",
    "artifact",
    "geographic map",
    "schematic map",
    "evidence-based reconstruction",
    "interpretive orientation image",
    "symbolic art",
}
ALLOWED_CLAIM_LABELS = {
    "established",
    "probable",
    "possible",
    "disputed",
    "unknown",
    "interpretive",
}


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
    manifest_status = manifest.get("status")
    batch_number = manifest.get("batch_number")
    sensitive_dossiers = set(manifest.get("content_notice_required", []))

    if manifest_status not in ALLOWED_BATCH_STATUSES:
        errors.append(f"manifest status must be one of {sorted(ALLOWED_BATCH_STATUSES)}")
    if not isinstance(batch_number, int) or batch_number < 1:
        errors.append("batch_number must be a positive integer")
    if manifest.get("dossier_count") != len(dossiers):
        errors.append("dossier_count does not match dossier entries")
    if len(dossiers) != 10:
        errors.append(f"batch must contain 10 dossiers; found {len(dossiers)}")
    dossier_ids = {entry.get("id") for entry in dossiers}
    unknown_sensitive = sensitive_dossiers - dossier_ids
    if unknown_sensitive:
        errors.append(f"content_notice_required contains unknown dossiers: {sorted(unknown_sensitive)}")

    shared = load_json(SHARED_REGISTRY)
    shared_ids = {record.get("id") for record in shared.get("records", [])}
    visual_requests = shared.get("visual_requests", [])
    seen_visual_ids: set[str] = set()
    for visual in visual_requests:
        visual_id = visual.get("id", "<missing-visual-id>")
        if visual_id in seen_visual_ids:
            errors.append(f"duplicate visual request id: {visual_id}")
        seen_visual_ids.add(visual_id)
        if visual.get("record") not in shared_ids:
            errors.append(f"{visual_id}: unknown shared-world record")
        if visual.get("class") not in ALLOWED_VISUAL_CLASSES:
            errors.append(f"{visual_id}: missing or invalid visual class")
        if visual.get("claim_label") not in ALLOWED_CLAIM_LABELS:
            errors.append(f"{visual_id}: missing or invalid evidence claim label")
        publication_status = visual.get("publication_status")
        if publication_status == "ready":
            if visual.get("rights_status") != "verified":
                errors.append(f"{visual_id}: ready visual must have verified rights")
            if visual.get("status") != "complete":
                errors.append(f"{visual_id}: ready visual must be complete")
            for field in ("creator", "source_url", "license", "caption", "alt_text"):
                if not visual.get(field):
                    errors.append(f"{visual_id}: ready visual is missing {field}")
        elif publication_status == "blocked":
            if visual.get("rights_status") not in {"not-acquired", "verified"}:
                errors.append(f"{visual_id}: blocked visual has invalid rights status")
        else:
            errors.append(f"{visual_id}: publication status must be blocked or ready")
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
        if front.get("status") != manifest_status:
            errors.append(f"{dossier_id}: status must match the batch manifest")
        if front.get("batch") != str(batch_number):
            errors.append(f"{dossier_id}: batch must be {batch_number}")
        if dossier_id in sensitive_dossiers and not front.get("content_notice"):
            errors.append(f"{dossier_id}: sensitive dossier requires a content notice")
        if re.search(r"!\[[^\]]*\]\([^)]+\)", text):
            errors.append(f"{dossier_id}: direct image embedding bypasses shared visual review")

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
            if review.get("batch_id") != manifest.get("batch_id"):
                errors.append("review manifest batch_id must match the batch manifest")
            gates = review.get("human_gates", [])
            if not gates:
                errors.append("review manifest must define human review gates")
            elif any(gate.get("status") not in ALLOWED_REVIEW_STATUSES for gate in gates):
                errors.append("human review gate status must be pending or approved")
            else:
                gate_ids = {gate.get("id") for gate in gates}
                if gate_ids != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
                    errors.append("review manifest does not contain the required human gates")
                if any(gate.get("required") is not True for gate in gates):
                    errors.append("every human review gate must be required")
                pending = [gate for gate in gates if gate.get("status") == "pending"]
                publication_state = review.get("publication_state")
                if pending:
                    if publication_state != BLOCKED_PUBLICATION:
                        errors.append("pending human gates require blocked publication state")
                    if manifest_status != DRAFT_STATUS:
                        errors.append("pending human gates require drafted-review batch status")
                else:
                    if publication_state != APPROVED_PUBLICATION:
                        errors.append("all approved human gates require approved publication state")
                    if manifest_status != APPROVED_STATUS:
                        errors.append("all approved human gates require approved batch status")

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
    review = load_json(resolve_repo_path(load_json(manifest_path)["review_manifest"]))
    approved = sum(gate.get("status") == "approved" for gate in review["human_gates"])
    pending = sum(gate.get("status") == "pending" for gate in review["human_gates"])
    print(f"Human review gates: {approved} approved; {pending} pending")
    if pending:
        print("Publication gate: blocked pending remaining human review")
    else:
        print("Publication gate: approved for text publication")
    print("PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
