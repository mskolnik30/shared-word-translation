# Leviticus 8–10: Fluent source-based draft

All 80 public verses have a source-based draft and a verse-specific rationale, before/after text, comparator, exact source binding, and editorial F0–F3 assessment. The batch changes 79 verse texts and retains one. F0: 1; F2: 38; F3: 41. Independent editorial review and reader testing remain pending. QA_PASSED is qualified as structural; publication_allowed remains false.

The authoring model read every selected Hebrew record, then all TSW comparators, and reread the assembled chapters. The self-check followed garments, anointing and blood actions, all three right-side body applications, animal quantities, seven-day ordination and the eighth-day service, repeated commands, the fire descriptions in 9:24 and 10:2, deaths, mourning restrictions, holy/common versus unclean/clean, daughters’ permitted portions, and the Moses/Aaron exchange. Aaron’s silence and the precise unauthorized-fire violation remain unexplained where the source leaves them so. This was an authoring self-check, not independent scholarly review.

## Source and comparisons

Source: [Open Scriptures Hebrew Bible, pinned Lev.xml](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Lev.xml). Full file: 859 records; SHA-256 75a4a96e7b64f2145bede15ae37ac8a0b301f110d5d6b2daf9d8048adebbd2e6; Git blob 6025e0713ccfc79de0c90cb92ed0e8c0062d2614.

All 80 public/source verse numbers align directly. Leviticus 9:22 follows the read form “hands”; the exact source hash includes the written “hand” and the complete read note. Earlier chapter-6 numbering differences remain bound unchanged.

Selected NET translator notes were consulted after drafting for grammar, ambiguous agents, the Hebrew and ancient-version differences, ritual categories, and idioms: [Leviticus 8](https://www.biblegateway.com/passage/?search=Leviticus+8&version=NET), [9](https://www.biblegateway.com/passage/?search=Leviticus+9&version=NET), [10](https://www.biblegateway.com/passage/?search=Leviticus+10&version=NET). Their theological interpretations were not incorporated as source meaning. TSW served as a comparator, not a drafting template. No overlap quota was imposed.

## Verification and preservation

All 23 cumulative source-binding ledgers passed: 3,106 verses in 105 chapters. The translation-family audit, verse/paragraph coverage, poetry containment, quote balance, focused source/reading checks, and git diff --check passed. The before/after overlap report is mechanical triage, not proof of fidelity or originality.

Earlier revisions, TSW, unaffected approval records, and the separate Companion branch are preserved. Only chapters 8–10 supersede their previous wording’s approvals and bindings, with exact provenance retained in Git. Companion quotations and bindings for these chapters require later checking before installation. Nothing was published. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried.

Next connected scope: Leviticus 11–15. Continue from pinned Hebrew in complete chapters, checking animal identifications, bodily conditions, time periods and ritual categories, without inserting modern medical explanations. No routine approval pause is needed.

```bash
python audit/fluent-revision/2026-09-11-leviticus-8-10/verify_batch.py --genesis-source /path/to/genesis-pinned-hebrew.xml --exodus-source /path/to/exodus-pinned-hebrew.xml --leviticus-source /path/to/leviticus-pinned-hebrew.xml --james-source /path/to/james-pinned-greek.txt
```
