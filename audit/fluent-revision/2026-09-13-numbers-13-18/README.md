# Numbers 13–18: source-based Fluent revision

This larger batch completes 214 verses across six connected chapters: 33 + 45 + 41 + 50 + 13 + 32. Matt requested larger batches during this work. The source-reading, rationale and verification requirements remain unchanged; future batches should normally aim for connected scopes of roughly 150–250 verses when feasible.

Fluent’s goal is biblical fluency: readers can follow competing voices, recognize recurring words and images, and connect the narrative and ritual instructions. TSW serves as a comparator. The draft is not a synonym replacement of TSW.

## Source and method

Every selected Hebrew verse was read from [the pinned OSHB Numbers source](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Num.xml) before drafting. Source commit: `6a5db284c715c18b239422e57bb89684e6a19f00`; Git blob: `2e7252db3bd33d510d2361a8b5016ac680b27dbb`; SHA-256: `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`.

All 214 source records are bound by hashes of exact original XML substrings, including all 34 annotations across 33 records. These include written/read forms at 14:36 and 16:11, form annotations and the source’s public-numbering notices.

| Public verse range | Pinned Hebrew range |
| --- | --- |
| Numbers 13–15 | Numbers 13–15 |
| Numbers 16:1–35 | Numbers 16:1–35 |
| Numbers 16:36–50 | Numbers 17:1–15 |
| Numbers 17:1–13 | Numbers 17:16–28 |
| Numbers 18 | Numbers 18 |

Selected NET grammatical and lexical notes provided supplemental comparison: [Numbers 13–14](https://www.biblegateway.com/passage/?search=Numbers+13-14&version=NET), [Numbers 16](https://www.biblegateway.com/passage/?search=Numbers+16&version=NET), and [Numbers 18](https://www.biblegateway.com/passage/?search=Numbers+18&version=NET). The English was drafted from Hebrew. All 214 TSW comparator verses were then read. The ledger records before/after wording, source binding, comparator and an individual editorial rationale for each verse.

## Editorial decisions

- The twelve scouts retain their tribes, names and fathers. Hoshea remains Hoshea until the naming notice. The anomalous singular arrival verb at Hebron is noted; the text does not silently identify its subject as Caleb. Nephilim, the devouring land and grasshopper comparisons remain within the scouts’ report.
- Caleb and Joshua’s confidence contrasts with the people’s fears and plans. Bread, shade, eye-to-eye appearance, raised-hand oath, corpses, shepherd life and prostitution imagery remain visible. Pardon and subsequent judgment both remain explicit. The Exodus 34 quotation keeps shared wording only where this Hebrew quotation contains the corresponding clauses.
- All offering quantities remain in their ancient units. The resident foreigner shares the prescribed obligations and forgiveness. Unintentional error remains distinct from defiance. The Sabbath execution keeps its actors and lethal outcome; no unstated motive is assigned to the man.
- Tassels link seeing, remembering and acting, and the verb used for scouting returns in the warning about the heart and eyes. Sacrificial names were checked against earlier revised chapters: offering by fire, peace offering, sin offering, guilt offering and wave offering remain recognizable. Alternative labels appear selectively in vocabulary.
- Korah’s difficult opening syntax is noted. The rebels’ holiness claim and their description of Egypt as flowing with milk and honey remain their own speech. Eye-gouging, household deaths, little ones, Sheol and the separate fire remain explicit. The 250 incense offerers and the later 14,700 plague deaths are not conflated. Korah’s surviving sons are acknowledged by a cross-reference, not erased by overgeneralization.
- Twelve staffs remain twelve, with Aaron’s among them. Buds, blossoms and ripe almonds are all retained. The frightened people’s repeated approach/death language leads into the priestly and Levitical access distinctions.
- Chapter 18 distinguishes sanctuary responsibility from priesthood responsibility, male priestly portions from gifts shared by clean sons and daughters, mandatory firstborn redemption from sacrificial animals, and tithes received from a tithe of those tithes. The five-shekel price, twenty-gerah standard, right thigh and covenant of salt remain exact.

Numbers 16:32 retains its clear existing wording after source assessment (F0). The other 213 verses changed: 142 F2 and 71 F3. The before comparison found 135 identical and 73 nearly identical verses; afterward, four identical and ten nearly identical verses. These measurements are triage, not evidence of fidelity, independent authorship or reader comprehension. No change quota was used.

## Checks, status and continuation

`verify_batch.py` passed all 37 cumulative source-binding ledger audits, the translation-family audit and `git diff --check`. It checks complete coverage, original source hashes, source/public mapping, paragraph containment, quotation balance, poetic lineation, names, quantities, important repetitions, review status and preservation of earlier batches. `verification.json` and `overlap-before-after.json` retain the evidence. The authoring self-check also reviewed the connected final text and corrected terminology, quotation and paragraph boundaries before the passing run.

Cumulative revised-draft coverage: 4,398 verses across 140 chapters—James, Genesis, Exodus, Leviticus and Numbers 1–18. Structural QA is distinct from independent scholarly review and reader testing, which remain pending. Chapters retain structural `QA_PASSED`, editorial `REVIEW_PENDING`, and `publication_allowed: false`.

Only Numbers 13–18 supersede prior wording’s approvals and bindings. Historical provenance remains in Git; earlier batches, TSW and unrelated work are preserved. Companion quotations and bindings for these six chapters need later checking. No Companion branch or public deployment was changed. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried.

Next connected scope: Numbers 19–24. Recover the latest cumulative checkpoint first, continue the larger-batch preference, and preserve all source and review standards without routine approval pauses.
