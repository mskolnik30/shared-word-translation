#!/usr/bin/env python3
"""Validate the shared Biblical World visual-request safety contract.

This audit intentionally validates requests and publication controls. It does
not certify historical accuracy, geographic accuracy, rights, or visual
quality; those remain human scholarly and editorial gates.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "resources" / "biblical-world" / "registry.json"

ALLOWED_CLASSES = {
    "archaeological photograph",
    "artifact",
    "geographic map",
    "schematic map",
    "evidence-based reconstruction",
    "interpretive orientation image",
    "symbolic art",
}
ALLOWED_CLAIMS = {
    "established",
    "probable",
    "possible",
    "disputed",
    "unknown",
    "interpretive",
}


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    records = data.get("records", [])
    requests = data.get("visual_requests", [])
    errors: list[str] = []

    record_ids = [item.get("id") for item in records]
    request_ids = [item.get("id") for item in requests]

    for label, values in (("record", record_ids), ("visual request", request_ids)):
        missing = [index for index, value in enumerate(values) if not value]
        duplicates = sorted(value for value, count in Counter(values).items() if value and count > 1)
        if missing:
            errors.append(f"{label} entries missing id at indexes: {missing}")
        if duplicates:
            errors.append(f"duplicate {label} ids: {', '.join(duplicates)}")

    known_records = set(record_ids)
    for request in requests:
        request_id = request.get("id", "<missing-id>")
        target = request.get("record")
        visual_class = request.get("class")
        claim = request.get("claim_label")
        rights = request.get("rights_status")
        publication = request.get("publication_status")

        if target not in known_records:
            errors.append(f"{request_id}: unknown shared record {target!r}")
        if visual_class not in ALLOWED_CLASSES:
            errors.append(f"{request_id}: invalid visual class {visual_class!r}")
        if claim not in ALLOWED_CLAIMS:
            errors.append(f"{request_id}: invalid claim label {claim!r}")
        if not rights:
            errors.append(f"{request_id}: missing rights status")
        if publication not in {"blocked", "ready"}:
            errors.append(f"{request_id}: invalid publication status {publication!r}")
        if publication == "ready" and rights not in {"verified", "owned", "public-domain"}:
            errors.append(f"{request_id}: marked ready without verified rights")
        if visual_class in {
            "evidence-based reconstruction",
            "interpretive orientation image",
            "symbolic art",
        } and publication == "ready" and claim not in {"probable", "possible", "interpretive"}:
            errors.append(f"{request_id}: interpretive/reconstructed visual lacks an uncertainty label")

    class_counts = Counter(item.get("class", "<missing>") for item in requests)
    print("=== BIBLICAL WORLD VISUAL-PLAN AUDIT ===")
    print(f"Shared records: {len(records)}")
    print(f"Visual requests: {len(requests)}")
    for visual_class, count in sorted(class_counts.items()):
        print(f"  {visual_class}: {count}")
    print(f"Errors: {len(errors)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("PASSED: request structure and publication controls are internally consistent")
    print("NOTE: scholarly accuracy, rights, visual quality, and final publication remain human gates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
