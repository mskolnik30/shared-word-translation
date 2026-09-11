# Fluent Numbers 3–4 revision

All 100 verses (51 + 49) have a source-based editorial draft, exact original-source binding, before/after text, TSW comparator, verse-specific rationale and F0–F3 editorial assessment. This batch follows `ce1b25c8c533b82bc1c2cd55edfff348bfe2589a`. Cumulative coverage is 3,901 verses in 126 chapters: Genesis 1–50, Exodus 1–40, Leviticus 1–27, Numbers 1–4 and James 1–5.

Fluent’s purpose is biblical fluency through natural connected reading, recurring biblical vocabulary, clear relationships and selective notes. These chapters make the different family groups, census populations and sanctuary responsibilities understandable while retaining the full inventories, repeated formulas and ancient boundaries of access. TSW was read only after the independent Hebrew-based draft.

## Source and decisions

Source: [Open Scriptures Hebrew Bible, pinned Numbers XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Num.xml).

- Commit: `6a5db284c715c18b239422e57bb89684e6a19f00`.
- Git blob: `2e7252db3bd33d510d2361a8b5016ac680b27dbb`.
- SHA-256: `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`.
- Original file: 1,496,833 bytes and 1,289 original records. Public Numbers has 1,288 slots; later differences need explicit mapping. All 100 records in this batch align directly.
- Every selected Hebrew verse was read before drafting, including the two source annotations at 3:30 and 3:39. Exact raw verse hashes include those notes and the extraordinary dots on “and Aaron” at 3:39.

The draft preserves Aaron’s four sons and the deaths of Nadab and Abihu, the absence of sons, and the distinction between priests and Levites. “Given entirely” carries the emphatic repeated giving in 3:9. The Levites replace Israel’s firstborn, with livestock included in the substitution.

Chapter 3 counts males one month old and upward. Its clan figures are 7,500, 8,600 and 6,200, totaling 22,300, while 3:39 states 22,000. The draft preserves these figures and explains the discrepancy without supplying a harmonization. The redemption calculation uses the stated 22,000: 22,273 firstborn minus 22,000 leaves 273, at five shekels each, totaling 1,365 shekels. The sanctuary shekel remains twenty gerahs.

Chapter 4 counts men from thirty to fifty for sanctuary service. The three counts are 2,750, 2,630 and 3,200, totaling 8,580. The separate starting age at Numbers 8:24 was checked directly in the pinned Hebrew and noted without harmonizing it here.

The sanctuary vocabulary was checked against the earlier revised Exodus passages. The draft retains taḥash as an uncertain skin/leather material, with a note, rather than naming an uncertain animal. It distinguishes the inner curtain and entrance screens, each group’s inventory, colored covering layers and carrying equipment. Aaron and his sons cover the objects before the Kohathites carry them. Eleazar’s oversight and Ithamar’s supervision remain distinct. Execution language at 3:10 and 3:38 remains different from the warnings of death at 4:15 and 4:20. The difficult expressions at 4:20 and 4:49 receive short notes; equipment assignment “by name” at 4:32 remains distinct from assigning each man his task at 4:19.

Supplemental comparison after reading the Hebrew used NET translators’ discussions of [Numbers 3](https://www.biblegateway.com/passage/?search=Numbers+3&version=NET) and [Numbers 4](https://www.biblegateway.com/passage/?search=Numbers+4&version=NET). The ESV wording of [Numbers 4:20](https://www.biblegateway.com/passage/?search=Numbers+4:20&version=ESV) was checked after drafting. These comparisons do not govern the draft’s wording. All 100 TSW verses were read afterward.

## Verification and limits

All 32 cumulative verse-ledger audits passed, covering exact source identity, parent before-text objects, chapter and comparator hashes, coverage and verse bindings. Focused checks passed for genealogical names, clan leaders, inventories, covering colors and order, age bands, each census figure, the deliberately retained discrepancy, redemption arithmetic, role boundaries and death language. Verse order, paragraph containment, quotation balance, translation-family structure and `git diff --check` passed.

All 100 verse texts changed: 66 F2 and 34 F3 editorial assessments. Automated TSW comparison moved from 66 identical and 33 near-identical verses to zero identical and three near-identical verses. Near-identical means nonidentical word similarity of at least 0.90. Short formulas, proper names and numeral formatting affect the scores. These measurements are triage, not proof of fidelity, originality or comprehension; no change quota was imposed.

The source comparisons and focused checks were performed by the authoring model. Independent scholarly review and reader testing remain pending. `QA_PASSED` is qualified as structural; revised chapters retain `editorial_status: REVIEW_PENDING` and `publication_allowed: false`.

Only Numbers 3–4 supersede their previous wording’s approvals and bindings. Earlier batches, including Numbers 1–2, remain unchanged. Unaffected Numbers records and TSW are preserved. Historical provenance remains in exact Git history. Companion quotations and bindings involving Numbers 3–4 need checking before later installation; no separate Companion branch was modified and no text was publicly deployed.

## Continue

Next: Numbers 5–6, with attention to agency, gender, ritual details, real harms and consequential ambiguity in the jealousy ordeal, and to Nazirite vows and the priestly blessing. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried. Continue from the latest cumulative checkpoint without routine approval pauses.
