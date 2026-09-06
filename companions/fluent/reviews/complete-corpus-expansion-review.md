---
review_record: fluent-companion-complete-corpus-expansion
review_status: PENDING_HUMAN_REVIEW
publication_status: blocked
scope: every Fluent chapter in the 66-book Protestant canon
canonical_chapter_count: 1189
---

# Complete-corpus expansion human review record

The complete chapter-by-chapter production target is the repository's 1,189
Fluent chapter files: 929 Old Testament chapters and 260 New Testament
chapters. The earlier representative-coverage release definition is
superseded.

## Production composition

- 83 previously drafted chapter records.
- 12 additional hand-shaped short-prophet chapter records.
- 1,094 source-derived generated chapter records.
- 1,189 total source-bound chapter records.
- 66 book introductions.

All content remains unpublished. Generated records use each source chapter's
own headings, verse ranges, notes, vocabulary, book position, and neighboring
chapters. Generation does not constitute editorial or publication approval.

## Automated gate

The end-of-corpus audit passed on 2026-09-06:

- Content records: 1,189
- Book introductions: 66
- Old Testament coverage: 929 of 929
- New Testament coverage: 260 of 260
- Errors: 0
- Warnings: 0
- Translation-family, apparatus, and TSW regression audits: PASS

This mechanical pass confirms completeness, structure, exact source bindings,
citation bounds, and the audited safety-language rules. It does not substitute
for the human gates below.

## Expanded Round 1 evidence packet

**Decision state:** READY_FOR_HUMAN_DECISION

**Content-corpus digest:**
`56ab1cd5f555a0b3f632679a436487e8da7f4b0d05d41180c4b4d0b9e3a5b320`

Round 1 evaluates structural integrity, source provenance, chapter specificity,
and reader-facing cleanliness. It does not decide the later historical,
interpretive, formation, accessibility, or publication gates.

The first pass failed and was not advanced for approval. It found:

- 298 single-section chapters whose prompts repeated the same heading as both
  the beginning and end of a supposed movement.
- 416 generated records with improper lowercasing of `Israel`.
- 85 generated Gospel records with improper lowercasing of `Gospel`.
- 829 generated records with doubled vocabulary punctuation.
- Reader-facing repository paths and technical `source apparatus` wording in
  all 1,094 generated records.
- Older apparatus markup leaking labels such as `v03`, bullets, repeated verse
  references, and raw vocabulary delimiters into reader-facing prose.

The generator and audit were then corrected, all 1,094 generated records were
rebuilt, and the full audit returned 0 errors and 0 warnings. The audit now
also verifies every generated Chapter Path against the section ranges in its
bound Fluent source and rejects all recurrence of the defects above.

Cross-genre close reading sampled:

- Genesis 2; Leviticus 19; Numbers 25; Deuteronomy 7
- 2 Kings 25; Job 3; Psalm 119; Ecclesiastes 10
- Isaiah 53; Jeremiah 31
- Matthew 5; Luke 10; Acts 15
- 1 Corinthians 11; 1 Timothy 2
- Revelation 13

The corrected sample preserves the Fluent chapter structure, keeps source-note
uncertainty visible, distinguishes single-section and headingless chapters,
uses `Psalm` for individual psalm titles, and exposes no repository paths or
raw editorial markup to readers.

## Human gates

| Gate | Status | Reviewer | Date | Notes |
|---|---|---|---|---|
| Source fidelity | Pending |  |  | Compare generated descriptions and contextual excerpts with each bound Fluent source. |
| Context and uncertainty | Pending |  |  | Preserve literary form, historical limits, textual uncertainty, and unresolved tension. |
| Theological restraint | Pending |  |  | Confirm the Companion does not displace Scripture or force later synthesis into the chapter. |
| Formation and safety | Pending |  |  | Review agency, non-coercion, trauma awareness, power, violence, gender, and vulnerable readers. |
| Chapter-specific depth | Pending |  |  | Replace or deepen source-derived baseline prose where a chapter needs more than structural orientation. |
| Plain-language clarity | Pending |  |  | Test with curious teen and adult readers. |
| Accessibility and reader integration | Pending |  |  | Verify labels, reading order, reflow, controls, and unavailable-state behavior. |
| Publication approval | Blocked |  |  | Requires all prior gates and approval of an exact release commit. |
