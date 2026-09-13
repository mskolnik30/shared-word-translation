# Numbers 31–36: Fluent revision

This connected batch completes the Numbers draft: 228 public verses, each drafted from its corresponding pinned Hebrew record. Numbers now has 1,288 revised public verses bound to all 1,289 Hebrew records. Cumulative coverage is 5,001 public verses in 158 chapters across James, Genesis, Exodus, Leviticus and Numbers.

The aim is biblical fluency: readers can follow speakers, narrative movement, conditions and recurring biblical language in a distinct natural-reading voice. TSW was read as a comparator after drafting. Similarity does not govern translation choices or establish independent authorship, fidelity or reader comprehension.

## Source and editorial choices

The source is openscriptures/morphhb commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Num.xml`, Git blob `2e7252db3bd33d510d2361a8b5016ac680b27dbb`, SHA-256 `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`. Every selected verse was read before drafting. Exact original XML substrings, including written/read annotations at 32:7 and 34:4 and the annotation at 32:30, are hashed in the ledger. This batch aligns directly; earlier numbering offsets and the two-record binding at public 26:1 remain intact.

- Chapter 31 preserves vengeance language, the killing and captivity of women and children, both purification stages, the two equal shares and different levies, human captives within those levies, and atonement language in the officers’ gift. Uncertain ornament names receive a brief note.
- Chapter 32 makes the tribes’ pledge and military obligations clear, keeps the alternative Canaan allotment in verse 30, and preserves all eastern settlement names. Machir’s collective family reference is explained.
- Chapter 33 retains every journey stage and the repeated travel pattern, all dates and quantities, the Hahiroth and Iyim forms, and the distinctions between Sin and Zin. The warning of dispossession and its reversal against Israel remain explicit.
- Chapter 34 retains every boundary marker and allotment leader, with selective geographical notes. The two Mount Hor settings are distinguished without supplying uncertain modern coordinates.
- Chapter 35 preserves both pasture measurements without an invented layout, protection and communal judgment, intentional and unintentional killing, the avenger’s role, residence until the high priest’s death, witness restrictions and both no-ransom rules. Bloodguilt remains distinct from ritual impurity.
- Chapter 36 retains both the daughters’ choice and the restriction on marriages involving inherited land. It preserves their exact name order and paternal-cousin relationship.

Supplemental primary comparison: [NET translators’ notes on Numbers 31](https://www.biblegateway.com/passage/?search=Numbers+31&version=NET), consulted before drafting, and [Numbers 35](https://www.biblegateway.com/passage/?search=Numbers+35&version=NET), consulted after drafting. These were lexical and grammatical aids; their extended interpretations were not imported into Fluent’s notes.

## Checks and limits

All forty cumulative verse-ledger audits passed, along with the translation-family audit and `git diff --check`. The focused checks cover the campaign totals and levy arithmetic, every itinerary stage, boundary and leader names, the refuge conditions and inheritance restrictions. All 228 verses remain ordered within chapter paragraph wrappers. The ledger includes before/after wording, exact source binding, TSW comparison, and an individual editorial rationale for every verse.

The batch changes 222 verse texts and retains six: 31:29, 31:33–34, 31:44–45 and 34:21. The before/after comparison records whole-verse TSW matches falling from 169 to 8; near-identical nonmatches fall from 52 to 13 under the audit’s 0.90 threshold. Short numerical and naming formulas appropriately remain shared. These measurements are triage, not editorial approval.

The complete Numbers consistency self-check is next. Draft completion and structural QA do not constitute independent scholarly review or reader testing. Every revised chapter has structural QA qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`.

Only chapters 31–36 supersede the previous wording’s approvals in this batch. Earlier revisions, exact historical provenance, TSW and unrelated work are preserved. Companion quotations and bindings for these chapters will require checking before later installation; the separate Companion branch was not changed. GitHub upload remains blocked by the established connection restriction, and no rejected write was retried. Nothing was publicly deployed.

Run `verify_batch.py` with the five pinned source files to reproduce the recorded structural and source-binding checks. The full source files are not redistributed in this packet.
