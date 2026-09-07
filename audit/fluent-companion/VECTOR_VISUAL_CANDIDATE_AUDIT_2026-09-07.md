# Fluent Companion vector visual candidate audit

Date: 2026-09-07

Candidate set: `biblical-world-reader-visuals-2026-09-07-v2`

Publication status: **blocked**

## Result

- Registered shared visual requests: 68
- Requests suitable for deterministic vector treatment: 65
- SVG candidates generated: 65
- Geographic orientation maps with physical baselayers: 11
- Reader explanation graphics: 54
- Sourced raster requests deferred: 3
- Missing vector requests: 0
- Duplicate SVG byte content: 0
- XML/accessibility/manifest/hash errors: 0
- Review-gallery references: 65 of 65
- Independent Inkscape renders: 65 of 65
- Rendered elements outside the 1200 × 800 view box: 0

## Corrections made during render review

The first render pass exposed collisions between wrapped headings and Bible
passage citations, overflow in dense four-step diagrams, and overlapping labels
on close geographic points. The shared renderer was revised to:

- calculate heading and citation positions from wrapped line count;
- use smaller, consistently wrapped node text;
- replace the dense four-card treatment with an open two-by-two reading guide;
- remove arrows that falsely implied a time sequence in comparisons and topic
  groupings;
- replace labels plotted directly over map points with numbered markers and a
  separate legend; and
- keep publication controls in the manifest and review gallery rather than
  placing internal production warnings inside reader-facing art.

The second render pass followed direct reader review. The coordinate-grid
placeholders were rejected because they did not show recognizable geography.
All eleven maps now include:

- land and water shapes;
- modern coastlines and major rivers from GSHHG through Basemap;
- a north arrow and scale bar;
- plain-language certainty labels;
- a concise explanation of what the map does and does not claim; and
- no invented ancient borders or travel routes.

Reader-facing jargon was also removed or explained. Labels such as “Primary
texts,” “Reading caution,” “reception history,” “christological,” “regnal
dates,” and “lexical-history schematic” no longer appear in the generated
visuals or alternative text.

High-risk samples re-rendered after correction included Job, Jude, Ephesians,
Philippi, Jericho/Bethel/Ai, and the Martha/Mary household guide.

## Scholarly controls

- Every vector is bound to one registered request and its claim label.
- Every vector identifies the Bible passages it accompanies.
- Geographic maps cite external place or archaeology sources using HTTPS.
- Geographic maps identify GSHHG as the physical coastline and river source.
- Disputed and representative locations are labeled explicitly.
- No ancient border is reconstructed.
- No route is drawn where the text or evidence does not establish one.
- The low-table Martha scene is replaced by a text-based guide that states
  the house, furniture, meal, and seating are not described.
- The Corinthian assembly and Bethlehem threshing-floor requests are likewise
  rendered as text-based guides rather than invented documentary
  rooms.
- Job, Jude, Ephesians, 2 Thessalonians, and 2 Timothy use the corrected
  attribution and textual wording from the red-team review.

## Remaining gates

The SVG set has not received final geographic, archaeological, biblical-
studies, accessibility, design, or publication approval. Machine validation
establishes internal consistency and catches recurrent production defects; it
does not establish that every scholarly judgment is correct.

The three deferred raster requests are:

1. Jericho / Tell es-Sultan archaeological photograph.
2. Caesarea Philippi archaeological photograph.
3. Deuteronomic-law comparative artifact image.

These require source-specific rights records and captions before integration.

## Audit commands

```bash
python3 tools/audit_biblical_world_visual_plan.py
python3 tools/audit_biblical_world_vector_candidates.py
python3 tools/audit_biblical_profile_plan.py
```

## Decision

**VECTOR CANDIDATE SET COMPLETE; HUMAN REVIEW REQUIRED; PUBLICATION BLOCKED.**
