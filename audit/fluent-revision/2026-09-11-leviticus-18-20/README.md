# Fluent Leviticus 18–20 revision

All 94 verses (30 + 37 + 27) received source-based drafting and verse-specific rationales. Cumulative coverage is 3,454 verses in 115 chapters: Genesis 1–50, Exodus 1–40, Leviticus 1–20, and James 1–5. Independent editorial review and reader testing remain pending. Structural QA does not authorize publication.

## Source and method

All 94 Hebrew verses and their annotations were read from the [pinned OSHB Leviticus source](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Lev.xml) before drafting. The file's SHA-256, Git blob and 859-record count were verified. Public and Hebrew numbering align in this batch. Verse hashes cover exact original XML substrings, including annotation notes at 18:17, 19:1 and 20:2.

Selected NET translator notes for [chapter 18](https://www.biblegateway.com/passage/?search=Leviticus+18&version=NET), [chapter 19](https://www.biblegateway.com/passage/?search=Leviticus+19&version=NET) and [chapter 20](https://www.biblegateway.com/passage/?search=Leviticus+20&version=NET), and [NRSVUE 19:20](https://www.biblegateway.com/passage/?search=Leviticus+19:20&version=NRSVUE), were consulted after Hebrew reading and before drafting. They served as lexical and grammatical comparators. All 94 TSW verses were read after the independent draft. During apparatus review, [Daniel Vainstub's discussion of the mlk offering interpretation](https://www.thetorah.com/article/molekh-the-sacrifice-of-babies) was consulted to substantiate an alternative mentioned in the note; that interpretation was not imposed on the main text.

The assembled English was reread. The authoring self-check corrected ambiguous pronoun attachment in 19:20 and made the kinship referent in 18:17 clearer. These checks are not independent scholarly review.

## Editorial decisions

Chapter 18 preserves the male-addressed kinship list, both parental nakedness expressions, half-sibling and household alternatives, paternal and maternal aunts, grandchildren, in-law relationships, and the rival-sister lifetime qualification. Sexual euphemisms are clarified where needed; relational nakedness images and their repetitions remain visible. Molech is retained with a concise note about the disputed term. Neither fire nor a modern sexual identity category is inserted into verses that do not name them. The land's defilement, punishment and vomiting image remain explicit, as do native-born and resident-foreigner scope and cutting off.

Chapter 19 preserves the mother-before-father order, peace-offering timetable, gleanings, wages held overnight, deaf and blind people, impartial judgment, and the love-as-yourself command for both neighbor and foreigner. The uncertain clauses about a neighbor's blood, rebuke and guilt are noted. The enslaved woman's status, lack of redemption and freedom, uncertain inquiry/punishment/compensation term, and the man's offering and sin remain distinct; consent is not invented. The fruit remains “uncircumcised,” with the three-, fourth- and fifth-year sequence intact. Blood, body markings, exploitation of a daughter, honest measures and both ancient units are preserved.

Chapter 20 keeps the stated agents and penalties, including stoning, burning with fire, killing animals, cutting off and the blood-responsibility formula. The family mentioned under divine opposition is not automatically equated with every follower in the following penalty clause. The pinned repetition in 20:10 remains. Nakedness, the menstrual fountain image, “die childless” versus “be childless,” singular nation, milk and honey, and the shared set-apart/distinguish root are retained. Consulting spirits and having a spirit remain distinguishable. Notes do not adjudicate contemporary application.

## Verification and disposition

`leviticus-verse-review.json` records before/after text, the TSW comparator, exact source binding and a rationale for every verse. Ninety-three verses changed: 51 F2 and 42 F3 decisions. One F0 verse, 19:25, was retained because its wording remains clear and source-faithful. No minimum-change percentage was imposed.

`verification.json` records successful audits for all 27 ledgers, 94 unique new source records, cumulative coverage, paragraph and metadata checks, focused assertions covering 80 verses, preservation of previous records, the translation-family audit and `git diff --check`.

`overlap-before-after.json` is triage only. Before revision: 18 identical and 73 near-identical verses against TSW; afterward: 1 identical and 5 near-identical. Mean similarity changed from 0.948617 to 0.679133. These measures do not prove fidelity, originality, comprehension or approval.

Only chapters 18–20 supersede prior wording approvals and bindings. Historical provenance remains in the exact Git history. Earlier revisions, TSW, unrelated work and the separate Companion branch are unchanged. Companion quotations and bindings for these chapters require later checking. No public deployment occurred. GitHub upload remains blocked under the previously established restriction; no rejected write was retried.

Next: Leviticus 21–22 from verified pinned Hebrew, in complete connected chapters.
