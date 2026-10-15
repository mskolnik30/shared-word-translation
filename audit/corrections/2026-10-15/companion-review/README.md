# PR 152 — Companion reconciliation and reader verification

15 October 2026 · Base correction commit `3762f893a436c70c5c4a2dfb75f3d5ce92cf754b`

## Completed in this follow-up

Eleven affected Fluent Companion chapters have source-bound reconciliation candidates. The work includes continuous reading of their **395 numbered source verses** and checking **25 cross-reference ranges** against the available Fluent files. Ten New Testament drafts were revised to replace obsolete note sampling and generic heading summaries with chapter-specific explanation. The previously revised 2 Chronicles 4 body from checkpoint 18 is preserved verbatim; its SHA-256 and Git blob were reproduced before reuse.

The eleven chapters are 1 Corinthians 13–14; 2 Corinthians 11; Acts 9; John 19; Luke 22–24; Revelation 15 and 20; and 2 Chronicles 4. The reconciliation includes the corrected source account at 1 Corinthians 13:3, the precise Luke bracket distinctions, the retained single copies of clause continuations, Fluent identity after embedded metadata removal, and the corrected altar dimensions. Interpretive questions are explicitly retained rather than turned into settled conclusions.

`RECONCILIATION.json` records the source hashes, previous checkpoint queue entries, exact candidate hashes, observations, and unresolved questions. `SOURCE_EXCERPTS.json` contains the numbered text and current translation notes used for these comparisons, plus the cross-reference passages. Their inclusion records what was read; it does not turn AI-assisted review into independent linguistic certification.

## Why the candidates are in audit space

The current translation branch contains TSW Study Companion resources but does not contain the separate Fluent Companion production tree. The Fluent Companion baseline is commit `7bb3417d824785383e7ca0cea564b585978b6bd5`; checkpoint 18 carries later revisions to that baseline. Its recovery instructions explicitly keep the older Companion branch separate from the newer translation checkout.

Accordingly, this follow-up does **not** merge the older production branch, overwrite checkpoint 18, rewrite historical queues, or register a new public Companion. The eleven candidates are under `candidates/`, with their intended canonical resource paths recorded in the ledger. They can be incorporated into the complete Companion workflow without losing the intervening work. Previous approvals are not transferred.

This is a completed **targeted reconciliation candidate**, not completion of the whole Fluent Companion. Independent human review, broader editorial audits, and final signoff remain pending. The existing TSW Study dossiers and their publication labels are unchanged. The TSW Study directory and one manifest/dossier were inspected for context, not comprehensively re-audited for every indirect reference to the seven changed TSW chapters. That broader dependency review remains open.

## Live reader findings

Fresh, read-only WPVibe requests on 15 October reached the actual Church Commons reader and the MVP gateway. The tested Church Commons TSW verse responses still show the old issues at Genesis 2, 24, and 35; 2 Chronicles 4; Ezekiel 42; Micah 5; and Revelation 4. The returned HTML for Genesis 24:59 also contains the old misnumbered consent statement. The tested Fluent note responses still contain the old source-account statements in 1 Corinthians 13 and Luke 22–24.

The live vocabulary samples in 1 Corinthians 13 and Revelation 15 still embed their definitions in the term field and leave the separate definition field empty. This is an observation about four inspected entries, not a new whole-site count. The full Revelation 15 chapter response reports version `2026.09.21-aba00a6e` and supplies the verse/block/notes/vocabulary structure used to design the comparator.

MVP's current `/bible.html` script requests its reader through `/api/gateway/bible/reader`. The inspected server routes forward the reader and chapter/passage requests to Church Commons. Actual MVP passage responses at Genesis 24:59 and 2 Chronicles 4:1 match the inspected Church Commons responses. This is evidence for a shared data route, not a reason to upload two independent Bible datasets. Post-update cache behavior and browser interaction must still be checked.

The live Companion registry currently lists `tsw-study`, not the Fluent Companion. These unfinished Fluent candidates are therefore not replacements for already displayed Fluent Companion entries. `LIVE_READER_OBSERVATIONS.json` preserves selected returned fields, exact endpoints, and scope limitations. The observations are transcriptions of native-tool responses, not byte-exact HTTP archives.

**No website content was modified.** Old live responses are expected before deployment; they are not evidence that the branch corrections failed to save. Equally, they must not be described as successful deployment.

## Verification

The 44 existing correction regressions were rerun successfully. Twenty additional offline tests check the eleven source bindings, retained unpublished status, full chapter-reference coverage, cross-reference excerpts, checkpoint-18 preservation, and the API comparator's rejection of missing verses, wrong identities, duplicated records, stale notes, malformed vocabulary, and failed network reads. Total: **64 tests**, with their limited scopes recorded separately.

The rebuilt local reader candidate was also compared with its pinned source model through the new comparator: **1,196 chapter payloads and 31,272 verse records matched**. This consists of all 1,189 Fluent chapters and only the seven selected TSW chapters. It is not a complete TSW rebuild, a whole-Bible accuracy certification, or a live-site result.

`tools/check_reader_correction_targets.py` is read-only. It can compare the eighteen corrected source chapters plus the Numbers 22 export-reference case across both sites: 38 API targets. Its complete request plan has been exercised with local fixtures, including network-failure cases. The fresh online observations in this session are the narrower scope above; no claim is made that all 38 online calls were run here.

The checker uses an explicit requested output file and never publishes. A nonzero exit status means at least one target differs or cannot be verified; before deployment, differences are expected. A successful content comparison is still not browser testing or publication approval.

## Release boundaries

This follow-up changes no biblical text, merges no branch, and grants no publication permission. The regenerated reader output remains review-only. Do not replace a whole TSW data directory with the seven-chapter subset. Before a live update, confirm the production reader's deployment mechanism, preserve its current data, apply only the approved source/data changes, and compare public chapter, passage, search, and rendered-reader behavior afterward. Source-branch merging and website publication are separate decisions.
