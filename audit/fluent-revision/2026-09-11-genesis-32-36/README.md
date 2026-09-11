# Fluent source-based revision: Genesis 32–36

September 11, 2026. This connected batch completes 155 public verses in five chapters, from Jacob’s approach to Esau through the family and political records of Edom. Genesis 1–36 and James 1–5 now have draft revision coverage: 1,192 verses in 41 chapters. Genesis 37–50 is next.

## Source and method

Every verse was read from the verified [Open Scriptures Hebrew Bible Genesis XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Gen.xml), commit `6a5db284c715c18b239422e57bb89684e6a19f00`, blob `dcc8be362134981d3054e9b64d3a465d08492a33`. The 1,533-record source file matched both its Git blob and SHA-256. The ledger hashes exact original XML verse substrings, including the scribal markings in 33:4 and written/read records for Jeush in 36:5 and 36:14.

English Genesis 32:1–32 corresponds to Hebrew Genesis 32:2–33. Hebrew Genesis 32:1 was already bound to English Genesis 31:55 in the preceding ledger. The public labels remain `v01` through `v32`, each bound to its exact Hebrew record, and numbering realigns at Genesis 33. The source audit now supports an explicitly excluded record within a chapter scope, so Hebrew 32:1 cannot be silently duplicated in both ledgers.

The [verse ledger](genesis-verse-review.json) records all 155 source-specific decisions, before/after wording, TSW comparators, source bindings, and editorial F0–F3 classifications. TSW was used as a comparator, not an English base. Nine decisions retain clear existing wording, 85 address syntax or idiom, and 61 flag consequential interpretive, textual, social, or versification choices. There is no minimum-change requirement. Surface difference is not proof of fidelity, originality, or comprehension.

## Focused editorial pass

- Genesis 32 preserves the angel/messenger repetition, two camps, Jacob’s deferential language toward Esau, fear, prayer, exact livestock numbers, staged gift, face wordplay, Jabbok crossing, unidentified wrestler, injury, Israel name association, Peniel/Penuel forms, and later Israelite food practice. Abraham is identified as Jacob’s grandfather while the ancestral prayer formula is disclosed.
- The approach to Esau keeps the two wives, two enslaved women, eleven children, four hundred men, seven bows, Esau’s initiative, kiss, embrace, and mutual weeping. The dotted Hebrew word for “kissed” is noted without overriding the received wording.
- Jacob calls his gift a “blessing,” says he has “everything,” and compares Esau’s face with God’s face. These connections to chapters 27 and 32 remain audible without asserting that the gift formally returns the earlier blessing. Esau’s travel offer, Jacob’s stated destination of Seir, the move to Succoth, “safely” or Salem, the qesitah, and El-Elohe-Israel receive concise notes where needed.
- Genesis 34 names Shechem’s rape of Dinah directly. Dinah’s ordinary visit is not made the cause of his violence; his later attachment does not erase it; and her absent voice is not filled with an invented response. Defilement names Shechem’s act, not Dinah’s guilt.
- The chapter also preserves the brothers’ deceit, the misuse of circumcision as a trap, the city leaders’ economic appeal, Simeon and Levi’s killing of every male, the wider plunder, and the captivity of women and children. Dinah’s violation does not hide the collective harm inflicted on the city. Jacob’s fear-centered response and his sons’ unanswered final question both remain unresolved.
- Genesis 35 keeps the foreign gods, ritual preparation, terebinth, terror from God, return to Bethel, Deborah’s death, reaffirmed name Israel, ancestral promises, Rachel’s fatal labor, both names given to Benjamin, Reuben’s act with Bilhah, and Isaac’s death. Bilhah’s voice and consent are not invented.
- The clause “Jacob had twelve sons,” present in Hebrew 35:22 but absent from the earlier Fluent wording, has been restored before the list. Bilhah and Zilpah remain enslaved women. The summary that the sons were born in Paddan-aram remains despite its tension with the immediately preceding location of Benjamin’s birth.
- Genesis 36 was checked name by name and relationship by relationship. The wife lists’ differences from 26:34 and 28:9, the Jeush written/read form, Korah’s placement in two lines, the uncertain `yemim`, the non-dynastic king succession, and Hadar/Hadad variation are disclosed rather than harmonized. Horite families and Edomite rulers are retained as part of Genesis’s world, not treated as disposable names.

The authoring model reread every source verse and the assembled English and made local corrections, including removing an unsupported “other” from the identity of the sons in 34:27, restoring the repeated city-gate language in 34:24, and removing an added chronology marker from 36:20. This is a self-check, not an independent editorial review or a human reading test.

The [NET translators’ notes for Genesis 32](https://www.biblegateway.com/passage/?search=Genesis+32&version=NET), [Genesis 33](https://www.biblegateway.com/passage/?search=Genesis+33&version=NET), [Genesis 34](https://www.biblegateway.com/passage/?search=Genesis+34&version=NET), [Genesis 35](https://www.biblegateway.com/passage/?search=Genesis+35&version=NET), and [Genesis 36](https://www.biblegateway.com/passage/?search=Genesis+36&version=NET) were recorded as comparison aids for difficult readings. They are not Fluent’s source text and do not govern its wording.

## Verification and limits

The [verification record](verification.json) contains the audit outputs and focused assertions. [Before](overlap-before.json) and [after](overlap-after.json) reports measure surface resemblance to TSW; their results are triage, not a quality gate.

Chapter YAML retains `status: QA_PASSED` qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. Prior approval and old source bindings are superseded only for chapters 32–36. Earlier revision batches and historical records remain available. The legacy `chapter_reviews_complete` field counts completed draft passes, not scholarly approval.

TSW, Genesis 1–31, Genesis 37–50, James, and separate Companion content are unchanged. Companion chapter hashes and any exact quotations from Genesis 32–36 must be checked against this ledger before later installation. No Companion rewrite or public deployment occurred.

The cumulative checkpoint preserves exact Git history from base `984d86f25ff0c4e46b566e063fc0b86a8ed64eb7`. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried. Drafting and durable checkpoints can continue without it.
