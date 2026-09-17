# Fluent Companion reader integration contract

## Purpose

This contract connects the complete Fluent Companion corpus to the Church
Commons Bible Reader without confusing Companion material with Scripture. The
repository remains the source of truth; the reader is a renderer and must not
silently edit, summarize, or duplicate these records.

## Canonical index

The reader must resolve Fluent Companion content through
`companions/fluent/manifests/reader-index.json`. The index binds every one of
the 1,189 Fluent chapter sources to exactly one Companion record and binds all
66 book guides. It includes both hand-shaped and generated records, including
the five calibration records that intentionally live outside the ordinary
chapter directories.

The reader must not construct a Companion path from unchecked URL or shortcode
input. It should first resolve a canonical translation, book, and chapter, then
look up the exact source binding in the index. A missing or invalid entry must
produce the accessible message “Reading help is unavailable for this passage.”
It must not expose a server path, warning, or stack trace and must not substitute
another chapter.

## Public presentation

- Public label: **Understand the Passage**.
- Home translation: **Fluent**.
- Scripture remains the primary reading surface.
- The Companion is closed by default and never opens automatically in ordinary
  reading, worship, or a shared link unless the reader explicitly requested it.
- Opening or closing the Companion must preserve the book, chapter, verse range,
  and translation.
- The book guide and chapter Companion are distinct controls. Opening one must
  not discard the reader's place in the other.
- Generated and hand-shaped records receive the same public visual treatment;
  editorial workflow labels are not reader-facing.
- The current `unpublished` status is a hard block. The index and records must
  not be exposed publicly until the exact release commit receives publication
  approval.

## Markdown and accessibility

The renderer must sanitize Markdown and preserve its semantic order:

1. one chapter title;
2. Before You Read;
3. Read the Chapter;
4. After You Read;
5. Go Deeper.

Nested headings must remain headings rather than decorative text. Chapter Path
items remain lists, question labels remain visible, and descriptive link text
must be announced instead of a raw URL. Raw HTML, source footnote markers,
repository paths, front matter, and editorial status fields are never rendered.

The final reader implementation must also provide:

- complete keyboard operation and a visible focus indicator;
- programmatic names and expanded/collapsed state for every disclosure control;
- logical focus return when a panel or dialog closes;
- no horizontal page scrolling at phone width or 200% browser zoom;
- text resizing without clipped, overlapping, or hidden content;
- light and dark modes that retain WCAG AA contrast;
- print output that removes controls while retaining Scripture, headings, lists,
  and source-identifying labels;
- no fixed control layer that obscures Scripture or Companion text;
- a full-size, pinch-zoomable view for approved maps while blocked or
  unapproved visuals remain absent.

## Acceptance checks

Before publication, test Genesis 1, Psalm 13, Mark 1 and 5, Philippians 1–4,
Romans 8, and Revelation 21. For each applicable passage, verify full-chapter
reading, selected verse ranges, book guide, chapter Companion, independent
translation and Companion selection, copied URL, reload persistence, keyboard
navigation, phone reflow, 200% zoom, dark mode, and print.

The content-side gate passes only when the reader index has 1,189 unique source
bindings, 1,189 existing Companion files, 66 book guides, valid record hashes,
the approved public label, and unpublished status. Runtime accessibility and
deployment verification still occur against the exact release build.
