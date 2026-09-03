# Mark — Fluent Book-Level QA

**Status: QA_PASSED / ready for a development PR after installation.**

Mark contains 16 public chapters and 678 public verse slots. Five public verse numbers (7:16; 9:44, 46; 11:26; 15:28) are absent from the pinned SBLGNT critical text and therefore remain intentional numbering gaps. The package contains 673 verse-labeled entries, including Mark 16:9–20 as a clearly separated ancient textual tradition.

## Production model

Mark is the first sustained production-scale Fluent book. It was reviewed internally in four units (1–5, 6–10, 11–15, 16) but is delivered as **one book, one branch, one PR**.

## Book-level anchors

- preserve Mark’s **immediately / at once** urgency without mechanically reproducing every connective;
- preserve **good news** and **kingdom of God**;
- preserve **hand over** (`paradidōmi`) through mission, betrayal, arrest, trial, and suffering;
- preserve **authority**, **follow / come after**, and **the way**;
- retain **Son of Man**;
- preserve the `sōzō` **save / heal / restore** network;
- preserve **clean / unclean / defilement** language;
- preserve seeing, hearing, understanding, and **hardened heart** as a perception network;
- preserve restrained disclosure / commands to silence without reducing them to one theory;
- preserve servant/slave/greatness/ransom language culminating in 10:42–45;
- preserve cross-bearing, cup, hand-over, saving irony, and abandonment through the passion.

## Major textual decisions

- **1:1** — SBLGNT main text omits “Son of God”; the important variant is noted.
- **1:41** — SBLGNT reads “moved with anger”; “moved with compassion” is an important variant and current TSW reading.
- **6:22** — pinned source supports the daughter-of-Herodias construction.
- **7:16; 9:44, 46; 11:26; 15:28** — absent from SBLGNT; numbering gaps retained.
- **14:24** — “blood of the covenant,” not the later expanded “new covenant.”
- **16:1–8** — continuous SBLGNT main text.
- **16:9–20** — included under an explicit “Ancient Textual Tradition” heading; the shorter ending is noted in apparatus.

## Validation gates

The installer refuses to commit unless source retrieval and source-binding succeed, all expected verse labels match, intentional critical-text gaps match, paragraph tags are balanced, headings occur outside paragraph tags, Notes/Vocabulary are present exactly once, duplicate apparatus entries are absent, apparatus verse references resolve to public verse slots, literal escaped-newline residue is absent, `git diff --check` is clean, per-verse F0–F3 review records are generated, and source SHA-256 bindings are written.
