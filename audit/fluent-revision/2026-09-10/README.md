# Fluent biblical-fluency revision: James

Date: September 10, 2026. Status: complete-book editorial draft; not published.

## What changed

All five chapters of James (108 verses) have been revised against the existing pinned SBLGNT Greek source. The aim is sustained comprehension: clear speakers and referents, manageable sentences, recognizable biblical vocabulary, and a connected argument that readers can follow aloud or silently.

The revision keeps James's distinctive voice, concrete images, demanding claims, and unresolved interpretive questions. It establishes a practical editorial standard in [Fluent's philosophy](../../../FLUENT_TRANSLATION_PHILOSOPHY.md). It does not rewrite TSW or claim that the rest of Fluent has received this pass.

## Read the revised chapters

- [James 1](../../../translations/fluent/NT/james/James_01.md)
- [James 2](../../../translations/fluent/NT/james/James_02.md)
- [James 3](../../../translations/fluent/NT/james/James_03.md)
- [James 4](../../../translations/fluent/NT/james/James_04.md)
- [James 5](../../../translations/fluent/NT/james/James_05.md)

## Comparison with TSW

This is a comparison of matching public verse labels, excluding headings, metadata, notes, and vocabulary. It preserves verse continuation lines, normalizes Unicode and capitalization, and compares word tokens without punctuation. “Near-identical” means a nonidentical verse with a token-sequence similarity of at least 90%. It is a triage category, not a test of fidelity or plagiarism. Five unmatched labels are reported separately; they arise from the documented Romans 16 and Nehemiah 7 versification differences.

| Scope | Matched verses | Identical before | Identical after | Near-identical before | Near-identical after |
|---|---:|---:|---:|---:|---:|
| James | 108 | 11 (10.19%) | 0 (0.0%) | 28 | 0 |
| Whole corpus | 31,083 | 20,301 (65.31%) | 20,290 (65.28%) | 5,453 | 5,425 |

Zero whole-verse overlap in this James draft is an observed result, not an editorial requirement. Clear shared clauses, biblical quotations, and necessary theological vocabulary remain. “Mercy triumphs over judgment” is retained. Lower overlap does not establish source fidelity or reader comprehension.

## Examples of the reading approach

| Passage | Previous Fluent wording | Revised Fluent wording |
|---|---|---|
| James 1:22 | Be doers of the word, and not hearers only, deceiving yourselves. | Do what the word says. If you only listen to it, you are deceiving yourselves. |
| James 2:9 | But if you show partiality, you are committing sin and are convicted by the law as transgressors. | But if you show favoritism, you sin. The law finds you guilty of breaking it. |
| James 3:13 | Who among you is wise and understanding? Let that person show by good conduct their works done in the gentleness of wisdom. | Who among you is wise and understanding? Show it through a good life and deeds done with the gentleness that wisdom brings. |
| James 4:17 | So whoever knows the right thing to do and does not do it, for that person it is sin. | So if you know the good you should do and leave it undone, you sin. |
| James 5:14 | Is anyone among you sick? Let that person call for the elders of the church, and let them pray over them, anointing them with oil in the name of the Lord. | Is anyone among you sick? Call the church's elders. They should pray over the sick person and anoint that person with oil in the Lord's name. |

## Source and editorial accountability

The [pinned Greek source](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/Jas.txt) matches Git blob `283a675fdfab4ca4967ca5a72500a1aff2bd07c7`. The source SHA-256 and per-verse hashes are in the [108-verse ledger](james-verse-review.json), alongside the prior Fluent wording, revised wording, TSW comparator, delta classification, and specific rationale. The [pinned apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/Jas.txt) was checked for 1:12, 2:3, 2:20, and 5:4.

F1 marks a wording adjustment, F2 a syntax or idiom adjustment, and F3 a consequential interpretive or textual choice. These are editorial assessments, not classifications inferred from an overlap score. F3 entries remain open for editorial review. No F4 decisions or fabricated human approvals are present.

The source check corrected the handling of James 2:3's placement language and the vocabulary headword at 5:4. It also exposed choices that the former notes left implicit: the fire attachment in 5:3, “on a day of slaughter” in 5:5, and the statement/question at 5:6. Notes now distinguish these options. James 4:5 remains explicitly disputed; 2:21–25 remains unharmed by harmonization with Romans.

Notes and vocabulary have been edited for selectivity and relevance to the new wording. The word “works” remains in the vocabulary bridge for the recurring “deeds” translation. Familiar biblical terms and images are explained selectively rather than systematically removed.

## Verification and publication state

- Corpus coverage and public verse-label parity: passed, with only the existing documented exceptions.
- James source blob and SHA-256: verified.
- All 108 source references, before/after chapter hashes, TSW hashes, and ledger text: verified.
- Paragraph structure, verse order, unique apparatus headings, and draft metadata: passed.
- Targeted audit checks: continuation text retained; notes excluded; duplicate labels rejected; changed source, altered wording, missing verse, and F4 decision detected.
- Human language, exegetical, and reading-aloud review: pending; no user comprehension testing has been claimed.
- Website deployment: not performed.

The existing chapter `QA_PASSED` field is now explicitly qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. The book and chapter review records no longer carry the previous wording's approval forward. This draft must not be deployed merely because the legacy structural audit passes.

All five James chapter hashes changed. Any Fluent Companion bound to those previous chapters must be rebound and checked for quotations, wording-dependent comments, and vocabulary references before publication. The separate Companion branch is not changed in this revision.

## Remaining corpus work

The global result is substantial: 20,290 aligned verses still have identical words after this James batch. The following books have the largest absolute numbers of identical verses. Names, lists, quotations, and short clauses need judgment rather than automatic rewriting.

| Book | Matched verses | Identical verses after James revision | Identical share |
|---|---:|---:|---:|
| psalms | 2,461 | 2,142 | 87.04% |
| jeremiah | 1,364 | 1,171 | 85.85% |
| genesis | 1,533 | 1,159 | 75.6% |
| isaiah | 1,292 | 1,066 | 82.51% |
| job | 1,070 | 1,016 | 94.95% |
| 1chronicles | 942 | 923 | 97.98% |
| numbers | 1,288 | 911 | 70.73% |
| proverbs | 915 | 878 | 95.96% |
| ezekiel | 1,273 | 862 | 67.71% |
| 1kings | 816 | 771 | 94.49% |
| 2chronicles | 822 | 748 | 91.0% |
| exodus | 1,213 | 748 | 61.67% |
| 1samuel | 810 | 680 | 83.95% |
| 2kings | 719 | 628 | 87.34% |
| 2samuel | 695 | 617 | 88.78% |

Suggested next editorial batch: Genesis 1–11, followed by further connected narrative units and selected complete psalms. Genesis provides a high-overlap, foundational narrative setting for testing Fluent's voice beyond a letter. This is a proposed queue, not a claim that those passages are already revised. A complete-book check must follow any chapter batches.

## Reproduce the checks

From the repository root, download the exact Greek file linked above to a local path and run:

```bash
python3 tools/audit_translation_family.py
python3 tools/audit_fluent_revision.py audit/fluent-revision/2026-09-10/james-verse-review.json --source-text /path/to/Jas.txt
python3 tools/audit_translation_overlap.py --json-output /tmp/fluent-overlap.json
git diff --check
```

The saved [before](overlap-before.json) and [after](overlap-after.json) reports include per-book counts, unmatched labels, method, and the base commit. Add `--include-locations` to regenerate every exact/near-exact verse location; the saved reports omit those large lists to keep the change reviewable. The after report describes the revised working tree; the ledger binds the five changed chapter files by hash.
