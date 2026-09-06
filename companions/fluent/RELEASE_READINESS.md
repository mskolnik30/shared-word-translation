# Fluent Companion release readiness

This branch begins complete chapter-by-chapter production. It does not authorize publication.

## Completion requirement

- 66 source-locked book introductions.
- One substantive, source-locked Companion for every Fluent chapter file.
- Repository inventory: 1,189 chapters (929 Old Testament; 260 New Testament).
- Current candidate coverage: 1,189 of 1,189 chapters.
- Remaining chapter files to create: 0.
- Complete-corpus audit: PASS on 2026-09-06 with 0 errors and 0 warnings.

The earlier representative-coverage definition has been withdrawn. The full
chapter corpus is now present and passes the automated coverage gate. Expanded
human-review Rounds 1–4 are approved, but the consolidated depth, clarity, and
accessibility review and final publication gate remain pending.
This is an unpublished candidate, not an approved or live release.

## Completed in the production draft

- Complete book introductions for Jonah, Ruth, James, and 1 John.
- Complete chapter companions for all 18 chapters in those books.
- Calibration companions for Genesis 1, Psalm 13, Mark 1, Romans 8, and Revelation 21.
- Complete book introductions and chapter companions for Obadiah, Philemon, 2 John, 3 John, and Jude.
- Exact bindings to QA-passed Fluent chapter sources.
- Structural, binding, placeholder, duplication, and safety-language audit tooling.
- A required agency, trauma-awareness, and non-coercion safeguard in every
  source-derived generated prayer-and-practice section.
- Explicit unpublished and human-review-required metadata on every record.

## Required before a live push

- [ ] Content editor approves every production-wave and calibration record.
- [ ] Translation editor verifies each summary and citation against its bound Fluent chapter.
- [ ] Formation reviewer checks questions, prayer, practices, and safety notes.
- [ ] Accessibility reviewer checks labels, reading order, zoom behavior, and plain-language clarity in the reader.
- [ ] Maps and other factual visuals retain source and uncertainty notes.
- [ ] Reader integration contains no raw Markdown, code tokens, or unresolved placeholders.
- [ ] Mobile and desktop smoke tests pass for all new books and chapters.
- [ ] Final content audit passes on the exact release commit.
- [ ] A human publication approver records approval for the exact release commit.
- [ ] Deployment is initiated only after that approval.

## Human-review and release sequence

1. Review the complete-corpus audit report.
2. Review every generated chapter, prioritizing all high-risk passages and
   replacing baseline prose where chapter-specific depth is needed.
3. Record human decisions in `reviews/complete-corpus-expansion-review.md`.
4. Re-run the audit and build the reader from the approved commit.
5. Perform mobile and desktop smoke tests.
6. Approve and deploy the exact commit; verify the live URL.
