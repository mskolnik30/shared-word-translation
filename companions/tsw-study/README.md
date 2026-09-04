# TSW Study Companion

The TSW Study Companion is a public companion for readers who want to examine how a passage works and how its interpretation has shaped communities.

Every dossier must:

1. stay anchored to the wording and literary shape of TSW;
2. distinguish translation, historical reconstruction, theological judgment, and later reception;
3. name significant interpretive disagreements without manufacturing false balance;
4. include Jewish interpretation when reading Israel's Scriptures and avoid treating Christian reception as replacement;
5. represent major Christian traditions and relevant modern critical voices fairly;
6. identify uses of the passage that have authorized domination, exclusion, or harm;
7. place questions directly before the public reader, without facilitator-only language;
8. reference shared people, places, maps, and images rather than duplicating them;
9. label uncertain claims and visual reconstructions honestly; and
10. pass both structural audit and human theological/editorial review before publication.

## Standard public sequence

Each dossier uses these sections:

- **First Look** — the passage's movement and central pressure.
- **Why This Matters** — why interpretation changes reading or practice.
- **Look Closely** — language, syntax, textual evidence, and literary detail.
- **More Than One Reading** — the principal live interpretations.
- **Across Christian History** — reception without a triumphalist master story.
- **Power and Consequences** — effects on bodies, communities, institutions, and creation.
- **Consider Together** — public questions in a visually distinct interface block.
- **Shared Biblical World** — translation-neutral references and visual needs.
- **Continue Exploring** — concise next paths.
- **Sources and Further Study** — a transparent source ledger.

Machine validation is implemented by `tools/audit_companion_batch.py`. Passing the audit means a dossier is structurally ready for review; it does not mean its interpretive judgments have been approved.

## Publication states

- `DRAFTED_REVIEW_REQUIRED` means at least one required human gate remains pending and publication is blocked.
- `APPROVED_FOR_PUBLICATION` means every required human gate is approved and the release audit passes.

Approval of a text dossier does not approve unfinished visuals. A dossier may be published as text while requested images remain blocked in the shared biblical-world registry. Visuals become public only after their provenance, rights, classification, evidence label, caption, and alternative text pass their own record-level requirements.

## Published and active batches

- **Batch One:** ten dossiers approved for text publication; unfinished visuals remain individually blocked.
- **Batch Two:** ten dossiers approved for text publication through one consolidated review; unfinished visuals remain individually blocked.
