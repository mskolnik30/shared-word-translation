# Fluent Companion content audit — updated 2026-09-05

## Result

**PASS — automated candidate checks only. Human approval has not been performed, and publication remains blocked.**

## Audited scope

- 83 chapter companion records
- 66 canonical book introductions
- 18 complete-book chapters across Jonah, Ruth, James, and 1 John
- 5 complete one-chapter books: Obadiah, Philemon, 2 John, 3 John, and Jude
- 5 cross-genre calibration chapters: Genesis 1, Psalm 13, Mark 1, Romans 8, and Revelation 21
- 4 mature Philippians pilot chapters
- 51 representative first-edition chapters across Torah, history, wisdom, prophets, Gospels, Acts, and letters
- 56,440 chapter-companion words including front matter
- 23,809 book-introduction words including front matter
- Canonical first-edition coverage: 66 of 66 books; candidate text complete

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
| Exact long-paragraph duplication | Pass |
| Deterministic unsafe-phrase scan | Pass |
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
- Added a canonical coverage audit and batch-specific high-risk human-review registers.

## Human gates still open

- Source fidelity and exegetical judgment
- Historical and cultural context
- Theological restraint and ambiguity
- Formation, trauma awareness, and non-coercion
- Plain-language reader testing
- Accessibility and reader integration
- Final publication approval on an exact release commit

## Command

Run from the repository root:

```bash
python3 tools/audit_fluent_companion.py
python3 tools/audit_fluent_companion_coverage.py
```

The content audit exits nonzero if any deterministic check fails. The coverage audit exits nonzero unless all 66 books are represented. A passing result never authorizes publication.
