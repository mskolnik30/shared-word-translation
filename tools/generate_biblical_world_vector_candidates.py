#!/usr/bin/env python3
"""Generate deterministic, publication-blocked Biblical World SVG candidates."""

from __future__ import annotations

import hashlib
import html
import json
import math
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
    "land": "#E9DFC9",
    "river": "#75AAB4",
    "soft_teal": "#E8F1EF",
    "soft_rust": "#F5E9E2",
}

MAP_BASE_SOURCE = "https://www.soest.hawaii.edu/pwessel/gshhg/"


def diagram(title, texts, nodes, caution):
    return {"title": title, "primary_texts": texts, "nodes": nodes, "caution": caution}


DIAGRAMS = {
    "visual-moriah-traditions": diagram(
        "Moriah: what Genesis says and Chronicles later connects", ["Genesis 22:2", "2 Chronicles 3:1"],
        ["Genesis names the land of Moriah", "Chronicles names Mount Moriah as the temple site", "The exact Genesis location remains disputed"],
        "Genesis and Chronicles make different statements about Moriah. This guide does not claim that its exact modern location is known."),
    "visual-horeb-sinai-traditions": diagram(
        "Horeb / Sinai: a disputed location", ["Exodus 3:1", "Exodus 19:1–20:21", "Deuteronomy 1:2, 6"],
        ["Exodus and Deuteronomy use both names", "Travel details show broad relationships", "Several modern locations have been proposed", "No proposal is conclusive"],
        "No modern mountain is presented as established."),
    "visual-mercy-seat": diagram(
        "The ark, its cover, and the Day of Atonement", ["Exodus 25:10–22", "Leviticus 16:11–17"],
        ["Exodus describes the ark", "The cover and cherubim are above it", "Leviticus describes the Day of Atonement ceremony", "No surviving ark confirms its appearance"],
        "The positions and dimensions follow the Bible, but no surviving ark confirms its exact appearance."),
    "visual-corinth-assembly": diagram(
        "The church in Corinth: voices and order", ["1 Corinthians 11:17–34", "1 Corinthians 12:4–27", "1 Corinthians 14:26–40"],
        ["A gathered church with unequal social standing", "Many gifts and speaking roles", "Speech should build up the church and be understood", "The community weighs what is said and participates in order"],
        "The Bible does not describe the room, table, seating plan, or individual appearances, so none is shown as if known."),
    "visual-gibeah-region": diagram(
        "Gibeah: probable, not certain", ["Judges 19–20", "1 Samuel 10:26", "1 Samuel 15:34"],
        ["Biblical Gibeah belongs to Benjamin", "Narratives connect it with Saul", "Tell el-Ful is a common proposal", "The identification is probable rather than certain"],
        "This guide identifies a likely area, not a street-by-street map."),
    "visual-amalek-memory-map": diagram(
        "Amalek in Israel's memory", ["Exodus 17:8–16", "Deuteronomy 25:17–19", "1 Samuel 15", "Esther 3:1"],
        ["Exodus remembers an attack", "Deuteronomy turns the memory into a command", "Samuel tells of royal violence", "Esther calls Haman an Agagite, recalling this older conflict"],
        "This guide follows how later biblical books remember Amalek. It does not make a geographic claim or justify violence today."),
    "visual-ecclesiastes-times": diagram(
        "A time for every matter", ["Ecclesiastes 3:1–8"],
        ["Birth and death", "Weeping and laughing", "Silence and speech", "War and peace"],
        "These are examples from the poem's paired lines, not a prediction or a fixed schedule for life."),
    "visual-martha-household": diagram(
        "Martha, Mary, and Jesus: what Luke tells us", ["Luke 10:38–42"],
        ["Martha welcomes Jesus", "Mary listens at Jesus' feet", "Martha voices her burden", "Jesus answers Martha directly"],
        "This guide follows the conversation only. Luke does not describe the house, furniture, meal, or seating."),
    "visual-romans-love-flow": diagram(
        "Love without pretense", ["Romans 12:9–21"],
        ["Hold fast to the good", "Honor, hospitality, and shared life", "Bless persecutors; do not repay evil", "Overcome evil with good"],
        "The passage includes 'if possible, so far as it depends on you'; it does not require unsafe reconciliation."),
    "visual-james-faith-works": diagram(
        "Faith shown in action", ["James 2:14–26"],
        ["A claim to faith", "A neighbor lacks food or clothing", "Words without material care do not help", "Living faith becomes visible in action"],
        "This guide follows James's argument without reducing salvation to a scorecard."),
    "visual-millennium-views": diagram(
        "Three common ways Christians read Revelation 20", ["Revelation 20:1–10"],
        ["Revelation describes a thousand-year scene", "Christ returns before the thousand years (premillennial)", "The thousand years picture Christ's present reign (amillennial)", "A long era of faithfulness comes before Christ returns (postmillennial)"],
        "These are three later Christian interpretations. The guide does not declare one of them certain."),
    "visual-levitical-holiness-context": diagram(
        "Leviticus 18 and 20: ancient laws and today's questions", ["Leviticus 18", "Leviticus 20"],
        ["Israel is called to holiness", "Family, household, social standing, and land shape the laws", "The prohibitions belong to an ancient social world", "Readers disagree about how the laws apply today"],
        "The ancient categories do not match modern identities one-for-one."),
    "visual-sotah-ritual-sequence": diagram(
        "The ritual following a husband's accusation", ["Numbers 5:11–31"],
        ["A husband brings an accusation", "The priest carries out the required ceremony", "An oath and bitter water are described", "The woman bears consequences that the husband does not"],
        "The steps come from the passage. The room, vessel, clothing, and bodily effects are not pictured or reconstructed."),
    "visual-bethlehem-threshing-floor": diagram(
        "Ruth 3: movement and risk", ["Ruth 3"],
        ["Naomi proposes a plan", "Ruth approaches the threshing floor", "Ruth and Boaz negotiate protection", "Ruth returns with grain"],
        "This guide follows the story only. The floor, shelter, clothing, and sleeping arrangement are not described."),
    "visual-david-sends-takes": diagram(
        "Royal power: David sends and takes", ["2 Samuel 11"],
        ["David sends for information", "David sends messengers and takes Bathsheba", "David sends orders concerning Uriah", "The prophet later exposes the abuse of power"],
        "The guide keeps David's use of royal power in view and does not romanticize coercion."),
    "visual-pericope-manuscripts": diagram(
        "Where John 7:53–8:11 appears in ancient copies", ["John 7:53–8:11"],
        ["Absent from the earliest surviving Greek copies", "Present in many later manuscripts", "Placed at different locations in some ancient copies", "Printed with explanatory notes in modern Bibles"],
        "This overview simplifies how surviving copies differ. A specialist must verify individual manuscripts, dates, and readings."),
    "visual-acts-property-contrast": diagram(
        "Sharing, honesty, and deception", ["Acts 4:32–5:11"],
        ["Believers share to meet needs", "Barnabas gives transparently", "Ananias and Sapphira misrepresent a gift", "Peter says the property remained under their authority"],
        "The contrast concerns deception and communal trust, not a mandate for coerced giving."),
    "visual-reconciliation-agency": diagram(
        "God begins the work of reconciliation", ["2 Corinthians 5:14–21"],
        ["God acts in Christ", "Reconciliation is entrusted as a message", "Messengers appeal as ambassadors", "The appeal is grounded in God's new creation"],
        "The passage must not be used to force contact with an abuser or take away a person's safety and freedom to choose."),
    "visual-galatians-status-pairs": diagram(
        "One in Christ across social divisions", ["Galatians 3:26–29"],
        ["Jew and Greek", "Enslaved and free", "Male and female", "One in Christ; heirs according to promise"],
        "Unity does not erase real differences or excuse unequal treatment."),
    "visual-ephesians-household-syntax": diagram(
        "Ephesians 5:21–6:9: how the sentences connect", ["Ephesians 5:21–6:9"],
        ["5:21 calls for mutual submission", "Wives and husbands", "Children and fathers", "Enslaved people and masters"],
        "Because 5:21 comes immediately before the household instructions, readers debate how the call to mutual submission shapes everything that follows."),
    "visual-census-plague-temple": diagram(
        "Census, plague, altar, and temple memory", ["2 Samuel 24", "1 Chronicles 21", "2 Chronicles 3:1"],
        ["A census is ordered", "A plague follows", "An altar is built at a threshing floor", "Chronicles connects the site with the temple"],
        "Samuel and Chronicles describe who caused the census differently; this guide preserves both accounts."),
    "visual-chronicles-land-covenant": diagram(
        "Temple prayer, land, exile, and return", ["2 Chronicles 6–7", "2 Chronicles 36:15–23"],
        ["Temple dedication and prayer", "Warnings about covenant unfaithfulness", "Destruction and exile", "Return under Persian rule"],
        "This sequence follows the book's message. It is not a formula for blaming communities for disaster."),
    "visual-nehemiah-debt-flow": diagram(
        "Debt and loss in Nehemiah 5", ["Nehemiah 5:1–13"],
        ["Food shortage and taxation", "Fields and houses mortgaged", "Debt pushes children into servitude", "Nehemiah demands restoration and an end to interest"],
        "The guide shows how debt traps families instead of treating the crisis as only a spiritual problem."),
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
        "The letter speaks indirectly and leaves key details unexplained; proposed historical identifications remain debated."),
    "visual-authentein-interpretations": diagram(
        "1 Timothy 2:12 and a disputed verb", ["1 Timothy 2:8–15"],
        ["Learning in quietness", "The rare Greek verb authentein is translated in more than one way", "A restriction paired with teaching", "Readers debate the situation, who is addressed, and whether the instruction is temporary"],
        "These questions remain debated; the guide does not choose one answer."),
    "visual-scripture-purpose": diagram(
        "Sacred writings and their purpose", ["2 Timothy 3:14–17"],
        ["The letter recalls learned sacred writings", "They make wise for salvation through faith", "Scripture is described as God-breathed", "Teaching, correction, and formation equip for good work"],
        "This guide reports what 2 Timothy says without assuming a decision about who wrote the letter."),
    "visual-job-reader-knowledge": diagram(
        "What Job knows—and what the reader knows", ["Job 1–2", "Job 38–42", "Job 42:7"],
        ["The reader sees the opening scene in heaven", "Job and his friends do not see that scene", "Job refuses the claim that suffering always proves guilt", "God says the friends did not speak rightly about God as Job did"],
        "Job's suffering is not presented as punishment for hidden wrongdoing."),
    "visual-proverbs31-labor-network": diagram(
        "The many forms of work in Proverbs 31", ["Proverbs 31:10–31"],
        ["Textiles and household provision", "Trade and purchase of a field", "Care for poor and vulnerable people", "Wisdom, teaching, and public honor"],
        "The poem praises skilled work and wise decisions; it is not a checklist imposed on every woman."),
    "visual-song-spring-imagery": diagram(
        "Spring imagery and mutual desire", ["Song of Songs 2:8–17"],
        ["Rain passes and flowers appear", "Birdsong and fruit signal a season", "The lovers call and answer", "Garden and animal images intensify desire"],
        "The images come from the poem. We cannot know exactly which plants or landscape the poet had in mind."),
    "visual-jeremiah-lament-movements": diagram(
        "Jeremiah 20: praise, protest, and curse", ["Jeremiah 20:7–18"],
        ["Jeremiah protests that his calling has overpowered him", "A word like fire cannot be contained", "Praise interrupts the lament", "The poem ends by cursing the day of birth"],
        "The emotional movements are preserved without forcing a neat resolution."),
    "visual-philemon-relationship": diagram(
        "Philemon: appeal inside a slaveholding world", ["Philemon 8–21"],
        ["The letter's sender appeals rather than commands", "Onesimus is called a beloved brother", "Philemon holds social and legal power", "The letter does not tell us what happened next"],
        "The appeal challenges the relationship, but the letter does not call for the end of Roman slavery."),
    "visual-hebrews-warning-encouragement": diagram(
        "Warning and encouragement in Hebrews", ["Hebrews 6:4–12", "Hebrews 10:19–39", "Hebrews 12:1–17"],
        ["Severe warnings name real danger", "Confidence rests in Jesus' work as high priest", "The community is urged to encourage one another", "People endure together, not through private fear"],
        "Warning passages must not be weaponized to control traumatized or questioning readers."),
    "visual-1peter-slavery-context": diagram(
        "1 Peter 2:18–25 in a slaveholding context", ["1 Peter 2:11–3:7"],
        ["The letter speaks to people with less power in Roman households", "Enslaved people face unjust suffering", "The letter points to Christ's suffering", "Modern readers must name slavery's violence"],
        "The passage does not authorize slavery or require anyone to remain in abuse."),
    "visual-2peter-text-variants": diagram(
        "2 Peter 3:10: why translations differ", ["2 Peter 3:8–13"],
        ["The day arrives unexpectedly", "Some ancient copies support 'will be found' or 'will be exposed'", "Other copies support destruction or burning language", "The chapter moves toward new heavens and a new earth"],
        "Ancient copies differ at this point. This guide summarizes the main readings; a specialist should verify the individual manuscripts."),
    "visual-lamentations-acrostic": diagram(
        "Lamentations and its Hebrew alphabet patterns", ["Lamentations 1–5"],
        ["Chapters 1 and 2 follow the Hebrew alphabet", "Chapter 3 repeats each letter three times", "Chapter 4 returns to the alphabet pattern", "Chapter 5 has twenty-two verses but no full alphabet pattern"],
        "The form orders grief without resolving it."),
    "visual-ezekiel-metaphor-layers": diagram(
        "How Ezekiel uses women to portray cities", ["Ezekiel 16", "Ezekiel 23"],
        ["Cities are portrayed as women", "Political alliances are described through sexual imagery", "Judgment is described through graphic violence", "This language is not a model for how people should speak or act"],
        "The imagery can reopen trauma. It must never be used to excuse sexual or domestic violence."),
    "visual-daniel7-symbol-key": diagram(
        "Daniel 7: symbols within the vision", ["Daniel 7"],
        ["Four beasts rise from the sea", "A boastful horn opposes the holy ones", "The Ancient One sits in judgment", "One like a human being receives authority"],
        "The chapter interprets beasts as kingdoms; later identifications remain debated."),
    "visual-hosea-sign-names": diagram(
        "The names in Hosea 1 and their reversal", ["Hosea 1–2"],
        ["Jezreel recalls earlier bloodshed", "Lo-Ruhamah signals 'no compassion'", "Lo-Ammi signals 'not my people'", "The poetry later reverses rejection toward mercy and belonging"],
        "Readers should notice the harm done when children and a wife are made into symbols."),
    "visual-joel-social-pairs": diagram(
        "The Spirit poured on all flesh", ["Joel 2:28–32"],
        ["Sons and daughters prophesy", "Old and young receive dreams and visions", "Male and female enslaved people receive the Spirit", "Deliverance is announced amid signs in the sky and on earth"],
        "The pairs show that the Spirit is given widely, not according to social rank."),
    "visual-1john-love-claims": diagram(
        "Love, fear, and truthful claims", ["1 John 4:7–21"],
        ["Love begins with God", "God's love is made visible in Jesus", "Mature love drives out fear", "Love for God is tested by love for a brother or sister"],
        "The passage critiques false claims; it must not suppress truthful naming of harm."),
    "visual-2john-hospitality-decisions": diagram(
        "2 John: hospitality and teaching boundaries", ["2 John 7–11"],
        ["Deceivers deny that Jesus Christ came in the flesh", "The community is told to watch itself", "Welcoming a traveling teacher helps that person's work", "The instruction addresses a specific teaching conflict"],
        "The passage is not a universal command to shun every disagreement."),
    "visual-3john-authority-network": diagram(
        "3 John: hospitality and a struggle over leadership", ["3 John"],
        ["The elder writes", "Gaius supports traveling coworkers", "Diotrephes rejects the elder and expels others", "Demetrius receives commendation"],
        "The guide shows a struggle over leadership, not a complete church organization chart."),
    "visual-jude-allusion-network": diagram(
        "Earlier stories and writings echoed in Jude", ["Jude 5–16", "1 Enoch 1:9"],
        ["Exodus, rebellious angels, and Sodom", "A later Jewish story connects Michael and Moses", "Cain, Balaam, and Korah", "Jude quotes 1 Enoch"],
        "The story about Michael and Moses and the quotation from 1 Enoch come from different ancient traditions. They should not be blended together."),
    "visual-romans-olive-tree": diagram(
        "The olive tree and the warning against boasting", ["Romans 11:11–32"],
        ["A cultivated root supports the branches", "Some branches are broken", "Wild branches are grafted in", "Gentile branches are warned not to boast"],
        "The image does not support contempt for Jewish people or the claim that the church has simply replaced Israel."),
    "visual-amos-justice-waters": diagram(
        "Justice like waters", ["Amos 5:21–24"],
        ["Festivals and offerings are rejected", "Songs are refused", "Justice must roll like waters", "Righteousness like an enduring stream"],
        "These lines echo the poem's imagery; they do not picture an ancient sanctuary."),
    "visual-micah-threefold-requirement": diagram(
        "What does the LORD require?", ["Micah 6:1–8"],
        ["Do justice", "Love faithful kindness", "Walk humbly with your God", "The answer comes within a scene like a courtroom, where God brings a charge against the people"],
        "These three phrases summarize 6:8 but do not replace the chapter's full setting."),
    "visual-habakkuk-vision-delay": diagram(
        "Vision, delay, and faithfulness", ["Habakkuk 2:1–5"],
        ["The prophet watches for an answer", "The vision is written plainly", "Its appointed time may seem delayed", "The righteous lives by faithfulness"],
        "Later Jewish and Christian interpretations matter, but they should not replace Habakkuk's own historical setting."),
    "visual-zephaniah-book-movement": diagram(
        "Zephaniah: judgment, a surviving people, and restoration", ["Zephaniah 1–3"],
        ["Judgment begins with Judah and Jerusalem", "The nations also face judgment", "A humble surviving people is envisioned", "The book closes with gathering and rejoicing"],
        "The movement does not turn historical violence into a timetable for current events."),
    "visual-haggai-temple-timeline": diagram(
        "Haggai's dated messages", ["Haggai 1:1", "Haggai 1:15", "Haggai 2:1", "Haggai 2:10, 20"],
        ["Year 2, month 6, day 1: rebuild", "Month 6, day 24: work begins", "Month 7, day 21: encouragement", "Month 9, day 24: messages about holiness and Zerubbabel"],
        "The dates given by the book are retained; their modern calendar equivalents vary slightly among scholars."),
    "visual-zechariah-mourning-groups": diagram(
        "Zechariah 12: households mourning", ["Zechariah 12:10–14"],
        ["House of David", "House of Nathan", "House of Levi and Shimei", "Every remaining family, each apart"],
        "The text lists households mourning separately. Later Christian readings about Jesus should not erase that first setting."),
    "visual-malachi-216-translations": diagram(
        "Malachi 2:16: a difficult Hebrew sentence", ["Malachi 2:13–16"],
        ["One reading: 'he hates divorce'", "Another: 'if he hates and divorces'", "The verse also condemns covering a garment with violence", "The translation changes with how the Hebrew sentence is divided and who is speaking"],
        "No English rendering should be used to trap someone in violence or abuse."),
    "visual-1cor6-translation-history": diagram(
        "1 Corinthians 6:9: disputed Greek terms", ["1 Corinthians 6:9–11"],
        ["malakoi literally means 'soft' and was used in several ways", "arsenokoitai is rare, and its exact meaning is disputed", "English translations have used different labels over time", "Modern identity labels are not direct one-word matches"],
        "This overview of the words does not erase moral debate or suggest that all scholars agree."),
}


MAPS = {
    "visual-philippi-regional": {
        "title": "Philippi in Macedonia", "primary_texts": ["Acts 16:6–40", "Philippians 1:1"],
        "bbox": [22.3, 39.8, 24.8, 41.2],
        "points": [["Philippi", 24.286, 41.013, "established"], ["Neapolis (port)", 24.413, 40.937, "established"], ["Amphipolis", 23.846, 40.823, "established"], ["Thessalonica", 22.944, 40.640, "established"]],
        "sources": ["https://pleiades.stoa.org/places/501482", "https://pleiades.stoa.org/places/501347"],
        "note": "This map shows where Philippi stood in relation to its port and nearby cities. Acts does not describe every part of the journey."},
    "visual-syro-ephraimite-region": {
        "title": "The Syro-Ephraimite crisis", "primary_texts": ["2 Kings 15:29–16:20", "Isaiah 7–8"],
        "bbox": [34.7, 31.2, 37.0, 34.1],
        "points": [["Jerusalem", 35.235, 31.778, "established"], ["Samaria", 35.189, 32.276, "established"], ["Damascus", 36.292, 33.513, "established"]],
        "sources": ["https://pleiades.stoa.org/places/687928", "https://pleiades.stoa.org/places/678370", "https://pleiades.stoa.org/places/678106"],
        "note": "This map locates the three capitals. Ancient borders and exact military routes are uncertain and are not shown."},
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
        "note": "This map shows the coastal region named by Mark. The Gospel does not give Jesus' exact route."},
    "visual-carmel-kishon-region": {
        "title": "Carmel, Kishon, and Jezreel", "primary_texts": ["1 Kings 18:19–46"],
        "bbox": [34.7, 32.2, 35.7, 33.0],
        "points": [["Mount Carmel", 35.050, 32.730, "regional"], ["Kishon River", 35.020, 32.800, "representative"], ["Jezreel", 35.322, 32.558, "probable"], ["Megiddo", 35.184, 32.585, "established"]],
        "sources": ["https://pleiades.stoa.org/places/678321", "https://whc.unesco.org/en/list/1108/"],
        "note": "The mountain and river labels mark broad areas. Elijah's exact path cannot be recovered."},
    "visual-jericho-bethel-route": {
        "title": "Jericho, Bethel, and Ai", "primary_texts": ["Joshua 6–8"],
        "bbox": [35.0, 31.7, 35.6, 32.1],
        "points": [["Jericho / Tell es-Sultan", 35.444, 31.871, "established"], ["Bethel (common identification)", 35.222, 31.938, "probable"], ["Ai / et-Tell proposal", 35.261, 31.917, "disputed"]],
        "sources": ["https://whc.unesco.org/en/list/1687/", "https://www.cambridge.org/core/books/new-cambridge-history-of-the-bible/archaeological-study-of-the-bible/3622CEDDB3F6F42D0005D3737A52E16A"],
        "note": "No route is drawn because scholars still debate the locations of Bethel and Ai and the course of the campaign."},
    "visual-persian-judah-return": {
        "title": "Judah within the Persian Empire", "primary_texts": ["Ezra 1–2", "Ezra 7–8"],
        "bbox": [34.0, 30.5, 50.0, 34.0],
        "points": [["Jerusalem", 35.235, 31.778, "established"], ["Babylon", 44.421, 32.536, "established"], ["Susa", 48.257, 32.190, "established"]],
        "sources": ["https://pleiades.stoa.org/places/687928", "https://pleiades.stoa.org/places/893951", "https://pleiades.stoa.org/places/912936"],
        "note": "This map shows the great distance between Jerusalem, Babylon, and Susa. The returnees did not all travel by one recorded route."},
    "visual-susa-persian-provinces": {
        "title": "Susa and the Persian Empire in Esther", "primary_texts": ["Esther 1:1–2", "Esther 8:9"],
        "bbox": [32.0, 20.0, 78.0, 42.0],
        "points": [["Susa", 48.257, 32.190, "established"], ["Jerusalem", 35.235, 31.778, "established"], ["Babylon", 44.421, 32.536, "established"], ["Indus region", 72.800, 30.000, "representative"]],
        "sources": ["https://pleiades.stoa.org/places/912936", "https://pleiades.stoa.org/places/893951"],
        "note": "This map shows the broad reach described by Esther. The book alone does not let us draw all 127 provinces with precise borders."},
    "visual-crete-assemblies": {
        "title": "Crete: representative urban centers", "primary_texts": ["Titus 1:5"],
        "bbox": [23.3, 34.7, 26.5, 35.7],
        "points": [["Gortyna", 24.947, 35.063, "established"], ["Knossos", 25.163, 35.298, "established"], ["Crete", 24.900, 35.200, "regional"]],
        "sources": ["https://pleiades.stoa.org/places/589796", "https://pleiades.stoa.org/places/589872"],
        "note": "Titus says elders should be appointed in every town but does not name those towns. Gortyna and Knossos provide geographic orientation."},
    "visual-edom-jerusalem-routes": {
        "title": "Edom and Jerusalem", "primary_texts": ["Obadiah 10–14"],
        "bbox": [34.5, 29.8, 36.2, 32.2],
        "points": [["Jerusalem", 35.235, 31.778, "established"], ["Bozrah / Busayra", 35.607, 30.733, "probable"], ["Petra / Sela traditions", 35.444, 30.329, "representative"]],
        "sources": ["https://pleiades.stoa.org/places/687928", "https://whitelevy.fas.harvard.edu/publications/busayra-excavations-crystal-bennett-1971-1980"],
        "note": "The map shows Edom's location south of Jerusalem. It does not claim an exact invasion or refugee route."},
    "visual-nineveh-fall-context": {
        "title": "The collapse of Assyrian power", "primary_texts": ["Nahum 1–3"],
        "bbox": [37.0, 32.0, 45.5, 37.5],
        "points": [["Nineveh", 43.152, 36.359, "established"], ["Harran", 39.031, 36.864, "established"], ["Carchemish", 38.014, 36.829, "established"], ["Babylon", 44.421, 32.536, "established"]],
        "sources": ["https://pleiades.stoa.org/places/874621", "https://pleiades.stoa.org/places/658427", "https://pleiades.stoa.org/places/658465", "https://pleiades.stoa.org/places/893951"],
        "note": "The map locates the major cities involved in Assyria's decline. Exact military routes and borders are not shown."},
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


def _svg_path(points, project, *, close=False) -> str:
    """Turn geographic point sequences into compact SVG path data."""
    projected = [project(float(x), float(y)) for x, y in points]
    if len(projected) < 2:
        return ""
    commands = [f"M {projected[0][0]:.1f} {projected[0][1]:.1f}"]
    commands.extend(f"L {x:.1f} {y:.1f}" for x, y in projected[1:])
    if close:
        commands.append("Z")
    return " ".join(commands)


def _nice_scale_km(map_width_km: float) -> int:
    options = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000)
    choices = [item for item in options if item <= map_width_km * 0.28]
    return choices[-1] if choices else 1


def render_diagram(spec: dict) -> tuple[str, str]:
    title = spec["title"]
    nodes = spec["nodes"]
    title_line_count = len(wrap(title, 47))
    passage_y = 154 + (title_line_count - 1) * 44
    y0 = max(242, passage_y + 52)
    body = [f'<rect x="40" y="36" width="1120" height="728" rx="30" fill="{PALETTE["panel"]}"/>']
    body.append(text_lines(80, 78, "READING GUIDE", size=15, width=30, weight=800, color=PALETTE["rust"], line=20))
    body.append(text_lines(80, 124, title, size=35, width=47, weight=760, color=PALETTE["navy"], line=44))
    body.append(text_lines(80, passage_y, "Bible passages  " + " · ".join(spec["primary_texts"]), size=18, width=105, color=PALETTE["muted"], line=24))

    cell_w = 500
    cell_h = 126
    positions = [(80, y0), (620, y0), (80, y0 + 150), (620, y0 + 150)]
    for index, node in enumerate(nodes):
        x, y = positions[index]
        accent = PALETTE["teal"] if index % 2 == 0 else PALETTE["rust"]
        body.append(f'<circle cx="{x+28}" cy="{y+31}" r="27" fill="{accent}"/>')
        body.append(text_lines(x+28, y+39, str(index+1), size=20, width=2, weight=800, color="#FFFFFF", anchor="middle"))
        body.append(text_lines(x+76, y+20, node, size=22, width=34, weight=650, line=29))
        body.append(f'<line x1="{x+76}" y1="{y+cell_h-12}" x2="{x+cell_w}" y2="{y+cell_h-12}" stroke="{PALETTE["line"]}" stroke-width="2"/>')

    note_y = y0 + 316
    body.append(f'<rect x="80" y="{note_y}" width="1040" height="118" rx="18" fill="{PALETTE["soft_teal"]}"/>')
    body.append(text_lines(108, note_y+36, "KEEP IN VIEW", size=15, width=30, weight=800, color=PALETTE["teal"]))
    body.append(text_lines(108, note_y+71, spec["caution"], size=19, width=94, line=25))
    body.append(text_lines(80, 739, "Church Commons · Fluent Companion", size=15, width=50, weight=650, color=PALETTE["muted"]))
    alt = f'{title}. Reader guide with four points: {"; ".join(nodes)}. Keep in view: {spec["caution"]}'
    return svg_shell("\n".join(body), title, alt), alt


def render_map(spec: dict) -> tuple[str, str]:
    try:
        from mpl_toolkits.basemap import Basemap
    except ImportError as exc:  # pragma: no cover - generation-time dependency
        raise SystemExit("Map generation requires the mpl_toolkits.basemap package") from exc

    title = spec["title"]
    min_lon, min_lat, max_lon, max_lat = spec["bbox"]
    title_line_count = len(wrap(title, 47))
    passage_y = 154 + (title_line_count - 1) * 44
    left, top, width, height = 62, max(208, passage_y + 38), 744, 392
    legend_x = 852

    def pos(lon, lat):
        x = left + (lon - min_lon) / (max_lon - min_lon) * width
        y = top + (max_lat - lat) / (max_lat - min_lat) * height
        return x, y

    basemap = Basemap(
        projection="cyl",
        llcrnrlon=min_lon,
        llcrnrlat=min_lat,
        urcrnrlon=max_lon,
        urcrnrlat=max_lat,
        resolution="i",
    )

    body = [f'<rect x="40" y="36" width="1120" height="728" rx="30" fill="{PALETTE["panel"]}"/>']
    body.append(text_lines(80, 78, "GEOGRAPHIC ORIENTATION", size=15, width=32, weight=800, color=PALETTE["rust"], line=20))
    body.append(text_lines(80, 124, title, size=35, width=47, weight=760, color=PALETTE["navy"], line=44))
    body.append(text_lines(80, passage_y, "Bible passages  " + " · ".join(spec["primary_texts"]), size=18, width=105, color=PALETTE["muted"], line=24))
    body.append(f'<defs><clipPath id="physical-map-clip"><rect x="{left}" y="{top}" width="{width}" height="{height}" rx="18"/></clipPath></defs>')
    body.append(f'<g id="physical-map-base" data-source="GSHHG" clip-path="url(#physical-map-clip)">')
    body.append(f'<rect x="{left}" y="{top}" width="{width}" height="{height}" fill="{PALETTE["water"]}"/>')
    for (xs, ys), polygon_type in zip(basemap.coastpolygons, basemap.coastpolygontypes):
        path = _svg_path(zip(xs, ys), pos, close=True)
        if not path:
            continue
        fill = PALETTE["land"] if polygon_type in (1, 3) else PALETTE["water"]
        body.append(f'<path d="{path}" fill="{fill}" stroke="none"/>')
    river_segments, _ = basemap._readboundarydata("rivers")
    for segment in river_segments:
        path = _svg_path(segment, pos)
        if path:
            body.append(f'<path d="{path}" fill="none" stroke="{PALETTE["river"]}" stroke-width="1.5" stroke-linecap="round"/>')
    for segment in basemap.coastsegs:
        path = _svg_path(segment, pos)
        if path:
            body.append(f'<path d="{path}" fill="none" stroke="{PALETTE["navy"]}" stroke-width="2.2" stroke-linejoin="round"/>')
    body.append('</g>')
    body.append(f'<rect x="{left}" y="{top}" width="{width}" height="{height}" rx="18" fill="none" stroke="{PALETTE["navy"]}" stroke-width="2.5"/>')
    body.append(text_lines(left+20, top+35, "N", size=18, width=2, weight=800, color=PALETTE["navy"]))
    body.append(f'<path d="M {left+26} {top+47} L {left+26} {top+82} M {left+18} {top+57} L {left+26} {top+47} L {left+34} {top+57}" stroke="{PALETTE["navy"]}" stroke-width="3.5" fill="none"/>')

    mid_lat = (min_lat + max_lat) / 2
    map_width_km = (max_lon - min_lon) * 111.32 * max(math.cos(math.radians(mid_lat)), 0.2)
    scale_km = _nice_scale_km(map_width_km)
    scale_px = width * scale_km / map_width_km
    scale_x = left + 22
    scale_y = top + height - 24
    body.append(f'<path d="M {scale_x} {scale_y} L {scale_x+scale_px:.1f} {scale_y}" stroke="{PALETTE["navy"]}" stroke-width="5"/>')
    body.append(f'<path d="M {scale_x} {scale_y-5} L {scale_x} {scale_y+5} M {scale_x+scale_px:.1f} {scale_y-5} L {scale_x+scale_px:.1f} {scale_y+5}" stroke="{PALETTE["navy"]}" stroke-width="2"/>')
    body.append(text_lines(int(scale_x+scale_px/2), int(scale_y-10), f"{scale_km} km", size=14, width=10, weight=700, color=PALETTE["navy"], anchor="middle"))

    certainty_labels = {
        "established": "known location",
        "probable": "probable location",
        "disputed": "location debated",
        "regional": "approximate area",
        "representative": "approximate area",
        "modern reference": "modern reference point",
    }
    label_positions = []
    for index, (label, lon, lat, certainty) in enumerate(spec["points"]):
        x, y = pos(lon, lat)
        plain_certainty = certainty_labels.get(certainty, certainty)
        label_positions.append((label, plain_certainty))
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{PALETTE["rust"]}" stroke="#FFFFFF" stroke-width="4"/>')
        body.append(text_lines(int(x), int(y+6), str(index+1), size=16, width=2, weight=800, color="#FFFFFF", anchor="middle"))
        ly = top + 34 + index * 78
        body.append(f'<circle cx="{legend_x}" cy="{ly-5}" r="14" fill="{PALETTE["rust"]}"/>')
        body.append(text_lines(legend_x, ly, str(index+1), size=15, width=2, weight=800, color="#FFFFFF", anchor="middle"))
        body.append(text_lines(legend_x+29, ly-6, label, size=19, width=24, weight=720, color=PALETTE["navy"], line=23))
        label_lines = len(wrap(label, 24))
        body.append(text_lines(legend_x+29, ly-6+label_lines*23, plain_certainty, size=14, width=27, weight=600, color=PALETTE["muted"], line=18))

    note_y = top + height + 32
    body.append(text_lines(80, note_y, "WHAT THIS MAP SHOWS", size=14, width=30, weight=800, color=PALETTE["teal"]))
    body.append(text_lines(80, note_y+30, spec["note"], size=17, width=105, color=PALETTE["ink"], line=22))
    body.append(text_lines(80, 739, "Modern coastlines and rivers are shown for orientation; no unrecorded route or ancient border is claimed.", size=13, width=132, weight=600, color=PALETTE["muted"], line=18))
    alt_points = "; ".join(f"{label}, {certainty}" for label, certainty in label_positions)
    alt = f"{title}. Geographic orientation map with land, water, coastlines, rivers, and these places: {alt_points}. {spec['note']}"
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
            sources = [*spec["sources"], MAP_BASE_SOURCE]
            primary_texts = spec["primary_texts"]
            format_type = "geographic-orientation-map"
            rights_basis = "Original SVG composition. Physical coastlines and rivers derive from GSHHG data distributed with Basemap; location claims are sourced separately."
        else:
            spec = DIAGRAMS[visual_id]
            content, alt = render_diagram(spec)
            sources = []
            primary_texts = spec["primary_texts"]
            format_type = "reader-explanation"
            rights_basis = "Original deterministic SVG composition generated in this repository; claims derive from the cited biblical passages."
        path = OUT / f"{visual_id}.svg"
        path.write_text(content, encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({
            "visual_id": visual_id,
            "record_id": request["record"],
            "requested_class": request["class"],
            "candidate_format": format_type,
            "claim_label": request["claim_label"],
            "title": spec["title"],
            "file": path.relative_to(ROOT).as_posix(),
            "sha256": digest,
            "primary_texts": primary_texts,
            "sources": sources,
            "alt_text": alt,
            "rights_basis": rights_basis,
            "rights_status": "owned-candidate",
            "scholarly_review": "required",
            "accessibility_review": "required",
            "publication_status": "blocked",
        })
    payload = {
        "schema_version": 2,
        "candidate_set": "biblical-world-reader-visuals-2026-09-07-v2",
        "asset_count": len(entries),
        "publication_status": "blocked",
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(entries)} SVG candidates")
    print(MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
