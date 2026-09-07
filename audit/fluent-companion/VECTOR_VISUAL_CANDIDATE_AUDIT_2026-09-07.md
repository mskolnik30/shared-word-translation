# Fluent Companion vector visual candidate audit

Date: 2026-09-07

Candidate set: `biblical-world-vectors-2026-09-07`

Publication status: **blocked**

## Result

- Registered shared visual requests: 68
- Requests suitable for deterministic vector treatment: 65
- SVG candidates generated: 65
- Geographic coordinate maps: 11
- Interpretive diagrams, uncertainty maps, reconstruction schematics, and symbolic treatments: 54
- Sourced raster requests deferred: 3
- Missing vector requests: 0
- Duplicate SVG byte content: 0
- XML/accessibility/manifest/hash errors: 0
- Rendered elements outside the 1200 × 800 view box: 0

## Corrections made during render review

The first render pass exposed collisions between wrapped headings and primary
text citations, overflow in dense four-step diagrams, and overlapping labels
on close geographic points. The shared renderer was revised to:

- calculate heading and citation positions from wrapped line count;
- use smaller, consistently wrapped node text;
- enlarge diagram cards without colliding with cautions;
- replace labels plotted directly over map points with numbered markers and a
  separate legend; and
- retain a visible schematic/unpublished disclosure on every candidate.

High-risk samples re-rendered after correction included Job, Jude, Ephesians,
Philippi, Jericho/Bethel/Ai, and the Martha/Mary household schematic.

## Scholarly controls

- Every vector is bound to one registered request and its claim label.
- Every vector identifies its primary biblical texts.
- Coordinate maps cite external place or archaeology sources using HTTPS.
- Disputed and representative locations are labeled explicitly.
- No ancient border is reconstructed.
- No route is drawn where the text or evidence does not establish one.
- The low-table Martha scene is replaced by a relational schematic that states
  the house, furniture, meal, and seating are not described.
- The Corinthian assembly and Bethlehem threshing-floor requests are likewise
  rendered as narrative/relational schematics rather than invented documentary
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
