# Fluent Numbers 1–2 revision

All 88 verses (54 + 34) have a source-based editorial draft, a verse-specific rationale, before/after wording, TSW comparator, editorial F0–F3 assessment and exact original-source binding. This batch continues from commit `cae294fa8084b00288c53f7815ff889fe8c207d1`. The cumulative draft now contains 3,801 verses across 124 chapters: Genesis 1–50, Exodus 1–40, Leviticus 1–27, Numbers 1–2 and James 1–5.

Fluent aims to help readers become fluent in Scripture through connected, natural English, stable biblical vocabulary, visible literary patterns and selective notes. The census remains a repeated prose sequence, with full eligibility criteria and family groupings, while chapter 2 makes the relationship between each tribe and its larger camp easier to follow. The repeated counts and ancient sanctuary boundaries remain part of the text.

## Source and editorial decisions

Source: [Open Scriptures Hebrew Bible, pinned Numbers XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Num.xml).

- Commit: `6a5db284c715c18b239422e57bb89684e6a19f00`.
- Git blob: `2e7252db3bd33d510d2361a8b5016ac680b27dbb`.
- File SHA-256: `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`.
- Original file: 1,496,833 bytes; 1,289 verse records. Public Numbers has 1,288 slots. This batch maps directly; later numbering differences need separate verification.
- All 88 source verses were read before drafting. Hashes cover exact original XML substrings, including the written/read annotation at 1:16. No normalized reconstruction was hashed.
- The census covers males twenty and older eligible for military service. It is not presented as the entire population. Clan and ancestral household remain distinct; a note explains the latter.
- The draft retains the numeral reading of the census totals and “thousands” as the organizational term at 1:16. Notes acknowledge the interpretive range of *eleph* without claiming arithmetic resolves historical population questions.
- Deuel at 1:14 and Reuel at 2:14 remain distinct, matching the pinned source. The note identifies the variation instead of silently harmonizing it.
- All twelve leader/father pairs, twelve tribal totals, four camp subtotals, cardinal directions and marching positions are preserved. “Last” remains “last” at 2:31.
- The tabernacle of the testimony, the Levites’ carrying and guarding duties, wrath and the prescribed death penalty for unauthorized approach are explicit. “Unauthorized” describes access to the service, not ethnicity.

NET translation and selected translators’ notes were used as supplemental comparison after the Hebrew reading; focused notes were checked again after drafting. See [Numbers 1](https://www.biblegateway.com/passage/?search=Numbers+1&version=NET) and [Numbers 2](https://www.biblegateway.com/passage/?search=Numbers+2&version=NET). All 88 TSW comparator verses were read after the independent draft. The wording was composed from the Hebrew.

## Checks and limits

All 31 cumulative verse-ledger audits passed: source identity, exact parent before-text objects, current chapter and comparator hashes, ordered coverage and verse bindings. Focused checks passed for the name pairs and variation, twelve paired counts, four camp subtotals and grand total, census scope, camp/march order, sanctuary duties and penalty. Ordered verse labels, paragraph containment and quote balance passed. The translation-family audit and `git diff --check` passed.

The draft changes all 88 verse texts: 68 F2 and 20 F3 editorial assessments. Case-folded word comparison with TSW moves from 61 identical and 24 near-identical verses to zero in both categories (near-identical means nonidentical similarity of at least 0.90). This is triage, not proof of source fidelity, originality or reader comprehension. Numeral formatting and very short name-list entries affect these figures; no overlap target drove the draft.

`verification.json` and `verify_batch.py` record structural/source checks and authoring self-checks. They do not represent independent scholarly review or reader testing. Revised chapter status `QA_PASSED` is qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING` and `publication_allowed: false`.

Only Numbers 1–2 supersede the earlier wording’s approvals and bindings. Numbers 3–36, TSW, all prior revision text and bindings, and unrelated work are preserved. Previous approval records remain recoverable from exact Git history. No public deployment occurred. Companion quotations and bindings using revised Numbers 1–2 need review when this wording is installed; the separate Companion branch has not been changed.

## Continuation

Next: Numbers 3–4. Preserve the Levite clans and duties, distinct census age bands, firstborn redemption figures, sanctuary boundaries and consequential ambiguities. Complete chapters from the pinned source and save verified checkpoints without routine approval pauses. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried.
