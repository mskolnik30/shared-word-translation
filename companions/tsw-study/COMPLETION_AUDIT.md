# TSW Study Companion Completion Audit

## Consolidated approval recorded

On 2026-09-05, all seven human gates were approved for the fifty text dossiers in Batches Three–Seven. The visual-evidence approval covers the control system only: all unfinished visuals remain excluded and blocked pending individual accuracy and rights review.

## Audit decision

This packet completes the planned first-edition study companion: seven batches, seventy dossiers, every book in the 66-book Protestant canon represented, and four additional dossiers for passages with exceptional interpretive stakes.

Batches One and Two are already approved. Batches Three through Seven are deliberately marked `DRAFTED_REVIEW_REQUIRED`. Their texts, manifests, and shared-world references pass machine validation, but publication remains blocked until the consolidated human audit below is recorded.

One decision may cover all five new batches. You do not need to approve each dossier or gate separately. The decision must explicitly cover all fifty texts and all seven gates; unfinished visuals remain excluded.

## Completion ledger

| Batch | Dossiers | State | Scope |
|---|---:|---|---|
| 1 | 10 | Approved | Foundational contested passages |
| 2 | 10 | Approved | Second foundational set |
| 3 | 10 | Human audit required | Leviticus, Numbers, Ruth, 2 Samuel, 1 Kings, John, Acts, 2 Corinthians, Galatians, Ephesians |
| 4 | 10 | Human audit required | 2 Kings, 1 Chronicles, 2 Chronicles, Ezra, Nehemiah, Colossians, 1–2 Thessalonians, 1–2 Timothy |
| 5 | 10 | Human audit required | Esther, Job, Proverbs, Song of Songs, Jeremiah, Titus, Philemon, Hebrews, 1–2 Peter |
| 6 | 10 | Human audit required | Lamentations, Ezekiel, Daniel, Hosea, Joel, 1–3 John, Jude, Romans 9–11 |
| 7 | 10 | Human audit required | Amos, Obadiah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi, 1 Corinthians 6 |

## Consolidated human review

Review representative dossiers from every batch, then inspect every dossier flagged by the issue under review. Record approval only when each answer is yes.

### 1. Source-language and textual evidence

- Do Hebrew, Aramaic, and Greek claims distinguish lexical possibility from contextual argument?
- Are textual variants named without overstating certainty?
- Do translation comparisons avoid treating an English gloss as the original meaning?

Priority dossiers: Leviticus 18/20; Numbers 5; John 7:53–8:11; 1 Timothy 2; 2 Peter 3; Malachi 2; 1 Corinthians 6.

### 2. Historical and archaeological claims

- Are dates, locations, institutions, and social practices appropriately qualified?
- Are literary depictions distinguished from independently established history?
- Does every reconstruction identify whether it is established, probable, possible, disputed, unknown, or interpretive?

Priority dossiers: Ruth 3; 1 Kings 18; Ezra 9–10; Esther 9; Daniel 7; Haggai 2.

### 3. Jewish and ecumenical Christian reception

- Does study of Israel's Scriptures include living Jewish interpretation rather than using Judaism as a Christian foil?
- Are Catholic, Orthodox, Protestant, and other relevant Christian receptions represented fairly?
- Are supersessionism and inherited anti-Jewish uses named where relevant?

Priority dossiers: 2 Chronicles 7; Galatians 3; Hebrews 6; Romans 9–11; Habakkuk 2; Zechariah 12.

### 4. Critical voices and perspectives

- Are feminist, womanist, liberation, disability, postcolonial, queer, ecological, and trauma-aware readings included when the passage materially calls for them?
- Are these voices treated as interpretive partners rather than decorative additions?
- Does the dossier avoid manufacturing false balance around well-documented harm?

Priority dossiers: Numbers 5; Ruth 3; 2 Samuel 11; Ezra 9–10; Ezekiel 16; Hosea 1–3; Nahum 3.

### 5. Power, safeguarding, and history of harm

- Does each dossier identify who controls speech, bodies, money, land, belonging, or punishment?
- Does safety language prevent a passage from being used to require submission to abuse or silence reporting?
- Are antisemitic, racist, colonial, anti-LGBTQ+, misogynistic, proslavery, and authoritarian receptions named where relevant?

Priority dossiers: all dossiers carrying content notices, especially Leviticus 18/20; 2 Samuel 11; Ephesians 5; Colossians 3; 1 Peter 2; Malachi 2; 1 Corinthians 6.

### 6. Public clarity and non-facilitator language

- Can a thoughtful nonspecialist understand every technical term from its immediate context?
- Do questions address the reader directly without hidden teacher instructions?
- Does the prose invite study without disguising disputed claims as settled facts?

### 7. Visual evidence and rights

- Confirm that all fifty new visual requests remain `publication_status: blocked` and `rights_status: not-acquired`.
- Confirm that no dossier directly embeds an image.
- Do not include any visual in the consolidated text approval. Each visual requires its own provenance, rights, evidence label, caption, and alt-text record.

## Machine audit

Run from the repository root:

```bash
python tools/audit_all_companion_batches.py
python tools/audit_tsw_study_coverage.py
python tools/audit_translation_family.py
python tools/tsw_format_apparatus.py
git diff --check
```

Expected completion figures:

- 7 of 7 batch manifests pass;
- 70 of 70 dossiers are present;
- 66 of 66 canonical books are represented;
- 4 additional high-stakes dossiers are present;
- 50 of 50 new visual requests remain blocked;
- both TSW and Fluent retain 66 books and 1,189 chapters.

## Approval record to add after audit

If the review passes, update each of Batches Three–Seven as follows:

1. set all fifty dossier statuses and all five manifest statuses to `APPROVED_FOR_PUBLICATION`;
2. set all thirty-five human gates to `approved`;
3. set all five review publication states to `APPROVED_FOR_PUBLICATION`;
4. record one consolidated approval date and scope covering all fifty texts;
5. leave every unfinished visual blocked;
6. rerun the complete machine audit on the release commit.

If any gate does not pass, keep all five batches blocked, record precise corrections by dossier and claim, and rerun the audit after revision.
