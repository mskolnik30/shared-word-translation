# Fluent Companion profile-visual pilot audit

Date: 2026-09-07

Scope: 14 raster candidates covering 17 of the 76 profile-plan records

Publication status: blocked

## Outcome

The pilot is suitable for organized human review, not for publication. The
manifest, files, SHA-256 bindings, dimensions, profile-plan references,
captions, alternative text, prompt records, and required gates pass the machine
audit with zero errors and zero warnings.

This is not a finding that the images are facial reconstructions or that every
material detail has been proved. They are AI-generated interpretive orientation
candidates. Historical-specialist review, visual review, rights review, reader
integration, and final publication approval remain open for every file.

## Pilot inventory

- Ten named-person candidates: Abraham, Sarah, Moses, Ruth, David, Mary of
  Nazareth, Mary Magdalene, Simon Peter, Paul, and Jesus.
- Four authorship-awareness editorials: Genesis, Isaiah, the four canonical
  Gospels, and Hebrews.
- The shared Gospel editorial binds four separate book-plan records, so the
  fourteen files cover seventeen profile-plan records.
- Fifty-nine profile-plan records remain without raster candidates.

## Deep red-team controls applied

### Identity and race

- Named figures are represented with brown West Asian, Judean, Galilean,
  Moabite, or eastern Mediterranean visual cues appropriate to the requested
  setting. Northern-European defaulting is explicitly prohibited.
- These cues describe a plausible regional range; they do not establish an
  individual's exact skin tone, facial structure, hair, or modern racial
  category.
- Captions explicitly state that the portraits are interpretive and not facial
  reconstructions.

### Beauty and idealization

- Sarah and David retain the Bible's explicit appearance language while
  rejecting modern cosmetics, sexualization, age erasure, and heroic styling.
- The other named figures are not beautified merely because they are biblical
  characters.
- Jesus is ordinary, sun-weathered, non-European, plainly dressed, unhaloed,
  and non-cinematic. The Shroud of Turin is explicitly excluded as facial
  evidence.

### Authorship uncertainty

- Genesis is not reduced to a portrait of Moses; anonymous hands and scroll
  materials signal transmission and compilation.
- Isaiah uses three broad historical horizons without claiming that exactly
  three recoverable people wrote the book.
- The Gospel visual avoids presenting traditional names as recoverable author
  portraits. One four-panel asset is linked to four distinct plan records.
- Hebrews leaves the human author's face unseen and includes no Pauline symbol.

### Material culture and pseudo-documentary risk

- The retained authorship editorials use tight, neutral tabletop compositions
  so they do not invent cities, monuments, rooms, or composition events.
- Initial generations with cinematic ancient skylines and overly specific
  architecture were rejected and were not copied into the repository.
- Writing surfaces are blank or indistinct. They must never be treated as
  legible manuscripts, palaeographic evidence, or reproductions of a biblical
  text.
- Reed pens, ink cups, textiles, garments, skin tones, and backgrounds remain
  illustrative. A specialist must still review them before publication.
- No dining-room reconstruction or low meal table is included in this pilot.
  The previously questioned Martha/Mary setting remains a schematic relational
  diagram in the vector set rather than a pseudo-documentary room image.

## Technical findings

- Candidate files: 14/14 present
- Unique SHA-256 hashes: 14/14
- Minimum dimensions: at least 1200 x 1200
- File format: PNG
- Profile-plan bindings: 17/17 valid
- Missing captions or alternative text: 0
- Publication-ready assets: 0
- Audit errors: 0
- Audit warnings: 0

Run from the repository root:

```bash
python3 tools/build_biblical_profile_candidate_manifest.py
python3 tools/build_biblical_profile_candidate_gallery.py
python3 tools/audit_biblical_profile_plan.py
python3 tools/audit_biblical_profile_candidates.py
```

## Sources and evidentiary boundary

The governing profile plan records book-specific authorship status and links to
the Yale Open Courses Hebrew Bible course, *The Cambridge Companion to the New
Testament*, and the Cambridge chapter on the formation of Isaiah. Primary-text
appearance and role controls are cited in the candidate manifest where needed.

Those sources support the editorial distinctions and historical horizons. They
do not supply recoverable faces. No image may be captioned or marketed as an
archaeological reconstruction of a biblical person's exact appearance.

## Remaining gates

1. Historical specialist reviews regional appearance, textiles, garments,
   writing tools, papyrus/leather treatment, and all environmental cues.
2. Biblical scholar reviews each caption, authorship classification, and
   textual appearance claim.
3. Human visual reviewer checks racial defaulting, idealization, AI artifacts,
   emotional tone, and consistency at mobile and desktop sizes.
4. Rights reviewer records the allowed publication basis and required AI-image
   disclosure.
5. Approved files are integrated only after exact-commit approval, followed by
   accessibility, reflow, performance, and live deployment checks.
