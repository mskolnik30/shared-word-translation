# Fluent revision: Leviticus 23–25

All 122 verses received an independent source-based draft, with an individual before/after record, TSW comparator, source binding and editorial rationale. The batch adds 44 verses in chapter 23, 23 in chapter 24 and 55 in chapter 25. Cumulative coverage is 3,633 verses across 120 chapters: Genesis 1–50, Exodus 1–40, Leviticus 1–25 and James 1–5.

Fluent aims at biblical fluency: connected reading, intelligible speakers and relationships, recognizable recurring vocabulary and images, and restrained notes that help readers return to the text. Its distinct voice develops from fresh translation decisions, not a required percentage of changed words.

## Source and comparison

Every selected verse was read from `openscriptures/morphhb`, commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Lev.xml`, Git blob `6025e0713ccfc79de0c90cb92ed0e8c0062d2614`. The full 859-record file has SHA-256 `75a4a96e7b64f2145bede15ae37ac8a0b301f110d5d6b2daf9d8048adebbd2e6`. The exact original XML substrings are hashed, including all five annotations in 23:13, 25:20, 25:30 and 25:46. Public and source numbering align in this batch. At 25:30, the source preserves the written “not” and the read “has a wall”; the draft follows the read form and records the decision.

Primary supplemental comparison used the [NET translators’ notes for chapter 23](https://www.biblegateway.com/passage/?search=Leviticus+23&version=NET), [chapter 24](https://www.biblegateway.com/passage/?search=Leviticus+24&version=NET), and [chapter 25](https://www.biblegateway.com/passage/?search=Leviticus+25&version=NET), after reading Hebrew and before drafting. All 122 TSW comparators were read after the independent draft. The full ancient source, not NET or TSW English, governed composition.

## Consequential decisions

- The calendar keeps all dates, quantities and repetitions. The ordinary-work restriction remains distinct from the comprehensive Sabbath and atonement-day prohibition. Sabbath counting remains open to its calendar interpretations. The firstfruits loaves remain leavened; the sound in 23:24 has no instrument supplied. Cutoff in 23:29 remains distinct from God’s “I will destroy” in 23:30.
- Booths, appointed times, atonement, wave offering and firstfruits remain recognizable terms. The fruit and branch list does not acquire unmentioned species or a booth-building instruction. The stated native-born scope remains intact.
- Chapter 24 distinguishes the two-tenths for each of twelve loaves from the two-loaf quantity in 23:17. It retains the mother’s and grandfather’s names and tribe, the custody before a divine ruling, the actual stoning, and the injury formulas. Notes identify uncertainty about speaking the Name and the phrase “his God.”
- The Jubilee rules retain the forty-nine/fifty count, sixth/eighth/ninth-year provision, original purchase price and remaining-harvest calculations, land versus city-house treatment, permanent Levitical redemption and unsellable pastureland. The difficult opening of 25:33 is translated provisionally without adding TSW’s negative. Its alternatives remain marked for review.
- Poverty, kinship, resident status and ownership remain explicit. The permanent inheritance of foreign slaves is not softened, nor is the scope of Israelite release extended beyond the text. “Slave” also keeps the repeated divine-ownership language visible in 25:42 and 55. Notes distinguish stated provisions from disputed connections and possible interpretations.

## Checks and limits

`verify_batch.py` passed all 29 cumulative verse-ledger audits, exact current source bindings, coverage and uniqueness checks, paragraph and verse-label structure, metadata gates, 102 verse-specific focused checks, annotation checks, preservation of prior batches and unrelated approvals, the translation-family audit and `git diff --check`.

All 122 verses changed: 74 F2 syntax/idiom decisions and 48 F3 consequential decisions. Before revision, 33 verses were word-identical to TSW and 78 additional verses were near-identical; afterward, none are identical and five are near-identical. Mean token-sequence similarity changed from 0.953495 to 0.628654. These measurements are mechanical triage, not evidence of fidelity, literary independence or reader comprehension.

The authoring model’s source reading and focused self-check are distinct from independent editorial review. Revised chapters retain `QA_PASSED` only with `qa_scope: structural`, `editorial_status: REVIEW_PENDING` and `publication_allowed: false`. Independent scholarly review and reader testing have not occurred.

Only this batch’s previous wording and approvals are superseded; prior records remain recoverable from exact parent commit `a320dd05347e33f14e9512ac9064f4dc3dee6e4e`. TSW, earlier revisions, the separate Companion branch and unrelated work are unchanged. Companion quotations and bindings for chapters 23–25 will require later checking before installation.

Next: Leviticus 26–27, followed by whole-book structural and selected thematic self-checks. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried. The cumulative checkpoint preserves the committed work and exact parent history.
