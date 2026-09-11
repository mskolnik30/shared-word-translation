# Numbers 9–10: source-based Fluent draft

All 59 verses (23 + 36) received a source-based draft assessment and a verse-specific rationale, with exact before/after wording, comparator and source bindings. This batch develops Fluent’s connected reading voice while retaining the repeated commands, detailed travel order and final poetry. Independent editorial review and reader testing remain pending.

## Source and method

Every selected Hebrew verse was read before drafting from [OSHB Numbers at the pinned commit](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Num.xml), Git blob `2e7252db3bd33d510d2361a8b5016ac680b27dbb`, SHA-256 `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`. Public numbering aligns directly here. All eight source annotations across 9:3, 9:10, 9:21, 10:9, 10:25, 10:34 and 10:36 are included in the original XML substring hashes. These include the extraordinary dot at 9:10 and inverted-nun annotations bracketing 10:35–36. No normalized substitute is hashed.

[NET Numbers 9](https://www.biblegateway.com/passage/?search=Numbers+9&version=NET) and [NET Numbers 10](https://www.biblegateway.com/passage/?search=Numbers+10&version=NET) provided supplemental grammatical and lexical comparison after the Hebrew reading. All 59 TSW verses were read after drafting. English comparators did not supply a template or synonym-replacement process.

## Editorial decisions

- The first-month Passover and the second-month provision both keep day fourteen and twilight. Corpse-related impurity is distinguished from refusal; the clean person’s failure retains the severe cut-off sanction and bearing sin. The resident foreigner shares the same rule, with Exodus 12’s further conditions referenced.
- The repeated divine-command refrain remains intact, including all four references to the LORD in 9:23. The day/night and extended “days” idioms have short notes. The pinned Hebrew’s 9:16 does not gain an explicit “by day” from another witness.
- Two trumpets summon the whole community; one summons leaders. The alarm signal is distinct from the assembly call. East and south remain the only camps assigned numbered signals in this instruction; no additional signals or musical patterns are invented.
- Departure remains dated to year two, month two, day twenty. All twelve tribal leaders and fathers, four banner groups and the intervening carriers remain in order. Deuel remains distinct from Reuel in 2:14.
- The Kohathites’ arrival and the prior setup of the tabernacle are separated clearly. Hobab’s marriage relationship remains qualified in a note, and his response to the renewed invitation is not invented. The eyes image and repeated good language remain audible.
- The ark goes ahead during the three-day journey; the text does not require a three-day gap. Both closing invocations remain poetry inside their verse paragraphs, with enemies, haters, return, and myriads of thousands intact.

The existing clear wording of 10:32 is retained after source assessment (F0). The other 58 verses changed: 33 F2 and 25 F3. No minimum-change or overlap quota was used. The overlap report is triage only; it does not establish fidelity, independent authorship or comprehension.

## Verification and next work

`verify_batch.py` checks all 35 cumulative verse ledgers, exact source bindings, chapter coverage and formatting, names, dates, conditions, source annotations, repeated phrases and poetry containment. It also runs the translation-family audit and `git diff --check`. `verification.json` records the results. The source-binding ledger stores normalized verse text for comparison; poetic lineation is checked directly in the chapter files.

Cumulative draft coverage is 4,133 verses across 132 chapters: James, Genesis, Exodus and Leviticus, plus Numbers 1–10. Structural checks and this authoring self-check are distinct from independent scholarly review, which has not occurred. Revised chapters remain `REVIEW_PENDING` for editorial purposes with publication disabled.

Only Numbers 9–10 supersede the earlier wording’s approvals and bindings. Earlier batches, TSW, unrelated work and historical provenance remain preserved. Companion quotations and bindings for these two chapters need checking before later installation; no Companion branch or public deployment was changed. GitHub upload remains blocked by the previously established access restrictions, and no rejected write was retried.

Next: Numbers 11–12, complaint, the seventy elders, quail, and Miriam and Aaron. Recover the latest cumulative checkpoint and continue without routine approval pauses.
