# Fluent Translation audit

17 September 2026 · Full corpus, with targeted bilingual review

**Finding: Fluent is substantially distinct from TSW. Compliance with the editorial criteria is partial, not yet complete.** The complete corpus passes the reproducible source-binding and structural checks. This audit corrected 31 chapters, including two Scripture verses, but does not certify every translation decision or authorize publication.

## Scope and standard

The audit covers **66 books, 1,189 chapters and 31,083 public verse records**, supported by 145 revision ledgers and 66 bound source files. Automated checks covered the entire corpus. Fresh bilingual self-review covered **103 selected verses across 34 books**, including every identical verse of at least 25 words, plus supplementary checks of edited transitions and notes. This was a targeted selection, not a random sample or a fresh verse-by-verse review of the whole Bible.

The standards are the four supplied documents and the repository's **Fluent Translation Philosophy**. Their exact copies and hashes accompany the audit. The shared requirements govern fidelity, ambiguity, gender, imagery, source choice and restraint. Fluent's specific policy supplies its natural-reading posture and expressly permits restructuring that preserves meaning. The older form-conscious instructions and Fluent's permission to restructure are not identical. This audit records that distinction rather than silently rewriting either policy: it tests whether restructuring improves intelligibility without losing significant syntax, repetition or uncertainty. Formal identity with TSW is not Fluent's goal.

## Distinction from TSW

The comparison removes punctuation, capitalization and markup, preserves words and continuation lines, and compares Scripture rather than headings or apparatus. A merely punctuated or capitalized revision therefore does not count as new wording.

| Measure | Result |
| --- | ---: |
| Matched public verse labels | 31,082 |
| Identical word sequences | 966 — **3.11%** |
| Nonidentical, but token similarity at least 90% | 2,477 — **7.97%** |
| Combined exact/near-exact share | **11.08%** |
| Mean verse-level token sequence similarity | **71.79%** |
| Chapters whose every Fluent verse is word-identical to TSW | **0** |
| Identical verses of at least 25 words | 25; all source-reviewed in this audit |
| Runs of at least three identical verses | 34; inventory included |

Thus **96.89% of matched verses differ in wording**. This is not a claim that 96.89% of the words are different, that every difference improves the text, or that a similarity score proves independent authorship.

The archived pre-revision baseline had 65.31% identical verses and 94.81% mean similarity. Its matched denominator was 31,083, one greater than today's, so it is a useful historical comparison rather than an exact controlled experiment. The change is nevertheless substantial.

The longest identical run is **Joshua 12:10–23**, a list of kings and repeated counts. The next is **Revelation 7:5–8**, a tribal list with repeated numbers. These were checked against the sources and retained. Ecclesiastes 3:6–8 likewise preserves deliberate paired repetition. Familiar quotations, names, numbers and meaningful repetition should not be distorted to make two translations look less alike. Of the 966 identical verses, 380 have ten or fewer words.

Distinctive reading choices are visible beyond statistics: Genesis 1:2 reduces mechanical conjunctions; Ruth 1:16 uses shorter repeated pledges; Psalm 23 sustains clear personal address; and Daniel 7:13 clarifies the sequence of approach and presentation. John 1:18 also follows a source reading different from TSW's. These examples support a distinct reading posture; they do not establish the drafting history independently of the records.

### Alignment qualifications

Six verse-label entries are unmatched: TSW Acts 19:41; Fluent Romans 16:24; TSW Romans 16:25–27; and TSW Nehemiah 7:68. They are excluded from the matched denominator. Acts' dismissal clause is included in the source's 19:40. Romans and Nehemiah involve documented source-text differences, not arbitrary omissions made to lower overlap.

The unusual Romans ending was separately checked: the published SBLGNT text ends at 16:24 and places the doxology in its apparatus. [SBLGNT Romans 16](https://www.biblegateway.com/passage/?search=Romans%2016&version=SBLGNT).

Some shared labels also contain different clause boundaries, including Philippians 2:7–8, 1 John 2:13–14 and Revelation 4:6–11. Psalm superscriptions add another difference in comparison scope. Consequently the overall similarity figure is a **triage measure**, not an exact measure of translation independence. Passage-level review must precede any revision at these locations. The evidence includes declared alignment exceptions; it does not claim an exhaustive clause-level alignment of both Bibles.

## Criteria findings

| Criterion | Finding | Evidence and limit |
| --- | --- | --- |
| Hebrew/Aramaic and critical Greek foundation | **Binding checks pass** | All 145 ledgers match their exact source files, source records, current English and TSW comparators. This verifies documentary consistency, not the correctness of every interpretation. |
| Complete source coverage and verse accounting | **Pass within the declared source editions** | Chapter counts, verse counts, merges, partitions and declared omissions validate. Different editions and versifications are not silently equated. |
| Clear, natural, reverent English | **Partially met; improvements applied** | Distinct connected prose is evident in the samples. Corrected two awkward Revelation expressions and paragraph problems. Sustained reading tests remain outstanding. |
| Significant syntax and argument | **Partially met; improvements applied** | Rejoined 24 paragraph boundaries that interrupted clauses, lists or linked arguments. Other paragraph and heading candidates remain for contextual review. |
| Repetition, concrete imagery and literary voice | **Supported in the sample; whole-book review open** | Checked repeated lists, Ecclesiastes' pairs, Psalm 23, maternal divine images, servant suffering and apocalypse. No global synonym substitutions were made. |
| Consequential ambiguity | **Qualified compliance** | Existing notes preserve several important alternatives. Neutralized a Galatians heading and added a missing alternative in 2 Thessalonians 1:12. Revelation 13:8 remains a reading-flow candidate. |
| Gender and divine reference | **Supported in the sample; not globally certified** | Specific family genders, female figures, generic humans and maternal metaphors remain. Revised Revelation 21:7 preserves both a generic recipient and the sonship formula. |
| Significant textual variants | **Sample supported; complete apparatus review open** | John 1:18, Mark's endings, John 7:53–8:11, Romans' ending and Revelation variants are visible. Presence of some good notes does not prove that every significant variant is adequately noted. |
| Lexical consistency and names | **Not fully established by this audit** | Word identity is not semantic consistency. Contextual choices such as kidneys/heart and faith/faithfulness need cross-book review. Source-hash success cannot replace that work. |
| Selective notes; no commentary or unnecessary defense | **Needs further revision** | Removed six commentary/application notes, revised two others and added one grammatical alternative. Many process-oriented or defensive notes remain as review candidates. |
| Chapter-file formatting | **Structural pass** | Front matter, labels, paragraph nesting and Notes/Vocabulary headings pass. Used the valid `## Notes`/`## Vocabulary` forms shown in the supplied example; the prose instruction's unspaced shorthand was not imposed. Final print/web typography was not audited. |
| Consistent presentation | **Needs a house-style pass** | 121 chapters use bold LORD/GOD somewhere in Scripture while others use plain forms. This is a formatting inconsistency, not a claim that the divine name is mistranslated. |
| Documented changes and review status | **Pass for this audit's records; approval pending** | Exact changes, source references, old/new hashes and updated chapter bindings are retained. Structural QA remains separate from independent editorial approval. |

## Corrections made

**31 chapter files changed; 29 retain exactly the same Scripture verse text.** Seventeen affected ledgers and all affected chapter review records were rebound. TSW and Companion content were unchanged.

| Correction | Result |
| --- | --- |
| 24 internal paragraph boundaries | Joined dependent clauses, lists and connected arguments, including Jeremiah 7:5–7 and 1 Corinthians 8:5–6. |
| Luke 3 and 6 | Added paragraphs at narrative/teaching transitions and descriptive headings. Luke 6 had been a single 1,072-word paragraph beneath “Lord of the Sabbath.” |
| Galatians 2 heading | Changed “Set Right through the Faithfulness of Christ” to “Justification and Life in Christ”; the heading no longer treats one interpretation of the genitive as settled. |
| Six apparatus entries | Removed commentary/application notes in Luke 6/21, 1 Corinthians 6, 2 Corinthians 1 and Galatians 2. Their wording is archived for possible future Companion review, not inserted there. |
| 1 Corinthians 7:15 note | Replaced pastoral application with the Greek distinction between enslaving and binding. |
| 2 Corinthians 4:17 note | Describes the light/weight and momentary/eternal contrasts without prescribing application. |
| 2 Thessalonians 1:12 note | Added the alternative “our God and Lord Jesus Christ” alongside the main text's “our God and the Lord Jesus Christ.” |
| Revelation 2:23 | “I will kill her children with death” → “I will put her children to death.” The note retains the literal expression and possible plague sense. |
| Revelation 21:7 | Made the generic singular referent explicit with “that person,” preserving “my son.” |

The two Scripture refinements barely affect the overlap score. They were made for faithful readability, not statistical differentiation.

## Work still required

1. **Finish the apparatus pass.** After these corrections, 445 entries in 346 chapters trigger the process-language screen; 484 trigger a broader defense-language screen. The sets overlap, and neither number is a count of confirmed errors. Review such wording as “pinned,” “the draft retains” and explanations of what the translator did not do. Preserve useful textual evidence while removing workflow language and unnecessary argument. Separately review all notes for commentary that keyword screens cannot identify.
2. **Finish continuous reading and paragraph/heading review.** Thirty-five punctuation-based boundary candidates remain; many may be legitimate poetic divisions or chapter boundaries. Two clear priority locations are the headings inside the continuing constructions at 2 Kings 5:19–20 and Proverbs 6:23–24. Review long units such as Revelation 18, Isaiah 43 and Daniel 11 in context; paragraph length alone is not an error.
3. **Check recurring language across books.** Compare source terms with their English renderings in context, especially covenant, righteousness, faith/faithfulness, flesh, Spirit/spirit, steadfast/faithful love, divine titles and bodily images. Do not replace context-sensitive vocabulary globally.
4. **Test the actual reading voice.** Prioritize the higher-overlap letters, including 1 Thessalonians, Colossians and Galatians, and difficult phrasing such as Revelation 13:8 and Psalm 23:6. A listener should be able to follow the argument while hearing its tensions and repetitions. Shared wording alone is not grounds for revision.
5. **Complete independent editorial review, reader testing, house style and Companion reconciliation.** Existing self-checks and this audit do not satisfy those separate gates. Historical approvals do not transfer automatically to revised wording. Publication remains disabled.

These are substantive qualifications. **“Distinct from TSW” is supported; “meets every criterion throughout” is not yet a defensible certification.**

## Reproducible evidence

The checkpoint includes the before/after corpus screens, every verse's comparison metrics, chapter summaries, identical runs, alignment caveats, full source-binding results, criteria copies, 103 exact source comparisons, targeted review judgments, the correction ledger and an ordered remaining-work list. `verify_audit.py` checks the revised state without relabeling historical verifiers as current approvals. All original source files and prior Git history remain available.

The figures describe the audited working text based on checkpoint 97, not an independently refreshed public website. The detailed book comparison follows.

## Book-by-book comparison

Exact and near-exact percentages are verse-label comparisons under the qualifications above. Near-exact excludes exact matches; 90% is a review threshold, not an acceptance rule.

| Book | Matched verses | Identical | Near-identical | Mean similarity |
| --- | ---: | ---: | ---: | ---: |
| Genesis | 1,533 | 29 (1.89%) | 57 (3.72%) | 66.83% |
| Exodus | 1,213 | 21 (1.73%) | 80 (6.60%) | 70.38% |
| Leviticus | 859 | 7 (0.81%) | 49 (5.70%) | 68.65% |
| Numbers | 1,288 | 18 (1.40%) | 60 (4.66%) | 67.15% |
| Deuteronomy | 959 | 14 (1.46%) | 58 (6.05%) | 70.83% |
| Joshua | 658 | 66 (10.03%) | 37 (5.62%) | 72.00% |
| Judges | 618 | 9 (1.46%) | 24 (3.88%) | 71.30% |
| Ruth | 85 | 3 (3.53%) | 5 (5.88%) | 68.49% |
| 1 Samuel | 810 | 4 (0.49%) | 19 (2.35%) | 66.83% |
| 2 Samuel | 695 | 18 (2.59%) | 33 (4.75%) | 71.39% |
| 1 Kings | 816 | 21 (2.57%) | 71 (8.70%) | 73.78% |
| 2 Kings | 719 | 7 (0.97%) | 42 (5.84%) | 71.38% |
| 1 Chronicles | 942 | 90 (9.55%) | 79 (8.39%) | 73.15% |
| 2 Chronicles | 822 | 11 (1.34%) | 59 (7.18%) | 71.90% |
| Ezra | 280 | 3 (1.07%) | 19 (6.79%) | 68.05% |
| Nehemiah | 405 | 40 (9.88%) | 38 (9.38%) | 73.87% |
| Esther | 167 | 2 (1.20%) | 5 (2.99%) | 68.62% |
| Job | 1,070 | 45 (4.21%) | 119 (11.12%) | 72.71% |
| Psalms | 2,461 | 82 (3.33%) | 199 (8.09%) | 71.07% |
| Proverbs | 915 | 51 (5.57%) | 120 (13.11%) | 74.52% |
| Ecclesiastes | 222 | 5 (2.25%) | 24 (10.81%) | 67.87% |
| Song of Songs | 117 | 5 (4.27%) | 12 (10.26%) | 78.26% |
| Isaiah | 1,292 | 4 (0.31%) | 32 (2.48%) | 63.31% |
| Jeremiah | 1,364 | 22 (1.61%) | 120 (8.80%) | 73.97% |
| Lamentations | 154 | 8 (5.19%) | 9 (5.84%) | 71.24% |
| Ezekiel | 1,273 | 31 (2.44%) | 93 (7.31%) | 71.26% |
| Daniel | 357 | 3 (0.84%) | 13 (3.64%) | 68.95% |
| Hosea | 197 | 9 (4.57%) | 18 (9.14%) | 76.76% |
| Joel | 73 | 2 (2.74%) | 13 (17.81%) | 79.26% |
| Amos | 146 | 0 (0.00%) | 13 (8.90%) | 74.51% |
| Obadiah | 21 | 1 (4.76%) | 4 (19.05%) | 81.88% |
| Jonah | 48 | 0 (0.00%) | 3 (6.25%) | 70.87% |
| Micah | 105 | 1 (0.95%) | 9 (8.57%) | 73.27% |
| Nahum | 47 | 0 (0.00%) | 1 (2.13%) | 71.30% |
| Habakkuk | 56 | 4 (7.14%) | 2 (3.57%) | 74.68% |
| Zephaniah | 53 | 0 (0.00%) | 6 (11.32%) | 76.55% |
| Haggai | 38 | 0 (0.00%) | 6 (15.79%) | 77.63% |
| Zechariah | 211 | 3 (1.42%) | 23 (10.90%) | 75.50% |
| Malachi | 55 | 0 (0.00%) | 6 (10.91%) | 73.31% |
| Matthew | 1,068 | 24 (2.25%) | 112 (10.49%) | 74.50% |
| Mark | 673 | 6 (0.89%) | 60 (8.92%) | 72.05% |
| Luke | 1,149 | 39 (3.39%) | 111 (9.66%) | 73.84% |
| John | 878 | 56 (6.38%) | 124 (14.12%) | 78.79% |
| Acts | 1,002 | 13 (1.30%) | 61 (6.09%) | 70.04% |
| Romans | 429 | 30 (6.99%) | 60 (13.99%) | 77.98% |
| 1 Corinthians | 437 | 34 (7.78%) | 69 (15.79%) | 77.78% |
| 2 Corinthians | 257 | 16 (6.23%) | 34 (13.23%) | 76.84% |
| Galatians | 149 | 16 (10.74%) | 28 (18.79%) | 82.28% |
| Ephesians | 155 | 12 (7.74%) | 22 (14.19%) | 77.91% |
| Philippians | 104 | 4 (3.85%) | 9 (8.65%) | 73.79% |
| Colossians | 95 | 12 (12.63%) | 10 (10.53%) | 79.00% |
| 1 Thessalonians | 89 | 14 (15.73%) | 11 (12.36%) | 81.85% |
| 2 Thessalonians | 47 | 2 (4.26%) | 10 (21.28%) | 81.00% |
| 1 Timothy | 113 | 11 (9.73%) | 17 (15.04%) | 79.56% |
| 2 Timothy | 83 | 4 (4.82%) | 15 (18.07%) | 78.94% |
| Titus | 46 | 1 (2.17%) | 5 (10.87%) | 72.43% |
| Philemon | 25 | 2 (8.00%) | 3 (12.00%) | 79.53% |
| Hebrews | 303 | 11 (3.63%) | 20 (6.60%) | 73.96% |
| James | 108 | 0 (0.00%) | 0 (0.00%) | 55.85% |
| 1 Peter | 105 | 5 (4.76%) | 10 (9.52%) | 74.31% |
| 2 Peter | 61 | 0 (0.00%) | 8 (13.11%) | 72.44% |
| 1 John | 105 | 5 (4.76%) | 20 (19.05%) | 79.72% |
| 2 John | 13 | 1 (7.69%) | 5 (38.46%) | 83.97% |
| 3 John | 15 | 0 (0.00%) | 7 (46.67%) | 87.39% |
| Jude | 25 | 0 (0.00%) | 5 (20.00%) | 74.71% |
| Revelation | 404 | 9 (2.23%) | 61 (15.10%) | 78.28% |
