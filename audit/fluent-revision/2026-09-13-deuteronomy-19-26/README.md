# Fluent Deuteronomy 19–26

This batch completes a source-based draft of all 179 public verses in eight connected chapters. Cumulative coverage is now 5,694 public verses across 184 chapters. All 44 current source-binding ledgers pass. Each selected verse has before/after wording, an individual rationale, an editorial F0–F3 choice, a TSW comparator, and the hash of its exact original Hebrew XML record.

## Source and numbering

Source: [pinned Open Scriptures Hebrew Bible Deuteronomy](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Deut.xml).

- Repository commit: `6a5db284c715c18b239422e57bb89684e6a19f00`.
- Git blob: `5317431fd1d1fb5848d7f9f1d22d0753152f9991`.
- SHA-256: `aad16a6a2dcbdc6ee36d7d051e80a63bfeb69ecaae19f775ec5b6aa67fe22355`.
- Complete book: 959 original source records.
- Public 22:30 binds Hebrew 23:1; public 23:1–25 binds Hebrew 23:2–26. All other verses in this batch align directly.
- All 693 Hebrew records through chapter 26 are now bound exactly once across four Deuteronomy ledgers.

Every selected source verse was read before drafting. The source file's SHA-256 and Git blob were verified. Verse hashes cover the full original XML, including the written/read forms, accent notes, and numbering notes. Written/read forms are not rendered twice.

Supplemental comparison used the NET translators’ notes for selected difficulties in [chapter 21](https://www.biblegateway.com/passage/?search=Deuteronomy+21&version=NET), [chapter 22](https://www.biblegateway.com/passage/?search=Deuteronomy+22&version=NET), [chapter 23](https://www.biblegateway.com/passage/?search=Deuteronomy+23&version=NET), and [chapter 26](https://www.biblegateway.com/passage/?search=Deuteronomy+26&version=NET). These notes do not govern the draft. All 179 TSW comparator verses were read after independent drafting from Hebrew.

## Reading and editorial choices

The draft makes cases, conditions, speakers, and actions easier to follow while retaining the text's particular legal distinctions and consequences.

- Refuge: accidental killing and prior hatred, three towns plus three more, the avenger of blood, malicious witnesses, and all five life-for-life correspondences.
- Warfare: exemptions before battle, forced labor under peace terms, killing and captivity, the different rules for distant towns and the six named peoples, and food trees during siege.
- Captivity and households: the captive woman's mourning and humiliation, the ban on sale or enslavement after rejection, inheritance despite paternal preference, the rebellious son's execution, and same-day burial after public hanging.
- Sexual cases: the claims and evidence attributed to the legal actors, distinct town and open-country cases, explicit rape and the victim's non-liability, and the seized unbetrothed woman's prescribed marriage. Consent is not inserted where it is unstated. Uncertain terms and assumptions are identified in notes.
- Assembly and camp: named exclusions and their duration, uncertain mamzer and cultic-role terms, the literal dog expression, bodily functions, divine presence, and the escaped slave's right not to be returned and choice of residence.
- Livelihood and responsibility: the conditional divorce sequence, millstones and life, kidnapping, household privacy, sunset return of a pledge, same-day wages, individual criminal liability, and repeated provision for the resident foreigner, fatherless, and widow.
- Justice and remembrance: forty blows, the widow's public action in a brother-in-law case, explicit hand amputation, honest measures, vulnerable stragglers attacked by Amalek, and the command to remember.
- Harvest declarations: the shift from “my father” to “us” and back to “I,” firstfruits, the third-year tithe, and reciprocal declarations of covenant belonging.

Clear shared wording remains where it serves the passage. Deuteronomy 26:9 is retained from the prior Fluent wording (F0); its movement and milk-and-honey image need no artificial alteration.

## Checks and limits

`verification.json` records all 44 ledger audits, exact public/source coverage, selected content checks, verse order, paragraph containment, speech delimiters, qualified chapter metadata, preservation of earlier revisions and unrelated work, the translation-family audit, and `git diff --check`.

The overlap report is mechanical triage only. Before revision, 51 verses were identical to TSW and another 121 near-identical by word-token comparison. After revision, one is identical and four near-identical; mean sequence similarity is 0.633393. These figures do not prove fidelity, originality, or comprehension. Of the 179 verses, 178 changed from prior Fluent wording; the ledger has 104 F2, 74 F3, and one F0 choice.

This is authoring self-check and structural QA, not independent scholarly review or reader testing. Revised chapters retain `status: QA_PASSED` qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. Earlier approvals are superseded only for these changed chapters, with exact historical parent commits preserved.

TSW, earlier Fluent batches, and the separate Companion branch are unchanged. Companion quotations and bindings for these chapters require checking before later installation. Nothing was publicly deployed. GitHub upload remains blocked by the previously established access restriction; rejected writes were not retried.

Next: Deuteronomy 27–34, then a whole-book consistency pass.
