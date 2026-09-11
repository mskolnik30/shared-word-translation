# Fluent source-based revision: Genesis 29–31

September 11, 2026. This connected batch completes 133 public verses in three chapters, from Jacob’s arrival at Laban’s household through the covenant boundary at Gilead. Genesis 1–31 and James 1–5 now have draft revision coverage: 1,037 verses in 36 chapters. Genesis 32–36 remains next; the original 29–36 work item was divided at the English chapter boundary after Jacob’s departure from Laban so that the completed unit could receive focused checks and a durable checkpoint.

## Source and method

Every verse was read from the verified [Open Scriptures Hebrew Bible Genesis XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Gen.xml), commit `6a5db284c715c18b239422e57bb89684e6a19f00`, blob `dcc8be362134981d3054e9b64d3a465d08492a33`. The 1,533-record source file matched both its Git blob and SHA-256. The ledger hashes exact original XML verse substrings, including the written/read note in 30:11 and the source’s versification note in Hebrew Genesis 32:1.

English Genesis 31:55 corresponds to Hebrew Genesis 32:1 in the pinned XML. The public label remains `v55`, but the ledger binds it to the full `Gen 32:1` record. The audit tool now supports explicit extra source records and public/source reference mapping, allowing the exception to be checked rather than normalized away. Public and Hebrew numbering realign at English Genesis 33.

The [verse ledger](genesis-verse-review.json) records all 133 source-specific decisions, before/after wording, TSW comparators, source bindings, and editorial F0–F3 classifications. TSW was used as a comparator, not an English base. Three decisions retain clear existing wording, 83 address syntax or idiom, and 47 flag consequential interpretive, textual, social, or versification choices. There is no minimum-change requirement. Surface difference is not proof of fidelity, originality, or comprehension.

## Focused editorial pass

- The recurring family relationships remain explicit: Laban is Rebekah’s brother and Rachel and Leah’s father; Jacob’s children are Laban’s grandchildren even where the Hebrew calls them sons. The seven-year periods, wedding week, twenty years, fourteen and six years, ten wage changes, three-day separation, seven-day pursuit, and the sons’ birth order were checked.
- Leah’s unequal standing is not softened: the source says she was hated. Her suffering, hopes, and naming speeches remain in her voice. The uncertain description of her eyes is rendered “gentle,” with alternatives disclosed.
- Zilpah and Bilhah remain enslaved women even when the narrative calls them wives. Rachel and Leah’s arrangements, the women’s rivalry, and bargaining over sexual access are made intelligible without inventing consent or motives. Dinah is named as a daughter without implying no other daughters existed.
- Reuben, Simeon, Levi, Judah, Dan, Naphtali, Gad, Asher, Issachar, Zebulun, Joseph, and the words associated with their names remain connected. The written and traditional reading behind Gad, the difficult Zebulun verb, and the mandrakes’ cultural association are disclosed without treating wordplay as exact etymology or the plants as a cause of pregnancy.
- The difficult flock account keeps the animal markings, Laban’s removal and separation, Jacob’s branches, and selective breeding practice visible. The translation does not manufacture a scientific explanation. The next chapter’s dream account attributes the marked offspring and protection to God, and the two presentations are not collapsed into one.
- Rachel and Leah’s assessment that Laban sold them and consumed the money paid for them remains their testimony. Laban’s claims of ownership and benevolent intent remain his speech, not narrator endorsements.
- The repeated theft language links Rachel’s taking of the household gods and Jacob’s secret departure without equating the actions. Rachel’s motive and the truth of her menstruation claim remain unstated. Jacob’s unknowing death pronouncement is preserved without making it cause Rachel’s later death.
- The uncertain “good or bad” warning is rendered as a prohibited pronouncement; alternatives are noted. “The Fear of Isaac” remains a distinctive divine title. Laban’s plural “judge” and appeal to the God of Abraham and the god of Nahor are preserved, while Jacob’s oath is distinguished.
- Jegar-sahadutha, Galeed, and Mizpah retain their linguistic associations. The heap and pillar mark a wary boundary under divine witness, not a sentimental promise of closeness.

The authoring model reread every Hebrew verse and the assembled English and made local corrections, including balancing a continued quotation in 31:42 and tightening the repeated kinship wording in 29:10. This is a self-check, not an independent editorial review or a human reading test.

The [NET translators’ notes for Genesis 29](https://www.biblegateway.com/passage/?search=Genesis+29&version=NET) were consulted for the broad kinship term, Leah’s eyes, the sexual euphemism, and the wedding week. The [Genesis 30 notes](https://www.biblegateway.com/passage/?search=Genesis+30&version=NET) were consulted for the Gad written/read form, Zebulun’s verb, and animal categories. The [Genesis 31 notes](https://www.biblegateway.com/passage/?search=Genesis+31&version=NET) were consulted for the “good or bad” idiom, “Fear of Isaac,” plural “judge,” and English/Hebrew versification. They are comparison aids, not Fluent’s source text.

## Verification and limits

The [verification record](verification.json) contains the actual audit outputs and focused assertions. [Before](overlap-before.json) and [after](overlap-after.json) overlap reports measure surface resemblance to TSW; their results are triage, not a quality gate.

Chapter YAML retains `status: QA_PASSED` qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. Prior approval and old source bindings are superseded only for chapters 29–31. Earlier revision batches and historical records remain available. The legacy `chapter_reviews_complete` field counts completed draft passes, not scholarly approval; its scope qualifier says so.

TSW, Genesis 1–28, Genesis 32–50, James, and separate Companion content are unchanged. Companion chapter hashes and any exact quotations from Genesis 29–31 must be checked against this ledger before later installation. No Companion rewrite or public deployment occurred.

The cumulative checkpoint preserves exact Git history from base `984d86f25ff0c4e46b566e063fc0b86a8ed64eb7`. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried. Drafting and durable checkpoints can continue without it.
