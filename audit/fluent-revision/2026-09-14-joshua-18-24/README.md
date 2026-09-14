# Fluent Joshua 18–24 revision

All 216 verses have a source-based draft and individual rationale. This completes the Joshua draft: 658 verses in 24 chapters. Fluent’s purpose is biblical fluency through clear speakers and relationships, connected natural reading, recognizable repeated terms and images, and selective notes that preserve consequential uncertainty. Every pinned Hebrew verse was read before drafting; every TSW verse was read afterward as a comparator.

## Source and coverage

[OSHB Joshua source](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Josh.xml): commit 6a5db284c715c18b239422e57bb89684e6a19f00, wlc/Josh.xml, Git blob 817453d2312e7cf359f6324e5456c5ba59c5bfa2. Full-file SHA-256 d32a65fc6dc7207625c05ddcd133a0833a0c48e3d2343ba6fff4e01be9d5beaf; 658 XML records. All 216 public references in chapters 18–24 map one to one to exact original XML substrings, including written/read notes.

Post-draft comparisons consulted the NET translators’ notes on [Joshua 21:36–37](https://www.biblegateway.com/passage/?search=Joshua+21%3A36-37&version=NET) for the Reubenite verses’ manuscript variation, and [Joshua 22:22](https://www.biblegateway.com/passage/?search=Joshua+22%3A22&version=NET) for the divine designations and uncertain singular addressee. Both Reubenite verses are present in the pinned source and retained in Fluent.

## Checks and editorial limits

All 48 cumulative source-binding ledger audits passed, totaling 6,618 verses in 216 chapters. The translation-family audit, paragraph and verse structure, historical-preservation checks, selected textual assertions and git diff --check passed. Fifty-six Hebrew/draft pairs were reread for focused risks. The four Levitical grant groups retain 13 + 10 + 13 + 12 town-and-pasture pairs, totaling 48. The source’s conflicting town totals in chapter 19 remain alongside its names, with notes.

This is authoring self-review, not independent scholarly approval. Revised chapter metadata retains status QA_PASSED qualified by qa_scope structural, editorial_status REVIEW_PENDING, and publication_allowed false. Earlier chapter reviews and revision batches remain at the exact parent commit; only chapters 18–24 are newly superseded. TSW and unrelated work remain unchanged. Joshua’s whole-book authoring consistency review remains next.

201 verse texts changed and 15 remained unchanged: 15 F0, 132 F2, 69 F3. Normalized whole-verse overlap with TSW moved from 193 identical and 21 near-identical verses to 23 identical and 14 near-identical verses. The remaining identical verses are place lists and town-and-pasture formulas. Near-identical means nonidentical similarity of at least 0.90. No overlap quota governed wording; these metrics do not certify originality or quality.

## Evidence and continuation

- joshua-verse-review.json: every verse’s before/after/comparator, source binding and individual rationale.
- focused-comparisons.json: 56 selected Hebrew/draft pairs and annotations.
- overlap.json: before/after comparison as triage.
- review.json: authoring decisions, unresolved questions and Companion impacts.
- verification.json and verify_batch.py: reproducible checks using pinned sources and exact Git history.

Next: Joshua whole-book consistency review, then Judges 1–5 after verifying the pinned source. GitHub upload remains blocked by established access restrictions. Nothing was publicly deployed; the separate Companion branch remains unchanged. Companion quotations and bindings for newly revised chapters require later reconciliation.
