# Church Commons Bible Reader: Translation Architecture v1

## Outcome

The Church Commons Bible Reader should become a translation-aware reader for The Shared Word Project. Readers should be able to move between TSW and Fluent without losing their book, chapter, or verse range. Existing TSW embeds and links must continue to work.

This document is the implementation contract for the WordPress reader. The reader plugin itself is maintained outside this repository and must be audited before code changes begin.

## Canonical data contract

The reader must load translation definitions from `translations/registry.json` in the mirrored repository. It must not hard-code public labels, root paths, or coverage in multiple places.

The initial identifiers are:

- `tsw` → files under `books/`
- `fluent` → files under `translations/fluent/`

Translation IDs are lowercase, stable public identifiers. Front-matter IDs remain `TSW` and `FLUENT`.

Until the two-translation reader passes staging and production QA, `tsw` remains the registry default. After the rollout is stable, Church Commons may deliberately change the default for new general reader sessions to `fluent`. Existing links and embeds must never change meaning when the default changes.

## Resolution and safety

Every passage request resolves this tuple:

`translation + testament + book slug + chapter + optional verse range`

The resolver must:

1. accept only translation IDs present in the registry;
2. resolve books through the existing canonical book map, not raw user paths;
3. require integer chapters within the canonical range;
4. parse verse selections against labels found in the selected chapter;
5. build file paths from trusted registry and book-map values;
6. reject traversal characters and never append unchecked shortcode or URL input to a filesystem path;
7. return an accessible “passage unavailable” state rather than exposing server paths or PHP warnings.

Both translation trees currently use the same testament, book-directory, and chapter-file conventions. The structural audit must pass before deployment.

The registry also declares the small number of source-driven public verse-label differences between editions. When a reader switches to a translation in which a requested public verse is not present, the reader must preserve the reference and explain that the verse is not present in that translation's source edition. It must not silently substitute an adjacent verse, renumber the passage, or fall back to the other translation.

## Public URL behavior

Translation choice must be shareable. Use the stable query parameter:

`?translation=fluent`

A switch must preserve the current book, chapter, and verse range. A copied URL must reopen the same passage and translation in a new browser.

Selection precedence for an interactive reader:

1. explicit translation in the current URL or shortcode;
2. the reader's remembered translation preference;
3. the registry `site_default`.

The preference may be stored locally in the browser. It must not overwrite an explicit link or author-selected embed.

## Shortcodes and embeds

Introduce a general shortcode:

```text
[bible book="philippians" chapter="1" translation="fluent"]
```

Requirements:

- `translation` accepts a registry ID.
- An omitted translation follows the selection precedence appropriate to the embedding context.
- The existing `[tsw]` shortcode remains supported as a permanent compatibility alias with translation fixed to `tsw`.
- Existing `[tsw]` content must not begin following a site-wide default.
- Verse and range attributes already supported by the reader must behave identically for both translations.

## Where a selector belongs

| Context | Behavior |
| --- | --- |
| Main Bible Reader | Visible TSW/Fluent selector; preserve the complete reference when switching |
| Interactive passage block | Visible selector unless the author intentionally locks the translation |
| Worship, presenter, course, and resource creation tools | Creator selects the translation when inserting a passage |
| Fixed quotation in an article or lesson | Preserve the author's chosen wording; label the translation; link the reference to the reader |
| Legacy `[tsw]` embed | Keep TSW fixed; no silent migration |

“Everywhere a Bible passage appears” therefore means every interactive passage surface becomes translation-aware, while authored quotations retain editorial integrity.

## Interface language

The selector should identify both name and posture without ranking readers:

- **TSW · Close Reading**
- **Fluent · Natural Reading**

An adjacent help link should lead to the translation comparison page. Avoid “literal vs. easy,” “scholarly vs. devotional,” or “advanced vs. beginner.”

## Rendering requirements

The current renderer's behavior must remain intact across both translations:

- headings appear only when their selected verses appear;
- verse ranges do not leave unrelated chapter headings behind;
- poetry lineation and indentation are preserved;
- notes and vocabulary remain anchored to the correct public verse labels;
- skipped, bridged, or lettered verse labels are handled without renumbering;
- registry-declared source-edition gaps produce an explanatory unavailable state rather than the wrong verse;
- keyboard use, focus state, screen-reader labels, and contrast meet the site's accessibility standard;
- the selector does not cause a full-reference reset.

## Pilot passages

Test a compact set that exercises different forms and reader behavior:

- Genesis 1 — structured narrative
- Psalm 13 — poetry and lament
- Mark 1 — narrative and headings
- Philippians 1–4 — complete short book and letters
- Romans 8 — sustained argument
- Revelation 21 — imagery and poetry-like form

For each pilot, test a full chapter, a single verse, a multi-verse range, notes, vocabulary, switching, copying a URL, reload persistence, mobile layout, and keyboard navigation.

## Acceptance criteria

The first release is ready when:

- `python tools/audit_translation_family.py` passes on the deployed corpus;
- both translations render every pilot reference;
- switching never changes the reference;
- copied URLs reproduce the selected translation;
- legacy `[tsw]` embeds remain unchanged;
- selected ranges display no unrelated headings, notes, or vocabulary;
- missing or invalid input fails safely;
- the selector works on mobile and by keyboard;
- caches do not mix TSW and Fluent output for the same reference;
- the translation comparison, TSW, and Fluent landing pages are published.

## Rollout sequence

1. Mirror the repository with `translations/registry.json` and both complete corpora.
2. Obtain and archive the current WordPress Bible Reader plugin source.
3. Map all shortcode, URL, caching, rendering, and content-insertion entry points.
4. Implement the registry-backed resolver and compatibility alias.
5. Deploy the pilot passages to staging.
6. Fix range, heading, poetry, notes, vocabulary, accessibility, and cache issues.
7. Publish the translation-family landing pages.
8. Release the reader selector on the main Bible Reader.
9. Extend translation selection to other interactive Church Commons passage surfaces.
10. Review evidence before changing the default for new sessions.
