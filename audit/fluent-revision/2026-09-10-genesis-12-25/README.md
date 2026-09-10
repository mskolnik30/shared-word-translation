# Fluent biblical-fluency revision: Genesis 12–25

September 10, 2026. This batch addresses all 394 verses in fourteen chapters. It follows the revisions of Genesis 1–11 and James. In total, 801 verses across thirty chapters have received this editorial pass. The rest of Fluent has not yet received it.

## Reading purpose

Fluent's distinct voice serves sustained understanding of Scripture. The main text uses clear speakers, manageable sentences, and connected paragraphs. It preserves recurring biblical language and the differences between voices. It does not generate new wording simply to lower overlap with TSW.

The Abraham narratives retain blessing, descendants, covenant, land, stranger, hearing, seeing, laughter, righteousness and justice, kindness and faithfulness, and the family-account formula. Notes and vocabulary help readers recognize these connections. Repetition in the promises, negotiations, and the servant's retelling remains part of the text.

The revision keeps the unequal relationships involving Hagar and the royal taking of Sarah explicit. It retains difficult commands, sexual violence, and the binding of Isaac without defending the characters, adding motives, or replacing the narrative with commentary. Rebekah's own answer in 24:58 remains direct. The deaths and genealogies preserve people, numbers, and property details that a compressed paraphrase could lose.

## Source and consequential choices

The Hebrew source is [Open Scriptures Hebrew Bible, Genesis](https://github.com/openscriptures/morphhb/blob/6a5db284c715c18b239422e57bb89684e6a19f00/wlc/Gen.xml), at commit `6a5db284c715c18b239422e57bb89684e6a19f00`, blob `dcc8be362134981d3054e9b64d3a465d08492a33`. The [verse ledger](genesis-verse-review.json) binds each complete original XML verse record, including written/read annotations, along with before/after text, TSW comparator, and a verse-specific rationale.

There are 59 consequential F3 choices identified for review. They include the blessing constructions, Melchizedek's title and the unnamed giving subject, the pronouns in 15:6, Hagar's seeing language, El Shaddai, changes between singular and plural address, the unspecified laughter in 21:9, the compressed child/shoulder clause, seeing/providing in chapter 22, and the rare verb in 24:63.

As targeted comparators, the NET translators' notes were consulted for the [seeing-language ambiguity in 16:13–14](https://www.biblegateway.com/passage/?search=Genesis+16&version=NET), [the eye-covering idiom in 20:16](https://www.biblegateway.com/passage/?search=Genesis+20&version=NET), and [the uncertain action in 24:63](https://www.biblegateway.com/passage/?search=Genesis+24&version=NET). These notes support the acknowledgment of uncertainty; they do not function as Fluent's source text. Other judgments are provisional readings of the pinned Hebrew, not claims of independent scholarly certification.

## Review status

386 verses have changed main-text wording or punctuation from previous Fluent. Nine F0 decisions retain clear sentences, introductions, or name lists after review. Similarity classifications remain separate from editorial F0/F2/F3 judgments.

Automated structural and source-binding QA is distinct from editorial approval. Every new chapter is marked `qa_scope: structural`, `editorial_status: REVIEW_PENDING`, and `publication_allowed: false`. The old chapter reviews are superseded through Git history. The book records identify both Genesis batches and preserve historical provenance without carrying approvals into revised wording. No independent human review or reader test has occurred.

The user's authorization allows continued drafting, checking, and checkpointing without pauses for approval. It is not recorded as an independent translator's review. Public deployment is not part of this batch. Companion quotations and chapter bindings need review when the revised wording is installed.

## Verification

The [verification record](verification.json) reports source identity, exact byte bindings, coverage, paragraph and verse formatting, and targeted name/number checks. All three revision ledgers pass. The translation-family audit passes with only the documented Romans 16 and Nehemiah 7 label differences. TSW, the earlier revised chapters, and Genesis 26–50 remain unchanged in this batch.

[Before](overlap-before.json) and [after](overlap-after.json) reports compare aligned public verse labels, excluding apparatus. They measure surface overlap, not translation fidelity, authorship, or reader comprehension. Their working-tree results are bounded by the current ledger's chapter hashes.

```bash
python3 tools/audit_fluent_revision.py audit/fluent-revision/2026-09-10-genesis-12-25/genesis-verse-review.json --source-text /path/to/Gen.xml
python3 tools/audit_translation_family.py
python3 tools/audit_translation_overlap.py --json-output /tmp/fluent-overlap.json
git diff --check
```

Next connected passage: Genesis 26–36. Continue with Genesis 37–50, then a whole-book consistency review before moving to another book. These are work items, not completed revisions.
