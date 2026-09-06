---
review_record: fluent-companion-complete-corpus-expansion
review_status: ROUND_4_APPROVED
publication_status: blocked
scope: every Fluent chapter in the 66-book Protestant canon
canonical_chapter_count: 1189
---

# Complete-corpus expansion human review record

The complete chapter-by-chapter production target is the repository's 1,189
Fluent chapter files: 929 Old Testament chapters and 260 New Testament
chapters. The earlier representative-coverage release definition is
superseded.

## Production composition

- 83 previously drafted chapter records.
- 12 additional hand-shaped short-prophet chapter records.
- 1,094 source-derived generated chapter records.
- 1,189 total source-bound chapter records.
- 66 book introductions.

All content remains unpublished. Generated records use each source chapter's
own headings, verse ranges, notes, vocabulary, book position, and neighboring
chapters. Generation does not constitute editorial or publication approval.

## Automated gate

The end-of-corpus audit passed on 2026-09-06:

- Content records: 1,189
- Book introductions: 66
- Old Testament coverage: 929 of 929
- New Testament coverage: 260 of 260
- Errors: 0
- Warnings: 0
- Translation-family, apparatus, and TSW regression audits: PASS

This mechanical pass confirms completeness, structure, exact source bindings,
citation bounds, and the audited safety-language rules. It does not substitute
for the human gates below.

## Expanded Round 1 evidence packet

**Decision state:** APPROVED

**Content-corpus digest:**
`56ab1cd5f555a0b3f632679a436487e8da7f4b0d05d41180c4b4d0b9e3a5b320`

Round 1 evaluates structural integrity, source provenance, chapter specificity,
and reader-facing cleanliness. It does not decide the later historical,
interpretive, formation, accessibility, or publication gates.

The first pass failed and was not advanced for approval. It found:

- 298 single-section chapters whose prompts repeated the same heading as both
  the beginning and end of a supposed movement.
- 416 generated records with improper lowercasing of `Israel`.
- 85 generated Gospel records with improper lowercasing of `Gospel`.
- 829 generated records with doubled vocabulary punctuation.
- Reader-facing repository paths and technical `source apparatus` wording in
  all 1,094 generated records.
- Older apparatus markup leaking labels such as `v03`, bullets, repeated verse
  references, and raw vocabulary delimiters into reader-facing prose.

The generator and audit were then corrected, all 1,094 generated records were
rebuilt, and the full audit returned 0 errors and 0 warnings. The audit now
also verifies every generated Chapter Path against the section ranges in its
bound Fluent source and rejects all recurrence of the defects above.

Cross-genre close reading sampled:

- Genesis 2; Leviticus 19; Numbers 25; Deuteronomy 7
- 2 Kings 25; Job 3; Psalm 119; Ecclesiastes 10
- Isaiah 53; Jeremiah 31
- Matthew 5; Luke 10; Acts 15
- 1 Corinthians 11; 1 Timothy 2
- Revelation 13

The corrected sample preserves the Fluent chapter structure, keeps source-note
uncertainty visible, distinguishes single-section and headingless chapters,
uses `Psalm` for individual psalm titles, and exposes no repository paths or
raw editorial markup to readers.

### Approval

- Approver: Matthew J. Skolnik
- Approval date: 2026-09-06
- Reviewed commit: `4661e199d8b31145e382d443d2c01d2cb52db74e`
- Approved content-corpus digest:
  `56ab1cd5f555a0b3f632679a436487e8da7f4b0d05d41180c4b4d0b9e3a5b320`
- Scope: Expanded Round 1 only—structural integrity, source provenance,
  chapter specificity, and reader-facing cleanliness.

This approval does not approve historical-context judgments, theological or
formation judgments, accessibility, publication, merging, or deployment.

## Round 2 evidence packet: context and uncertainty

**Decision state:** APPROVED

**Candidate content commit:**
`a3826231ff111c2bb91eeede7348f690503945b0`

Round 2 tests whether historical and cultural context is distinguished from
what a passage directly states, whether interpretive reconstruction is
identified as such, and whether disputed textual, chronological, authorship,
and symbolic questions remain visibly unresolved.

### Corpus-wide review

- Searched all 66 book guides for categorical claims about setting, dating,
  authorship, composition, ancient communities, and modern identification.
- Checked every generated `What Needs Context` section against its bound Fluent
  source. All 1,053 generated chapters with an importable context note now name
  the translation note and verse explicitly; 41 generated chapters without an
  importable note continue to rely on literary structure without inventing
  historical background.
- Added a permanent audit failure when generated context imports are not
  attributed to a translation note and verse.
- Re-ran the 1,189-chapter content and exact-coverage audits and the
  translation-family and TSW regressions: all passed with 0 errors and 0
  warnings.

### Corrections made

- Reframed imported note material across 1,053 generated chapters as attributed
  translation-note observations rather than unmarked historical fact.
- Qualified First Thessalonians' Corinth setting as the common reconstruction
  produced by coordinating the letter with Acts; the letter itself does not
  name Corinth.
- Placed the Psalms guide's superscription caution beside Psalm 122's source
  note so `Of David` is not silently collapsed into one modern theory of
  authorship.

### Close-reading sample

| Passage | Question tested | Result |
|---|---|---|
| Isaiah 7; Isaiah 53 | Immediate prophetic horizon and later Christian rereading | First horizon remains primary; later echoes are identified as later readings. |
| Ezra 9–10 | Covenant crisis, race, and the source of the divorce proposal | Ancient categories are not converted into race; divine command, Ezra's prayer, and Shecaniah's proposal remain distinct. |
| Daniel 7; Revelation 13 | Empire symbolism and modern timetables | Empires and symbols are not assigned a speculative modern schedule. |
| Ezekiel 16; Hosea 1 | Prophetic sexual and household metaphors | Rhetorical form and human cost are named without treating metaphor as literal ancestry or a modern prescription. |
| Matthew 27; Mark 16; John 7–8 | Textual variants and received traditions | Variant evidence and bracketed/longer traditions remain visible without panic or silent harmonization. |
| Acts 15; Romans 9 | Jewish–Gentile disputes | Internal first-century arguments are not generalized against Jewish people; textual and syntactic uncertainty remains visible. |
| 1 Corinthians 11, 14; 1 Timothy 2 | Gender, worship, and disputed vocabulary | Competing interpretations and the limits of reconstruction are stated rather than resolved by assertion. |
| Hebrews 7; 2 Peter 3 | Scriptural argument, chronology, and cosmic imagery | Selective analogy and textual variants are named; chronology is not converted into a date formula. |

Round 2 approval would cover historical/cultural context, explicit uncertainty,
and the distinction between text, source note, and interpretive reconstruction
for this exact candidate. It would not approve later theological, formation,
depth, clarity, accessibility, publication, merge, or deployment gates.

### Approval

- Approver: Matthew J. Skolnik
- Approval date: 2026-09-06
- Reviewed content commit: `a3826231ff111c2bb91eeede7348f690503945b0`
- Reviewed evidence-packet commit:
  `efca72d007214a6a889de6a0a39b286b49e1f461`
- Scope: Round 2 only—historical and cultural context, explicit uncertainty,
  and the distinction between text, source note, and interpretive
  reconstruction.

This approval does not approve later theological, formation, depth, clarity,
accessibility, publication, merging, or deployment gates.

## Round 3 evidence packet: theological restraint

**Decision state:** APPROVED

**Candidate review commit:**
`654b42c61ffa6b205e88f3cecd026b6cd2156b53`

Round 3 tests whether the Companion remains subordinate to Scripture, avoids
turning one theological synthesis into a chapter's only possible meaning, and
allows related passages to deepen rather than displace the passage being read.

### Corpus-wide review

- All 1,189 chapter records direct the reader to the Fluent Scripture text in
  the `Read the Chapter` step.
- All 1,094 generated records explicitly state that wider biblical connections
  should deepen attention to the passage rather than replace its own voice.
- A corpus-wide scan found no claims of an `only correct interpretation`, no
  commands that all or all true Christians must adopt one disputed reading, and
  no language claiming that the church replaced Israel.
- The audit now fails if a chapter omits its Fluent reading direction, if a
  generated record loses its non-displacement rule, or if defined
  forced-resolution language enters the corpus.
- The content, exact-coverage, translation-family, apparatus, and TSW regression
  audits all pass with 0 errors and 0 warnings.

### Close-reading sample

| Passage group | Theological pressure tested | Result |
|---|---|---|
| Genesis 1; Psalm 13 | Creation doctrine and movement from lament to trust | Poetry and narrative retain their own form; summary does not turn them into a later system or demand premature emotional resolution. |
| Isaiah 7, 53; Zechariah 12 | Christian rereading of Israel's prophetic texts | Immediate horizons remain visible; New Testament readings are traced without erasing unresolved first-horizon questions. |
| Matthew 5; Mark 9, 16; John 7–8 | Law, fulfillment, kingdom timing, and textual traditions | The Gospel's own sequence and textual evidence govern before harmonization or doctrinal synthesis. |
| Romans 8–11; Galatians 3 | Providence, election, Israel, and Gentile inclusion | Tensions remain within each letter's argument; suffering is not called good and Gentile inclusion is not framed as Israel's replacement. |
| 1 Corinthians 11, 14; 1 Timothy 2 | Worship, authority, and gender | Wider canonical evidence remains in conversation with local instructions; disputed vocabulary and scope are not resolved by assertion. |
| 1 Thessalonians 4; 2 Thessalonians 2 | Resurrection hope and Christ's coming | Pastoral purpose controls; imagery is not converted into an itinerary, identity chart, or countdown. |
| Hebrews 7; 2 Peter 3; Revelation 13, 21 | Fulfillment, cosmic renewal, and apocalypse | Analogy, symbol, and textual uncertainty remain visible; hope is not converted into speculative chronology or contempt for creation. |

No reader-facing content correction was required by Round 3. The reviewed
corpus consistently places Scripture first and marks synthesis as a secondary
act of reading. The audit additions preserve that boundary against regression.

Round 3 approval would cover Scripture-versus-Companion hierarchy, theological
restraint, and preservation of disputed readings for this exact candidate. It
would not approve formation and safety, chapter-specific depth, plain-language
testing, accessibility, publication, merge, or deployment.

### Approval

- Approver: Matthew J. Skolnik
- Approval date: 2026-09-06
- Reviewed audit/rule commit:
  `654b42c61ffa6b205e88f3cecd026b6cd2156b53`
- Reviewed evidence-packet commit:
  `96f38e7e33f6d04a2c97db16987d80f02195c5d9`
- Scope: Round 3 only—Scripture-versus-Companion hierarchy, theological
  restraint, and preservation of disputed readings.

This approval does not approve formation and safety, chapter-specific depth,
plain-language testing, accessibility, publication, merging, or deployment.

## Round 4 evidence packet: formation and safety

**Decision state:** APPROVED

**Candidate review commit:**
`1410a917907b2d763a5346f3d38b17925db200f7`

Round 4 tests whether questions, prayers, and practices preserve reader agency;
whether trauma, danger, unequal power, violence, gender, illness, slavery, and
grief are handled without coercion; and whether the Companion refuses to make
disclosure, reconciliation, continued exposure to harm, or promised healing a
condition of faithfulness.

### Corpus-wide review

- Read all 95 hand-shaped `Prayer and Practice` sections and reviewed their
  surrounding safety guidance. They retain passage-specific care, including
  permission to pause, survivor-centered language, medical and professional
  support, boundaries, consent, and non-coercive action where relevant.
- The first generated-corpus pass exposed a systemic weakness: all 1,094
  generated records asked for a personal response, but severe chapters could
  reach that exercise without an explicit agency or trauma boundary.
- Corrected all 1,094 generated `Prayer and Practice` sections. Every one now
  requires a voluntary and proportionate response attentive to people with
  less power, permits pausing when trauma or danger is involved, forbids forced
  disclosure or quick forgiveness and reconciliation, rejects continued
  exposure to harm, and permits trustworthy support.
- Made the complete safeguard an exact audit requirement for every generated
  record, so a later regeneration cannot silently remove it.
- Expanded the prohibited-language audit for coercive forgiveness or
  reconciliation, remaining in danger, submission to an abuser, spiritualized
  rejection of medical or professional care, victim-blaming, imitative
  violence, and endorsement of slavery. The corpus contains no matches.
- Re-ran the Fluent content and exact-coverage audits plus the translation
  family, apparatus, and all seven TSW batch regressions. All pass with 0
  errors and 0 warnings; all 1,189 Fluent chapters remain covered.

### Close-reading sample

| Passage group | Formation or safety pressure tested | Result |
|---|---|---|
| Numbers 31; Deuteronomy 20–22; Joshua 6, 10–11 | War, captives, destruction, and modern imitation | Severe source language remains visible; the guides reject timeless authorization for conquest; practices preserve agency and the safety of people with less power. |
| Judges 11, 19–21; 2 Samuel 11, 13 | Sacrificed women, sexual violence, institutional power, and victim-blaming | Harm is named without romanticizing it; survivors are not blamed or required to disclose, forgive quickly, reconcile, or remain accessible to offenders. |
| Psalm 13, 88, 137; Job 3; 1 Kings 19 | Grief, rage, despair, and a request to die | Readers may leave prayer unresolved or pause; despair is not shamed or converted into a lesson, and support is permitted rather than spiritualized away. |
| Mark 5; John 9; James 5; Philippians 4 | Healing, disability, distress, and prayer | Healing is not guaranteed, illness is not blamed on deficient faith, and prayer is allowed to accompany medical care and sustained support. |
| Matthew 18; 2 Corinthians 2, 5; 1 John 1 | Discipline, confession, forgiveness, and reconciliation | Restoration is not made coercive; the formation rule protects privacy, boundaries, safety, and truthful accountability. |
| 1 Corinthians 7, 11, 14; Ephesians 5; 1 Timothy 2; 1 Peter 3 | Marriage, gender, submission, authority, and worship | Disputed readings remain visible; mutuality never authorizes ownership or abuse, and people facing danger may seek safety and qualified help. |
| Exodus 21; 1 Timothy 6; Titus 2; Philemon | Slavery, constrained labor, and unequal social power | Slavery is named rather than disguised or endorsed; questions and practices turn toward freedom, fair treatment, relinquished control, and the agency of constrained people. |
| Ezekiel 16; Hosea 1–3; Nahum 3 | Sexualized prophetic imagery and gendered humiliation | The rhetoric's harm is named, its force is not sanitized, and readers are told not to imitate body-shaming, sexual humiliation, or gender contempt. |

Round 4 approval would cover formation, trauma awareness, non-coercion, power,
violence, gender, illness, slavery, and vulnerable readers for this exact
candidate. It would not approve chapter-specific depth, plain-language reader
testing, accessibility, publication, merge, or deployment.

### Approval

- Approver: Matthew J. Skolnik
- Approval date: 2026-09-06
- Reviewed content and audit commit:
  `1410a917907b2d763a5346f3d38b17925db200f7`
- Reviewed evidence-packet commit:
  `ce791000536e538579bc2151a54a04a83978803a`
- Scope: Round 4 only—formation, trauma awareness, non-coercion, power,
  violence, gender, illness, slavery, and vulnerable readers.

This approval does not approve chapter-specific depth, plain-language reader
testing, accessibility, publication, merging, or deployment.

## Consolidated Rounds 5–7 evidence packet

**Decision state:** READY FOR ONE HUMAN DECISION

**Candidate content and audit commit:**
`651d0d72265df1dd93288280bd2543df9b039ca9`

This packet combines the three remaining editorial rounds without collapsing
their criteria. One approval may accept all three repository-side gates for
this exact commit. It does not approve merging, publication, or deployment,
and it cannot certify browser or assistive-technology behavior that exists
only in the external Church Commons reader.

### Round 5: chapter-specific depth

- Rechecked all 1,094 generated records against their exact Fluent source
  headings, verse ranges, notes, vocabulary, and neighboring-chapter position.
- All 1,053 generated chapters with an importable source note retain an
  explicitly attributed, verse-labeled context observation.
- All 1,088 generated chapters with importable source vocabulary now retain a
  verse-labeled vocabulary observation. The audit fails if one is omitted.
- Repaired the 68 two-section chapters whose retelling prompt could repeat its
  closing heading instead of describing a genuine movement.
- Replaced exhaustive heading lists in 140 chapters with more than six named
  sections by a readable beginning–middle–end orientation while preserving the
  complete section sequence in `Chapter Path`.
- Split older multi-item apparatus blocks into discrete observations and
  removed raw footnote markers and duplicated chapter-and-verse prefixes.
- The 95 hand-shaped records remain unchanged and preserve their intentionally
  richer treatment of calibration, high-risk, and complete-book passages.

The generated chapters remain concise source-derived orientation rather than
technical commentary. Round 5 approval would accept that level of depth as the
first-edition baseline; it would not claim that every generated chapter has
received a bespoke line-by-line rewrite.

### Round 6: plain-language clarity

- All 1,189 records contain the same visible reading rhythm and exactly one
  level-one chapter title.
- No record contains a heading-level skip, raw HTML element, raw source
  footnote marker, vague link label, or sentence longer than 100 words.
- Reader-facing repository paths, editorial workflow labels, and raw apparatus
  syntax remain excluded by the permanent audit.
- Repeated two-section endpoints, oversized section enumerations, and
  duplicated verse references were corrected in the generator and rebuilt in
  every affected chapter.
- The content audit reports 0 errors and 0 warnings across 1,189 records and 66
  introductions.

This is a corpus-wide editorial and mechanical clarity review. It does not
invent participant evidence: comprehension observations from less-familiar
readers should still be recorded during release validation and used for later
improvements.

### Round 7: accessibility and reader integration

- Added `manifests/reader-index.json` with exactly 1,189 unique chapter
  bindings and all 66 book guides.
- Every indexed chapter is checked against its book, chapter, Fluent source,
  Companion file, workflow status, and SHA-256 record digest.
- The index uses the approved public label `Understand the Passage`, names
  Fluent as the home translation, and retains an explicit `unpublished` hard
  stop.
- Added `docs/FLUENT_COMPANION_READER_INTEGRATION.md` to preserve Scripture as
  the primary reading surface, keep the Companion closed by default, define an
  accessible unavailable state, preserve reader location, and prevent raw
  Markdown or editorial metadata from reaching the public UI.
- The contract defines release-build checks for keyboard operation, focus,
  screen-reader state, 200% zoom/reflow, phone/tablet/desktop layouts, dark
  mode, print, map zoom, and representative passages.

The repository-side accessibility structure and integration contract are
ready for approval. Runtime accessibility is deliberately not marked as
passed until the exact release build is exercised in the reader.

### Consolidated decision boundary

Approval of Rounds 5–7 would approve, for commit `651d0d72`:

1. first-edition chapter-specific depth as a source-derived baseline;
2. corpus-side plain-language and semantic-structure checks; and
3. the checksum-bound reader integration contract.

It would leave four release actions separate and blocked: merge, construction
of the exact reader release, runtime/device/accessibility testing, and final
publication/deployment approval.

## Human gates

| Gate | Status | Reviewer | Date | Notes |
|---|---|---|---|---|
| Structure, source fidelity, and reader cleanliness | Approved | Matthew J. Skolnik | 2026-09-06 | Expanded Round 1 approved against commit `4661e199`; exact source bindings, chapter paths, and repaired reader-facing imports accepted at gate level. |
| Context and uncertainty | Approved | Matthew J. Skolnik | 2026-09-06 | Round 2 approved for content commit `a3826231` and evidence-packet commit `efca72d0`. |
| Theological restraint | Approved | Matthew J. Skolnik | 2026-09-06 | Round 3 approved for audit/rule commit `654b42c6` and evidence-packet commit `96f38e7e`. |
| Formation and safety | Approved | Matthew J. Skolnik | 2026-09-06 | Round 4 approved for content/audit commit `1410a917` and evidence-packet commit `ce791000`. |
| Chapter-specific depth | Ready for consolidated decision |  |  | Round 5 evidence accepts source-derived orientation as the first-edition baseline while preserving 95 richer hand-shaped records. |
| Plain-language clarity | Ready for consolidated decision |  |  | Round 6 corpus checks pass; less-familiar-reader observations remain part of release validation and later improvement. |
| Accessibility and reader integration | Content-side ready; runtime pending |  |  | Round 7 index and contract pass; the external reader build must still be tested with devices and assistive technology. |
| Publication approval | Blocked |  |  | Requires all prior gates and approval of an exact release commit. |
