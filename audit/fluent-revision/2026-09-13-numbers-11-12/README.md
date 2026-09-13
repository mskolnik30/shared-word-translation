# Numbers 11–12: source-based Fluent draft

All 51 verses (35 + 16) received independent source-based drafting and a verse-specific rationale with before/after wording, comparator and exact source bindings. The connected reading voice serves biblical fluency through clear speakers, recurring vocabulary, preserved images and selective notes. Independent editorial review and reader testing remain pending.

## Source and method

Every selected Hebrew verse was read before drafting from [OSHB Numbers at the pinned commit](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Num.xml), Git blob `2e7252db3bd33d510d2361a8b5016ac680b27dbb`, SHA-256 `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`. Public numbering aligns directly in this batch. Exact original XML substring hashes include the written/read forms at 12:3 and the annotation at 12:9. No normalized substitute is hashed.

[NET Numbers 11](https://www.biblegateway.com/passage/?search=Numbers+11&version=NET) and [NET Numbers 12](https://www.biblegateway.com/passage/?search=Numbers+12&version=NET) supplied supplemental lexical and grammatical comparison after the Hebrew reading. All 51 TSW comparators were read after drafting; English comparators did not provide a rewriting template.

## Editorial decisions

- Complaint, fire, craving and plague retain their force. The food list and manna preparation remain complete; the uncertain taste expression has a restrained note. “Rabble” preserves the pejorative expression without inventing an ethnic identification.
- Moses’ exhaustion, accusations and plea for death remain explicit. His conceiving, giving birth and foster-father images are preserved together. The burden of carrying the people links his complaint with the elders’ commission.
- Seventy elders, Eldad and Medad, and registration remain as narrated without deciding whether the total was seventy or seventy-two. The elders did not prophesy again in the main rendering; the alternate ancient understanding “did not cease” is noted. Joshua’s youth and the alternative chosen-men reading receive a short note.
- All day counts and the six hundred thousand on foot remain exact. The LORD’s short-hand question retains its ancient image. Spirit and wind share a vocabulary connection. Quail extent, two-cubit elevation and the least collector’s ten homers remain distinct; the height-versus-depth question is acknowledged.
- Miriam and Aaron both speak against Moses. Both Cushite designations remain, without identifying the unnamed woman as Zipporah or inventing a second marriage chronology. The written/read forms behind “humble” remain in the source record.
- The vision/dream contrast, trusted servant, mouth-to-mouth speech, riddles and the LORD’s form remain poetic lines inside their verse paragraphs. Generic prophetic language is inclusive; specifically named people retain their identities.
- Miriam’s snowlike skin condition is not confidently equated with a modern diagnosis. The stillborn-child comparison, flesh half eaten away, both pleas in Moses’ prayer, the hypothetical spit/shame image and seven-day exclusion remain explicit. The narrative does not supply an exact moment of healing or explain why only Miriam was stricken.

All 51 verses changed: 19 F2 and 32 F3. No change quota was used. Before comparison: 41 identical and 10 nearly identical verses; after comparison: zero identical and two nearly identical verses. Automated overlap is triage, not proof of fidelity, independent authorship or comprehension.

## Verification and continuation

`verify_batch.py` passed all 36 cumulative verse-ledger audits, source identity and byte bindings, verse coverage and formatting, targeted names/numbers/ambiguity checks, the translation-family audit and `git diff --check`. `verification.json` records the evidence; `overlap-before-after.json` records comparison results. Poetic lineation is checked in chapter files, since the ledger normalizes whitespace for comparison.

Cumulative draft coverage is 4,184 verses across 134 chapters: James, Genesis, Exodus, Leviticus and Numbers 1–12. These structural checks and authoring self-checks do not constitute independent scholarly review. Chapters retain structural `QA_PASSED`, editorial `REVIEW_PENDING` and `publication_allowed: false`.

Only Numbers 11–12 supersede earlier wording’s approvals and bindings. Historical provenance, earlier batches, TSW and unrelated work remain intact. Companion quotations and bindings for these chapters require later checking; the separate Companion branch and public deployment remain untouched. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried.

Next: Numbers 13–14, the scouts, their reports, the people’s response and wilderness judgment. Recover the latest cumulative checkpoint and continue without routine approval pauses.
