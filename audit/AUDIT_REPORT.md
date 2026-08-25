# Shared Word Translation — Publication Audit Report

## Source snapshot

This audited repository was produced from the user-supplied GitHub download `shared-word-translation-main(1).zip`.

- Source SHA-256: `570a4b6b88531eb5caab997c5759e4706059f549e6c6d4bcf06ea1216190054f`
- The source ZIP was byte-for-byte equivalent to the internal audit baseline commit before audit changes were applied.
- Scope: the complete canonical Bible repository.

## Audit passes completed

### Pass 1 — Repository and chapter integrity

Normalized byte-zero YAML, UTF-8/LF presentation, chapter identity, canonical verse markers, paragraph structure, public verse numbering, Psalm superscriptions, and known cross-chapter Masoretic/public-English numbering differences. Missing/truncated biblical text detected in the source snapshot was restored in a limited set of chapters and is itemized in `MAIN_TEXT_CHANGES.md`.

### Pass 2 — Notes and Vocabulary apparatus

Normalized exact apparatus headings, verse-reference syntax, vocabulary structure, transliteration presentation, and editorial voice. Removed software/workflow references and commentary drift. Notes now focus on textual/translation issues; Vocabulary now functions as selective lexical apparatus.

### Pass 3 — Translation consistency and source-risk review

Applied high-confidence divine-name consistency, source-sensitive title repairs, critical-text verse treatment, selected parallel/versification checks, and literary-structure cleanup. Main-text wording changes were deliberately limited and are fully disclosed in `MAIN_TEXT_CHANGES.md`.

## Final repository statistics

- Canonical chapter files: **1189**
- Main-text verse markers: **31087**
- Notes entries: **590**
- Vocabulary entries: **4729**
- Intentional NT traditional-verse gaps in the critical-text main: **16**
- Unnumbered Psalm superscription blocks: **54**
- Chapters with intentionally empty Notes: **798**
- Chapters with intentionally empty Vocabulary: **19**

## Final validation result

**PASS — zero issues under the final structural/apparatus audit.**

Validated categories include:

- YAML begins at byte 0 and required identity fields are present.
- No UTF-8 BOM or CRLF drift.
- No duplicate chapter identities or case-path collisions.
- Canonical filenames remain intact, including numbered-book capitalization conventions.
- Verse markers are canonical and ordered.
- No duplicate verse identities remain.
- No unexpected internal verse gaps remain.
- The 16 intentional NT traditional-verse gaps are explicitly recognized by policy and documented in Notes.
- Paragraph tags are balanced and normalized.
- `##Notes` and `##Vocabulary` are exact and present in every chapter.
- Apparatus verse references resolve to valid public verse identities or approved textual-gap references.
- Vocabulary entries contain source-language script and definitions where entries exist.
- No software/plugin/website/workflow language remains in Notes or Vocabulary.

## Textual traditions and versification

- Public English verse numbering is retained while significant MT chapter-boundary differences are documented.
- Psalm superscriptions are unnumbered in public verse identity.
- Later traditional NT verses absent from the critical Greek text remain absent from main text at 16 recognized positions, with textual notes.
- Mark 16:9–20 is retained as an ancient longer-ending tradition with textual-status note.
- John 7:53–8:11 is retained as an ancient textual tradition with textual-status note.

## Main-text change disclosure

Main translation wording **was adjusted in limited, controlled cases**. These include restoration of missing verses, two critical-text removals, divine-name consistency, and a small number of high-confidence source/title/capitalization repairs. See `MAIN_TEXT_CHANGES.md` for the disclosure and machine logs in this directory for detailed occurrence maps.

## Recommended deployment

Use this audited repository as the new GitHub canonical source. Replace the existing repository contents (preserving Git history through a normal commit), review the staged diff, commit and push, and then run WordPress Full Reconciliation from that GitHub state. Do not merge older chapter ZIPs back into this audited tree afterward, because they may reintroduce formatting and naming drift.
