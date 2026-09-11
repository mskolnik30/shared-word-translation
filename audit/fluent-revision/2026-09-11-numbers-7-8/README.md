# Numbers 7–8: source-based Fluent draft

All 115 verses (89 + 26) were drafted from the pinned Hebrew, with a verse-specific rationale, before/after wording, TSW comparator, editorial F0–F3 assessment and exact source binding. The revision helps readers follow the dedication gifts and the Levites’ service through connected sentences and stable biblical vocabulary. The twelve offering lists remain complete; no list is replaced by a summary. Independent editorial review and reader testing remain pending.

## Source and comparison

Source: [OSHB Numbers, pinned commit](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Num.xml), Git blob `2e7252db3bd33d510d2361a8b5016ac680b27dbb`, SHA-256 `5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf`. All 115 selected Hebrew verses were read before drafting, including the twelve repetitions. Exact original XML substrings include all six annotations at 7:4, 7:32, 7:40, 7:55, 7:59 and 7:68. Public numbering aligns directly in this batch. The full source has 1,289 records; later public numbering requires explicit mapping.

[NET Numbers 7](https://www.biblegateway.com/passage/?search=Numbers+7&version=NET) and [NET Numbers 8](https://www.biblegateway.com/passage/?search=Numbers+8&version=NET) supplied supplemental lexical and grammatical comparison after the Hebrew reading. All 115 TSW comparator verses were read after drafting. No modern translation supplied the draft’s base text. Repeated Hebrew lists were transcribed through a shared authored pattern, without an English synonym-substitution process.

## Decisions and self-check

- Every donor, father’s name, tribe and day remains explicit, including Deuel in 7:42 without harmonizing Reuel in 2:14. Nahshon is not given an extra leader title in 7:12.
- The carts and oxen remain allocated 2/4 to Gershon and 4/8 to Merari; Kohath’s shoulder-carrying duty receives none.
- Each day retains the silver dish and basin at 130/70 sanctuary shekels, both filled; the gold ladle at 10; burnt offerings 1/1/1, sin offering 1, and peace offerings 2/5/5/5. Final totals remain 2,400 silver and 120 gold shekels, 12 of each burnt-offering kind, 12 sin-offering goats, and 24/60/60/60 peace-offering animals. Multiple lambs are phrased as “male lambs a year old” to prevent a count being mistaken for their age.
- Notes preserve uncertainty about the carts, the gold utensil and the last speaking subject in 7:89. “Atonement cover” connects with Exodus 25. The lampstand’s unnamed maker remains unspecified in 8:4.
- Moses, Aaron, the Israelites and the Levites retain their distinct ritual actions. The Levites are presented as a wave offering; the notes do not invent how people were physically moved. The firstborn substitution, Egypt’s deaths and the threat of plague remain explicit.
- Twenty-five in 8:24 is retained alongside thirty in chapter 4. Possible explanations are labeled as possibilities. Withdrawal at fifty and continued assistance are distinguished without inventing an exact division of tasks.

These are checks by the authoring model, not independent scholarly approval. All 115 verses changed: 83 F2 and 32 F3. Overlap is recorded in `overlap-before-after.json` as triage, not proof of fidelity, independent authorship or comprehension. No change quota was used.

## Verification and continuity

`verify_batch.py` runs all 34 cumulative source-binding audits, the translation-family audit and `git diff --check`, and checks complete labels, paragraph structure, quotation balance, chapter hashes, six original annotations, names, quantities, ritual roles and age distinctions. Its results are in `verification.json`. Coverage is now 4,074 verses across 130 chapters.

Earlier revisions, TSW, historical provenance and unaffected chapter approvals remain unchanged. Only Numbers 7–8 supersede their earlier wording and review bindings. The revised chapters have structural QA status with independent editorial review pending and publication disabled. No public deployment or Companion-branch change occurred; Companion quotations and bindings for these chapters require checking before later installation. GitHub upload remains blocked by the previously established access restrictions; no rejected write was retried.

Next: Numbers 9–10, Passover, cloud, trumpets and departure from Sinai. Continue from the latest cumulative checkpoint without routine approval pauses.
