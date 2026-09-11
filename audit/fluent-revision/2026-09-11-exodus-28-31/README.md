# Fluent Exodus 28–31 revision

All 145 public verses in Exodus 28–31 have a source-based draft, selective notes and vocabulary, and a verse-specific editorial rationale. This brings the cumulative revision to Genesis 1–50, Exodus 1–31, and James 1–5: 2,547 verses in 86 chapters.

The draft follows the passage’s movement from priestly clothing through ordination, offerings, sanctuary preparations, skilled work, and Sabbath. It keeps names on shoulders and heart, honor and beauty, judgment, holiness, atonement, and divine dwelling recognizable across the chapters. Ritual violence, blood application, death penalties, and exclusion sanctions remain explicit. Rare textiles, gemstone identifications, sacred contact, and anointing restrictions receive qualified notes. The Urim and Thummim receive no invented description or procedure.

The authoring model read every selected Hebrew verse and source annotation before composing its corresponding draft, then used TSW and supplemental translator notes as comparators. Its assembled-text self-check is not independent scholarly review or evidence of reader comprehension. A note that overstated a written/read spelling variation as a singular/plural difference was removed; the exact source record and both spellings remain bound in the ledger. The list of ram portions was clarified to avoid making the right thigh a type of fat.

## Source and evidence

- `exodus-verse-review.json`: all 145 before/after texts, TSW comparators, F0–F3 decisions, verse-specific rationales, exact source hashes and chapter bindings. There are 144 changed verse texts and one retained verse; F0: 1, F2: 97, F3: 47.
- `verify_batch.py` and `verification.json`: all 18 cumulative source-binding ledger audits passed; 2,547 verses, 86 chapters. Genesis covers all 1,533 source records, and Exodus covers 906 unique source records through chapter 31. Earlier public/Hebrew numbering mappings remain intact.
- Exact Exodus source: openscriptures/morphhb commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Exod.xml`, Git blob `9f1174a401696a1625e88c0d87ed2359889fb79e`, SHA-256 `5e53e6841562f2c7af6756984a643b05628b29c39dc690d914dce6c70c6c38cb`. All 1,213 full-book records verified. Selected verse hashes include original XML whitespace and annotations at 28:28 and 30:12.
- Focused assertions cover priestly and artisan names; six/six and twelve-stone patterns; garment measurements; blood actions; offering counts and quantities; the equal half-shekel payment; anointing/incense proportions; death and exclusion language; and Sabbath/creation imagery. Coverage, verse labels, paragraph containment, quotation balance, and uninterrupted multi-verse sentences passed.
- Translation-family audit and `git diff --check` passed. TSW, earlier revised chapter wording, prior batch records, unrelated work, and Companion files were preserved.
- `overlap-before-after.json`: identical TSW verses decreased from 31 to 2; nonidentical verses at similarity >= 0.90 decreased from 103 to 13. This is mechanical triage only, with no change quota and no claim that overlap proves fidelity or originality.

## Editorial and continuation state

Revised chapters have `QA_PASSED` qualified by `qa_scope: structural`; independent editorial status is `REVIEW_PENDING` and `publication_allowed` is false. Only chapters 28–31 supersede their former wording’s approvals and bindings. Earlier provenance remains in exact Git history.

Companion quotations and text bindings for these four chapters need checking before later installation. No Companion branch was changed and no text was publicly deployed. GitHub upload remains blocked by the previously established write-access restriction; no rejected write was retried.

Next connected scope: Exodus 32–34, followed by 35–40 and a whole-book consistency pass. Continue without routine approval pauses, using the latest cumulative checkpoint and exact source history.
