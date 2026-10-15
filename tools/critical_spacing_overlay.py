#!/usr/bin/env python3
"""Resolve a documented blank-line-only follow-up without rewriting old audits.

The original correction ledger, corpus contract, supersession record and old
fixtures stay byte-for-byte intact. This module verifies their bindings and the
explicit two-file formatting transition before returning in-memory expectations.
It never writes a source file or grants editorial/publication approval.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from critical_text_model import ContentError, sha256
from tsw_format_apparatus import normalize

AUDIT = Path("audit/corrections/2026-10-15")
FOLLOWUP = "APPARATUS_SPACING_FOLLOWUP.json"
TARGETS = {
    "books/OT/ezekiel/Ezekiel_42.md",
    "books/OT/genesis/Genesis_02.md",
}


def git_blob(data: bytes) -> str:
    import hashlib
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def validate_spacing_record(record: dict) -> str:
    """Verify exact old/new hashes, unchanged body and identical nonblank lines."""
    if record["path"] not in TARGETS:
        raise ContentError("Unexpected spacing-follow-up path")
    before = record["before_text"]
    raw = before.encode("utf-8")
    if sha256(raw) != record["before_sha256"] or git_blob(raw) != record["before_git_blob"]:
        raise ContentError("Spacing follow-up before evidence does not match its hashes")
    after = normalize(before)
    encoded = after.encode("utf-8")
    if sha256(encoded) != record["after_sha256"] or git_blob(encoded) != record["after_git_blob"]:
        raise ContentError("Spacing follow-up after evidence does not match canonical formatting")
    if before.split("## Notes", 1)[0] != after.split("## Notes", 1)[0]:
        raise ContentError("Spacing follow-up changed the Scripture body or metadata")
    if [s for s in before.splitlines() if s.strip()] != [s for s in after.splitlines() if s.strip()]:
        raise ContentError("Spacing follow-up changed a nonblank line")
    if record.get("publication_allowed") is not False:
        raise ContentError("Spacing follow-up must not authorize publication")
    return after


def resolve_correction_snapshot(repo: Path) -> tuple[dict, dict, dict | None]:
    """Return the current contract and ledger as copies, plus verified follow-up."""
    audit = Path(repo) / AUDIT
    contract = json.loads((audit / "CORPUS_CONTRACT.json").read_text(encoding="utf-8"))
    ledger = json.loads((audit / "CORRECTION_LEDGER.json").read_text(encoding="utf-8"))
    followup_path = audit / FOLLOWUP
    if not followup_path.exists():
        return contract, ledger, None
    if followup_path.is_symlink():
        raise ContentError("Unsafe spacing follow-up path")
    followup = json.loads(followup_path.read_text(encoding="utf-8"))
    if followup.get("schema_version") != 1 or followup.get("publication_allowed") is not False:
        raise ContentError("Invalid spacing follow-up status")
    if followup.get("independent_human_approval") is not False:
        raise ContentError("Formatting is not independent human approval")
    expected_documents = {"CORPUS_CONTRACT.json", "CORRECTION_LEDGER.json", "REVIEW_SUPERSESSION.json"}
    if set(followup["preserved_documents_sha256"]) != expected_documents:
        raise ContentError("Incomplete preserved-document bindings")
    for filename, digest in followup["preserved_documents_sha256"].items():
        if sha256((audit / filename).read_bytes()) != digest:
            raise ContentError("Historical correction evidence changed: " + filename)
    formatter = Path(repo) / "tools/tsw_format_apparatus.py"
    if git_blob(formatter.read_bytes()) != followup["formatter_git_blob"]:
        raise ContentError("The bound apparatus formatter has changed; review required")
    records = followup["records"]
    if len(records) != 2 or {r["path"] for r in records} != TARGETS:
        raise ContentError("Spacing follow-up must contain exactly the two reviewed chapters")
    contract = copy.deepcopy(contract)
    ledger = copy.deepcopy(ledger)
    chapters = {r["path"]: r for r in contract["chapters"]}
    corrections = {r["path"]: r for r in ledger["files"]}
    for record in records:
        path = record["path"]
        validate_spacing_record(record)
        if (chapters[path]["candidate_sha256"] != record["before_sha256"] or
                corrections[path]["after_sha256"] != record["before_sha256"] or
                corrections[path]["after_git_blob"] != record["before_git_blob"]):
            raise ContentError("Spacing transition is not bound to the prior correction: " + path)
        chapters[path]["candidate_sha256"] = record["after_sha256"]
        corrections[path]["after_sha256"] = record["after_sha256"]
        corrections[path]["after_git_blob"] = record["after_git_blob"]
    contract["formatting_followup"] = {
        "path": str(AUDIT / FOLLOWUP),
        "sha256": sha256(followup_path.read_bytes()),
        "publication_allowed": False,
    }
    return contract, ledger, followup
