# Fluent Leviticus 13–15 revision

All 149 verses (59 + 57 + 33) received a source-based draft and a verse-specific rationale. The cumulative revision now covers 3,310 verses in 110 chapters: Genesis 1–50, Exodus 1–40, Leviticus 1–15, and James 1–5. These are editorial drafts. Structural QA is not independent editorial approval; publication remains disallowed.

## Source and method

The complete selected Hebrew records were read from [OSHB's pinned Leviticus XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Lev.xml). The full file's SHA-256, Git blob and 859-record count were verified. The 149 selected verses align directly with public numbering; every source hash covers the exact original XML substring. The vowel annotation at 14:48 remains included. The source contains no verse-numbering or written/read annotation in this selected scope.

English was composed from the Hebrew. Selected [NET chapter 13](https://www.biblegateway.com/passage/?search=Leviticus+13&version=NET), [chapter 14](https://www.biblegateway.com/passage/?search=Leviticus+14&version=NET), and [chapter 15 translator notes](https://www.biblegateway.com/passage/?search=Leviticus+15&version=NET) were consulted for lexical and grammatical comparison after reading each Hebrew chapter, before and during drafting. Their speculative diagnoses and symbolic explanations were not adopted. All TSW verse comparators were read after drafting. The assembled text was then reread as connected instructions, and focused checks were run. This was an authoring-model self-check, not an independent scholarly review.

## Editorial decisions

- Chapter 13 preserves the observation criteria, provisional confinement, raw flesh, complete whitening, black versus yellow hair, repeated clean/unclean verdicts, and the exclusion outside the camp. The draft uses descriptive language and notes uncertain skin-condition terms. It does not assign modern diagnoses or add claims of contagion.
- The cloth instructions retain wool, linen, warp, weft and leather; unchanged appearance, fading, recurrence and disappearance have distinct outcomes. The uncertain corrosion and front/back wording is noted.
- Chapter 14 retains healing before the cleansing rite, live and slaughtered birds, all materials, return to camp before return to the tent, seven-day and eighth-day stages, two male lambs and a year-old female lamb, and the less costly offering provision. Ancient measures remain. Blood and oil sites and right/left distinctions are preserved. The slaughtering agent in 14:19 remains unspecified.
- The repeated affordability wording in 14:30–31 remains, with the one/other construction read across labels. House instructions preserve the LORD's agency, the owner's tentative report, emptying before inspection, material removal and destruction, outside-city disposal, and atonement for a house.
- Chapter 15 distinguishes the male discharge, semen, menstrual blood and prolonged bleeding. It retains blocked as well as flowing discharge, different touching/carrying rules, the man's unwashed hands, and sex-specific periods and offerings. The ambiguous pronoun in 15:23 and longer textual witnesses to 15:3 are noted; the pinned source is followed. The speech punctuation distinguishes the instructions relayed to Israel from the plural address to Moses and Aaron in 15:31.

## Evidence and limits

`leviticus-verse-review.json` records all before/after text, TSW comparators, source bindings, rationales and editorial F0–F3 choices. All 149 verses changed: 83 F2 and 66 F3 decisions. There was no required change percentage.

`verification.json` records successful audits of all 25 revision ledgers, 149 unique current-batch source bindings, 3,310 cumulative verses, chapter structure and metadata, focused content assertions, the translation-family audit, preservation of prior work, and `git diff --check`.

`overlap-before-after.json` is triage only. Against TSW, 29 identical and 115 near-identical verses before revision became 0 identical and 5 near-identical verses afterward; mean token similarity moved from 0.957501 to 0.672007. These figures do not establish fidelity, originality, comprehension, or approval.

Only chapters 13–15 supersede their prior wording's approvals and bindings. Earlier batches, historical provenance, TSW and unrelated work remain unchanged. Companion quotes or bindings for these chapters need checking at later installation; the separate Companion branch was not modified. No public deployment or rejected GitHub write was attempted. GitHub upload remains blocked by the previously established access restriction.

Next: Leviticus 16–17. Independent editorial review and reader testing remain pending.
