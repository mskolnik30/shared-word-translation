# Leviticus 4–7: Fluent source-based draft

All 122 public verses have been drafted from the pinned Hebrew, with one verse-specific rationale, before/after text, comparator, exact source binding and editorial F0–F3 assessment per verse. The batch changes 121 verse texts; one clear verse is retained. F0: 1; F2: 58; F3: 63. Independent editorial review and reader testing remain pending. Chapter QA_PASSED means structural QA only; publication_allowed is false.

The authoring self-check read all selected source records, then all TSW comparators, and reread the complete assembled chapters. It preserved the distinctions between sin and guilt offerings, general reparation and a named sacrifice, inner and outer blood rites, required animal sex, economic alternatives, restitution plus one fifth, priestly portions, food deadlines, and repeated sanctions. Notes identify uncertainties in the awareness clauses, unnamed agents, monetary valuation, holiness by contact, cooking terms and wave-offering movement. Offering terminology connects with the revised Exodus and Leviticus 1–3. This is not independent scholarly review.

## Source and numbering

Source: [Open Scriptures Hebrew Bible, pinned Lev.xml](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Lev.xml). Full file: 859 records; SHA-256 75a4a96e7b64f2145bede15ae37ac8a0b301f110d5d6b2daf9d8048adebbd2e6; Git blob 6025e0713ccfc79de0c90cb92ed0e8c0062d2614.

Public chapters 4–5 and 7 align directly with the Hebrew. Public 6:1–7 maps to Hebrew 5:20–26; public 6:8–30 maps to Hebrew 6:1–23. Every binding hashes the complete original XML verse substring, including numbering and BHS annotations. It does not reuse the earlier chapter-6 normalized fragment hashes.

Supplemental lexical and grammatical comparisons: NET translators’ notes for [Leviticus 4](https://www.biblegateway.com/passage/?search=Leviticus+4&version=NET), [5](https://www.biblegateway.com/passage/?search=Leviticus+5&version=NET), [6](https://www.biblegateway.com/passage/?search=Leviticus+6&version=NET), and [7](https://www.biblegateway.com/passage/?search=Leviticus+7&version=NET). Only selected notes were consulted after source-based drafting; their main translation was not a drafting template.

## Checks and preservation

All 22 cumulative source-binding ledgers passed: 3,026 verses in 102 chapters. The translation-family audit, paragraph/verse coverage, quote balance, focused names/amounts/actions/numbering checks and git diff --check passed. Before/after overlap with TSW changed from 24 identical and 92 near-identical verses to 1 identical and 10 near-identical verses, under the audit’s token-based definition. These numbers are triage only, not fidelity or originality evidence.

Only chapters 4–7 supersede their previous wording’s review records. Earlier batches and unaffected records, TSW, and the separate Companion branch are preserved. Companion quotations/bindings for these four chapters require checking before later installation. No publication occurred. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried.

Next connected scope: Leviticus 8–10, priestly installation, first service, and the deaths of Nadab and Abihu. Continue without routine approval pauses.

Reproduce checks from the repository with the four exact pinned source files:

```bash
python audit/fluent-revision/2026-09-11-leviticus-4-7/verify_batch.py --genesis-source /path/to/genesis-pinned-hebrew.xml --exodus-source /path/to/exodus-pinned-hebrew.xml --leviticus-source /path/to/leviticus-pinned-hebrew.xml --james-source /path/to/james-pinned-greek.txt
```
