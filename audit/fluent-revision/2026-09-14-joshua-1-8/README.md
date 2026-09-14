# Fluent Joshua 1–8 revision

All 186 verses have a source-based draft and individual editorial rationale. The purpose is biblical fluency: clear speakers and relationships, natural sustained reading, recognizable recurring words and images, and selective notes that preserve consequential uncertainty. TSW was read as a comparator after independent drafting, not used as the wording base.

## Source and coverage

The repository-pinned OSHB source is openscriptures/morphhb at commit 6a5db284c715c18b239422e57bb89684e6a19f00, wlc/Josh.xml, Git blob 817453d2312e7cf359f6324e5456c5ba59c5bfa2. The full file contains 658 records. SHA-256: d32a65fc6dc7207625c05ddcd133a0833a0c48e3d2343ba6fff4e01be9d5beaf. Public and source numbering align for all 186 verses in chapters 1–8. Every hash binds the exact original XML substring, including written/read and other notes.

[Source](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Josh.xml). A selected post-draft comparison of 8:13–14 with the [NET translation and translators’ notes](https://www.biblegateway.com/passage/?search=Joshua+8%3A12-14&version=NET) supported retaining the rear-position and appointed-place readings. Other attempted web results were not used as translation evidence.

## Checks and limitations

All 46 cumulative source-binding ledgers passed, totaling 6,146 verses in 200 chapters. The translation-family audit and git diff --check passed. All eight new chapters have ordered verse labels, complete paragraph wrappers, balanced main speech marks, and structural QA metadata. Twenty-three source/draft pairs received a second focused self-check after the complete initial source reading.

This is an authoring review, not independent scholarly approval. Revised chapters use status QA_PASSED only with qa_scope structural; editorial_status is REVIEW_PENDING and publication_allowed is false. Historical chapter reviews remain recoverable at the exact parent commit. Prior book-level triage entries are retained and superseded only for chapters 1–8. TSW, earlier revisions, later Joshua chapters and Companion are unchanged.

185 verse texts changed; one remained unchanged. Editorial decisions: 1 F0, 138 F2, 47 F3. Normalized whole-verse overlap with TSW moved from 146 identical and 38 near-identical verses to 2 identical and 8 near-identical verses. Near-identical means nonidentical similarity at least 0.90. This is triage, not a quality or originality certificate; no overlap quota governed wording.

## Files

- joshua-verse-review.json: every verse’s before/after text, comparator, exact source binding and rationale.
- review.json: decisions, limitations and Companion effects.
- overlap.json: before/after triage.
- focused-comparisons.json: the 23 selected Hebrew/draft pairs and source annotations.
- verification.json: structural, source-binding, preservation and family audit evidence.
- verify_batch.py: reproducible verification using the pinned source files and exact Git history.

## Continue

Next: Joshua 9–12, then Joshua 13–24 and a whole-book consistency review. GitHub write access remains blocked; the cumulative bundle preserves all revision commits. No public deployment occurred. Companion quotations and bindings for chapters 1–8 require later reconciliation.
