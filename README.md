# The Shared Word Project (Provisional)

The Shared Word Project is an ongoing translation project of the Christian Scriptures. It currently includes two complete, complementary English translations:

- **The Shared Word Translation (TSW) — Close Reading:** for close reading, preaching, study, and shared discernment.
- **Fluent Translation — Natural Reading:** for daily reading, devotion, teaching, and growing biblical fluency.

Both translations contain all 66 books and 1,189 chapters. They are translated from verified Hebrew, Aramaic, and Greek sources and should be understood as two reading postures within one project—not as “advanced” and “beginner” Bibles.

This repository contains the canonical source files for both translations. See [TRANSLATION_FAMILY.md](TRANSLATION_FAMILY.md) for how they relate, [TRANSLATION_PHILOSOPHY.md](TRANSLATION_PHILOSOPHY.md) for TSW, and [FLUENT_TRANSLATION_PHILOSOPHY.md](FLUENT_TRANSLATION_PHILOSOPHY.md) for Fluent.

## Repository layout

- `books/` — canonical TSW chapter files
- `translations/fluent/` — canonical Fluent chapter files
- `translations/registry.json` — machine-readable translation definitions for consumers
- `companions/` — translation-affiliated public reading and study layers
- `resources/biblical-world/` — shared people, places, contexts, maps, timelines, artifacts, and images
- `audit/exegetical-core/fluent-production/` — Fluent review records and source attribution
- `tools/audit_translation_family.py` — structural parity and front-matter audit
- `tools/audit_companion_batch.py` — structural and publication-gate audit for companion batches

## Deploying to Church Commons (WordPress)

GitHub is the single source of truth. WordPress renders a mirrored copy.

**Server mirror location (do not edit these files directly):**
- `wp-content/uploads/tsw-repo/`

**Update workflow**
1. GitHub → Code → Download ZIP (main)
2. Unzip locally
3. Upload the *contents* of the repo folder, including `books/`, `translations/`, and the project documentation, into:
   - `wp-content/uploads/tsw-repo/`
   Replace existing files as needed.
4. In WordPress, clear cache.

Do not edit the mirrored files in WordPress directly. GitHub remains the single source of truth.

**Current legacy shortcode**

- `[tsw book="philippians" chapter="1"]`

**Translation-aware reader contract**

- `[bible book="philippians" chapter="1" translation="fluent"]`
- Existing `[tsw]` shortcodes must remain supported and must continue to resolve to TSW.
- See [docs/BIBLE_READER_TRANSLATION_ARCHITECTURE.md](docs/BIBLE_READER_TRANSLATION_ARCHITECTURE.md) before updating the Church Commons reader plugin.

## Verify both corpora

Run the audit before a release or WordPress mirror update:

```bash
python tools/audit_translation_family.py
```

The audit verifies book/chapter parity, required front matter, translation identifiers, Fluent QA status, and public verse-label parity.

Draft TSW Study Companion batches have a separate audit. Passing it confirms structure, shared-world references, source-ledger presence, and a blocking human-review gate; it does not approve the theology or exegesis:

```bash
python tools/audit_companion_batch.py companions/tsw-study/manifests/batch01.json
```
