#!/usr/bin/env python3
"""Create exact source metadata and scope configs for the final NT continuation.

This utility does not generate translation wording. Each scope must already have
an independently authored authoring-input.tsv before the binding tool will run.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

R = Path(__file__).resolve().parents[1]
PARENT = "9ba4fd64124c93cf9e1b7c9a422701a2705f404c"
COMMIT = "c4d241a9c1c479a55b989ba35a4976c1d0b8052c"
BASE_DONE = ["Ephesians 6", "Philippians 1–4"]

SPECS = [
    ("Colossians", "colossians", "Col", range(1, 5), "COLOSSIANS_FLUENT_BOOK_QA.json", {
        "1": {"notes": [["14", "The pinned Greek reads ‘redemption, the forgiveness of sins’ without ‘through his blood.’"], ["24", "The difficult phrase about what is lacking in Christ’s afflictions is retained without implying a defect in Christ’s death."]], "vocabulary": [["15", "πρωτότοκος (prōtotokos)", "Firstborn; a title of rank and relation, used again of resurrection in verse 18."]]},
        "2": {"notes": [["18", "The pinned text reads ‘what he has seen’; the verb and the worship-of-angels construction remain difficult."], ["23", "The closing phrase can describe practices that fail to restrain bodily indulgence." ]], "vocabulary": [["08", "στοιχεῖα (stoicheia)", "Elements, basic principles or elemental powers; the same term returns in verse 20."]]},
        "3": {"notes": [["18–22", "The household instructions address wives, husbands, children, fathers and enslaved people specifically; the social hierarchy and potential harm are not erased." ]], "vocabulary": [["11", "Σκύθης (Skythēs)", "Scythian, an ancient ethnic designation used in this social list."]]},
        "4": {"notes": [["01", "The command to masters does not dissolve slavery; it places them under a heavenly Master and requires justice and fairness."], ["15", "The pinned reading names Nympha and uses a feminine possessive for the church in her house."]], "vocabulary": [["06", "ἅλας (halas)", "Salt; here a metaphor for speech that is fittingly seasoned."]]}}),
    ("1Thessalonians", "1thessalonians", "1Thess", range(1, 6), "1_THESSALONIANS_FLUENT_BOOK_QA.json", {
        "1": {"notes": [], "vocabulary": [["03", "ὑπομονή (hypomonē)", "Endurance or steadfastness under pressure."]]},
        "2": {"notes": [["07", "The pinned reading is ‘gentle’ and the following comparison is explicitly to a nursing mother."], ["14–16", "This severe first-century polemic is tied to named actions and Judean opponents; it must not be generalized to Jewish people."]], "vocabulary": []},
        "3": {"notes": [], "vocabulary": [["02", "στηρίζω (stērizō)", "Strengthen or establish; a recurring concern in this chapter."]]},
        "4": {"notes": [["04", "The word rendered ‘body’ literally means ‘vessel’ and may instead refer to acquiring or living with a wife."], ["15–17", "The sequence places the dead in Christ rising before the living are caught up together with them to meet the Lord."]], "vocabulary": [["17", "ἀπάντησις (apantēsis)", "A meeting or reception of an arriving person."]]},
        "5": {"notes": [["22", "‘Every kind of evil’ can also be rendered ‘every form of evil’; it does not merely mean looking evil." ]], "vocabulary": [["02", "ἡμέρα κυρίου (hēmera kyriou)", "Day of the Lord, pictured here as arriving like a thief at night."]]}}),
    ("2Thessalonians", "2thessalonians", "2Thess", range(1, 4), "2_THESSALONIANS_FLUENT_BOOK_QA.json", {
        "1": {"notes": [["06–10", "The letter voices retributive judgment in images of affliction, fire and lasting destruction; the violence is retained as the author’s claim." ]], "vocabulary": []},
        "2": {"notes": [["02", "The pinned text says ‘day of the Lord.’"], ["03", "The pinned text reads ‘man of lawlessness’; manuscripts also preserve a ‘sin’ reading."], ["06–07", "The text does not identify either the restraining power or the one who restrains."], ["13", "The pinned reading is ‘firstfruits’; another early reading can mean ‘from the beginning.’"]], "vocabulary": [["02", "ἐνίστημι (enistēmi)", "Be present or have arrived; the claim denied here is that the day is already present."]]},
        "3": {"notes": [["10", "The condition concerns someone unwilling to work, not a person unable to work."], ["14–15", "The social boundary is expressly limited: the person is to be warned as family, not treated as an enemy."]], "vocabulary": []}}),
    ("1Timothy", "1timothy", "1Tim", range(1, 7), "1_TIMOTHY_FLUENT_BOOK_QA.json", {}),
    ("2Timothy", "2timothy", "2Tim", range(1, 5), "2_TIMOTHY_FLUENT_BOOK_QA.json", {}),
    ("Titus", "titus", "Titus", range(1, 4), "TITUS_FLUENT_BOOK_QA.json", {}),
    ("Philemon", "philemon", "Phlm", range(1, 2), "PHILEMON_FLUENT_BOOK_QA.json", {}),
    ("Hebrews", "hebrews", "Heb", range(1, 14), "HEBREWS_FLUENT_BOOK_QA.json", {}),
    ("1Peter", "1peter", "1Pet", range(1, 6), "1_PETER_FLUENT_BOOK_QA.json", {}),
    ("2Peter", "2peter", "2Pet", range(1, 2), "2_PETER_FLUENT_BOOK_QA.json", {})
]

CRITICAL = {
    "colossians": ["1:14", "1:15", "1:19", "1:20", "1:24", "1:27", "2:2", "2:8", "2:9", "2:11", "2:14", "2:15", "2:18", "2:23", "3:5", "3:6", "3:11", "3:18", "3:22", "3:24", "4:1", "4:15"],
    "1thessalonians": ["1:3", "1:9", "2:7", "2:8", "2:14", "2:15", "2:16", "2:17", "3:3", "3:11", "4:4", "4:6", "4:13", "4:14", "4:15", "4:16", "4:17", "5:2", "5:3", "5:5", "5:10", "5:14", "5:18", "5:19", "5:20", "5:21", "5:22", "5:23"],
    "2thessalonians": ["1:5", "1:6", "1:7", "1:8", "1:9", "1:10", "2:2", "2:3", "2:4", "2:6", "2:7", "2:8", "2:9", "2:11", "2:12", "2:13", "2:15", "2:16", "3:3", "3:5", "3:6", "3:10", "3:14", "3:15"]
}

SPECIAL_APPARATUS = {
    "1timothy": {
        "1": {"notes": [["03–07", "The warning concerns speculative teaching and misuse of the law; the opponents are not named more precisely." ]], "vocabulary": []},
        "2": {"notes": [["11–12", "The instructions name a woman and a man specifically. The rare verb authentein can denote exercising authority or domineering; its force and the scope of the prohibition require independent review."], ["15", "The claim about being saved through childbearing is difficult; the following condition is plural and names faith, love, holiness and self-control."]], "vocabulary": [["12", "αὐθεντέω (authenteō)", "A rare verb meaning exercise authority, assume authority or domineer; interpretation is disputed."]]},
        "3": {"notes": [["02, 12", "The phrases literally describe a ‘one-woman man’; their implications for marital history and office qualifications require review." ]], "vocabulary": [["01", "ἐπίσκοπος (episkopos)", "Overseer or supervisor."]]},
        "4": {"notes": [["10", "The statement calls God Savior of all people, especially of believers; ‘especially’ is retained rather than explained." ]], "vocabulary": []},
        "5": {"notes": [["03–16", "The passage distinguishes enrolled widows, younger widows and family responsibility in its ancient household setting."], ["17", "‘Double honor’ may include material support, as the following quotations suggest."]], "vocabulary": []},
        "6": {"notes": [["01–02", "The text addresses enslaved people and masters within slavery; it does not call slavery harmless or erase its coercion."], ["10", "The text says love of money—not money itself—is a root of all kinds of evil."]], "vocabulary": []}},
    "2timothy": {
        "1": {"notes": [["07", "The Greek word can denote cowardice or timidity; the contrast names power, love and self-control." ]], "vocabulary": []},
        "2": {"notes": [["15", "‘Cutting straight’ evokes accurate handling; the precise metaphor may draw on roads, craft or plowing." ]], "vocabulary": []},
        "3": {"notes": [["16", "The Greek can mean ‘all Scripture is God-breathed and useful’ or ‘every God-breathed scripture is also useful.’"]], "vocabulary": [["16", "θεόπνευστος (theopneustos)", "God-breathed or breathed out by God."]]},
        "4": {"notes": [["14", "The prayer entrusts repayment for Alexander’s harmful acts to the Lord; it is not a command for personal retaliation."], ["16", "The request that abandonment not be counted against others limits the preceding judgment language."]], "vocabulary": []}},
    "titus": {
        "1": {"notes": [["06", "The household qualification describes a ‘one-woman man’ with believing or faithful children; both expressions require contextual review."], ["12", "The ethnic insult is quoted as a Cretan prophet’s saying and then endorsed in the next verse; its harmful rhetoric is retained, not universalized beyond the text."]], "vocabulary": []},
        "2": {"notes": [["09–10", "The passage addresses enslaved people inside slavery and demands submission; its coercive social setting is not softened." ]], "vocabulary": []},
        "3": {"notes": [["10", "The term describes a divisive or faction-making person; later technical meanings should not be assumed automatically." ]], "vocabulary": []}},
    "philemon": {"1": {"notes": [["10–16", "Onesimus is treated within an enslaving relationship. Paul’s appeal changes the relationship’s moral terms but does not explicitly order legal manumission."], ["18–19", "The debt language carries real economic and relational pressure; Paul also invokes Philemon’s debt of self to him."]], "vocabulary": [["16", "δοῦλος (doulos)", "Slave; the social status is stated directly before the appeal to receive Onesimus as a beloved brother."]]}},
    "hebrews": {},
    "1peter": {
        "1": {"notes": [["13", "The command’s literal clothing image is ‘gird up the loins of your mind.’"]], "vocabulary": []},
        "2": {"notes": [["18–25", "The address is to household slaves and includes suffering under unjust masters. The harm and coercive hierarchy are retained rather than moralized as harmless." ]], "vocabulary": [["18", "οἰκέτης (oiketēs)", "A household servant or slave."]]},
        "3": {"notes": [["01–07", "The household instructions are gender-specific and arise in an unequal ancient setting; verse 7 warns husbands that abuse of honor disrupts prayer."], ["19", "The identity of the spirits in prison and the time and manner of Christ’s proclamation remain disputed."], ["21", "The text relates baptism to salvation while denying that mere removal of bodily dirt is the point."]], "vocabulary": []},
        "4": {"notes": [["06", "The ‘dead’ may be people who heard while alive and have since died, or the proclamation may be portrayed as reaching the dead; the verse is compressed." ]], "vocabulary": []},
        "5": {"notes": [], "vocabulary": [["01", "πρεσβύτερος (presbyteros)", "Elder; here used for community leaders and also by the writer of himself."]]}},
    "2peter": {"1": {"notes": [["01", "The pinned Greek reads ‘Simeon Peter.’"], ["19", "The ‘morning star’ rising in hearts can mark inward illumination connected to the future day."], ["20", "The phrase can mean that no prophecy comes from the prophet’s own interpretation or that no prophecy is a matter of private interpretation." ]], "vocabulary": [["05–07", "ἐπιχορηγέω (epichorēgeō)", "Supply or furnish generously; the verb frames the chain of qualities."]]}}
}

for slug, data in SPECIAL_APPARATUS.items():
    for i, spec in enumerate(SPECS):
        if spec[1] == slug:
            SPECS[i] = spec[:-1] + (data,)

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-repository", type=Path, required=True)
    ap.add_argument("--staging-directory", type=Path, required=True)
    args = ap.parse_args()
    remaining = []
    for book, slug, osis, chapters, qa_file, apparatus in SPECS:
        first, last = min(chapters), max(chapters)
        remaining.append(f"{book.replace('1Thessalonians','1 Thessalonians').replace('2Thessalonians','2 Thessalonians').replace('1Timothy','1 Timothy').replace('2Timothy','2 Timothy').replace('1Peter','1 Peter').replace('2Peter','2 Peter')} {first}" + (f"–{last}" if first != last else ""))
    done = BASE_DONE.copy()
    for idx, (book, slug, osis, chapters0, qa_file, app0) in enumerate(SPECS):
        chapters = list(chapters0)
        source_rel = f"data/sblgnt/text/{osis}.txt"
        data = (args.source_repository/source_rel).read_bytes()
        records = []
        for line in data.decode().splitlines():
            m = re.fullmatch(r"\S+ (\d+):(\d+)\t(.*)", line)
            if m:
                records.append((int(m[1]), int(m[2]), m[3]))
        expected = sum(c in chapters for c, _, _ in records)
        source_name = f"{slug}-pinned-greek.txt"
        assert (args.staging_directory/source_name).read_bytes() == data
        label = remaining[idx]
        done.append(label)
        following = remaining[idx+1:]
        apparatus = {str(c): {"notes": [], "vocabulary": []} for c in chapters}
        for c, payload in app0.items():
            apparatus[c] = payload
        cfg = {
            "parent_commit": PARENT, "parent_library_version": 94,
            "source_omissions": {}, "heading_overrides": {},
            "supersede_entry_records": ["BOOK_VERSE_REVIEW_LEDGER.json"],
            "book": book, "slug": slug, "chapters": chapters, "scope": label,
            "expected_verses": expected, "source_filename": source_name,
            "book_record_files": [qa_file, "BOOK_VERSE_REVIEW_LEDGER.json"],
            "next_scope": "; ".join(following) if following else "2 Peter 2–3; 1 John 1–5; 2 John 1; 3 John 1; Jude 1; Revelation 1–22",
            "completed_block_scope": "; ".join(done),
            "source": {
                "id": "NT.SBLGNT.1.2", "repository": "Faithlife/SBLGNT",
                "repository_commit": COMMIT, "file": source_rel,
                "git_blob_sha": git_blob(data), "sha256": sha256(data),
                "raw_url": f"https://raw.githubusercontent.com/Faithlife/SBLGNT/{COMMIT}/{source_rel}",
                "format": "tab_separated", "osis_book_id": osis,
                "book_verse_count": len(records), "languages": ["Greek"],
                "verse_hash_method": "SHA-256 of exact tab-separated Greek payload, retaining whitespace and variant markers."
            },
            "f3": CRITICAL.get(slug, []), "apparatus": apparatus
        }
        out = R/f"audit/fluent-revision/2026-09-17-{slug}-{min(chapters)}-{max(chapters)}"/"config.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

if __name__ == "__main__":
    main()
