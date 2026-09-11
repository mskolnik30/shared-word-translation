# Leviticus 11–12: Fluent source-based draft

All 55 public verses have a source-based draft and verse-specific rationale, before/after text, comparator, exact original XML source binding and editorial F0–F3 assessment. The batch changes 52 verse texts and retains three clear verses. F0: 3; F2: 13; F3: 39. Independent editorial review and reader testing remain pending. QA_PASSED means structural QA only; publication_allowed remains false.

The authoring model read every selected Hebrew record and reread the assembled chapter text. The self-check preserved animal-list coverage and provisional identifications, both land and water food criteria, the ancient locomotion categories, carcass touching/carrying/eating, water and material exceptions, repeated holiness language and the exodus reference. Chapter 12 preserves male/female birth distinctions, all four time periods, eighth-day circumcision, the two offering categories and the less costly bird option. It retains cleanness as the result without adding a forgiveness formula. The draft does not insert modern biological explanations or a rationale for the differing birth periods.

## Sources and numbering

Source: [Open Scriptures Hebrew Bible, pinned Lev.xml](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Lev.xml). Full file: 859 records; SHA-256 75a4a96e7b64f2145bede15ae37ac8a0b301f110d5d6b2daf9d8048adebbd2e6; Git blob 6025e0713ccfc79de0c90cb92ed0e8c0062d2614.

All 55 public/source references align directly. Hashes cover complete original verse substrings, including the written/read difference at 11:21 and the large-letter annotation at 11:42. Earlier chapter-6 mappings remain unchanged. Verse 11:21 follows the read form indicating possession of jumping legs, while the written form is the negative word.

Selected [NET Leviticus 11 translator notes](https://www.biblegateway.com/passage/?search=Leviticus+11&version=NET) were consulted for lexical comparison before drafting and grammatical comparison afterward. [NET Leviticus 12 notes](https://www.biblegateway.com/passage/?search=Leviticus+12&version=NET) and all 55 TSW verse comparators were read after drafting. The main text was composed from the Hebrew. Provisional animal labels require further independent lexical review; no claim of certain zoological identification is made. Speculative explanations in comparators were not adopted.

## Checks and preservation

All 24 cumulative source-binding ledger audits passed, covering 3,161 verses in 107 chapters. The translation-family audit, verse/paragraph coverage, quote balance, focused content checks and git diff --check passed. The overlap report is mechanical triage, not evidence of fidelity, originality or comprehension. This was an authoring self-check, not independent scholarly review.

Only chapters 11–12 supersede their earlier wording’s approvals and bindings; exact historical records remain in Git. Earlier batches, unaffected records, TSW and the separate Companion branch are preserved. Companion quotes and bindings for these two chapters require checking before later installation. Nothing was published. GitHub upload remains blocked by the established access restriction; no rejected write was retried.

Next: Leviticus 13–15 in complete connected chapters from the same pinned source. Preserve the distinctions among ritual impurity, illness and sin; check uncertain condition names, bodily details, time periods, and rites without adding modern medical claims. No routine approval pause is needed.

```bash
python audit/fluent-revision/2026-09-11-leviticus-11-12/verify_batch.py --genesis-source /path/to/genesis-pinned-hebrew.xml --exodus-source /path/to/exodus-pinned-hebrew.xml --leviticus-source /path/to/leviticus-pinned-hebrew.xml --james-source /path/to/james-pinned-greek.txt
```
