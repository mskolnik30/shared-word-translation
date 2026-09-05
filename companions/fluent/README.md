# Fluent Companion

The Fluent Companion helps curious teen and adult readers stay with the biblical text. It provides basic orientation, follows a chapter's movement, traces connections through Scripture, and offers non-coercive questions, prayer, and practice.

It is distinct from the TSW Study Companion. Fluent Companion content supports sustained reading and formation; TSW Study dossiers examine language, contested interpretation, reception, power, and harm in greater depth.

## Public rhythm

Each chapter follows the locked Template 1.0 rhythm:

1. Before You Read — Where You Are, Chapter Path, Watch For
2. Read the Chapter — a pointer to the exact Fluent source, never a duplicate translation
3. After You Read — recall, brief summary, movement, scriptural threads, questions, prayer, and practice
4. Go Deeper — only context and interpretive material needed for responsible reading

## Status contract

All material in this directory is an unpublished candidate until its individual and batch review gates are approved by a human editor. Machine audits may detect structural, binding, duplication, and safety-language problems; they cannot approve theology, formation, accessibility, or publication.

The first-edition build currently contains complete-book candidates for Jonah, Ruth, James, 1 John, and Philippians; the one-chapter books Obadiah, Philemon, 2 John, 3 John, and Jude; five cross-genre calibration chapters; and representative chapters for 30 additional books across Torah, history, wisdom, and the prophets. Canonical coverage is 45 of 66 books, with Waves 06–07 still in production.

## Paths

- `books/<book>/introduction.md` — book-level orientation
- `chapters/<book>/<chapter>.md` — complete-book chapter companions
- `calibration/<book>-<chapter>.md` — cross-genre calibration records
- `reviews/` — batch and human-gate records
- `manifests/` — machine-readable scope and binding records

Run `python3 tools/audit_fluent_companion.py` from the repository root before requesting editorial review.

Run `python3 tools/audit_fluent_companion_coverage.py` to check the 66-book first-edition completion gate. It intentionally fails until every canonical book has both a book guide and at least one chapter companion.
