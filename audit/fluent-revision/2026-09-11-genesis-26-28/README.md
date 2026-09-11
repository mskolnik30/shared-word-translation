# Fluent source-based revision: Genesis 26–28

September 11, 2026. This connected batch completes 103 verses in three chapters, from Isaac’s residence in Gerar through Jacob’s vow at Bethel. Genesis 1–28 and James 1–5 now have draft revision coverage: 904 verses in 33 chapters. Genesis 29–36 remains next; the original 26–36 work item was divided at Jacob’s departure and dream to allow focused review and a complete-chapter checkpoint.

## Source and method

Every verse was read from the verified [Open Scriptures Hebrew Bible Genesis XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Gen.xml), commit `6a5db284c715c18b239422e57bb89684e6a19f00`, blob `dcc8be362134981d3054e9b64d3a465d08492a33`. The 1,533-record source file matched both its Git blob and SHA-256. The ledger hashes exact original XML verse substrings, including written/read notes in 27:3 and 27:29. Displayed Hebrew used for reading is not substituted for the original bytes in those bindings.

The [verse ledger](genesis-verse-review.json) records all 103 source-specific decisions, before/after wording, TSW comparators, source bindings, and editorial F0–F3 classifications. TSW was used as a comparator, not an English base. Of these decisions, one retains the existing wording (26:23), 80 address syntax or idiom, and 22 flag consequential interpretive choices. There is no minimum-change requirement. A changed sentence is not thereby certified as a better or independent translation.

## Focused editorial pass

- Promises retain descendants, blessing, land, the stranger’s residence, and God’s presence. The two blessing constructions follow the earlier draft’s choices in 12:3 and 22:18, with alternatives disclosed.
- Isaac’s growing wealth and the repeated well disputes remain concrete. Esek, Sitnah, Rehoboth, Shibah, and Beersheba are retained with concise naming notes. The visitors’ claims of good treatment are not turned into a narrator’s endorsement.
- Rebekah’s retelling is not harmonized with Isaac’s original words: the LORD’s presence occurs in her report. Jacob’s direct false identification and invocation of “your God” remain explicit.
- The recurring nefesh blessing idiom is rendered “heartfelt blessing,” with its literal form and interpretation noted. Esau’s firstborn claim, repeated pleas, bitter cry, and weeping remain distinct. Birthright and blessing are not conflated.
- Both blessings retain poetic lineation inside verse paragraphs. Earth’s richness, heaven’s dew, grain, new wine, sword, and yoke remain concrete images.
- The separative reading in 27:39, the difficult verb in 27:40, the stairway/ladder in 28:12, the pronoun in 28:13, and the vow boundary in 28:21 remain provisional decisions with brief notes.
- The stone in 28:11 is placed by Jacob’s head; a pillow is not asserted. The LORD’s position is translated “above it,” with “beside him” retained as an alternative. Abraham’s actual relationship to Jacob is made explicit as grandfather.
- Numbers and relationships were checked: hundredfold yield; forty-year-old Esau; two young goats; few days; twice; tenth; all four directions; both parents; all three named wives in these chapters; and the Bethuel–Laban–Rebekah relationships. Names in 36:2–3 were checked but not harmonized into this batch.

The authoring model also reread the assembled English chapters and made local corrections, including removing an added act of overhearing from 28:6 and removing an unintended endpoint implication from 28:3. This is a self-check, not an independent editorial review or a human reading test.

The [NET translators’ notes for Genesis 27](https://www.biblegateway.com/passage/?search=Genesis+27&version=NET) were consulted for the written/read form in 27:3, the nefesh idiom, and competing interpretations of the preposition in 27:39. The [Genesis 28 notes](https://www.biblegateway.com/passage/?search=Genesis+28&version=NET) were consulted for the stone’s location and the rare stairway noun. They are comparison aids, not Fluent’s source text. No unstated motives, historical fulfillment claims, or architectural reconstruction were adopted from commentary.

## Verification and limits

The [verification record](verification.json) contains the actual audit outputs and focused assertions. [Before](overlap-before.json) and [after](overlap-after.json) overlap reports measure surface resemblance to TSW; their results are triage, not evidence of fidelity or independent authorship.

Chapter YAML retains `status: QA_PASSED` qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. Prior approval and old source bindings are superseded only for chapters 26–28. Earlier revision batches and historical records remain available. The legacy `chapter_reviews_complete` field counts completed draft passes, not scholarly approval; an explicit scope qualifier now says so.

TSW, Genesis 1–25, Genesis 29–50, James, and the separate Companion content are unchanged. Companion chapter hashes and any exact quotations from Genesis 26–28 must be checked against this ledger before later installation. No Companion rewrite or public deployment occurred.

The canonical checkpoint preserves the exact cumulative Git history from base `984d86f25ff0c4e46b566e063fc0b86a8ed64eb7`. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried. Drafting and saved checkpoints can continue without it.
