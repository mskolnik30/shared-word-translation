# Fluent revision: Numbers 19–24

This batch gives all 182 verses a source-based draft assessment, with a verse-specific rationale and exact before/after, Hebrew-source and TSW-comparator bindings. It continues Matt’s request for larger connected batches. The purpose is biblical fluency: readable sustained narrative, recognizable recurring language, understandable speakers and relationships, and poetry that retains its images and force.

The text changes 180 verses and retains the clear prior wording of 22:39 and 24:19. Formatting the latter as poetry does not count as a change to its normalized verse wording. Editorial choices are recorded as 117 F2, 63 F3 and 2 F0. These categories are editorial judgments, not similarity scores.

## Source and decisions

Source: openscriptures/morphhb, commit `6a5db284c715c18b239422e57bb89684e6a19f00`, `wlc/Num.xml`, Git blob `2e7252db3bd33d510d2361a8b5016ac680b27dbb`, SHA-256 `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`. The full source has 1,289 original verse records. Public Numbers 19–24 aligns directly with its 182 selected records. Exact original XML substrings, including seven annotations in seven records, are hashed without normalization.

Every selected Hebrew verse was read before drafting. Selected primary NET translators’ notes were consulted on grammatical and lexical difficulties; links are in the ledger. All TSW comparator verses were read after the independent draft. TSW was not used as a rewrite template. The authoring self-check included:

- The red cow’s requirements, preparation agents, ash storage, third/seventh-day purification and evening cleanness; ritual impurity is not automatically treated as personal wrongdoing.
- Miriam’s death without an invented year, the staff/speaking instruction, two strikes, both leaders’ responsibility, Edom’s two refusals and changed water offer, Aaron’s garment transfer and thirty days of mourning.
- Journey names, the snake/bronze wordplay, ancient poetic fragments, explicit destruction and captivity, and the difficult final line of the Heshbon poem.
- The singular return after the plural capture in 21:32. Both written and read verb forms are singular; their stem differs. The draft and note were corrected during the source check, rather than misdescribing this as a number variant.
- Differences among the messages reported by God, Balaam and the officials; permission followed by anger; the donkey seeing before Balaam; three beatings, the sword irony and the difficult conditional at 22:33.
- Partial views, three sets of seven altars/bulls/rams, repeated blessing formulas, the divine-word/mouth image, wild ox and lion poetry, violent victory images, and disputed names and pronouns in chapter 24.

Selective notes preserve consequential uncertainty: purification clause division, water/people referents, written/read forms, rare words, and several poetic lines. The draft does not silently identify the coming ruler, every place or every later historical event. It preserves both familiar shared blessing language and distinct natural sentence flow.

## Checks and limits

`verify_batch.py` passed all 38 cumulative `tools/audit_fluent_revision.py` checks, the translation-family audit and `git diff --check`. It also checked verse order, paragraph containment including poetry, quotation balance, source annotation hashes, quantities and names at focused risk points, and preservation of earlier revisions, TSW and unaffected approval records. Total revised draft coverage is now 4,580 verses in 146 chapters: James 1–5, Genesis 1–50, Exodus 1–40, Leviticus 1–27 and Numbers 1–24.

The before/after overlap report counts 132 identical and 46 near-identical verses before revision, compared with 3 identical and 17 near-identical afterward. Near-identical means nonidentical with a word-token SequenceMatcher ratio of at least 0.90. These figures are triage only: no minimum-change target was applied, and overlap does not demonstrate fidelity, originality or comprehension.

Chapter status `QA_PASSED` is qualified by `qa_scope: structural`; independent editorial status is `REVIEW_PENDING`, with `publication_allowed: false`. No human scholarly review or reader testing is claimed. Earlier approvals remain recoverable in exact Git history and are superseded only for this batch’s changed chapters; prior revision batches are preserved.

GitHub upload remains blocked by the previously established access restriction; no rejected write was retried. No public deployment or Companion-branch change occurred. Companion quotations and bindings for Numbers 19–24 need checking before later installation.

Next: Numbers 25–30. Map its numbering explicitly, including the two source records in public 26:1 and chapter 30’s shifted numbering. Continue complete chapters and source-specific rationales in the larger batch size.
