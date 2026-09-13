# Fluent revision: Numbers 25–30

All 193 public verses in this six-chapter batch have a source-based draft assessment and a verse-specific rationale. The draft changes 191 verse texts and retains the clear wording of 25:17 and 28:10. Its purpose is biblical fluency: readers should follow the narrative, family relationships, offering calendar and legal conditions while recognizing recurring biblical language. Editorial choices are recorded as 136 F2, 55 F3 and 2 F0; no minimum-change target was applied.

## Source and verse numbering

Source: openscriptures/morphhb commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Num.xml`, Git blob `2e7252db3bd33d510d2361a8b5016ac680b27dbb`, SHA-256 `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`. The full source contains 1,289 original records.

The 193 public verses bind 194 complete original Hebrew records. Public 26:1 combines Hebrew 25:19 and 26:1; public 29:40 corresponds to Hebrew 30:1; public 30:1–16 corresponds to Hebrew 30:2–17. Other selected verses align directly. All 25 annotations in 24 records are retained in the exact source hashes, including the written/read note at 26:9, enlarged-letter notice at 27:5 and extraordinary point at 29:15.

The new ledger uses schema version 3 and an optional `source_segments` list for public 26:1. Each component has its own source reference and exact original XML hash; the primary source binding remains present. The audit tool now validates those components, coverage, uniqueness, order and agreement with the primary binding, while continuing to accept earlier single-record ledgers unchanged. Seven negative checks reject a missing component, corrupted hash, duplicate, reversed order, unknown reference, invalid list shape and a primary binding absent from the component list. No normalized concatenation substitutes for either original verse.

## Authoring self-check

Every selected Hebrew record was read before drafting. Selected primary NET translators’ notes were consulted on grammatical and lexical difficulties in Numbers 25, 27 and 30; links are in the ledger. All 193 TSW comparator verses were read after the independent draft. The comparison does not make TSW a base text.

Focused checks covered:

- Peor’s sexual and worship language, Moabite/Midianite distinctions, public punishment, the stabbing of both named victims, 24,000 deaths, repeated zeal and the covenant of peace. Notes do not invent a specific fertility rite or an explicit sexual position.
- All twelve tribal figures, totaling 601,730; the separate 23,000 male Levites from one month old; all clan founders; the five daughters, Serah, Korah’s surviving sons and the two named census exceptions.
- Zelophehad’s daughters speaking publicly, the explicit affirmation of their claim, their land inheritance and the ordered fallback heirs; Moses and Aaron’s shared responsibility; Joshua’s spirit, commission, authority, hands and the Urim.
- Exact offering dates, animals, ages, soundness and grain/drink ratios; separate daily and monthly additions; all-work versus ordinary-work restrictions; thirteen through seven bulls totaling seventy, with the eighth day kept distinct.
- The vow rules’ specific genders and household statuses; same-day objection, confirmation by silence, widows and divorced women, divine forgiveness and the husband bearing guilt after later cancellation.

The source’s difficult claims and consequential ambiguity remain visible. Notes and vocabulary are selective reading aids, not sermons or a replacement for the Companion.

## Results and limits

All 39 cumulative source-binding ledger audits passed, along with the translation-family audit, paragraph/verse/quotation checks, focused checks and `git diff --check`. Revised draft coverage is now 4,773 public verses in 152 chapters: James 1–5, Genesis 1–50, Exodus 1–40, Leviticus 1–27 and Numbers 1–30. Numbers contributes 1,060 public verses bound to 1,061 source records.

Before revision, 140 verses were identical to TSW under case-folded word comparison and 48 were nearly identical. After revision, 2 are identical and 8 nearly identical. Near-identical means a nonidentical SequenceMatcher word ratio of at least 0.90. These figures are triage, not proof of fidelity, originality or reader comprehension.

`QA_PASSED` is qualified by `qa_scope: structural`. Independent editorial status remains `REVIEW_PENDING`, and `publication_allowed` remains false. These checks are an authoring self-check and structural validation, not human scholarly review or reader testing. Only the current six chapters supersede their older approvals; exact prior wording and records remain in Git history, and all prior revision batches are preserved.

No GitHub write was retried under the established access restriction. No public deployment or Companion-branch change occurred. Companion quotations and bindings for Numbers 25–30 need checking before later installation.

Next: Numbers 31–36 as a connected 228-verse batch, then a whole-book Numbers consistency self-check. Any correction to an earlier chapter must rebind its ledger and preserve historical provenance.
