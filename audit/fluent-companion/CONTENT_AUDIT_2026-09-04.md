# Fluent Companion complete-corpus content audit — 2026-09-06

## Result

**PASS. All 1,189 canonical Fluent chapters have exactly one source-bound
Companion candidate. The audit reports 0 errors and 0 warnings. Expanded Rounds
1–4 are human-approved; later human gates remain pending, and publication remains
blocked.**

## Audited scope

- 1,189 chapter companion records
- 66 canonical book introductions
- 95 preserved hand-shaped chapter records
- 1,094 source-derived generated chapter records requiring human editorial review
- 920,624 chapter-companion words including front matter
- 23,819 book-introduction words including front matter
- Canonical book representation: 66 of 66 books
- Old Testament chapter coverage: 929 of 929 chapters
- New Testament chapter coverage: 260 of 260 chapters
- Complete-corpus chapter coverage: 1,189 of 1,189 chapters
- Missing or duplicate chapter companions: 0
- Candidate status: text complete; automated audit passed; human review pending

## Passing checks

| Check | Result |
|---|---|
| Required template headings | Pass |
| Manifest coverage | Pass |
| Exact QA-passed source existence | Pass |
| SHA-256 source locks | Pass |
| Chapter-path citation bounds | Pass |
| Unpublished status | Pass |
| Placeholder and raw source-markup leakage | Pass |
| Explicit attribution of imported context notes | Pass |
| Scripture-first reading hierarchy | Pass |
| Generated cross-reference non-displacement rule | Pass |
| Forced theological-resolution language | Pass |
| Exact long-paragraph duplication | Pass |
| Deterministic unsafe-phrase scan | Pass |
| Generated formation-safeguard requirement | Pass |
| Exact complete-corpus coverage | Pass |
| JSON syntax | Pass |
| Python syntax | Pass |
| Git whitespace check | Pass |
| Existing translation-family audit | Pass |
| Existing TSW Study Companion batch audit | Pass |

## Corrections made during audit

- Corrected the Psalm 13 title/metadata singular-plural mismatch.
- Corrected one transcribed Jonah 3 source-lock digest and reran the exact binding audit.
- Imported and normalized the mature Philippians pilot without weakening its richer chapter structure.
- Added source-locked representative coverage for 30 books in Waves 03–05.
- Added source-locked representative coverage for the final 21 books in Waves 06–07.
- Added batch-specific high-risk human-review registers.
- Superseded the representative-book coverage gate with an exact 1,189-chapter corpus gate.
- Added 12 hand-shaped short-prophet chapters and 1,094 source-derived generated chapter records.
- Bound every chapter record to its exact Fluent source path and SHA-256 digest.
- Expanded CI so both content and exact complete-corpus coverage audits run on every relevant change.
- Corrected the Psalm 119 three-digit verse-range parser and removed repeated headingless-chapter fallback prose.
- Reworked all 298 one-section or headingless generated chapters so prompts no
  longer invent movement between identical headings.
- Corrected capitalization, doubled punctuation, Psalm display titles, and
  internal verse-label or Markdown leakage across generated reader prose.
- Removed reader-facing repository paths and technical source-apparatus labels.
- Added an exact generated Chapter Path versus bound-source structure check and
  permanent regression rules for the corrected editorial defects.
- Explicitly attributed every imported generated-context observation to its
  translation note and verse, preventing note interpretation from appearing as
  unattributed historical fact.
- Qualified the reconstructed Corinth setting in the First Thessalonians guide
  and placed the Psalms guide's superscription caution beside Psalm 122's
  categorical source note.
- Required every Companion's reading step to direct readers to the Fluent
  Scripture text and required generated scriptural connections to deepen rather
  than replace the chapter's own voice.
- Added a permanent regression check for forced single-interpretation and
  theological-closure language.
- Added an agency, trauma-awareness, and non-coercion safeguard to all 1,094
  generated prayer-and-practice sections and made its presence an audit
  requirement.
- Expanded the unsafe-phrase regression scan for coercive forgiveness or
  reconciliation, remaining in danger, spiritualized rejection of care,
  victim-blaming, imitative violence, and endorsement of slavery.

## Human gates still open

- Chapter-specific depth
- Plain-language reader testing
- Accessibility and reader integration
- Final publication approval on an exact release commit

## Command

Run from the repository root:

```bash
python3 tools/audit_fluent_companion.py
python3 tools/audit_fluent_companion_coverage.py
```

The content audit exits nonzero if any deterministic check fails. The coverage
audit exits nonzero unless all 1,189 canonical Fluent chapter sources have
exactly one Companion and all 66 book introductions exist. A passing result
never authorizes publication.
