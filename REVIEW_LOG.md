# TSW Review Log

This log records the work of the auto-translator. Each entry names the chapters drafted in a run, flags judgment calls (textual variants, contested renderings, gender language decisions), and notes anything else worth a human translator's review.

---

## 2026-04-30T22:13Z

**Drafted:** Jeremiah 29, Psalm 46, Ephesians 2

**Judgment calls:**
- Jeremiah 29:11 — Rendered the famous verse as "plans I am planning concerning you ... plans for well-being and not for harm, to give you a future and a hope." Used "well-being" to render shālôm in this context (avoiding "prosper / prosperity," which carries individualist freight) and kept the doubled "plans / planning" to honor the Hebrew cognate construction (maḥshābôt ... ḥōshēv). Flagged "future and hope" (aḥarît / tiqwâ) in the Vocabulary section so a reader can see why those English words are doing the work.
- Jeremiah 29:14 — "Restore your fortunes" for shûv shevût; the alternative "bring back your captivity" is ancient and defensible, but the parallel verbs of return in vv.10–14 favor the broader "fortunes" reading. Noted in the chapter notes.
- Jeremiah 29:22 — Kept the curse formula intact ("whom the king of Babylon roasted in the fire"). The harshness is in the Hebrew; softening it would be a different kind of unfaithfulness. Worth a human pass to confirm tone.
- Psalm 46:10 — "Be still" preserved at the front of the verse for liturgical familiarity, but the note explicitly opens the verb (rāphâ — "let go," "drop your hands") so the reader sees the wider range. The verse functions on at least two registers (address to nations / address to the soul); both are honored.
- Psalm 46 — Refrain at vv.7 and v.11 rendered identically, which is what the Hebrew supports.
- Ephesians 2:5 — Kept Paul's parenthetical "by grace you have been saved" inside em-dashes mid-sentence; it interrupts the verb chain in the Greek and the translation should mirror that.
- Ephesians 2:8 — On the long-disputed antecedent of "this" (τοῦτο), the translation lets the ambiguity stand. Note explains the grammatical issue.
- Ephesians 2:11–22 — Used "Messiah" rather than "Christ" throughout this chapter to keep the Jew/Gentile theme audible (Messiah names the long Jewish hope to which the Gentiles are now joined). This matches conventions used in earlier TSW chapters where the Jewish horizon of the gospel is in view; worth a human check for consistency across the corpus.
- Ephesians 2:15 — Rendered "the law of commandments in decrees" as the object set aside, not "the law" tout court. The translation reflects a view that what is broken is the wall, not the Torah; this is a real interpretive call and a human translator may want to revisit.
- "Children of wrath / disobedience" (Eph 2:2–3) — kept "children" rather than smoothing to "those who" because the Hebraic idiom is theologically meaningful.

**Skipped:**
- None this run. Tier 1 priorities advanced cleanly.

**Notes:**
- Auto-translator discovery: the repo contains ~1,072 stub `.md` files (under 200 bytes, frontmatter only with `<!-- Translation pending. -->`) scaffolded across the canon. These were not visible to a casual `Glob`/`find` listing of "translated" content but they DO exist. The TRANSLATION_ROADMAP "Already Translated" list (~103 chapters) accurately reflects what has actual content; the stubs are scaffolds. Implication for future runs: the rule "pick chapters that do NOT yet exist as files" needs to be read as "pick chapters where the file is a stub OR missing," because new translations will frequently overwrite a pending stub rather than create a fresh file. I overwrote the Ephesians 2 stub today after reading its contents; this seems consistent with the project's intent.
- Roadmap housekeeping items (still open from a prior pass): `books/OT/jeremiah/Jeremiah _31.md` rename, and `books/OT/psalms/Psalms_118.md` duplicate verification. Did not touch either; both are user-noted cleanup tasks.
- Calibration files reviewed (1 Cor 13, Psalm 91, Proverbs 3) and used for register/format. No errors found in those files during this pass.
- **Git status:** The repo root in the sandbox does not contain a populated `.git` directory at the time of this run. `git status` from the sandbox reports "not a git repository," and a write attempt yielded an index-lock permission error inside the sandbox overlay. No commit or push was performed this run. The three new files (Jeremiah_29.md, Psalm_046.md, Ephesians_02.md) and this REVIEW_LOG.md are saved in place in the working folder; the user can commit them from their local terminal. Future runs should be able to commit normally if the host folder includes the project's `.git` directory.
