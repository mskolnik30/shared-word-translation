# Fluent Joshua 9–17 revision

All 256 verses have a source-based draft and individual rationale. Fluent’s purpose is biblical fluency: clear speakers and relationships, natural connected reading, recognizable repeated terms and images, and selective notes that preserve consequential uncertainty. Every pinned Hebrew verse was read before drafting; all TSW verses were read afterward as comparators.

## Source and coverage

[OSHB Joshua source](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Josh.xml): openscriptures/morphhb commit 6a5db284c715c18b239422e57bb89684e6a19f00, wlc/Josh.xml, Git blob 817453d2312e7cf359f6324e5456c5ba59c5bfa2. Full-file SHA-256 d32a65fc6dc7207625c05ddcd133a0833a0c48e3d2343ba6fff4e01be9d5beaf; 658 XML records. All 256 public references in chapters 9–17 map one to one to exact original XML substrings, including written/read notes.

Selected post-draft comparisons consulted the NET translators’ notes on [Joshua 9](https://www.biblegateway.com/passage/?search=Joshua+9%3A3-27&version=NET) for the uncertain verb, bread, provisions and servitude, and [Joshua 15:17–19](https://www.biblegateway.com/passage/?search=Joshua+15%3A17-19&version=NET) for kinship and pronoun alternatives. Fluent retains its own source-based choices and describes relevant alternatives. Unavailable pages and unrelated search results were not used as translation evidence.

## Checks and editorial limits

All 47 cumulative source-binding ledger audits passed, totaling 6,402 verses in 209 chapters. The translation-family audit, paragraph and verse structure checks, historical-preservation checks and git diff --check passed. Fifty-three Hebrew/draft pairs were reread for focused risks. The kings’ repeated one tally matches thirty-one in both Hebrew and English. Joshua 15 name order was checked against the read comparator with explicit source spelling exceptions; names and the conflicting stated totals remain intact.

This is authoring self-review, not independent scholarly approval. New chapter metadata retains status QA_PASSED qualified by qa_scope structural, editorial_status REVIEW_PENDING, and publication_allowed false. Earlier chapter reviews remain at the exact parent commit. Prior book records are preserved; only chapters 9–17 are newly superseded. Earlier batches, TSW, later Joshua chapters and the separate Companion branch remain unchanged.

225 verse texts changed and 31 remained unchanged: 31 F0, 162 F2, 63 F3. Normalized overlap with TSW moved from 243 identical and 13 near-identical verses to 41 identical and 15 near-identical verses. The identical verses are place lists and counting formulas. Near-identical means nonidentical similarity of at least 0.90. No overlap quota governed wording, and these metrics are not a quality or originality certificate.

## Evidence and continuation

- joshua-verse-review.json: every verse’s before/after/comparator, source binding and rationale.
- focused-comparisons.json: 53 selected source/draft pairs with annotations.
- overlap.json: before/after comparison as triage.
- review.json: authoring decisions, unresolved questions and Companion impacts.
- verification.json and verify_batch.py: reproducible checks using pinned sources and exact Git history.

Next: Joshua 18–24, then the whole-book consistency pass. GitHub upload remains blocked by established access restrictions. No public deployment occurred. Companion quotations and bindings for newly revised chapters require later reconciliation.
