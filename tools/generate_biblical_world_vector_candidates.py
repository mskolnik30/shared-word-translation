#!/usr/bin/env python3
"""Generate deterministic, publication-blocked Biblical World SVG candidates."""

from __future__ import annotations

import hashlib
import html
import json
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "resources" / "biblical-world" / "registry.json"
OUT = ROOT / "resources" / "biblical-world" / "candidates" / "vectors"
MANIFEST = OUT / "manifest.json"

PALETTE = {
    "navy": "#19354D",
    "teal": "#2B7773",
    "rust": "#A6533F",
    "ink": "#26333B",
    "muted": "#5D6B72",
    "paper": "#F7F2E8",
    "panel": "#FFFDFC",
    "line": "#CAD5D2",
    "gold": "#C49347",
    "water": "#DDECEE",
}


def diagram(title, texts, nodes, caution):
    return {"title": title, "primary_texts": texts, "nodes": nodes, "caution": caution}


DIAGRAMS = {
    "visual-moriah-traditions": diagram(
        "Moriah: text and later identification", ["Genesis 22:2", "2 Chronicles 3:1"],
        ["Genesis names the land of Moriah", "Chronicles names Mount Moriah as the temple site", "The exact Genesis location remains disputed"],
        "This is an evidence-and-tradition diagram, not a claim that one modern point is certain."),
    "visual-horeb-sinai-traditions": diagram(
        "Horeb / Sinai: a disputed location", ["Exodus 3:1", "Exodus 19:1–20:21", "Deuteronomy 1:2, 6"],
        ["The texts use Horeb and Sinai", "Travel notices provide broad relationships", "Several modern identifications compete", "No proposal is conclusive"],
        "No modern mountain is presented as established."),
    "visual-mercy-seat": diagram(
        "Ark and cover: textual relationships", ["Exodus 25:10–22", "Leviticus 16:11–17"],
        ["Ark described in Exodus", "Cover and cherubim described above it", "Cloud and atonement ritual in Leviticus 16", "No surviving ark confirms appearance"],
        "Schematic only; dimensions and relationships follow the texts, while visual details remain unknown."),
    "visual-corinth-assembly": diagram(
        "The Corinthian assembly: voices and order", ["1 Corinthians 11:17–34", "1 Corinthians 12:4–27", "1 Corinthians 14:26–40"],
        ["A gathered body with unequal status", "Many gifts and speaking roles", "Edification and intelligibility", "Discernment and ordered participation"],
        "No room, table, seating plan, or individual appearance is reconstructed."),
    "visual-gibeah-region": diagram(
        "Gibeah: probable, not certain", ["Judges 19–20", "1 Samuel 10:26", "1 Samuel 15:34"],
        ["Biblical Gibeah belongs to Benjamin", "Narratives connect it with Saul", "Tell el-Ful is a common proposal", "The identification is probable rather than certain"],
        "Site-identification schematic; not a precise ancient street map."),
    "visual-amalek-memory-map": diagram(
        "Amalek in Israel's memory", ["Exodus 17:8–16", "Deuteronomy 25:17–19", "1 Samuel 15", "Esther 3:1"],
        ["Attack remembered in Exodus", "Memory becomes a command in Deuteronomy", "Royal violence in Samuel", "Agagite language echoes in Esther"],
        "A literary-memory map, not a geographic claim or modern warrant for violence."),
    "visual-ecclesiastes-times": diagram(
        "A time for every matter", ["Ecclesiastes 3:1–8"],
        ["Birth and death", "Weeping and laughing", "Silence and speech", "War and peace"],
        "Symbolic arrangement of the poem's pairs; not a prediction or fixed life schedule."),
    "visual-martha-household": diagram(
        "Martha, Mary, and Jesus: the narrated exchange", ["Luke 10:38–42"],
        ["Martha welcomes Jesus", "Mary listens at Jesus' feet", "Martha voices her burden", "Jesus answers Martha directly"],
        "Relational schematic only. The house, furniture, meal, and seating are not described."),
    "visual-romans-love-flow": diagram(
        "Love without pretense", ["Romans 12:9–21"],
        ["Hold fast to the good", "Honor, hospitality, and shared life", "Bless persecutors; do not repay evil", "Overcome evil with good"],
        "The passage includes 'if possible, so far as it depends on you'; it does not require unsafe reconciliation."),
    "visual-james-faith-works": diagram(
        "Faith shown in action", ["James 2:14–26"],
        ["A claim to faith", "A neighbor lacks food or clothing", "Words without material care do not help", "Living faith becomes visible in action"],
        "This diagram follows James's argument without reducing salvation to a scorecard."),
    "visual-millennium-views": diagram(
        "Revelation 20 and later millennial readings", ["Revelation 20:1–10"],
        ["The text's thousand-year scene", "Premillennial readings", "Amillennial readings", "Postmillennial readings"],
        "The three labels describe later interpretive traditions; the diagram does not select one as certain."),
    "visual-levitical-holiness-context": diagram(
        "Holiness, kinship, and disputed application", ["Leviticus 18", "Leviticus 20"],
        ["Israel's holiness code", "Kinship, household, status, and land", "Prohibitions in an ancient social world", "Disputed modern ethical applications"],
        "Ancient categories are not mapped one-to-one onto modern identities."),
    "visual-sotah-ritual-sequence": diagram(
        "The jealousy ordeal in sequence", ["Numbers 5:11–31"],
        ["A husband brings an accusation", "The priest administers the prescribed rite", "An oath and bitter water are described", "The text assigns consequences asymmetrically"],
        "Sequence only; no room, vessel, clothing, or bodily effect is reconstructed."),
    "visual-bethlehem-threshing-floor": diagram(
        "Ruth 3: movement and risk", ["Ruth 3"],
        ["Naomi proposes a plan", "Ruth approaches the threshing floor", "Ruth and Boaz negotiate protection", "Ruth returns with grain"],
        "Narrative schematic only. The floor, shelter, clothing, and sleeping arrangement are unknown."),
    "visual-david-sends-takes": diagram(
        "Royal power: David sends and takes", ["2 Samuel 11"],
        ["David sends for information", "David sends messengers and takes Bathsheba", "David sends orders concerning Uriah", "The prophet later exposes the abuse of power"],
        "The diagram centers royal agency and does not romanticize coercion."),
    "visual-pericope-manuscripts": diagram(
        "John 7:53–8:11 in the manuscript tradition", ["John 7:53–8:11"],
        ["Absent from the earliest surviving Greek witnesses", "Present in many later manuscripts", "Placed at different locations in some witnesses", "Printed with textual notes in modern editions"],
        "A simplified transmission diagram; manuscript dates and readings require textual-specialist review."),
    "visual-acts-property-contrast": diagram(
        "Shared property and deceptive performance", ["Acts 4:32–5:11"],
        ["Believers share to meet needs", "Barnabas gives transparently", "Ananias and Sapphira misrepresent a gift", "Peter says the property remained under their authority"],
        "The contrast concerns deception and communal trust, not a mandate for coerced giving."),
    "visual-reconciliation-agency": diagram(
        "God's reconciling initiative", ["2 Corinthians 5:14–21"],
        ["God acts in Christ", "Reconciliation is entrusted as a message", "Messengers appeal as ambassadors", "New creation frames the calling"],
        "The passage must not be used to compel contact with an abuser or erase safety and agency."),
    "visual-galatians-status-pairs": diagram(
        "Baptismal belonging across status pairs", ["Galatians 3:26–29"],
        ["Jew and Greek", "Enslaved and free", "Male and female", "One in Christ; heirs according to promise"],
        "Unity does not erase embodied difference or excuse unequal treatment."),
    "visual-ephesians-household-syntax": diagram(
        "Ephesians 5:21–6:9: sequence and debated syntax", ["Ephesians 5:21–6:9"],
        ["5:21 calls for mutual submission", "Wives and husbands", "Children and fathers", "Enslaved people and masters"],
        "Verse 5:21 immediately precedes the household speech; its grammatical relation and scope are debated."),
    "visual-census-plague-temple": diagram(
        "Census, plague, altar, and temple memory", ["2 Samuel 24", "1 Chronicles 21", "2 Chronicles 3:1"],
        ["A census is ordered", "A plague follows", "An altar is built at a threshing floor", "Chronicles connects the site with the temple"],
        "Samuel and Chronicles narrate agency differently; the diagram preserves both accounts."),
    "visual-chronicles-land-covenant": diagram(
        "Temple prayer, land, exile, and return", ["2 Chronicles 6–7", "2 Chronicles 36:15–23"],
        ["Temple dedication and prayer", "Warnings about covenant unfaithfulness", "Destruction and exile", "Return under Persian rule"],
        "A literary-theological movement, not a formula for blaming communities for disaster."),
    "visual-nehemiah-debt-flow": diagram(
        "Debt and loss in Nehemiah 5", ["Nehemiah 5:1–13"],
        ["Food shortage and taxation", "Fields and houses mortgaged", "Debt pushes children into servitude", "Nehemiah demands restoration and an end to interest"],
        "The diagram makes economic coercion visible rather than spiritualizing the crisis."),
    "visual-colossian-household-voices": diagram(
        "Household voices in Colossians", ["Colossians 3:18–4:1"],
        ["Wives and husbands", "Children and fathers", "Enslaved people", "Masters addressed under a heavenly Master"],
        "Description of an ancient hierarchy is not endorsement of slavery or abuse."),
    "visual-thessalonians-meeting": diagram(
        "The letter's account of resurrection and meeting", ["1 Thessalonians 4:13–18"],
        ["The Lord descends", "The dead in Christ rise first", "The living are caught up together", "All meet the Lord; the community comforts one another"],
        "The sequence follows the letter's imagery; it is not a modern end-times timetable."),
    "visual-lawless-one-interpretations": diagram(
        "The lawless one and the restraint", ["2 Thessalonians 2:1–12"],
        ["Rebellion and a lawless figure", "A restraining presence or power", "Deceptive signs", "Defeat at the Lord's appearing"],
        "The letter's account is highly allusive; historical identifications remain disputed."),
    "visual-authentein-interpretations": diagram(
        "1 Timothy 2:12 and a disputed verb", ["1 Timothy 2:8–15"],
        ["Learning in quietness", "The rare verb authentein", "A restriction paired with teaching", "Debates over situation, scope, and duration"],
        "The diagram presents the interpretive questions and does not resolve them by assertion."),
    "visual-scripture-purpose": diagram(
        "Sacred writings and their purpose", ["2 Timothy 3:14–17"],
        ["The letter recalls learned sacred writings", "They make wise for salvation through faith", "Scripture is described as God-breathed", "Teaching, correction, and formation equip for good work"],
        "Claims are attributed to the letter rather than automatically to the historical Paul."),
    "visual-job-reader-knowledge": diagram(
        "What Job knows—and what the reader knows", ["Job 1–2", "Job 38–42", "Job 42:7"],
        ["The reader sees the heavenly prologue", "Job and the friends do not", "Job refuses simple punishment logic", "God says the friends did not speak rightly about God as Job did"],
        "Job's suffering is not presented as punishment for hidden wrongdoing."),
    "visual-proverbs31-labor-network": diagram(
        "The woman of strength: a labor network", ["Proverbs 31:10–31"],
        ["Textiles and household provision", "Trade and purchase of a field", "Care for poor and vulnerable people", "Wisdom, teaching, and public honor"],
        "The poem praises skilled economic agency; it is not a checklist imposed on every woman."),
    "visual-song-spring-imagery": diagram(
        "Spring imagery and mutual desire", ["Song of Songs 2:8–17"],
        ["Rain passes and flowers appear", "Birdsong and fruit signal a season", "The lovers call and answer", "Garden and animal images intensify desire"],
        "Symbolic botanical arrangement; species identifications and the pictured landscape are not reconstructions."),
    "visual-jeremiah-lament-movements": diagram(
        "Jeremiah 20: praise, protest, and curse", ["Jeremiah 20:7–18"],
        ["The speaker protests overpowering vocation", "A word like fire cannot be contained", "Praise interrupts the lament", "The poem ends by cursing the day of birth"],
        "The emotional movements are preserved without forcing a neat resolution."),
    "visual-philemon-relationship": diagram(
        "Philemon: appeal inside a slaveholding world", ["Philemon 8–21"],
        ["The letter's sender appeals rather than commands", "Onesimus is called a beloved brother", "Philemon holds social and legal power", "The outcome is not narrated"],
        "The appeal unsettles status but does not explicitly abolish Roman slavery."),
    "visual-hebrews-warning-encouragement": diagram(
        "Warning and encouragement in Hebrews", ["Hebrews 6:4–12", "Hebrews 10:19–39", "Hebrews 12:1–17"],
        ["Severe warnings name real danger", "Confidence rests in Jesus' priestly work", "The community is urged to encourage one another", "Endurance is communal, not solitary fear"],
        "Warning passages must not be weaponized to control traumatized or questioning readers."),
    "visual-1peter-slavery-context": diagram(
        "1 Peter 2:18–25 in a slaveholding context", ["1 Peter 2:11–3:7"],
        ["The letter addresses household subordinates", "Enslaved people face unjust suffering", "Christ's suffering is invoked", "Modern readers must name slavery's violence"],
        "The passage does not authorize slavery or require anyone to remain in abuse."),
    "visual-2peter-text-variants": diagram(
        "2 Peter 3:10: major textual outcomes", ["2 Peter 3:8–13"],
        ["The day arrives unexpectedly", "Some witnesses yield 'will be found/exposed'", "Others support destruction or burning language", "The chapter moves toward new heavens and new earth"],
        "A simplified textual map; exact witness groupings require specialist verification."),
    "visual-lamentations-acrostic": diagram(
        "Lamentations and alphabetic form", ["Lamentations 1–5"],
        ["Chapters 1 and 2 use alphabetic acrostics", "Chapter 3 triples the alphabetic pattern", "Chapter 4 returns to an acrostic", "Chapter 5 has twenty-two verses without a full acrostic"],
        "The form orders grief without resolving it."),
    "visual-ezekiel-metaphor-layers": diagram(
        "Ezekiel's city-wife metaphors: layered reading", ["Ezekiel 16", "Ezekiel 23"],
        ["Cities are personified as women", "Political alliances become sexual metaphor", "Judgment is narrated through graphic violence", "Readers must distinguish rhetoric from an ethical model"],
        "The imagery can retraumatize; it must never legitimate sexual or domestic violence."),
    "visual-daniel7-symbol-key": diagram(
        "Daniel 7: symbols within the vision", ["Daniel 7"],
        ["Four beasts rise from the sea", "A boastful horn opposes the holy ones", "The Ancient One sits in judgment", "One like a human being receives dominion"],
        "The chapter interprets beasts as kingdoms; later identifications remain debated."),
    "visual-hosea-sign-names": diagram(
        "Hosea's sign-names and reversal", ["Hosea 1–2"],
        ["Jezreel names remembered bloodshed", "Lo-Ruhamah signals 'no compassion'", "Lo-Ammi signals 'not my people'", "The poetry later reverses rejection toward mercy and belonging"],
        "The children's symbolic use and the marriage metaphor require explicit harm-aware review."),
    "visual-joel-social-pairs": diagram(
        "The Spirit poured on all flesh", ["Joel 2:28–32"],
        ["Sons and daughters prophesy", "Old and young receive dreams and visions", "Male and female enslaved people receive the Spirit", "Deliverance is announced amid cosmic signs"],
        "The social pairs emphasize breadth rather than a hierarchy of recipients."),
    "visual-1john-love-claims": diagram(
        "Love, fear, and truthful claims", ["1 John 4:7–21"],
        ["Love originates in God", "God's love is made visible in Jesus", "Perfected love drives out fear", "Love of God is tested by love of sibling"],
        "The passage critiques false claims; it must not suppress truthful naming of harm."),
    "visual-2john-hospitality-decisions": diagram(
        "2 John: hospitality and teaching boundaries", ["2 John 7–11"],
        ["Deceivers deny Jesus Christ coming in flesh", "The community is told to watch itself", "Receiving a traveling teacher implies support", "The instruction addresses a specific teaching conflict"],
        "The passage is not a universal command to shun every disagreement."),
    "visual-3john-authority-network": diagram(
        "3 John: hospitality and contested authority", ["3 John"],
        ["The elder writes", "Gaius supports traveling coworkers", "Diotrephes rejects the elder and expels others", "Demetrius receives commendation"],
        "The network shows competing authority claims, not a complete church organization chart."),
    "visual-jude-allusion-network": diagram(
        "Jude's scriptural and traditional allusions", ["Jude 5–16", "1 Enoch 1:9"],
        ["Exodus, rebellious angels, and Sodom", "Michael and Moses: a tradition later associated with the Assumption of Moses", "Cain, Balaam, and Korah", "Jude explicitly quotes wording from 1 Enoch"],
        "The Moses tradition and the quotation from 1 Enoch must not be conflated."),
    "visual-romans-olive-tree": diagram(
        "The olive tree and the warning against boasting", ["Romans 11:11–32"],
        ["A cultivated root supports the branches", "Some branches are broken", "Wild branches are grafted in", "Gentile branches are warned not to boast"],
        "The metaphor does not justify contempt for Jewish people or replacement theology."),
    "visual-amos-justice-waters": diagram(
        "Justice like waters", ["Amos 5:21–24"],
        ["Festivals and offerings are rejected", "Songs are refused", "Justice must roll like waters", "Righteousness like an enduring stream"],
        "Symbolic art based on the poem; not a reconstruction of an ancient sanctuary."),
    "visual-micah-threefold-requirement": diagram(
        "What does the LORD require?", ["Micah 6:1–8"],
        ["Do justice", "Love covenant loyalty", "Walk humbly with your God", "The answer stands within a covenant lawsuit"],
        "The three phrases summarize 6:8 without erasing the chapter's legal and communal setting."),
    "visual-habakkuk-vision-delay": diagram(
        "Vision, delay, and faithfulness", ["Habakkuk 2:1–5"],
        ["The prophet watches for an answer", "The vision is written plainly", "Its appointed time may seem delayed", "The righteous lives by faithfulness"],
        "Later Jewish and Christian uses are reception history, not replacements for Habakkuk's setting."),
    "visual-zephaniah-book-movement": diagram(
        "Zephaniah: judgment, remnant, and restoration", ["Zephaniah 1–3"],
        ["Judgment begins with Judah and Jerusalem", "The nations also face judgment", "A humble remnant is envisioned", "The book closes with gathering and rejoicing"],
        "The movement does not turn historical violence into a timetable for current events."),
    "visual-haggai-temple-timeline": diagram(
        "Haggai's dated messages", ["Haggai 1:1", "Haggai 1:15", "Haggai 2:1", "Haggai 2:10, 20"],
        ["Year 2, month 6, day 1: rebuild", "Month 6, day 24: work begins", "Month 7, day 21: encouragement", "Month 9, day 24: holiness and Zerubbabel oracles"],
        "Regnal dates are retained; modern calendar equivalents vary slightly by reconstruction."),
    "visual-zechariah-mourning-groups": diagram(
        "Zechariah 12: households mourning", ["Zechariah 12:10–14"],
        ["House of David", "House of Nathan", "House of Levi and Shimei", "Every remaining family, each apart"],
        "The text lists household groups; later christological readings belong to reception history."),
    "visual-malachi-216-translations": diagram(
        "Malachi 2:16: a difficult Hebrew sentence", ["Malachi 2:13–16"],
        ["One reading: 'he hates divorce'", "Another: 'if he hates and divorces'", "The verse also condemns covering a garment with violence", "Translation depends on syntax, speaker, and textual judgment"],
        "No English rendering should be used to trap someone in violence or abuse."),
    "visual-1cor6-translation-history": diagram(
        "1 Corinthians 6:9: disputed Greek terms", ["1 Corinthians 6:9–11"],
        ["malakoi has a broad history of meanings", "arsenokoitai is rare and disputed", "English labels have shifted across translation history", "Modern identity terms are not automatic lexical equivalents"],
        "A lexical-history schematic; it does not erase moral debate or claim scholarly unanimity."),
}


MAPS = {
    "visual-philippi-regional": {
        "title": "Philippi in Macedonia", "primary_texts": ["Acts 16:6–40", "Philippians 1:1"],
        "bbox": [22.3, 39.8, 24.8, 41.2],
        "points": [["Philippi", 24.286, 41.013, "established"], ["Neapolis (port)", 24.413, 40.937, "established"], ["Amphipolis", 23.846, 40.823, "established"], ["Thessalonica", 22.944, 40.640, "established"]],
        "sources": ["https://pleiades.stoa.org/places/501482", "https://pleiades.stoa.org/places/501347"],
        "note": "Coordinate orientation only; no unmentioned route is asserted."},
    "visual-syro-ephraimite-region": {
        "title": "The Syro-Ephraimite crisis", "primary_texts": ["2 Kings 15:29–16:20", "Isaiah 7–8"],
        "bbox": [34.7, 31.2, 37.0, 34.1],
        "points": [["Jerusalem", 35.235, 31.778, "established"], ["Samaria", 35.189, 32.276, "established"], ["Damascus", 36.292, 33.513, "established"]],
        "sources": ["https://pleiades.stoa.org/places/687928", "https://pleiades.stoa.org/places/678370", "https://pleiades.stoa.org/places/678106"],
        "note": "The map locates capitals; borders and campaign routes are not reconstructed."},
    "visual-nineveh-region": {
        "title": "Nineveh and the Assyrian heartland", "primary_texts": ["Jonah 1–4", "Nahum 1–3"],
        "bbox": [42.5, 35.7, 44.0, 36.9],
        "points": [["Nineveh", 43.152, 36.359, "established"], ["Modern Mosul", 43.130, 36.340, "modern reference"]],
        "sources": ["https://pleiades.stoa.org/places/874621", "https://pleiades.stoa.org/places/874609"],
        "note": "Ancient Nineveh is located across the Tigris from modern Mosul."},
    "visual-tyre-region": {
        "title": "Tyre and the southern Phoenician coast", "primary_texts": ["Mark 7:24–30"],
        "bbox": [34.8, 32.7, 36.1, 33.7],
        "points": [["Tyre", 35.196, 33.270, "established"], ["Sidon", 35.369, 33.560, "established"], ["Caesarea Philippi", 35.693, 33.248, "established"]],
        "sources": ["https://pleiades.stoa.org/places/678437", "https://pleiades.stoa.org/places/678393", "https://pleiades.stoa.org/places/678324"],
        "note": "Regional orientation; Mark names the region of Tyre but does not narrate a precise route."},
    "visual-carmel-kishon-region": {
        "title": "Carmel, Kishon, and Jezreel", "primary_texts": ["1 Kings 18:19–46"],
        "bbox": [34.7, 32.2, 35.7, 33.0],
        "points": [["Mount Carmel", 35.050, 32.730, "regional"], ["Kishon River", 35.020, 32.800, "representative"], ["Jezreel", 35.322, 32.558, "probable"], ["Megiddo", 35.184, 32.585, "established"]],
        "sources": ["https://pleiades.stoa.org/places/678321", "https://whc.unesco.org/en/list/1108/"],
        "note": "River and mountain markers are representative; Elijah's exact path is not recoverable."},
    "visual-jericho-bethel-route": {
        "title": "Jericho, Bethel, and Ai", "primary_texts": ["Joshua 6–8"],
        "bbox": [35.0, 31.7, 35.6, 32.1],
        "points": [["Jericho / Tell es-Sultan", 35.444, 31.871, "established"], ["Bethel (common identification)", 35.222, 31.938, "probable"], ["Ai / et-Tell proposal", 35.261, 31.917, "disputed"]],
        "sources": ["https://whc.unesco.org/en/list/1687/", "https://www.cambridge.org/core/books/new-cambridge-history-of-the-bible/archaeological-study-of-the-bible/3622CEDDB3F6F42D0005D3737A52E16A"],
        "note": "No route line is drawn because Bethel/Ai identifications and the campaign reconstruction are debated."},
    "visual-persian-judah-return": {
        "title": "Judah within the Persian imperial world", "primary_texts": ["Ezra 1–2", "Ezra 7–8"],
        "bbox": [34.0, 30.5, 50.0, 34.0],
        "points": [["Jerusalem", 35.235, 31.778, "established"], ["Babylon", 44.421, 32.536, "established"], ["Susa", 48.257, 32.190, "established"]],
        "sources": ["https://pleiades.stoa.org/places/687928", "https://pleiades.stoa.org/places/893951", "https://pleiades.stoa.org/places/912936"],
        "note": "The points establish scale; the returnees did not all follow one documented route."},
    "visual-susa-persian-provinces": {
        "title": "Susa and the world imagined by Esther", "primary_texts": ["Esther 1:1–2", "Esther 8:9"],
        "bbox": [32.0, 20.0, 78.0, 42.0],
        "points": [["Susa", 48.257, 32.190, "established"], ["Jerusalem", 35.235, 31.778, "established"], ["Babylon", 44.421, 32.536, "established"], ["Indus region", 72.800, 30.000, "representative"]],
        "sources": ["https://pleiades.stoa.org/places/912936", "https://pleiades.stoa.org/places/893951"],
        "note": "Representative scale only. The book's 127 provinces are not reconstructed as precise borders."},
    "visual-crete-assemblies": {
        "title": "Crete: representative urban centers", "primary_texts": ["Titus 1:5"],
        "bbox": [23.3, 34.7, 26.5, 35.7],
        "points": [["Gortyna", 24.947, 35.063, "established"], ["Knossos", 25.163, 35.298, "established"], ["Crete", 24.900, 35.200, "regional"]],
        "sources": ["https://pleiades.stoa.org/places/589796", "https://pleiades.stoa.org/places/589872"],
        "note": "Titus does not name the individual cities where elders were to be appointed."},
    "visual-edom-jerusalem-routes": {
        "title": "Edom and Jerusalem", "primary_texts": ["Obadiah 10–14"],
        "bbox": [34.5, 29.8, 36.2, 32.2],
        "points": [["Jerusalem", 35.235, 31.778, "established"], ["Bozrah / Busayra", 35.607, 30.733, "probable"], ["Petra / Sela traditions", 35.444, 30.329, "representative"]],
        "sources": ["https://pleiades.stoa.org/places/687928", "https://whitelevy.fas.harvard.edu/publications/busayra-excavations-crystal-bennett-1971-1980"],
        "note": "No invasion or refugee route is asserted; the map only shows regional relationship."},
    "visual-nineveh-fall-context": {
        "title": "The collapse of Assyrian power", "primary_texts": ["Nahum 1–3"],
        "bbox": [37.0, 32.0, 45.5, 37.5],
        "points": [["Nineveh", 43.152, 36.359, "established"], ["Harran", 39.031, 36.864, "established"], ["Carchemish", 38.014, 36.829, "established"], ["Babylon", 44.421, 32.536, "established"]],
        "sources": ["https://pleiades.stoa.org/places/874621", "https://pleiades.stoa.org/places/658427", "https://pleiades.stoa.org/places/658465", "https://pleiades.stoa.org/places/893951"],
        "note": "Orientation to major centers; military routes and imperial borders are not reconstructed."},
}


def wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def text_lines(x: int, y: int, value: str, *, size=28, width=34, weight=400, color=None, line=36, anchor="start") -> str:
    color = color or PALETTE["ink"]
    spans = []
    for index, item in enumerate(wrap(value, width)):
        dy = 0 if index == 0 else line
        spans.append(f'<tspan x="{x}" dy="{dy}">{html.escape(item)}</tspan>')
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{"".join(spans)}</text>'


def svg_shell(body: str, title: str, description: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800" role="img" aria-labelledby="title desc">
  <title id="title">{html.escape(title)}</title>
  <desc id="desc">{html.escape(description)}</desc>
  <rect width="1200" height="800" fill="{PALETTE['paper']}"/>
  <style>text {{ font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}</style>
  {body}
</svg>
'''


def render_diagram(spec: dict) -> tuple[str, str]:
    title = spec["title"]
    nodes = spec["nodes"]
    title_line_count = len(wrap(title, 45))
    primary_y = 140 + title_line_count * 46
    y0 = max(260, primary_y + 62)
    body = [f'<rect x="48" y="44" width="1104" height="712" rx="32" fill="{PALETTE["panel"]}" stroke="{PALETTE["line"]}" stroke-width="3"/>']
    body.append(text_lines(96, 112, title, size=38, width=45, weight=750, color=PALETTE["navy"], line=46))
    body.append(text_lines(96, primary_y, "Primary texts: " + "; ".join(spec["primary_texts"]), size=20, width=92, color=PALETTE["muted"], line=26))
    node_w = 228
    gap = 35
    total = len(nodes) * node_w + (len(nodes) - 1) * gap
    start = (1200 - total) // 2
    for index, node in enumerate(nodes):
        x = start + index * (node_w + gap)
        if index:
            body.append(f'<path d="M {x-gap+8} {y0+104} L {x-10} {y0+104}" stroke="{PALETTE["teal"]}" stroke-width="5" stroke-linecap="round"/>')
            body.append(f'<path d="M {x-22} {y0+92} L {x-10} {y0+104} L {x-22} {y0+116}" fill="none" stroke="{PALETTE["teal"]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
        fill = PALETTE["water"] if index % 2 == 0 else "#F2E4DA"
        body.append(f'<rect x="{x}" y="{y0}" width="{node_w}" height="224" rx="22" fill="{fill}" stroke="{PALETTE["line"]}" stroke-width="2"/>')
        body.append(f'<circle cx="{x+node_w//2}" cy="{y0+44}" r="22" fill="{PALETTE["navy"]}"/>')
        body.append(text_lines(x+node_w//2, y0+52, str(index+1), size=22, width=4, weight=700, color="#FFFFFF", anchor="middle"))
        body.append(text_lines(x+18, y0+88, node, size=21, width=17, weight=650, line=27))
    body.append(f'<rect x="96" y="560" width="1008" height="122" rx="20" fill="#FFF6E8" stroke="{PALETTE["gold"]}" stroke-width="2"/>')
    body.append(text_lines(126, 598, "Reading caution", size=21, width=30, weight=750, color=PALETTE["rust"]))
    body.append(text_lines(126, 635, spec["caution"], size=20, width=90, line=27))
    body.append(text_lines(96, 724, "UNPUBLISHED CANDIDATE • HUMAN SCHOLARLY REVIEW REQUIRED", size=18, width=90, weight=700, color=PALETTE["muted"]))
    alt = f'{title}. Four-part interpretive diagram. {"; ".join(nodes)}. Caution: {spec["caution"]}'
    return svg_shell("\n".join(body), title, alt), alt


def render_map(spec: dict) -> tuple[str, str]:
    title = spec["title"]
    min_lon, min_lat, max_lon, max_lat = spec["bbox"]
    title_line_count = len(wrap(title, 45))
    primary_y = 140 + title_line_count * 46
    left, top, width, height = 100, max(230, primary_y + 55), 640, 360
    legend_x = 790

    def pos(lon, lat):
        x = left + (lon - min_lon) / (max_lon - min_lon) * width
        y = top + (max_lat - lat) / (max_lat - min_lat) * height
        return x, y

    body = [f'<rect x="48" y="44" width="1104" height="712" rx="32" fill="{PALETTE["panel"]}" stroke="{PALETTE["line"]}" stroke-width="3"/>']
    body.append(text_lines(96, 112, title, size=38, width=45, weight=750, color=PALETTE["navy"], line=46))
    body.append(text_lines(96, primary_y, "Primary texts: " + "; ".join(spec["primary_texts"]), size=20, width=92, color=PALETTE["muted"], line=26))
    body.append(f'<rect x="{left}" y="{top}" width="{width}" height="{height}" rx="18" fill="{PALETTE["water"]}" stroke="{PALETTE["navy"]}" stroke-width="3"/>')
    for step in range(1, 5):
        x = left + width * step / 5
        y = top + height * step / 5
        body.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+height}" stroke="#B8CCCF" stroke-width="1"/>')
        body.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+width}" y2="{y:.1f}" stroke="#B8CCCF" stroke-width="1"/>')
    body.append(text_lines(left+18, top+34, "N", size=22, width=2, weight=800, color=PALETTE["navy"]))
    body.append(f'<path d="M {left+24} {top+48} L {left+24} {top+96} M {left+14} {top+60} L {left+24} {top+48} L {left+34} {top+60}" stroke="{PALETTE["navy"]}" stroke-width="4" fill="none"/>')
    label_positions = []
    for index, (label, lon, lat, certainty) in enumerate(spec["points"]):
        x, y = pos(lon, lat)
        label_positions.append((label, certainty))
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="17" fill="{PALETTE["rust"]}" stroke="#FFFFFF" stroke-width="4"/>')
        body.append(text_lines(int(x), int(y+7), str(index+1), size=18, width=2, weight=800, color="#FFFFFF", anchor="middle"))
        ly = top + 42 + index * 76
        body.append(f'<circle cx="{legend_x}" cy="{ly-7}" r="15" fill="{PALETTE["rust"]}"/>')
        body.append(text_lines(legend_x, ly, str(index+1), size=16, width=2, weight=800, color="#FFFFFF", anchor="middle"))
        body.append(text_lines(legend_x+30, ly-7, label, size=20, width=25, weight=700, color=PALETTE["navy"], line=24))
        label_lines = len(wrap(label, 25))
        body.append(text_lines(legend_x+30, ly-7+label_lines*24, f'[{certainty}]', size=15, width=25, weight=650, color=PALETTE["muted"], line=20))
    body.append(text_lines(100, 660, spec["note"], size=20, width=94, color=PALETTE["ink"], line=27))
    body.append(text_lines(96, 724, "SCHEMATIC COORDINATE MAP • NO ANCIENT BORDERS OR UNATTESTED ROUTES", size=18, width=90, weight=700, color=PALETTE["muted"]))
    alt_points = "; ".join(f"{label}, {certainty}" for label, certainty in label_positions)
    alt = f"{title}. Schematic coordinate map showing {alt_points}. {spec['note']}"
    return svg_shell("\n".join(body), title, alt), alt


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    requests = {item["id"]: item for item in registry["visual_requests"]}
    raster_ids = {"visual-jericho-archaeology", "visual-caesarea-philippi", "visual-deuteronomic-law-context"}
    expected = set(requests) - raster_ids
    actual = set(DIAGRAMS) | set(MAPS)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise SystemExit(f"Vector spec mismatch; missing={missing}; extra={extra}")

    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    for visual_id in sorted(actual):
        request = requests[visual_id]
        if visual_id in MAPS:
            spec = MAPS[visual_id]
            content, alt = render_map(spec)
            sources = spec["sources"]
            primary_texts = spec["primary_texts"]
            format_type = "schematic-coordinate-map"
        else:
            spec = DIAGRAMS[visual_id]
            content, alt = render_diagram(spec)
            sources = []
            primary_texts = spec["primary_texts"]
            format_type = "interpretive-diagram"
        path = OUT / f"{visual_id}.svg"
        path.write_text(content, encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({
            "visual_id": visual_id,
            "record_id": request["record"],
            "requested_class": request["class"],
            "candidate_format": format_type,
            "claim_label": request["claim_label"],
            "file": path.relative_to(ROOT).as_posix(),
            "sha256": digest,
            "primary_texts": primary_texts,
            "sources": sources,
            "alt_text": alt,
            "rights_basis": "Original deterministic SVG generated in this repository; source facts remain attributed separately.",
            "rights_status": "owned-candidate",
            "scholarly_review": "required",
            "accessibility_review": "required",
            "publication_status": "blocked",
        })
    payload = {
        "schema_version": 1,
        "candidate_set": "biblical-world-vectors-2026-09-07",
        "asset_count": len(entries),
        "publication_status": "blocked",
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(entries)} SVG candidates")
    print(MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
