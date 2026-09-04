# Fluent Companion Batch 0 Source Provenance Reconciliation

**Status:** Exact source objects reconciled; Ruth human source-lock review approved
**Date:** September 4, 2026
**Base commit:** `b0542f9a4cc64cbc39016832fd1dfb70a0755409`

## Purpose

This record closes exact source-provenance gaps discovered during the Fluent Companion corpus inventory. It records only source identities that can be resolved directly from the pinned Git repositories. The follow-up Ruth review records the qualified human decision required by the original reconciliation. It does not change translation text, approve Companion material, or authorize publication.

## Resolved source objects

| Book | Repository | Commit | File | Git blob |
|---|---|---|---|---|
| Jonah | `openscriptures/morphhb` | `6a5db284c715c18b239422e57bb89684e6a19f00` | `wlc/Jonah.xml` | `158c18ecbf3026fa845105d34b8766d89bcd039e` |
| Ruth | `openscriptures/morphhb` | `6a5db284c715c18b239422e57bb89684e6a19f00` | `wlc/Ruth.xml` | `e4aea25dfc593685e7e8f7ec995b96789f5c7060` |
| James | `Faithlife/SBLGNT` | `c4d241a9c1c479a55b989ba35a4976c1d0b8052c` | `data/sblgnt/text/Jas.txt` | `283a675fdfab4ca4967ca5a72500a1aff2bd07c7` |
| Mark | `Faithlife/SBLGNT` | `c4d241a9c1c479a55b989ba35a4976c1d0b8052c` | `data/sblgnt/text/Mark.txt` | `3f50fe360d1d2351db6b6c3000de47c16abccf84` |
| Matthew | `Faithlife/SBLGNT` | `c4d241a9c1c479a55b989ba35a4976c1d0b8052c` | `data/sblgnt/text/Matt.txt` | `d19efbdff018c2bde83ba0fc01e0d8cb399b496b` |

Each blob identifier was read from the tree of the exact recorded source commit. No identifier was inferred from a current branch tip.

## Dispositions

### Jonah

The existing QA record already identifies `OT.OSHB.WLC.2.2`, revision `6a5db28`, and the public/WLC versification difference. The repository, full commit, file, and Git blob are now recorded. The book's existing `QA_PASSED` status is unchanged.

### James

The existing QA record already identifies the repository, exact commit, and source file. The exact Git blob is now recorded. The book's existing `QA_PASSED` status is unchanged.

### Mark and Matthew

The existing QA records identify the repository, exact commit, source file, raw URL, and a 64-character SHA-256 checksum. A SHA-256 file checksum is useful for byte verification but is not a Git blob identifier. The exact 40-character Git blob from each pinned source tree is now recorded without removing the existing SHA-256 checksum or changing either book's `QA_PASSED` status.

### Ruth

The exact OSHB/WLC source object was reviewed against all four Fluent chapters. Matthew J. Skolnik approved the exact source lock on September 4, 2026. The completed review established that:

- the source commit and Git blob match the pinned QA record;
- all 85 OSHB/WLC verses match all 85 Fluent verse labels;
- all four chapter-review records remain `QA_PASSED`;
- no F4 material is present;
- the stale Ruth 1 source-lock warning and Ruth 4:16 wording record are reconciled; and
- the book is promoted to `QA_PASSED` with `source_lock_status` set to `HUMAN_APPROVED_EXACT_SOURCE_LOCK`.

## Companion effect

After the human Ruth review, Jonah, Ruth, James, Mark, and Matthew have complete strict source packages for Companion binding. Ruth's former source-package blocker is closed. The representative reader-test, accessibility, and template gates remain closed for all mass Companion drafting and publication.
