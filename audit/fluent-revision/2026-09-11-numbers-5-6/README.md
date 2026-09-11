# Fluent Numbers 5–6 revision

All 58 verses (31 + 27) have a source-based draft, exact source binding, before/after text, TSW comparator, verse-specific rationale and F0–F3 editorial assessment. This batch follows `2e7038c947b7956652b04ffa82cddd46ff140731`. Cumulative draft coverage is 3,959 verses across 128 chapters: Genesis 1–50, Exodus 1–40, Leviticus 1–27, Numbers 1–6 and James 1–5.

The aim remains biblical fluency: clear sustained reading, recognizable biblical language, explicit relationships and restrained notes. The translation preserves difficult ritual actions and consequential uncertainty. The blessing keeps familiar source-faithful wording and the repeated face images; its words were not changed to meet an overlap target.

## Source and approach

Source: [Open Scriptures Hebrew Bible, pinned Numbers XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Num.xml).

- Commit: `6a5db284c715c18b239422e57bb89684e6a19f00`.
- Git blob: `2e7252db3bd33d510d2361a8b5016ac680b27dbb`.
- SHA-256: `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`.
- Original file: 1,496,833 bytes; 1,289 original records. Public Numbers has 1,288 slots, with later mapping differences that need separate handling.
- All 58 selected source verses were read before drafting. They align directly with public Numbers 5–6; no source note elements occur in this scope. Hashes use exact original XML verse substrings.

Supplemental comparison followed the Hebrew reading: [NET Numbers 5](https://www.biblegateway.com/passage/?search=Numbers+5&version=NET) and [NET Numbers 6](https://www.biblegateway.com/passage/?search=Numbers+6&version=NET), especially lexical and grammatical notes. The Hebrew/English text at [Mechon-Mamre, Numbers 5](https://mechon-mamre.org/p/pt/pt0405.htm) was checked after drafting. All 58 TSW comparator verses were also read after drafting. These translations did not serve as the English base text.

## Decisions needing editorial attention

Camp exclusion includes males and females and all three stated categories; a note distinguishes ritual uncleanness from moral guilt. Confession, full restitution, the added fifth, the family redeemer and the separate ram remain distinct. The possible pronoun referents at 5:10 are noted.

The ordeal keeps the husband’s suspicion separate from the woman’s guilt. Both alternatives in 5:14 and the innocent outcome in 5:28 remain explicit. The husband brings her; the priest directs the procedure and makes her drink. The draft retains the interrupted speech in 5:20, the woman’s doubled “Amen,” the bodily harm and public curse, and the asymmetrical final statement. “Thigh waste away” and “belly swell” preserve the bodily expressions; the note identifies reproductive implications and uncertainty without declaring pregnancy, a precise diagnosis or a medical mechanism. The repeated drinking instructions are retained without inventing a required number of separate drinks. Notes do not turn the passage into a political or doctrinal argument.

The Nazirite vow explicitly includes a man or woman; singular “they” continues that reference. Grape restrictions, uncut hair, the four named close relatives, seventh/eighth-day sequence, bird alternatives and loss of earlier days remain present. The unexpected death is involuntary, but the source’s sin, atonement and guilt-offering terminology is retained with a qualifying note. Each animal’s sex, age, condition and offering category is preserved. The hair goes into the fire beneath the peace-offering sacrifice. Priestly portions and permission to resume wine come in their stated order.

The blessing retains its three invocations of the LORD, singular “you,” the shining and lifted face, grace, peace and the placing of God’s name on Israel. God’s emphatic promise to bless remains separate from the priests’ speech. Poetry stays inside the verse paragraphs.

## Checks and limits

All 33 cumulative verse-ledger audits passed, including exact source-file identity, parent before-text objects, chapter and comparator hashes, coverage and verse bindings. Focused checks cover the sensitive conditions and agency, repeated divine name in the curse, interrupted oath, bodily order, restitution fraction, Nazirite gender scope, dates, animal details, offering sequence and blessing. Ordered verse labels, paragraph containment, quotation balance, translation-family audit and `git diff --check` passed.

All 58 verse texts changed: 25 F2 and 33 F3 editorial assessments. Automated comparison moved from 22 identical and 34 near-identical TSW verses to zero identical and three near-identical verses. Near-identical means nonidentical word similarity of at least 0.90. Shared short formulas remain where clear. These measures are triage, not evidence of fidelity, independent authorship or reader comprehension.

The work is an authoring-model draft and self-check. Independent scholarly review and reader testing remain pending. Revised chapters retain `QA_PASSED` qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING` and `publication_allowed: false`.

Only Numbers 5–6 supersede their earlier wording’s approvals and bindings. Earlier batches, TSW, unaffected Numbers records and unrelated work remain unchanged. Exact historical provenance is preserved. Companion quotations and bindings for these revised chapters require checking before later installation; the separate Companion branch was not modified and no public deployment occurred.

## Continuation

Next: Numbers 7–8, dedication gifts and Levite consecration. Preserve the twelve-day repetitions, donor names, exact quantities and service-age distinctions. Continue from the latest cumulative checkpoint without routine approval pauses. GitHub upload remains blocked by the previously established access restriction; no rejected write was retried.
