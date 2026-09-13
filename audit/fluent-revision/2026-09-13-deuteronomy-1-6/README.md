# Deuteronomy 1–6: Fluent revision

This connected batch adds 219 source-based draft verses in six complete chapters. Cumulative draft coverage is 5,220 public verses in 164 chapters: Genesis, Exodus, Leviticus, Numbers, Deuteronomy 1–6, and James.

Fluent's goal is biblical fluency: readers can follow speakers, narrative movement, conditions, and recurring biblical language in a distinct natural-reading voice. Every selected Hebrew verse was read before drafting. All 219 TSW verses were read afterward as comparators. No synonym replacement procedure or minimum-change target governed the wording.

## Source and decisions

The verified source is [Open Scriptures Hebrew Bible, Deuteronomy](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Deut.xml), commit `6a5db284c715c18b239422e57bb89684e6a19f00`, Git blob `5317431fd1d1fb5848d7f9f1d22d0753152f9991`, SHA-256 `aad16a6a2dcbdc6ee36d7d051e80a63bfeb69ecaae19f775ec5b6aa67fe22355`. The complete XML has 959 records. All 219 public verses in chapters 1–6 align directly with their corresponding records. Exact original XML substrings are hashed, including all annotations in 26 selected records: written/read differences at 2:33 and 5:10, alternative accentuation in chapter 5, and other notes. Alternative accent notes are not treated as different lexical readings.

- Chapters 1–3 retain Moses' retrospective account, all place and people names, dates and durations, the grants to Esau and Lot's descendants, the eastern tribes' obligations, and his attribution of his exclusion to the people. The violence against men, women, and children remains explicit. Og's bed is distinguished from a measurement of his body.
- Chapter 4 connects hearing, remembering, and teaching. It preserves the voice/no-form distinction, the consuming-fire and mercy descriptions, the singular ancestral suffix issue at 4:37, and the refuge towns' names and conditions. Sion at 4:48 is retained as written.
- Chapter 5 preserves the emphatic “not ... but” covenant statement without adding “only.” It retains this account's Sabbath wording and liberation rationale, explicit rest for enslaved people, the different verbs of desire, and the wife/house/field order. The read form “my commands” at 5:10 is followed and the written form recorded.
- Chapter 6 keeps the consequential “one”/“alone” question visible, repeated total devotion, concrete binding and writing instructions, everyday teaching, the unearned-abundance list, the out-to-in movement, and conditional righteousness language. Notes do not turn these choices into doctrinal arguments.

Supplemental primary comparison used [NET translators' notes on Deuteronomy 6](https://www.biblegateway.com/passage/?search=Deuteronomy+6&version=NET) before drafting and on [Deuteronomy 1](https://www.biblegateway.com/passage/?search=Deuteronomy+1&version=NET), [3](https://www.biblegateway.com/passage/?search=Deuteronomy+3&version=NET), and [5](https://www.biblegateway.com/passage/?search=Deuteronomy+5&version=NET) during the post-draft self-check. Interpretive discussions were not imported wholesale into Fluent's notes.

## Checks and limits

All 41 cumulative source-binding ledger audits passed, along with the translation-family audit, paragraph/verse structure checks, focused names/numbers/conditions checks, and `git diff --check`. Every verse has before/after text, its TSW comparator, source binding, an individual rationale, and an editorial F0–F3 classification. Exact Git parents remain available for before-text verification.

The batch changes 216 verse texts and retains three. Editorial classifications are 166 F2, 50 F3, and three F0. Whole-verse TSW matches fall from 175 to three; near-identical nonmatches fall from 38 to ten under the 0.90 threshold. These figures measure surface overlap, not fidelity, legal originality, reader comprehension, or scholarly approval.

Only Deuteronomy 1–6 supersede their previous wording's approvals and bindings. Earlier batches, unrevised chapters, historical provenance, TSW, and unrelated work are preserved. The revised chapters have `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. Independent scholarly review and reader testing have not occurred. Companion quotations and bindings for these chapters require later checking; the separate Companion branch remains unchanged. GitHub upload remains blocked by the established connection restriction; no rejected write was retried. Nothing was publicly deployed.

Next: Deuteronomy 7–12, then 13–18, in larger connected batches. Resolve the latest checkpoint and verify source/public mapping before proceeding. The source-reading draft inputs are not a substitute for the authoritative ledger and chapter files in this batch.

To reproduce structural and binding verification, run `verify_batch.py` with `--genesis-source`, `--exodus-source`, `--leviticus-source`, `--numbers-source`, `--deuteronomy-source`, and `--james-source`, pointing to the exact pinned files. The source manuscript files are not redistributed here.
