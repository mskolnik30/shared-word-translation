# Fluent Companion release readiness

This branch prepares content for review. It does not authorize publication.

## Completed in the production draft

- Complete book introductions for Jonah, Ruth, James, and 1 John.
- Complete chapter companions for all 18 chapters in those books.
- Calibration companions for Genesis 1, Psalm 13, Mark 1, Romans 8, and Revelation 21.
- Complete book introductions and chapter companions for Obadiah, Philemon, 2 John, 3 John, and Jude.
- Exact bindings to QA-passed Fluent chapter sources.
- Structural, binding, placeholder, duplication, and safety-language audit tooling.
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

## Tomorrow morning sequence

1. Review the audit report and every warning.
2. Sample at least one chapter per book plus all high-risk notes.
3. Record human decisions in `reviews/wave01-review.md`.
4. Re-run the audit and build the reader from the approved commit.
5. Perform mobile and desktop smoke tests.
6. Approve and deploy the exact commit; verify the live URL.
