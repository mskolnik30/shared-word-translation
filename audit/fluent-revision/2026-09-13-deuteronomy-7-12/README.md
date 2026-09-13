# Deuteronomy 7–12: Fluent revision

This connected batch adds 161 source-based draft verses in six complete chapters. Cumulative draft coverage is 5,381 public verses in 170 chapters: Genesis, Exodus, Leviticus, Numbers, Deuteronomy 1–12, and James.

Fluent aims at biblical fluency through natural sustained reading, clear speakers and conditions, and recognizable recurring language. All 161 selected Hebrew records were read before drafting; all 161 TSW verses were read afterward as comparators. No synonym engine or minimum-change quota governed the wording.

## Source and mapping

The verified source is [Open Scriptures Hebrew Bible, Deuteronomy](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Deut.xml), commit `6a5db284c715c18b239422e57bb89684e6a19f00`, Git blob `5317431fd1d1fb5848d7f9f1d22d0753152f9991`, SHA-256 `aad16a6a2dcbdc6ee36d7d051e80a63bfeb69ecaae19f775ec5b6aa67fe22355`, with 959 original records.

Public 7–11 and 12:1–31 align directly. Public 12:32 binds Hebrew 13:1 in full, including the source's KJV numbering note. All original XML substrings include their written/read and other annotations; none is normalized before hashing. Thirteen selected records contain annotations. At 7:9 and 8:2, written/read spelling differences represent one word, not duplicate phrases. The new draft avoids the duplicated command phrase found in the earlier 8:2 comparator without modifying TSW.

## Editorial choices

- Chapter 7 retains all seven nations, the destruction and no-mercy commands, love and oath as the basis for choice, fertility and disease claims, and the repeated snare image. Hornets remains in the text with its lexical uncertainty noted. Gradual removal is not harmonized with the quick destruction language in chapter 9.
- Chapter 8 carries the contrast between wilderness dependence and pride amid abundance. It preserves hunger, manna, the father-son discipline image, every listed land product and mineral, fiery snakes, and the warning against crediting one's own hand.
- Chapter 9 keeps all three denials that Israel receives land for its righteousness, the finger-of-God image, repeated forty-day notices, the your-people exchange, Aaron's danger, and the calf's destruction. The retelling is not reorganized into an imposed chronology.
- Chapter 10 preserves the ark-making and journey accounts as given, including Moserah as the named place of Aaron's death. The note identifies the difference from Numbers. Circumcised hearts and stiff necks remain bodily images. Justice for the fatherless and widow and love for the resident foreigner retain their concrete food-and-clothing expression.
- Chapter 11 unfolds the elliptical eyewitness contrast, preserves foot-irrigation and land-drinking imagery, distinguishes the first-person divine rain promise, repeats daily teaching instructions, and retains all boundary names and the Gerizim/Ebal assignment.
- Chapter 12 distinguishes ordinary local meat from offerings brought to the chosen place, clean/unclean diners from animal categories, and blood disposal in the two settings. Enslaved people and Levites remain explicitly included in shared meals. Child burning is explicit, and no unnamed city or slaughter method is inserted.

Supplemental primary comparison: [NET translators' notes on Deuteronomy 7](https://www.biblegateway.com/passage/?search=Deuteronomy+7&version=NET) and [11](https://www.biblegateway.com/passage/?search=Deuteronomy+11&version=NET), consulted before drafting for selected lexical and grammatical questions. Their extended interpretations were not imported into Fluent's apparatus.

## Checks and limits

All 42 cumulative source-binding ledger audits passed, as did the translation-family audit, verse/paragraph structure checks, focused textual assertions, and `git diff --check`. Each verse has before/after wording, an individual rationale, an editorial F0–F3 choice, exact source binding, and a TSW comparator. Source records are unique across current ledgers, including the boundary record at Hebrew 13:1.

The batch changes 159 verse texts and retains two. Classifications: 111 F2, 48 F3, two F0. Whole-verse TSW matches fall from 106 to two; near-identical nonmatches fall from 50 to eleven under the 0.90 threshold. Overlap is surface triage, not proof of fidelity, legal originality, or reader comprehension.

Only chapters 7–12 supersede their previous wording's approvals and bindings. Prior batches, unrevised chapters, historical provenance, TSW, and the separate Companion branch are preserved. Revised chapters have structural QA, independent editorial review pending, and publication disallowed. No human scholarly review or reader testing occurred. Companion quotations and bindings for these chapters require later checking. GitHub upload remains blocked by the established connection restriction; no rejected write was retried, and nothing was publicly deployed.

Next: Deuteronomy 13–18, then 19–26. Public chapter 13 begins with Hebrew 13:2; verify the full next mapping before drafting so Hebrew 13:1 is neither duplicated nor omitted.

Reproduce the checks with `verify_batch.py` and the six exact pinned source files, supplied through `--genesis-source`, `--exodus-source`, `--leviticus-source`, `--numbers-source`, `--deuteronomy-source`, and `--james-source`. Source manuscript files are not redistributed in this checkpoint.
