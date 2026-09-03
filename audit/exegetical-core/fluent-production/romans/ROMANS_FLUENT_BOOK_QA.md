# Romans — Fluent Book-Level QA

**Status: QA_PASSED / retained for NT Batch 01.**

- 16/16 chapters
- 433 public verse-number slots
- 432 included verse labels
- one intentional pinned-SBLGNT public-number gap: **Romans 16:25–27**
- Notes and Vocabulary present exactly once in every chapter
- paragraph structure balanced
- no escaped-newline or trailing-whitespace defects

## Frozen lexical decisions

- `dikaioō` → **set right** where its Romans justification/restoration sense is active
- Romans 3:22 → **through the faithfulness of Jesus Christ, for all who trust**
- Romans 3:25 `hilastērion` → **a place of atonement**
- preserve Sin/death/reign/slavery architecture in Romans 5–8
- preserve flesh/Spirit without treating physical embodiment as evil
- Romans 9–11 must preserve Israel, Gentile grafting, anti-boasting, future fullness, mercy, and God’s irrevocable calling
- Phoebe is a **deacon** and **benefactor**; Junia is feminine and **outstanding among the apostles** in the main rendering

## Deployment

Do not publish Romans independently. The batch installer must retrieve the immutable SBLGNT Romans source at install time, verify the Romans 16:25–27 gap, hash-bind all 432 included verses, bind the canonical TSW comparator blobs from `main`, then commit/push only after the entire book passes.

## Final-text correction

The pinned SBLGNT main text contains Romans 16:24 and ends there. Public Romans 16:25–27,
the familiar doxology in many modern critical editions, are therefore treated as textual-tradition
apparatus rather than continuous Fluent main text in this pinned-source production edition.
