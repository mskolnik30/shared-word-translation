#!/usr/bin/env python3
"""Build the source-aware 76-image Biblical profile production plan."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resources" / "biblical-world" / "profiles" / "plan.json"

OT_SOURCE = "https://oyc.yale.edu/religious-studies/rlst-145"
NT_SOURCE = "https://www.cambridge.org/core/books/cambridge-companion-to-the-new-testament/"
ISAIAH_SOURCE = "https://www.cambridge.org/core/books/cambridge-companion-to-the-book-of-isaiah/formation-of-the-book-of-isaiah/D02324B83F2BF701A9035AB757B3C31F"


BOOKS = [
    ("genesis", "Genesis", "composite-anonymous", "Pentateuchal traditions shaped over time; Moses is the traditional author, not a recoverable portrait of the final writer."),
    ("exodus", "Exodus", "composite-anonymous", "Pentateuchal traditions shaped over time; the book's Moses is a character and traditional authorial figure."),
    ("leviticus", "Leviticus", "composite-anonymous", "Priestly and holiness traditions; final authorship is not represented by one face."),
    ("numbers", "Numbers", "composite-anonymous", "Composite Pentateuchal traditions; Moses is central in the narrative but final authorship is layered."),
    ("deuteronomy", "Deuteronomy", "composite-anonymous", "Mosaic voice, Deuteronomic tradition, and later shaping must remain distinguishable."),
    ("joshua", "Joshua", "anonymous-edited", "Anonymous narrative associated with Deuteronomistic literary shaping."),
    ("judges", "Judges", "anonymous-edited", "Anonymous collection and shaping of older traditions; no single author portrait."),
    ("ruth", "Ruth", "anonymous", "The narrator is anonymous; neither Ruth nor Samuel should be portrayed as the certain author."),
    ("1-samuel", "1 Samuel", "anonymous-edited", "Anonymous historical narrative containing multiple traditions; Samuel is not author of the entire book."),
    ("2-samuel", "2 Samuel", "anonymous-edited", "Anonymous historical narrative containing court and royal traditions."),
    ("1-kings", "1 Kings", "anonymous-edited", "Part of a larger Deuteronomistic historical work; no known individual author."),
    ("2-kings", "2 Kings", "anonymous-edited", "Part of a larger Deuteronomistic historical work; no known individual author."),
    ("1-chronicles", "1 Chronicles", "anonymous-edited", "Usually associated with an anonymous Chronicler or school using earlier sources."),
    ("2-chronicles", "2 Chronicles", "anonymous-edited", "Usually associated with an anonymous Chronicler or school using earlier sources."),
    ("ezra", "Ezra", "composite-anonymous", "Narrative, lists, Aramaic documents, and Ezra material are combined; final authorship is composite."),
    ("nehemiah", "Nehemiah", "composite-anonymous", "Nehemiah memoir material is embedded in a shaped work; Nehemiah is not simply the final author."),
    ("esther", "Esther", "anonymous", "Anonymous Jewish diaspora narrative; Mordecai is not treated as certain author."),
    ("job", "Job", "composite-anonymous", "Anonymous wisdom work with prose frame and poetic dialogues; no recoverable author face."),
    ("psalms", "Psalms", "anthology", "A multi-period anthology naming David, Asaph, Korahites, Moses, Solomon, and others; many psalms remain anonymous."),
    ("proverbs", "Proverbs", "anthology", "An anthology linked with Solomon, the wise, Hezekiah's scribes, Agur, and Lemuel."),
    ("ecclesiastes", "Ecclesiastes", "persona-anonymous", "Qoheleth is the book's speaking persona; equation with the historical Solomon is traditional, not certain."),
    ("song-of-songs", "Song of Songs", "anthology-or-anonymous", "The title links the work with Solomon, while composition and voice are debated."),
    ("isaiah", "Isaiah", "layered-prophetic", "Isaiah ben Amoz anchors chapters 1–39; major scholarship distinguishes later exilic and postexilic voices and shaping."),
    ("jeremiah", "Jeremiah", "layered-prophetic", "Jeremiah traditions, Baruch traditions, prose narratives, poetry, and editorial shaping form a complex book."),
    ("lamentations", "Lamentations", "anonymous", "The poems are anonymous; attribution to Jeremiah is traditional and should not be visualized as certain."),
    ("ezekiel", "Ezekiel", "prophetic-tradition-edited", "The book is anchored in Ezekiel's prophetic persona and activity while showing literary development."),
    ("daniel", "Daniel", "composite-pseudonymous", "Court tales and visions reached final form in the Hellenistic period; the ancient Daniel persona is not a certain author portrait."),
    ("hosea", "Hosea", "prophetic-tradition-edited", "Sayings associated with Hosea are preserved and edited; a portrait remains interpretive."),
    ("joel", "Joel", "unknown-prophet", "The book names Joel son of Pethuel, but biography and date remain uncertain."),
    ("amos", "Amos", "prophetic-tradition-edited", "Traditions are associated with Amos of Tekoa and later shaping; appearance is unknown."),
    ("obadiah", "Obadiah", "unknown-prophet", "The prophet's identity and date are uncertain; the name cannot support a facial reconstruction."),
    ("jonah", "Jonah", "anonymous-about-named-figure", "An anonymous narrative about Jonah son of Amittai, not an autobiography."),
    ("micah", "Micah", "prophetic-tradition-edited", "Traditions are associated with Micah of Moresheth and later editorial shaping."),
    ("nahum", "Nahum", "unknown-prophet", "The book names Nahum the Elkoshite, but biography and Elkosh's location are uncertain."),
    ("habakkuk", "Habakkuk", "unknown-prophet", "The book names Habakkuk, but almost no recoverable biography supports portrait specificity."),
    ("zephaniah", "Zephaniah", "named-prophet", "The superscription names Zephaniah and a genealogy; appearance remains unknown."),
    ("haggai", "Haggai", "named-prophet", "Dated oracles name Haggai; portrait details remain interpretive."),
    ("zechariah", "Zechariah", "layered-prophetic", "Chapters 1–8 are associated with Zechariah son of Berechiah; chapters 9–14 are widely treated as later material."),
    ("malachi", "Malachi", "name-or-title-uncertain", "Malachi may function as a name or as 'my messenger'; no certain biography or face exists."),
    ("matthew", "Matthew", "anonymous-traditional-attribution", "The Gospel does not name its author; attribution to Matthew is early tradition, not a facial identification."),
    ("mark", "Mark", "anonymous-traditional-attribution", "The Gospel does not name its author; attribution to Mark is early tradition."),
    ("luke", "Luke", "anonymous-traditional-attribution", "The Gospel and Acts share an anonymous author; attribution to Luke is traditional."),
    ("john", "John", "anonymous-johannine", "The Gospel's beloved disciple, witnesses, narrator, and final author/editor should not be collapsed into one certain face."),
    ("acts", "Acts", "anonymous-traditional-attribution", "Acts shares an anonymous author with Luke; attribution to Luke is traditional."),
    ("romans", "Romans", "named-undisputed", "Paul is the letter's author; Tertius identifies himself as the person who wrote the physical letter in Romans 16:22."),
    ("1-corinthians", "1 Corinthians", "named-undisputed", "The letter names Paul and Sosthenes; Pauline authorship is widely accepted."),
    ("2-corinthians", "2 Corinthians", "named-undisputed-composite-letter-debate", "Pauline authorship is widely accepted; many scholars debate whether the canonical letter combines multiple letters."),
    ("galatians", "Galatians", "named-undisputed", "Pauline authorship is widely accepted."),
    ("ephesians", "Ephesians", "disputed-pauline", "The letter presents itself as Pauline; modern scholarship is divided over direct Pauline authorship."),
    ("philippians", "Philippians", "named-undisputed-letter-composition-debate", "Pauline authorship is widely accepted; some scholars debate whether multiple letters were combined."),
    ("colossians", "Colossians", "disputed-pauline", "The letter presents itself as Pauline; modern scholarship is divided over direct Pauline authorship."),
    ("1-thessalonians", "1 Thessalonians", "named-undisputed", "The letter names Paul, Silvanus, and Timothy; Pauline authorship is widely accepted."),
    ("2-thessalonians", "2 Thessalonians", "disputed-pauline", "The letter presents itself as Pauline; modern scholarship is divided over direct Pauline authorship."),
    ("1-timothy", "1 Timothy", "disputed-pauline", "The letter presents itself as Pauline; much modern scholarship treats the Pastoral Letters as later."),
    ("2-timothy", "2 Timothy", "disputed-pauline", "The letter presents itself as Pauline; much modern scholarship treats the Pastoral Letters as later."),
    ("titus", "Titus", "disputed-pauline", "The letter presents itself as Pauline; much modern scholarship treats the Pastoral Letters as later."),
    ("philemon", "Philemon", "named-undisputed", "Pauline authorship is widely accepted; Timothy is also named in the greeting."),
    ("hebrews", "Hebrews", "anonymous", "The work does not name its author; attribution to Paul is a later tradition and should not control the image."),
    ("james", "James", "attributed-identity-debated", "The writer names James, a servant of God and Jesus; which James and the composition history remain debated."),
    ("1-peter", "1 Peter", "attributed-authorship-debated", "The letter names Peter; direct Petrine authorship and the role of Silvanus remain debated."),
    ("2-peter", "2 Peter", "pseudonymous-majority-view", "The letter speaks as Peter; most critical scholarship regards it as written after Peter's lifetime."),
    ("1-john", "1 John", "anonymous-johannine", "The work is anonymous and belongs to Johannine tradition; it should not receive an apostle headshot as certainty."),
    ("2-john", "2 John", "elder-anonymous", "The sender identifies as 'the elder'; equation with a specific John is debated."),
    ("3-john", "3 John", "elder-anonymous", "The sender identifies as 'the elder'; equation with a specific John is debated."),
    ("jude", "Jude", "attributed-identity-debated", "The writer names Jude, brother of James; identity and composition remain debated."),
    ("revelation", "Revelation", "named-john-identity-debated", "The seer calls himself John and writes from Patmos; he is not automatically John the apostle or Gospel author."),
]

KEY_FIGURES = [
    ("abraham", "Abraham", "Genesis 11:26–25:11", "West Asian pastoral household world; exact date, clothing, and face are unknown.", False),
    ("sarah", "Sarah", "Genesis 11:29–23:20", "West Asian matriarch; Genesis 12:11 describes her as beautiful, but exact appearance is unknown.", True),
    ("moses", "Moses", "Exodus–Deuteronomy", "Ancient Egyptian and Levantine setting; Moses' exact date, face, and dress are unrecoverable.", False),
    ("ruth", "Ruth", "Ruth", "Moabite woman in an Iron Age narrative world; ethnicity should be West Asian, not northern European.", False),
    ("david", "David", "1 Samuel 16–1 Kings 2", "Ancient Judahite king; 1 Samuel 16:12 describes striking eyes and good appearance, without supporting a modern heroic ideal.", True),
    ("mary-of-nazareth", "Mary of Nazareth", "Matthew 1–2; Luke 1–2; selected Gospel scenes", "Jewish woman from Roman-period Galilee; no textual beauty claim or recoverable face.", False),
    ("mary-magdalene", "Mary Magdalene", "Luke 8:1–3; Gospel passion and resurrection narratives", "Jewish woman associated with Magdala; no textual beauty claim or recoverable face.", False),
    ("simon-peter", "Simon Peter", "The Gospels; Acts; Galatians", "Jewish Galilean fisherman and apostolic leader; no recoverable face or textual beauty claim.", False),
    ("paul", "Paul", "Acts; undisputed Pauline letters", "Jewish man from Tarsus active across the Roman Mediterranean; later portrait traditions are not facial evidence.", False),
    ("jesus", "Jesus of Nazareth", "The four Gospels", "Jewish man from Roman-period Galilee; ordinary, weathered, non-European, and not idealized. Exact face and clothing are unknown; the Shroud of Turin is excluded as facial evidence.", False),
]


def book_strategy(status: str) -> str:
    if status in {"named-undisputed", "named-prophet", "unknown-prophet", "prophetic-tradition-edited"}:
        return "interpretive-named-figure-portrait"
    if "prophetic" in status:
        return "authorship-aware-multi-voice-editorial"
    if "pauline" in status or "pseudonymous" in status or "attributed" in status or "identity-debated" in status:
        return "attribution-and-debate-editorial"
    return "anonymous-or-composite-scribal-editorial"


def main() -> None:
    entries = []
    for slug, title, status, note in BOOKS:
        sources = [OT_SOURCE] if len(entries) < 39 else [NT_SOURCE]
        if slug == "isaiah":
            sources.append(ISAIAH_SOURCE)
        strategy = book_strategy(status)
        entries.append({
            "id": f"profile-book-{slug}",
            "kind": "book-authorial-identity",
            "book": title,
            "subject_label": f"Voices behind {title}",
            "authorship_status": status,
            "evidence_note": note,
            "visual_strategy": strategy,
            "beauty_claim": "not-applicable",
            "racial_accuracy": "Use historically plausible West Asian, North African, eastern Mediterranean, or relevant imperial-period appearance; never default to modern northern European whiteness.",
            "portrait_limit": "Any face, clothing, room, landscape, and writing material are illustrative rather than reconstructed.",
            "sources": sources,
            "publication_status": "blocked",
            "human_scholarly_review": "required",
            "human_visual_review": "required",
        })
    for slug, name, texts, note, beauty in KEY_FIGURES:
        entries.append({
            "id": f"profile-person-{slug}",
            "kind": "named-biblical-person",
            "book": None,
            "subject_label": name,
            "primary_texts": texts,
            "authorship_status": "not-applicable",
            "evidence_note": note,
            "visual_strategy": "interpretive-named-figure-portrait",
            "beauty_claim": "textually-described" if beauty else "not-described",
            "racial_accuracy": "Use historically plausible West Asian, North African, or eastern Mediterranean appearance as appropriate; never default to modern northern European whiteness.",
            "portrait_limit": "The face, skin tone within a plausible regional range, hair, clothing, and background are illustrative rather than reconstructed.",
            "sources": [OT_SOURCE if slug in {"abraham", "sarah", "moses", "ruth", "david"} else NT_SOURCE],
            "publication_status": "blocked",
            "human_scholarly_review": "required",
            "human_visual_review": "required",
        })
    payload = {
        "schema_version": 1,
        "plan_id": "biblical-profile-program-2026-09-07",
        "book_profile_count": len(BOOKS),
        "key_person_count": len(KEY_FIGURES),
        "total_count": len(entries),
        "global_constraints": [
            "No image is a facial reconstruction.",
            "No modern northern European racial default.",
            "No idealized beauty unless the biblical text describes beauty or striking appearance.",
            "No halo, superhero physique, fantasy costume, modern makeup, or modern racial caricature.",
            "Anonymous, composite, layered, pseudonymous, and disputed authorship must remain visible in the visual strategy.",
            "The Shroud of Turin is not facial evidence for Jesus.",
            "Publication remains blocked until scholarly, visual, rights, and accessibility review are complete.",
        ],
        "entries": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} profile plans to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
