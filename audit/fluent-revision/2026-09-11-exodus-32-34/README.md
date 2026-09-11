# Fluent Exodus 32–34 revision

All 93 public verses in Exodus 32–34 have a source-based draft, selective notes and vocabulary, and a verse-specific rationale. The cumulative revision now covers Genesis 1–50, Exodus 1–34, and James 1–5: 2,640 verses in 89 chapters.

The passage moves from the golden calf through Moses’ intercession, judgment, the question of God’s presence, covenant renewal, and Moses’ shining face. The draft preserves plural “gods” alongside a single calf, the shift of “your people” between speakers, Aaron’s account in contrast with his narrated manufacture, the approximate three-thousand death count, and Moses’ unfinished plea. It retains the LORD’s relenting as stated and the judgments that follow, without a doctrinal explanation imposed on the sequence.

The authoring self-check also kept face-to-face speech and the prohibition on seeing God’s face, hand/back imagery, the ambiguous writing subject in 34:28, and the actual order of veiling and unveiling. Consequential ambiguities receive short notes. “Faithful love,” the intergenerational-guilt phrase, “Lord GOD,” festivals, and firstborn instructions were checked against earlier Exodus chapters. The absence of the limiting phrase from 20:5 in 34:7 is preserved. No ritual sexual acts, fading radiance, or identity for the unnamed book were added.

## Source and validation

The authoring model read all 93 selected verses and their source annotations from the pinned Hebrew, composed the draft, then consulted NET translator notes and read all TSW comparators. It reread the assembled English and clarified divine conversation referents and repeated terminology. This was a source-based authoring pass and self-check, not independent scholarly review or reader testing.

- `exodus-verse-review.json`: before and after verse text, TSW comparator, exact source binding, and editorial rationale for every verse. Of 93 verse texts, 91 changed and 2 were retained; F0: 2, F2: 47, F3: 44.
- `verify_batch.py` and `verification.json`: all 19 cumulative verse-ledger audits passed, covering 2,640 verses in 89 distinct chapters. All 1,533 Genesis records and 999 unique Exodus records through chapter 34 are bound with prior public/source numbering mappings preserved.
- Exact source: openscriptures/morphhb commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Exod.xml`, Git blob `9f1174a401696a1625e88c0d87ed2359889fb79e`, SHA-256 `5e53e6841562f2c7af6756984a643b05628b29c39dc690d914dce6c70c6c38cb`. All 1,213 full-book records verified. Exact verse hashes include annotations at 32:17, 32:19, 33:10, 33:16, and 34:6.
- Coverage, labels, paragraph containment, uninterrupted cross-verse sentences, and quotation balance passed. Lineated speech in 32:18 and proclamation in 34:6–7 remain inside their verse paragraphs. Focused assertions cover names, numbers, human and divine actions, repeated terms, consequential ambiguity, and relevant narrative sequence.
- Translation-family audit and `git diff --check` passed. Earlier chapter wording and all previous batch records remain unchanged; only the current three chapters supersede their former approvals and bindings.
- `overlap-before-after.json`: identical TSW verses decreased from 74 to 2; nonidentical verses at similarity >= 0.90 decreased from 14 to 3. These figures are triage, not evidence of fidelity or originality. No change quota was used.

## Status and continuation

Chapter status `QA_PASSED` is qualified by `qa_scope: structural`. Independent editorial status remains `REVIEW_PENDING`, and `publication_allowed` is false. Companion quotations and bindings for these chapters require later checking before installation. TSW, unrelated work, and the separate Companion branch were not changed. Nothing was publicly deployed.

GitHub upload remains blocked by the previously established write-access restriction; no rejected write was retried. Exact cumulative Git history and complete changed files are included in the saved checkpoint.

Next: Exodus 35–40, then a whole-book Exodus consistency self-check. Rebind any affected earlier ledgers if that review changes their chapter text. Continue from the latest canonical checkpoint without routine approval pauses.
