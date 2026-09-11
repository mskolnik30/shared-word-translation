# Fluent Leviticus 16–17 revision

All 50 verses (34 + 16) received source-based drafting and verse-specific rationales. The cumulative revision covers 3,360 verses in 112 chapters: Genesis 1–50, Exodus 1–40, Leviticus 1–17, and James 1–5. Independent editorial review and reader testing remain pending. Structural QA does not authorize publication.

## Source and method

All selected Hebrew verses were read from the [pinned OSHB Leviticus source](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Lev.xml). The original file's SHA-256, Git blob and 859-record count were verified. These chapters align directly with public numbering. Each verse hash covers the exact original XML substring, including both written and read forms at 16:21.

Selected [NET Leviticus 16 translator notes](https://www.biblegateway.com/passage/?search=Leviticus+16&version=NET) and [Leviticus 17 translator notes](https://www.biblegateway.com/passage/?search=Leviticus+17&version=NET) were consulted after all 50 Hebrew records were read, before drafting. They served as lexical and grammatical comparators. All TSW verses were read after drafting independently from the Hebrew. The assembled text was reread before focused checks. No independent scholarly or human review took place.

## Editorial decisions

The draft distinguishes the inner sanctuary, tent and unnamed altar. It retains the four linen garments, bathing and clothing changes, personal and community offerings, two goats, lots, incense cloud, blood applications and sevenfold sprinklings. The four occurrences of Azazel remain; its debated meaning is noted. The live goat receives both hands and the confession of wrongdoing, rebellions and sins, then carries the wrongdoing away. The text does not add later details about its fate.

The annual date, self-denial, complete rest, native-born and resident-foreigner scope, priestly succession, and repeated atonement for places and people remain explicit. Ambiguities involving atonement over the goat, east-side/eastward sprinkling, the appointed/ready escort, the syntax of 16:30 and the final actor in 16:34 are documented.

Chapter 17 keeps the broad wording about slaughter of three domestic species and the distinct rule for hunted edible game. Bloodguilt, cutting off, the LORD setting his face against the eater, and the prostitution metaphor for pursuing goat demons are retained. The relation of blood and life is repeated without inserting a complete doctrinal interpretation. The same Hebrew life/person term spans human eaters and animal life; vocabulary makes that connection visible. Carrion rules preserve washing, bathing, evening and bearing guilt.

## Verification

`leviticus-verse-review.json` records every before/after verse, exact source binding, TSW comparator and rationale. All 50 verses changed: 26 F2 and 24 F3 choices. No minimum-change percentage was imposed.

`verification.json` records successful audits for all 26 ledgers, 50 unique current-batch source records, cumulative coverage of 3,360 verses, formatting and metadata, focused assertions, prior-record preservation, the translation-family audit and `git diff --check`.

`overlap-before-after.json` is triage only: before revision, 6 identical and 42 near-identical verses against TSW; afterward, 0 identical and 1 near-identical. Mean similarity changed from 0.954929 to 0.730909. These figures do not prove fidelity, originality, comprehension or approval.

Only chapters 16–17 supersede their prior wording's approvals and bindings. Earlier revisions, TSW and unrelated work are unchanged. Companion quotations and bindings for these chapters require later checking; no separate Companion branch was modified. No public deployment occurred. GitHub upload remains blocked under the previously established access restriction; no rejected write was retried.

Next: Leviticus 18–20, from verified Hebrew with the same source and editorial standards.
