# Fluent biblical-fluency revision: Genesis 1–11

September 10, 2026. Complete passage draft; editorial review pending. This batch follows the James revision and does not revise Genesis 12–50.

## Purpose and reading approach

Fluent helps readers follow the Bible's stories, arguments, imagery, and recurring vocabulary in natural English. This revision addresses all 299 verses of Genesis 1–11; 297 have changed main-text wording or punctuation. Names and clear inherited wording remain where they serve the text. Distinctiveness comes from sustained translation judgment, not a required percentage of different words.

The chapters retain the creation-day refrain, human/ground connection, image and likeness, offspring, walking with God, corruption and destruction, all flesh, covenant, remembering, and the family-account formula. Short notes explain consequential choices and connect repeated terms. Vocabulary gives readers a bridge into biblical language without requiring Hebrew knowledge.

Read a section through before consulting its notes. Then look for a repeated word or image and trace what changes around it: the ground in chapters 2–5, the waters in chapters 1 and 7–8, or the covenant's living partners in chapter 9. Genealogical formulas and numbers are part of the text's structure and remain visible.

## What is preserved and clarified

- Genesis 2:4 includes the complete source verse under one label. Poetry in 2:23 and subsequent chapters stays within its verse paragraphs.
- Divine plurals, the serpent's identity, the offspring in 3:15, the unfinished speech in 3:22, the sons of God, and the Nephilim are not resolved by added narrative explanation.
- Genesis 4:8 supplies no missing speech. “Side” in 2:21, the roof wording in 6:16, seven pairs in 7:2, and other consequential decisions are flagged for review.
- Every age, date, named family member, and place in the selected source passage is retained. Genealogies do not turn compressed three-son lists into claims of simultaneous births.
- The covenant includes nonhuman creatures. Genesis 9 preserves Canaan as the curse recipient and the unresolved pronoun in 9:27.

## Source and review record

The Hebrew source is [Open Scriptures Hebrew Bible, Genesis](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Gen.xml), at commit `6a5db284c715c18b239422e57bb89684e6a19f00`, blob `dcc8be362134981d3054e9b64d3a465d08492a33`.

The [verse ledger](genesis-verse-review.json) records all 299 before/after texts, TSW comparators, exact source-verse hashes, and individual rationales. Source hashes include the complete original XML verse record, including written/read annotations. They do not hash a reserialized or normalized substitute. The full source has 1,533 verses; the audit independently extracts the 299 records in chapters 1–11.

The 58 F3 decisions identify consequential interpretive choices for review. F0/F2/F3 labels are editorial assessments; overlap scores are separate observations. Automated checks verify source identity, coverage, file bindings, paragraph wrappers, verse labels, and ledger consistency. They do not certify Hebrew interpretation or actual reader comprehension. No independent human editorial approval or reader testing has occurred.

Revised chapter metadata explicitly distinguishes structural QA from `REVIEW_PENDING` editorial status and sets `publication_allowed: false`. Prior chapter reviews are superseded through their recorded Git history. Old book-level deployment data and mechanical ledger entries are historical for chapters 1–11; chapters 12–50 retain their previous records and have not received this pass. Any Companion linked to the older chapter wording must be rebound and reviewed before publication; that separate branch is not changed here.

## Comparison and verification

The [before](overlap-before.json) and [after](overlap-after.json) reports measure matching verse labels, excluding apparatus. Near-identical means nonidentical wording with token-sequence similarity at least 90%. This is an editorial triage measure, not a fidelity or originality test. The five existing corpus alignment exceptions remain documented in the reports.

Genesis 1–11 has four verses with identical normalized words to TSW after revision, including short name lists; ten more meet the near-identical threshold. Those are retained where the editorial reading supports them. Whole-corpus identical-word counts move from 20,290 after James to 20,072 after this batch. The remainder of Fluent still needs sustained source-based review.

From the repository root, using the exact source file above:

```bash
python3 tools/audit_fluent_revision.py audit/fluent-revision/2026-09-10-genesis-1-11/genesis-verse-review.json --source-text /path/to/Gen.xml
python3 tools/audit_fluent_revision.py audit/fluent-revision/2026-09-10/james-verse-review.json --source-text /path/to/Jas.txt
python3 tools/audit_translation_family.py
python3 tools/audit_translation_overlap.py --json-output /tmp/fluent-overlap.json
git diff --check
```

Next passage: Genesis 12–25, followed by the remaining connected Genesis narratives and a whole-book consistency review.
