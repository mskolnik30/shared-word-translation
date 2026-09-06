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

The complete chapter-by-chapter candidate contains a source-locked book introduction for all 66 canonical books and an unpublished Companion record for each of the repository's 1,189 Fluent chapters. The corpus includes 95 hand-shaped chapter records and 1,094 source-derived generated records. Expanded human-review Rounds 1 and 2 are approved; later review gates and publication approval remain pending.

## Paths

- `books/<book>/introduction.md` — book-level orientation
- `chapters/<book>/<chapter>.md` — complete-book chapter companions
- `calibration/<book>-<chapter>.md` — cross-genre calibration records
- `reviews/` — batch and human-gate records
- `manifests/` — machine-readable scope and binding records

Run `python3 tools/audit_fluent_companion.py` from the repository root before requesting editorial review.

Run `python3 tools/audit_fluent_companion_coverage.py` to check the complete-corpus gate. It passes only when every Fluent chapter file has exactly one source-bound Companion record and every canonical book has an introduction. A passing coverage result does not authorize publication.
