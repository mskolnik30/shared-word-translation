# Fluent Deuteronomy 13–18

This batch drafts all 134 public verses of Deuteronomy 13–18 from the pinned Hebrew, with an individual rationale, editorial F0–F3 choice, before/after wording, TSW comparator, and exact source-record hash for each verse. It brings cumulative coverage to 5,515 public verses across 176 chapters. All 43 current source-binding ledgers pass.

The reading voice uses shorter clauses and clear conditions while retaining deliberate repetitions, concrete images, biblical vocabulary, and the ancient laws' stated consequences. TSW was read after the independent draft as a comparator. Clear shared language is retained where it serves the passage; there is no overlap quota.

## Source and numbering

Source: [Open Scriptures Hebrew Bible, pinned Deuteronomy](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Deut.xml).

- Commit: `6a5db284c715c18b239422e57bb89684e6a19f00`.
- Git blob: `5317431fd1d1fb5848d7f9f1d22d0753152f9991`.
- SHA-256: `aad16a6a2dcbdc6ee36d7d051e80a63bfeb69ecaae19f775ec5b6aa67fe22355`.
- Complete source: 959 original verse records.
- Public 13:1–18 binds Hebrew 13:2–19. Public 14–18 aligns directly.
- Hebrew 13:1 is excluded from this batch because the preceding ledger binds it to public 12:32. All source records through Hebrew 18:22 are now bound exactly once across the Deuteronomy ledgers.

Every selected Hebrew verse was read before drafting. Hashes cover exact original XML substrings, including all written/read, accent, and numbering notes. The written/read town pronoun in Hebrew 13:16 is translated once, at public 13:15.

Supplemental translator notes were consulted for selected difficulties in [Deuteronomy 14](https://www.biblegateway.com/passage/?search=Deuteronomy+14&version=NET), [Deuteronomy 15](https://www.biblegateway.com/passage/?search=Deuteronomy+15&version=NET), and [Deuteronomy 18](https://www.biblegateway.com/passage/?search=Deuteronomy+18&version=NET). These are comparison resources, not the translation's template. Earlier Fluent Leviticus 11 equivalents were checked for consistent animal names without imposing its different list on Deuteronomy.

## Editorial decisions

- Chapter 13 preserves fulfilled signs that lead toward other gods, close family relationships, investigation, execution, the killing of a town's inhabitants and livestock, total burning, and the ban on retaining plunder. It is not reduced to social exclusion.
- Chapter 14 represents every animal-list entry. Uncertain species are qualified; the additional dayyah term is retained with an explanation. It preserves the distinction between resident foreigner and foreigner, and between the annual tithe meal and the third-year local food provision.
- Chapter 15 retains debt release without concealing the debate over its duration. It keeps the conditional no-poor assurance and the continuing-poverty statement together. Both male and female slaves, six years of service, seventh-year freedom, material departure provisions, bodily piercing, and permanent slavery remain explicit. The scope of the short female-slave clause is noted.
- Chapter 16 keeps flock and herd, cooking terminology, six days followed by the seventh assembly, seven weeks, the three festivals, inclusive celebration lists and the specifically male appearance requirement. The repeated “Justice, justice” remains audible.
- Chapter 17 retains witness thresholds and participation, the difficult categories of cases, binding judgments, royal limits, the king's own written copy and lifelong reading, and the prohibition against a raised heart above fellow Israelites.
- Chapter 18 retains the specified priestly portions, the obscure ancestral-resource clause, all the prohibited practices, child passage through fire, wholehearted allegiance, the singular prophet like Moses, and the distinction between failed predictions and the chapter 13 warning.

## Verification and limits

`verification.json` records all 43 ledger audits, exact source coverage and mapping, selected content checks, verse order, paragraph containment, speech delimiters, chapter metadata, preservation of earlier revisions and unrelated work, the translation-family audit, and `git diff --check`.

`overlap-before-after.json` records mechanical comparison with TSW. Before drafting, 42 of 134 verses were identical and another 85 near-identical by the audit's word-token definition. After drafting, none are identical and two are near-identical; mean token-sequence similarity is 0.626937. These figures are triage, not proof of fidelity, originality, or reader comprehension. All 134 verses changed from the prior Fluent wording, with 80 F2 and 54 F3 choices.

This is source-based authoring and structural QA. Independent scholarly review and reader testing remain pending. Chapter status `QA_PASSED` is qualified by `qa_scope: structural`; `editorial_status` remains `REVIEW_PENDING` and `publication_allowed` remains false. Prior approvals are superseded only for the changed chapters, with exact historical parent objects preserved.

TSW and the separate Companion branch are unchanged. Companion quotations and bindings for these chapters require checking before later installation. No public deployment occurred. GitHub upload remains blocked by the previously established write-access restriction; rejected writes were not retried.

Next connected scope: Deuteronomy 19–26, followed by 27–34 and a whole-book consistency pass.
