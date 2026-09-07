# Shared Biblical World

This layer stores reusable people, places, historical settings, maps, timelines, artifacts, and images for both Fluent and TSW companions.

Companions reference stable IDs from `registry.json`; they do not copy the same biography, map, or image into translation-specific folders. A companion may frame a shared item differently, but the underlying identity, provenance, caption facts, rights, and uncertainty labels remain shared.

## Visual evidence labels

Every visual must be identified as one of:

- archaeological photograph;
- artifact;
- geographic map;
- schematic map;
- evidence-based reconstruction;
- interpretive orientation image; or
- symbolic art.

Maps must separate established, probable, possible, disputed, and unknown claims. Where scale matters, the preferred set is far view, regional view, and close view.

## Publication requirements for visuals

A requested visual is not a published visual. Every visual remains blocked until its shared record includes:

- creator or responsible organization;
- original source URL;
- license or other permission basis;
- an explicit rights-verification result;
- one of the approved visual classes above;
- an evidence label: established, probable, possible, disputed, unknown, or interpretive;
- a factual caption that distinguishes evidence from reconstruction;
- alternative text that communicates the visual's purpose; and
- publication status marked `ready`.

Generated or commissioned art must be labeled as interpretive, symbolic, schematic, or reconstructed rather than documentary. A companion dossier may be published without its requested visuals; it must not embed a placeholder or unverified image while those visual records remain blocked.

## Scholarly visual gate

Run `python3 tools/audit_biblical_world_visual_plan.py` from the repository root
to verify the request structure and publication controls. A passing machine
audit does not establish historical accuracy, geographic accuracy, rights, or
visual quality. Those require the documented specialist and human review gates.

The binding red-team controls are recorded in
`audit/fluent-companion/VISUAL_SCHOLARLY_RED_TEAM_RECOVERY_2026-09-07.md`.

## Vector candidates

The deterministic SVG candidate set is stored under
`candidates/vectors/`. Its manifest binds every file to the shared visual
request, Bible passages, source URLs where geographic coordinates are used,
alternative text, SHA-256 digest, rights basis, and open human gates.

The geographic candidates use GSHHG physical coastline and river data through
Basemap, with modern geography shown only for orientation. They do not infer
ancient borders or undocumented travel routes. Location claims remain tied to
the place-specific sources listed in the manifest. Reader-facing labels use
plain language; technical review terminology belongs in the manifest and audit
records rather than in the published visual.

Regenerating the maps requires `basemap==2.0.0` (including its
`basemap_data==2.0.0` dependency). The committed SVGs and their audits do not
require Basemap at review or publication time.

Run `python3 tools/audit_biblical_world_vector_candidates.py` to verify this
candidate set. The manifest and review gallery keep every file explicitly
publication-blocked; a passing audit does not constitute visual or scholarly
approval.

The 76-image book-author/key-person profile program is defined in
`profiles/plan.json`. It assigns different treatments to named figures,
anonymous works, composite books, layered prophetic books, disputed
attributions, and pseudonymous voices. Run
`python3 tools/audit_biblical_profile_plan.py` before generating or integrating
any profile image.

Fourteen checksum-bound raster pilot candidates are stored under
`profiles/candidates/`. They cover all ten named-person pilot records plus
Genesis, Isaiah, Hebrews, and one shared four-Gospel authorship-awareness
editorial (17 of the 76 plan records). Every file is labeled as interpretive,
remains blocked, and still requires scholarly, visual, and rights review.
Run `python3 tools/audit_biblical_profile_candidates.py` to verify the files,
hashes, plan bindings, disclosures, and gates.

Open `candidates/vectors/review-gallery.html` locally to review every vector
candidate together with its primary texts, alternative text, sources, and
publication status.

Open `profiles/candidates/review-gallery.html` locally to review the raster
pilot candidates, captions, alternative text, red-team notes, sources, exact
generation prompts, and SHA-256 bindings. The gallery is a review surface, not
a publication package.
