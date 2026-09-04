#!/usr/bin/env python3
"""Run the publication-gate audit for every registered TSW companion batch."""

from __future__ import annotations

import sys
from pathlib import Path

from audit_companion_batch import REPO_ROOT, audit


def main() -> int:
    manifests = sorted((REPO_ROOT / "companions/tsw-study/manifests").glob("batch*.json"))
    if not manifests:
        print("FAILED: no TSW Study Companion batch manifests found")
        return 1

    failed = False
    for manifest in manifests:
        relative = manifest.relative_to(REPO_ROOT)
        errors = audit(manifest)
        print(f"=== {relative} ===")
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR: {error}")
        else:
            print("PASSED")

    if failed:
        print("FAILED: one or more companion batches did not pass")
        return 1
    print(f"PASSED: {len(manifests)} companion batch manifest(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
