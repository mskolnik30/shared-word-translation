# Bible Reader Companion and Worship Contract

## Product rule

Every Church Commons Scripture surface should use one shared passage component. That component carries four separate decisions:

1. the biblical passage;
2. the translation;
3. optional reading help;
4. the presentation context.

This separation preserves user agency. TSW and Fluent remain biblical translations. Their companions remain optional resources, not alternate Bibles and not mandatory overlays.

## Companion independence

Companions may have a home translation, called `translation_affinity`, but approved companion text may be used with either translation when `cross_translation_use` is true.

When a reader opens TSW Study beside Fluent, the interface should say that wording observations were written alongside TSW. It must not force a translation change. The same rule applies when Fluent Companion is used beside TSW.

The default reading-help state is `none`.

## Worship contexts

| Identifier | Use | Controls |
| --- | --- | --- |
| `reader` | Ordinary Bible reading, formation, articles | Translation visible; companion closed; notes and vocabulary available |
| `worship` | Personal or congregational worship page | Compact translation choice; one quiet companion action; no study toolbar |
| `worship-planning` | Leader preparation | Translation, companion, notes, and vocabulary available |
| `worship-display` | Projection or service display | Scripture plus a small translation label; no interactive help |
| `embed` | Minimal iframe | Existing compact behavior |

No companion opens automatically in `reader` or `worship`. A planning surface may remember a leader's explicitly selected companion. A display surface never renders companion content.

## Compatibility

- Existing `[tsw]`, `[tsw_passage]`, and `[tsw_bible_reader]` interfaces remain fixed to TSW.
- New generic Bible passages default to reader translation choice unless an author deliberately fixes the translation.
- Existing `/bible/read/`, `/bible/embed/`, and `tsw/v1` interfaces remain stable.
- TSW remains the site default unless a later reviewed decision changes it.
- Switching translation preserves passage, companion choice, and context.

## Provider boundary

The Bible Reader owns Scripture rendering and state. Companion providers own their approved entries and metadata. Shared Biblical World owns reusable people, places, historical contexts, maps, timelines, artifacts, and images.

Providers should expose stable IDs, public labels, translation affinity, cross-translation permission, passage ranges, publication state, and structured sections. The reader must reject unpublished text and blocked visual assets.

## Current publication state

- TSW Study Companion: first-edition text approved, 70 dossiers.
- TSW Study unfinished visuals: 50 blocked and excluded.
- Fluent Companion: maintained outside this repository; connect through the provider boundary.
- Shared Biblical World: foundation registry only; publish individual records only after their evidence and rights gates pass.
