# Fluent revision: Genesis 42–45

This batch covers all 134 verses of Genesis 42–45, from the brothers’ first journey to Joseph’s disclosure and Jacob’s decision to see him. It advances the connected Genesis 42–50 queue in complete chapters. Genesis 46–50 remains next, followed by the whole-book Genesis consistency review.

Cumulative draft coverage is Genesis 1–45 and James 1–5: 1,495 verses in 50 chapters. Independent editorial review remains pending. No publication or Companion installation occurred.

## Source and editorial method

Every source verse was read before drafting from the exact [Open Scriptures Hebrew Bible Genesis XML](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Gen.xml), commit `6a5db284c715c18b239422e57bb89684e6a19f00`, Git blob `dcc8be362134981d3054e9b64d3a465d08492a33`. Both whole-file hashes and the 1,533-record count were verified. Verse hashes cover original XML substrings, including the written/read material and source annotations at 43:28. Public and Hebrew verse numbering align in these four chapters.

TSW was read as a comparator after the Hebrew draft. Supplemental comparison used the [NET Genesis 43 text](https://bible.org/sites/bible.org/resources/netbible/gen43.htm) and [NET Genesis 44 translators’ notes](https://bible.org/sites/bible.org/resources/netbible/gen44_notes.htm). These aided assessment of drinking language, the steward’s changed penalty, divination, pronouns, and gray-head imagery. Attempts to retrieve the corresponding Genesis 45 page failed; no consultation of that page is claimed. Fluent’s wording is bound to the Hebrew source, not to a secondary translation.

The [verse ledger](genesis-verse-review.json) records source bindings, before and after text, TSW comparators, and individual rationales. Editorial classifications are F0 for one retained wording, F2 for 70 syntax/idiom decisions, and F3 for 63 consequential decisions. These classes describe editorial choices, not a measure of translation quality.

## Decisions needing later independent review

- The recognition and hearing language remains repeated. Joseph’s concealed identity, harsh treatment, weeping, and detention of Simeon are kept together without adding motives.
- “The land’s nakedness” becomes “where the land lies exposed,” with the underlying image in a note. “One is not” stays open as “one is no longer with us” in 42:13 and 42:32; explicit death language remains where Jacob or Judah uses it.
- The initial detention proposal and its reversal are both preserved. The brothers’ reports about Joseph’s questions and their discovery of silver are not harmonized with the earlier narrated scenes.
- Reuben’s offer of his sons’ deaths remains explicit. Judah’s guarantee is personal, and his full appeal culminates in offering himself as a slave in Benjamin’s place.
- “Servant” remains a deferential self-description in court speech; “slave” names imposed or offered loss of freedom. Benjamin’s age and maternal relationship are made understandable without treating him as a literal small child throughout the story.
- The gift list, double-silver ambiguity, three separate dining groups, fivefold portion, and final intoxication verb remain. Compassion in Israel’s prayer and Joseph’s response uses the same English word.
- The planted cup, divination claims, proposed execution, reduced penalty, and collective return are explicit. The narrator’s knowledge is kept distinct from what the brothers fear or confess.
- Judah’s repeated father/son references and the image of bound lives remain intact. The likely father subject of death in 44:22 is made explicit, with the alternative pronoun reading noted. Gray head, Sheol, and the differing grief/misery terms remain.
- Joseph names his brothers’ sale and interprets his arrival as God’s sending. Remnant, great deliverance, father to Pharaoh, direct mouth/eyes recognition, and the fat of the land remain with selective explanations.
- Exact periods, gifts, and animals were checked: ten traveling brothers, twelve brothers claimed, three days in custody, fivefold food portion, two famine years elapsed and five remaining, three hundred pieces of silver, five clothing sets, ten male donkeys, and ten female donkeys.
- Joseph’s kiss and tears precede renewed speech. Neither the brothers’ unreported answer nor a claim that every family tension has ended is supplied. The final warning allows the alternative senses of quarrelling, agitation, or fear in a note.

The authoring model reread the assembled English and made corrections: it explicitly restored completed footwashing in 43:24, clarified Benjamin’s relationship to the speakers in 44:20, named both lives in 44:30, and replaced an overprecise rank equation in 44:18 with the source’s comparison to Pharaoh. This is an editorial self-check, not a human scholarly review or independent reading test.

## Verification

The [verification record](verification.json) reports eight successful cumulative source-binding audits, 1,387 unique Genesis source references through chapter 45, translation-family structural parity, formatting checks, and the targeted assertions. The [verification script](verify_batch.py) preserves the actual checks and can be rerun with the pinned Genesis and James source files.

The [focused before/after overlap report](overlap-before-after.json) covers only these 134 verses. Before revision, 103 verses had identical word tokens and 31 were near-identical to TSW. After revision, two had identical word tokens and five were near-identical; mean word similarity was 0.685065. Near-identical here means nonidentical with SequenceMatcher similarity at least 0.90. These results are triage, not proof of fidelity, originality, or comprehension. The clear recognition sentence at 42:8 was deliberately retained.

Chapter status `QA_PASSED` is qualified by `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. Only chapters 42–45 supersede their earlier approval records and bindings. Prior revision batches and unaffected records are preserved exactly.

TSW, earlier revised chapters, Genesis 46–50, and separate Companion content are unchanged. Any exact Companion quotations or chapter bindings for Genesis 42–45 must be checked before later installation. GitHub upload remains blocked by the established access restriction; no rejected write was retried. The cumulative bundle preserves exact parent commit objects from base `984d86f25ff0c4e46b566e063fc0b86a8ed64eb7`.
