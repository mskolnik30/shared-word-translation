# Fluent Genesis 46–50 revision

All 146 public verses have a source-based draft and an individual decision record. This completes the initial revision draft of Genesis: 1,533 verses in 50 chapters. Together with James, cumulative coverage is 1,641 verses in 55 chapters. Whole-book Genesis consistency review and independent editorial review remain pending.

The authoring model read all selected verses from the exact pinned Hebrew XML before drafting. It then read all TSW comparators and reread the assembled English. TSW supplied comparison evidence, not a base for synonym replacement. Editorial self-check is not independent scholarly approval or reader testing.

## Source and decisions

Source: OpenScriptures MorphHB, commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Gen.xml`, Git blob `dcc8be362134981d3054e9b64d3a465d08492a33`. The full file contains 1,533 verse records. Its SHA-256 is `e5ab737c323d3879733e03882ecf17b7d917115133f87f9cd97895ac98f2b1a4`. Source hashes cover exact original XML verse substrings, including the written/read annotations at 49:10–11. Public and source numbering align throughout this batch.

The draft preserves:

- The full family list, women’s relationships, dead sons, and the distinct 33/16/14/7/66/70 totals. It retains Job at 46:13, rather than silently adopting Jashub from another record.
- Both life-saving food provision and the population’s loss of land and freedom. At 47:21 it follows the pinned cities reading and notes the enslavement variant; purchased people and slavery remain explicit elsewhere in the chapter.
- Jacob’s bodily oath, bed/staff ambiguity, adoption claim, crossed hands, and the reversal of firstborn priority. The extra portion/Shechem ambiguity and sword-and-bow claim are not harmonized away.
- Poetry, animal imagery, pronoun shifts, anger, bodily fertility, and disputed phrases in chapter 49. Shiloh remains opaque in the text with alternatives noted. The reading follows beautiful words rather than silently substituting fawns, and forebears rather than silently substituting ancient mountains.
- The burial account’s repetitions, differing mourning periods, the brothers’ reported command, their renewed fear, Joseph’s repeated intended/intended contrast, his knees, his bones, and the final coffin in Egypt.

Self-check corrections explicitly named Israel as the one embracing the sons, retained the young donkey in 49:11, made the observers’ mourning statement natural English, and used facing Mamre consistently with 23:17–19. Earlier revised chapters were not changed.

## Supplemental comparisons

After independent Hebrew drafting, selected ambiguities were compared with NET translation notes. These references support textual and grammatical comparison; the NET notes’ theological and social evaluations are not adopted as Fluent commentary.

- [Genesis 46 notes, Biblical Studies Press](https://bible.org/sites/bible.org/resources/netbible/gen46_notes.htm): names, household totals, and idioms.
- [Genesis 47 NET notes, hosted by Bible Gateway](https://www.biblegateway.com/passage/?search=Genesis+47&version=NET): the city/enslavement variant and bed/staff reading.
- [Genesis 48 NET notes, hosted by Bible Gateway](https://www.biblegateway.com/passage/?search=Genesis+48&version=NET): inheritance, bodily gestures, and pronouns.
- [Genesis 49 notes, Biblical Studies Press](https://bible.org/sites/bible.org/resources/netbible/gen49_notes.htm): disputed readings in the poem, with proposed emendations kept distinct from the pinned text.
- [Genesis 50 NET, Biblical Studies Press](https://bible.org/sites/bible.org/resources/netbible/gen50.htm): secondary comparison of the closing narrative.

The direct bible.org chapter 47 and 48 pages were unavailable; the successful Bible Gateway versions supplied those comparisons. No unavailable page is claimed as consulted.

## Verification

`verify_batch.py` records the checks in `verification.json`:

- All nine cumulative source-binding ledgers passed `tools/audit_fluent_revision.py`.
- The unique Genesis source references now equal all 1,533 source XML records, with no duplicate coverage.
- This batch has all 146 verses in order, valid paragraph placement including poetry, balanced double quotation marks, complete before/after and comparator bindings, and explicit pending-review metadata.
- Focused checks cover all genealogical names, numbers, hand directions, ownership language, disputed readings, repeated promises, and the final burial location.
- Prior batches and unaffected approval records remain unchanged. Only this batch’s chapters supersede their prior wording’s approvals and bindings.
- `tools/audit_translation_family.py` and `git diff --check` passed. TSW, prior revisions, and Companion files are unchanged.

One verse retains its previous wording (49:16), with new poetic lineation. Editorial categories: F0 1, F2 74, F3 71. The 145 changed verse texts are not a change target.

The focused overlap report covers only Genesis 46–50. Before: 105 identical and 36 near-identical verses with TSW. After: 0 identical and 6 near-identical. Mean token similarity changes from 0.985280 to 0.684169. Near-identical means a nonidentical token sequence with SequenceMatcher similarity at least 0.90. These measurements are triage, not evidence of fidelity, independent authorship, comprehension, or editorial approval.

## Continuation and installation

Next is the whole-book Genesis consistency review: key words, names, chronology, source ambiguities, paragraph flow, and notes/vocabulary. Any changes to earlier chapters must rebind their affected ledgers while preserving historical provenance. Exodus 1–18 follows.

All revised chapters retain `status: QA_PASSED` qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. No human scholarly review or public deployment occurred. Companion quotations and bindings for Genesis 46–50 need checking before later installation. GitHub upload remains blocked under the previously established access restriction; no rejected write was retried.
