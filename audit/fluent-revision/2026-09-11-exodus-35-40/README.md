# Fluent Exodus 35–40 revision

All 214 verses in Exodus 35–40 have a source-based draft, selective notes and vocabulary, and a verse-specific rationale. This completes the Exodus draft. Cumulative coverage is Genesis 1–50, Exodus 1–40, and James 1–5: 2,854 verses in 95 chapters.

The passage moves from Sabbath and voluntary contributions through the artisans’ work, the inventories and garment making, Moses’ inspection and installation, and the cloud and glory filling the tabernacle. The draft keeps women’s skilled spinning and willing participation explicit, distinguishes named and unnamed makers, and retains the detailed measurements, material lists, and deliberate repetitions. “Atonement cover,” “bread of the Presence,” the uncertain taḥash skins, and provisional gemstone names remain consistent with the earlier commands.

The authoring self-check compared the instructions and their fulfillment without importing details absent from the later account. It preserved the singular/plural shifts among craftsmen, the repeated pomegranate placement, the exact metal totals, and the lack of an explicit linen noun in 39:24, where an alternative understanding is noted. The final scene includes Moses among those who would wash their hands and feet, then preserves his inability to enter the glory-filled tabernacle. Day/night imagery and both positive and negative conditions for departure remain intact.

## Source and validation

The authoring model read all 214 pinned Hebrew verses with their annotations and drafted independently, then read all TSW comparators and consulted supplemental NET translator notes for chapters 35, 38, 39 and 40. It reread the assembled English and checked measurements, materials, names, inventories, repetitions, and terminology against chapters 25–31. This was an authoring self-check, not independent scholarly review or reader testing.

- `exodus-verse-review.json`: before/after text, comparator, exact source binding and verse-specific rationale. Of 214 verse texts, 210 changed and 4 were retained; F0: 4, F2: 167, F3: 43.
- `verify_batch.py` and `verification.json`: all 20 cumulative verse-ledger audits passed, covering 2,854 verses in 95 distinct chapters. All 1,533 Genesis and all 1,213 Exodus source records are bound exactly once; earlier public/source numbering mappings are preserved.
- Source: openscriptures/morphhb commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Exod.xml`, Git blob `9f1174a401696a1625e88c0d87ed2359889fb79e`, SHA-256 `5e53e6841562f2c7af6756984a643b05628b29c39dc690d914dce6c70c6c38cb`. All 1,213 full-book records verified. Exact verse hashes retain annotations at 35:7, 35:11, 36:2, 37:8, 39:4 and 39:33, including written/read forms.
- Coverage, labels, paragraph containment, cross-verse sentence boundaries and quotation balance passed. Focused checks cover women’s participation, artisan identities, dimensions and census-metal arithmetic, gemstone rows, repeated fulfillment language, washing agents, and the final glory/cloud sequence. Arithmetic checks verify internal numerical relationships, not historical census accuracy.
- Translation-family audit and `git diff --check` passed. Earlier chapter wording and previous batch records remain unchanged; only these six chapters supersede former approvals and bindings.
- `overlap-before-after.json`: identical TSW verses decreased from 196 to 5; nonidentical verses at similarity >= 0.90 changed from 17 to 19. These figures are triage, not evidence of fidelity or originality. No change quota was used.

## Status and continuation

`QA_PASSED` is qualified by `qa_scope: structural`. Independent editorial status remains `REVIEW_PENDING`; `publication_allowed` is false. Companion quotations and bindings for these chapters require later checking before installation. TSW and the separate Companion branch are unchanged. Nothing was published.

GitHub upload remains blocked by the established write-access restriction; no rejected write was retried. The cumulative checkpoint preserves exact Git history and complete changed files.

Next: whole-book Exodus consistency self-check, then Leviticus 1–7 from its verified pinned source. Rebind affected ledgers if earlier chapter text changes; preserve historical provenance and resume from the latest canonical checkpoint without routine approval pauses.
