# TSW Main-Text Change Report

This report records changes that affected the biblical main text or its public verse identity during the publication audit. It is intentionally separate from apparatus-only and formatting-only normalization.

## Change policy

- Main-text wording was not globally rewritten for style.
- Wording changes were limited to restoration of missing text, source/critical-text corrections, divine-name consistency, and a small number of high-confidence grammatical/capitalization repairs.
- Structural changes such as paragraph normalization, verse-marker repair, and public versification are listed separately from wording changes.
- Notes and Vocabulary were edited much more broadly than the main translation, but those apparatus edits do not count as translation wording changes.

## Restored missing biblical text

- `books/NT/luke/Luke_04.md` — vv38–44 restored
- `books/NT/mark/Mark_07.md` — vv10–13, 17–23, 31–37 restored; v16 remains intentionally absent from the critical-text main
- `books/NT/mark/Mark_08.md` — vv10, 13, 22–26, 31–38 restored
- `books/NT/acts/Acts_21.md` — vv37–40 restored
- `books/NT/john/John_07.md` — v53 restored as the opening verse of the ancient John 7:53–8:11 textual tradition, with textual-status note
- `books/OT/exodus/Exodus_14.md` — vv01–18 restored
- `books/OT/exodus/Exodus_24.md` — vv17–18 restored
- `books/OT/joshua/Joshua_03.md` — vv01–06 restored
- `books/OT/joshua/Joshua_24.md` — vv04–13 and 26–33 restored
- `books/OT/judges/Judges_04.md` — vv10–24 restored
- `books/OT/isaiah/Isaiah_43.md` — v01 restored
- `books/OT/ezekiel/Ezekiel_37.md` — vv15–28 restored
- `books/OT/leviticus/Leviticus_19.md` — vv03–14 and 19–37 restored
- `books/OT/numbers/Numbers_21.md` — vv01–03 and 10–35 restored
- `books/OT/psalms/Psalm_053.md` — public v01 restored; superscription unnumbered and body renumbered to public English convention

## Critical-text main-text removals

- **Matthew 17:21** — Removed from the critical-text main; later-manuscript reading documented in Notes.
- **Luke 17:36** — Removed from the critical-text main; later-manuscript reading documented in Notes.

## Intentional traditional-verse gaps retained in public numbering

These positions are intentionally absent from the critical-text main. Each is documented in the chapter Notes:

Matthew 17:21, Matthew 18:11, Matthew 23:14, Mark 7:16, Mark 9:44, Mark 9:46, Mark 11:26, Mark 15:28, Luke 17:36, Luke 23:17, John 5:4, Acts 8:37, Acts 15:34, Acts 24:7, Acts 28:29, Romans 16:24

The longer ending of Mark (16:9–20) and John 7:53–8:11 are retained as ancient textual traditions with explicit textual-status notes.

## Public-versification repairs

- **Exodus 7–8:** Hebrew 7:26–29 moved to public English 8:1–4; remaining chapter 8 renumbered accordingly.
- **1 Kings 4–5:** Hebrew 5:1–14 mapped to public English 4:21–34; remaining chapter 5 renumbered accordingly.
- **1 Chronicles 5–6:** Hebrew 5:27–41 mapped to public English 6:1–15; remaining chapter 6 renumbered accordingly.
- **Ezekiel 20–21:** Hebrew 21:1–5 mapped to public English 20:45–49; remaining chapter 21 renumbered accordingly.
- **Hosea 1–2:** Hebrew chapter-boundary duplication removed so public English numbering is retained.
- **Genesis 35:** A split continuation was merged and following public verse numbers corrected.
- **1 Chronicles 12:** A split continuation was merged and following public verse numbers corrected.
- **1 Kings 22:** A split continuation was merged and following public verse numbers corrected.
- **Philippians 2:** A split continuation was merged and following public verse numbers corrected.
- **Luke 15:** A split continuation was merged and following public verse numbers corrected.
- **Psalms:** Superscriptions were made unnumbered where required; public English verse numbers retained.

## Divine-name and source-consistency wording changes

The following automated categories affected main-text wording/capitalization. Counts are occurrence-level replacements, not numbers of verses:

- **YHWH/Yahweh form normalized to `LORD`: 206**
- **Ezekiel bare divine-name forms normalized to `the LORD` where English grammar required: 258**
- **Ezekiel `Adonai YHWH` normalized to `Lord GOD`: 39**
- **`Lord YHWH` / equivalent normalized to `Lord GOD`: 58**
- **`LORD of hosts` normalized to `LORD of Hosts`: 36**
- **Micah 6 erroneous `Holy One` substitutions repaired to the LORD where the Hebrew has YHWH: 9**
- **Numbers 6 erroneous `Holy One` substitutions repaired to the LORD where the Hebrew has YHWH: 18**
- **Psalm 8 erroneous `Holy One` substitutions repaired to the LORD where the Hebrew has YHWH: 2**
- **Psalm 15 erroneous `Holy One` substitutions repaired to the LORD where the Hebrew has YHWH: 3**
- **High-confidence divine-pronoun capitalization normalized to standard TSW English: 5**
- **English article normalization around `LORD`: 186** occurrence-level changes across several grammatical patterns.

## Main-text formatting repairs that did not intentionally change wording

- Paragraph markup normalized across 1189 chapter files.
- Canonical verse-line representation applied to 31086 verse lines.
- Embedded duplicate verse labels removed: 23.
- HTML `&emsp;` artifacts removed: 67.
- HTML `<br>` artifacts removed: 13.
- Stray code fences removed: 1.
- Raw source-language contamination lines removed where they were not part of the intended public translation: 6.

## File-level machine logs

Detailed occurrence/file maps are preserved in `audit/PASS3_MAIN_WORDING_CHANGES.json`, `audit/MAIN_TEXT_CHANGELOG_PASS3.json`, and `audit/PASS3_FORMATTING_CHANGES.json`.
