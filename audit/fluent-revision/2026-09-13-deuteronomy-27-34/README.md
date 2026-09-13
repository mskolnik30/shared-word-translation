# Fluent Deuteronomy 27–34 revision

This batch completes a source-based draft of Deuteronomy: 266 new public verses, bound to 266 complete Hebrew XML records. Across all completed batches, 5,960 public verses in 192 chapters have been revised. All five books of the Torah and James now have revised drafts. Deuteronomy's whole-book consistency review remains next in the queue; independent scholarly review and reader testing remain pending for all revised text.

The English was drafted after reading every selected verse of the pinned Hebrew, with individual editorial rationales. All 266 TSW comparator verses were then read. Selective NET translator notes for chapters 29, 32, and 33 were consulted for difficult expressions. The comparator did not supply the wording base. The draft retains familiar shared phrases where they remain clear and faithful.

## Reading decisions

- Twelve separate curse responses in chapter 27 retain the people's repeated Amen. The tribes on Gerizim and Ebal remain in their source order.
- Chapter 28 keeps the repeated fruit, overtaking, one/seven, and head/tail patterns. Sexual violence, child cannibalism, captive children, failed self-sale into slavery, and the divine rejoicing in destruction are not softened.
- The covenant renewal keeps its inclusive assembly, oath sanctions, hidden/revealed distinction, return language, heart circumcision, and choice of life. The obscure watered/thirsty expression remains open with a note.
- The seven-year public reading includes men, women, children, and resident foreigners. The song's plural write/singular teach instructions distinguish Moses and Joshua. The scroll is placed beside the ark.
- Chapters 32–33 retain poetic lineation inside verse paragraphs. Rock, eagle, birth, poison, arrows, sword, shoulders, sea, and everlasting arms remain images. Changes of speaker and pronoun are marked without pretending all uncertainties are resolved.
- The pinned text governs children of Israel in 32:8, Hoshea in 32:44, and the written/read forms in 33:2. Notes identify consequential alternatives. No blessing for Simeon has been invented.
- The closing narrative retains the unnamed burial agent, the LORD's knowing Moses face to face, Moses' age of 120, thirty days of mourning, and the complete geographical panorama.

## Source and mapping

Source: [Open Scriptures Hebrew Bible, pinned Deuteronomy XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Deut.xml).

Commit: `6a5db284c715c18b239422e57bb89684e6a19f00`.
Git blob: `5317431fd1d1fb5848d7f9f1d22d0753152f9991`.
SHA-256: `aad16a6a2dcbdc6ee36d7d051e80a63bfeb69ecaae19f775ec5b6aa67fe22355`.
Full book: 959 XML verse records.

Public 29:1 binds Hebrew 28:69; public 29:2–29 binds Hebrew 29:1–28. Other verses in this batch align directly. All 959 Deuteronomy records are now bound exactly once across five ledgers, preserving the earlier chapter 12/13 and 22/23 mappings. Exact original XML substrings, including written/read variants, numbering notes, and scribal annotations, are hashed without normalization.

Supplemental comparisons: [NET Deuteronomy 29 notes](https://www.biblegateway.com/passage/?search=Deuteronomy+29&version=NET), [NET Deuteronomy 32 notes](https://www.biblegateway.com/passage/?search=Deuteronomy+32&version=NET), [NET Deuteronomy 33 notes](https://www.biblegateway.com/passage/?search=Deuteronomy+33&version=NET).

## Verification and limits

All 45 cumulative `audit_fluent_revision.py` ledger audits pass. `verify_batch.py` also checks complete coverage, exact mapping, retained annotations, paragraph containment, balanced double quotation marks, selected names and numbers, difficult readings, and preservation of earlier batches and unrelated files. `audit_translation_family.py` and `git diff --check` pass. The executable verifier and its results are included.

The automated overlap report changes from 207 identical and 51 near-identical verses to 8 identical and 31 near-identical verses (near-identical: nonidentical word similarity at least 0.90). These measurements are triage, not evidence of fidelity, originality, reader comprehension, or independent approval. Seven verse texts remain exactly unchanged from the previous Fluent wording; 259 change. Editorial choices comprise 7 F0, 187 F2, and 72 F3 entries.

Chapter `QA_PASSED` remains qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. Earlier wording approvals are superseded only for the changed chapters, with provenance recoverable from the exact base commit. The whole-book records preserve every earlier revision batch. TSW and the separate Companion branch remain unchanged. Companion quotations and bindings for these chapters require later checking before installation or publication. No deployment occurred.

GitHub upload remains blocked by the established access restriction. Rejected writes were not retried. The local commit and cumulative checkpoint preserve the work.
