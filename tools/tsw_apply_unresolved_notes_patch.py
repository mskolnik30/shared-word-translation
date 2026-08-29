#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys
import shutil
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv

spec = importlib.util.spec_from_file_location("recover", "tools/tsw_recover_notes.py")
recover = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = recover
spec.loader.exec_module(recover)

ADDITIONS = [('books/NT/acts/Acts_08.md', 'v36', 'Some manuscripts add a verse between vv36 and 38 in which Philip asks about wholehearted belief and the eunuch confesses Jesus Christ as the Son of God. The earliest textual witnesses omit this verse.'), ('books/NT/colossians/Colossians_01.md', 'v22–23', 'The conditional clause “if indeed you continue in the faith” remains grammatically connected to the purpose of reconciliation in v22. Paul holds the completed act of reconciliation together with continuing, grounded faith.'), ('books/NT/luke/Luke_15.md', 'v20', 'The father’s compassion precedes the son’s spoken confession: while the son is still far off, the father sees him, runs, embraces him, and kisses him. The movement of the scene closes the distance before the son speaks.'), ('books/NT/luke/Luke_15.md', 'v21–22', 'The son repeats his confession but not his rehearsed request to become a hired worker. The father’s commands move immediately toward restored clothing, status, and belonging.'), ('books/NT/luke/Luke_17.md', 'v35', 'The paired sayings place separation within ordinary shared settings. Some manuscripts add a further example in which two are in a field and one is taken while the other is left.'), ('books/NT/luke/Luke_23.md', 'v16', 'Pilate has found no basis for a sentence of death, yet the scene moves toward punishment, the release of Barabbas, and Jesus being handed over to the crowd’s demand. Some manuscripts add here a statement that Pilate was obliged to release one prisoner at the festival.'), ('books/NT/mark/Mark_09.md', 'v42', 'The commands concerning hand, foot, and eye use deliberately extreme bodily imagery to intensify the danger of causing stumbling and entering judgment.'), ('books/NT/mark/Mark_09.md', 'v43', 'Some manuscripts repeat the saying about the undying worm and unquenched fire after the sayings about the hand and the foot, producing the traditional vv44 and 46. The earliest textual witnesses omit those repetitions.'), ('books/NT/matthew/Matthew_17.md', 'v20', 'Some manuscripts add after this verse a saying that this kind does not come out except by prayer and fasting. The earliest textual witnesses omit the added verse traditionally numbered v21.'), ('books/NT/philippians/Philippians_02.md', 'v6–8', 'The movement of vv6–8 is downward: equality is not treated as something to exploit, but is followed by self-emptying, servanthood, humility, and obedience to death. Christ’s identity is narrated through self-giving rather than self-assertion.'), ('books/NT/romans/Romans_03.md', 'v4', 'The citation from the Psalms is forensic in tone: God is shown to be true and vindicated in judgment even as human faithlessness is exposed.'), ('books/OT/1chronicles/1Chronicles_08.md', 'v6–7', 'The notice that the people of Geba were “carried away” is compressed, and the precise relationship between Gera and the preceding families is not fully clear. The genealogy preserves the displacement without explaining its circumstances.'), ('books/OT/1chronicles/1Chronicles_08.md', 'v33–40', 'The genealogy reaches Saul’s family and continues through Jonathan’s line, joining Benjamin’s wider network of households to the royal house while tracing its continuing descendants.'), ('books/OT/1chronicles/1Chronicles_12.md', 'v18', 'The Hebrew says that the Spirit “clothed” Amasai. The image gives his declaration public and compelling force as he answers David’s concern with a pledge of peace and loyalty.'), ('books/OT/1chronicles/1Chronicles_12.md', 'v22', '“Like the camp of God” can describe overwhelming size or strength while also echoing the language of God’s host. The comparison presents David’s gathering force as extraordinary without removing the military character of the scene.'), ('books/OT/1chronicles/1Chronicles_12.md', 'v32', '“Under their command” is literally “according to their mouth,” an idiom portraying the Issacharite leaders and their kin as acting in coordinated obedience to a shared judgment.'), ('books/OT/1chronicles/1Chronicles_12.md', 'v33', 'The Hebrew expression behind “without a divided heart” repeats the word “heart.” The image is of undivided purpose rather than merely military competence.'), ('books/OT/1chronicles/1Chronicles_12.md', 'v38–40', 'The military lists culminate in communal celebration rather than battle. Israel’s unity in making David king is expressed through shared food, drink, provision, and joy.'), ('books/OT/1chronicles/1Chronicles_21.md', 'v29–30', 'The narrative contrasts the established sanctuary and altar at Gibeon with the newly recognized altar at Ornan’s threshing floor. David’s fear of the angel’s sword prevents him from approaching the former site.'), ('books/OT/1chronicles/1Chronicles_26.md', 'v10', 'Shimri is called “the chief” even though he was not the firstborn. The text does not explain the appointment, but explicitly distinguishes appointed leadership from birth order.'), ('books/OT/1chronicles/1Chronicles_26.md', 'v26–28', 'The treasuries include things dedicated by David and other leaders, including goods from war and spoil. These materials are presented as consecrated for strengthening the house of the LORD.'), ('books/OT/1chronicles/1Chronicles_26.md', 'v29–32', 'Levitical service extends beyond temple gates and treasuries into public administration. Their work concerns both “every matter of God” and “every matter of the king,” holding religious and royal responsibilities together without collapsing them.'), ('books/OT/1kings/1Kings_04.md', 'v22', 'A *cor* was a large dry measure. The text leaves the quantities in ancient units rather than converting them, emphasizing the scale of the royal household’s daily provisions.'), ('books/OT/1kings/1Kings_04.md', 'v25', '“Each under their vine and under their fig tree” is an image of settled security, household abundance, and freedom from threat. The description of peace extends from political stability into ordinary life.'), ('books/OT/1kings/1Kings_04.md', 'v29', '“Breadth of heart” describes expansive discernment and capacity for understanding. In biblical Hebrew, the heart can denote thought, judgment, and purpose as well as feeling.'), ('books/OT/1kings/1Kings_04.md', 'v32', 'The Hebrew says literally, “his song was one thousand and five.” The singular can function collectively; the sense is a count of songs.'), ('books/OT/1kings/1Kings_09.md', 'v3', 'The LORD’s promise to put the divine “name” in the house joins chosen presence with continuing freedom: the temple bears the LORD’s name, while the LORD’s “eyes” and “heart” attend to it.'), ('books/OT/1kings/1Kings_09.md', 'v7', '“A proverb and a taunt” describes Israel becoming an object lesson among the nations—a people whose ruin is spoken of with scorn.'), ('books/OT/1kings/1Kings_09.md', 'v21–23', 'The text distinguishes the peoples assigned to forced labor from Israelites assigned to military and administrative roles, while also naming officials who rule over those doing the work. The structure of royal power remains plainly visible.'), ('books/OT/1kings/1Kings_13.md', 'v21', 'The expression translated “rebelled against the command” is literally “rebelled against the mouth of the LORD,” presenting the divine command as spoken authority to be heeded.'), ('books/OT/1kings/1Kings_13.md', 'v31–32', 'The old prophet asks for his bones to be laid beside the man of God whom he deceived. His confidence that the oracle “will surely come to pass” stands in sharp contrast to Jeroboam’s refusal to turn.'), ('books/OT/1samuel/1Samuel_01.md', 'v28', '“Lent” continues the chapter’s wordplay on the Hebrew root for asking or requesting: the child asked from the LORD is now given over to the LORD for his lifetime.'), ('books/OT/exodus/Exodus_08.md', 'v9', 'Moses’ unusual reply gives Pharaoh the privilege of naming when prayer should be made. Pharaoh chooses the time, but the LORD alone removes the frogs.'), ('books/OT/exodus/Exodus_08.md', 'v17', 'The precise identity of the Hebrew *kinnim* is uncertain; it may refer to gnats, lice, or another small biting insect. The translation conveys the pervasive nuisance without claiming certainty about the species.'), ('books/OT/exodus/Exodus_08.md', 'v21', 'The Hebrew word rendered as a “swarm” does not identify the creatures precisely. It may denote a mixture of insects or a particular kind of biting fly; the emphasis falls on their overwhelming presence.'), ('books/OT/exodus/Exodus_08.md', 'v23', 'The Hebrew noun can be associated with “redemption” or “ransom,” while some ancient witnesses support a sense like “distinction” or “separation.” The clause marks the LORD’s differentiated treatment of Israel and Egypt.'), ('books/OT/exodus/Exodus_08.md', 'v26', 'What is “an abomination to the Egyptians” may refer to animals regarded as unsuitable for sacrifice or as sacred. Moses does not specify the offerings, but insists that Israel’s worship cannot simply be contained within Pharaoh’s terms.'), ('books/OT/exodus/Exodus_24.md', 'v18', '“Forty days and forty nights” is a recurring biblical period associated with preparation, testing, and divine encounter. The narrative does not explain its significance here.'), ('books/OT/ezekiel/Ezekiel_09.md', 'v9', 'The people’s claim that “the LORD has forsaken the land” and “does not see” is reported within a description of bloodshed and injustice. The narrative presents perceived divine absence as part of the moral world of the city, not as the LORD’s own verdict.'), ('books/OT/ezekiel/Ezekiel_13.md', 'v14', 'The exposed foundation makes visible the wall’s instability. The image completes the critique of false assurances represented by the whitewashed wall.'), ('books/OT/ezekiel/Ezekiel_21.md', 'v5', 'The declaration that “all flesh shall know” makes the sword’s judgment publicly recognizable as the LORD’s action; once drawn, the sword will not return to its sheath.'), ('books/OT/ezekiel/Ezekiel_21.md', 'v3–4', 'The pairing “righteous and wicked” emphasizes the breadth of the coming sword. The text leaves unresolved the tension created by judgment falling across moral categories.'), ('books/OT/ezekiel/Ezekiel_21.md', 'v13', 'The Hebrew of the line containing “testing” is compressed and difficult, and the clause has been understood in more than one way. The wording should not be pressed into a single explanatory scheme.'), ('books/OT/ezekiel/Ezekiel_21.md', 'v27', 'The threefold “ruin” intensifies the announcement of overthrow. The following clause postpones resolution until the arrival of one “whose right it is,” without identifying that figure within the verse.'), ('books/OT/genesis/Genesis_35.md', 'v22', 'Reuben’s act violates his father’s household and authority. The narrative records that Israel heard of it but gives no immediate response.'), ('books/OT/genesis/Genesis_35.md', 'v23–26', 'The completed list of twelve sons gathers Jacob’s household into the ancestral framework of the tribes of Israel.'), ('books/OT/isaiah/Isaiah_05.md', 'v25', '“For all this his anger has not turned away, and his hand is stretched out still” functions as a recurring refrain in Isaiah, extending the announcement of judgment beyond a single act of punishment.'), ('books/OT/micah/Micah_06.md', 'v1–2', 'The courtroom imagery establishes a covenant lawsuit. The mountains and enduring foundations of the earth serve as witnesses, giving the dispute a public and long-standing horizon.'), ('books/OT/numbers/Numbers_06.md', 'v22–23', 'The blessing is introduced as the LORD’s own command to Moses for Aaron and his sons. Priestly speech mediates a blessing whose source remains God.'), ('books/OT/numbers/Numbers_06.md', 'v24–26', 'The three lines repeat the divine name and move through keeping, gracious presence, favorable attention, and peace. “Lift up the face” is an idiom of favorable regard, while “peace” (*shalom*) carries the wider sense of wholeness and well-being.'), ('books/OT/psalms/Psalm_021.md', 'v1', 'The king’s joy is located in the LORD’s strength and salvation; royal victory is presented as received rather than attributed to the king’s own power.'), ('books/OT/psalms/Psalm_021.md', 'v7', 'The king’s stability is grounded in trust in the LORD and in the steadfast love of the Most High.'), ('books/OT/psalms/Psalm_021.md', 'v13', 'The closing imperative turns from the king’s deliverance to direct praise of the LORD’s strength, gathering the royal celebration into worship.'), ('books/OT/psalms/Psalm_030.md', 'v3', '“Sheol” and “the Pit” evoke the realm of death and the grave. The speaker describes deliverance as restoration from the edge of death.'), ('books/OT/psalms/Psalm_030.md', 'v5', 'The briefness of anger and the endurance of favor are set beside the movement from nighttime weeping to morning rejoicing. The verse does not deny suffering; it places it within a larger confession of restoring favor.'), ('books/OT/psalms/Psalm_030.md', 'v7', '“My mountain” is an image of established security and strength. When God hides the divine face, that apparent stability is exposed as dependent on God’s favor.'), ('books/OT/psalms/Psalm_030.md', 'v9', 'The questions appeal to the loss of praise that death would bring. They express the psalmist’s urgent plea for life rather than offering a full account of life after death.'), ('books/OT/psalms/Psalm_030.md', 'v12', '“Glory” may refer to the speaker’s honor, inner self, or whole being. The open wording allows the final praise to gather the psalmist’s restored life into thanksgiving.'), ('books/OT/psalms/Psalm_034.md', 'v7', '“The angel of the LORD” presents the LORD’s protection in personal, encircling imagery. The verse does not explain the precise identity of this messenger.'), ('books/OT/psalms/Psalm_034.md', 'v19–20', 'The promise of deliverance does not deny the righteous person’s many troubles. The language of unbroken bones intensifies the claim of God’s preserving care.'), ('books/OT/psalms/Psalm_034.md', 'v21–22', 'The same Hebrew root associated with guilt closes both verses: those who hate the righteous incur guilt, while those who take refuge in the LORD are not held guilty.'), ('books/OT/psalms/Psalm_036.md', 'v1', 'The Hebrew has a difficult first-person expression, “within my heart,” even though the surrounding lines concern the wicked person. The syntax has produced differing construals, and the tension should not be resolved too quickly.'), ('books/OT/psalms/Psalm_036.md', 'v2', 'The wording is compressed. Self-flattery is portrayed as preventing the wicked from discovering and hating their own guilt.'), ('books/OT/psalms/Psalm_036.md', 'v5–6', 'The psalm answers the confined world of the wicked with the immeasurable scale of God’s steadfast love, faithfulness, righteousness, and judgments; the imagery moves from the heavens and mountains to the great deep.'), ('books/OT/psalms/Psalm_036.md', 'v7–8', 'The refuge of God’s wings is joined with abundance, nourishment, and flowing water. The imagery gathers protection and delight without reducing them to a single setting.'), ('books/OT/psalms/Psalm_036.md', 'v11–12', 'The prayer closes with both a plea for protection and a declaration of the evildoers’ downfall. “There” points dramatically to the place of their collapse without specifying it.'), ('books/OT/psalms/Psalm_053.md', 'v3', '“Not even one” intensifies the universal scope of the psalm’s accusation: the claim concerns the whole human field being surveyed, not merely a particular group of evildoers.'), ('books/OT/psalms/Psalm_053.md', 'v5', 'The phrase “where there was no fear” makes the terror strikingly disproportionate to any visible cause, locating the reversal in God’s action rather than in the enemy’s apparent circumstances.'), ('books/OT/psalms/Psalm_058.md', 'v9', 'The Hebrew of the thorn-and-pot image is difficult. The line emphasizes the swiftness of judgment before the cooking fire can take effect, while the precise sense of the terms describing the thorns remains uncertain.'), ('books/OT/psalms/Psalm_058.md', 'v11', 'The closing acclamation voices the conclusion that righteousness is not futile and that there is a God who judges on the earth.')]

def make_entry(ref, text):
    return recover.NoteEntry(ref, [f"{ref}: {text}"])

def body_sig(entry):
    return recover.normalize_note_body(entry)

def without_notes(text):
    lines = text.splitlines()
    bounds = recover.section_bounds(lines, "Notes")
    if not bounds:
        return "\n".join(lines).rstrip()
    a, z = bounds
    return "\n".join(lines[:a] + lines[z:]).rstrip()

errors = []
planned = {}
skipped_existing = 0

for rel, ref, note_text in ADDITIONS:
    path = Path(rel)
    if not path.exists():
        errors.append(f"MISSING FILE: {rel}")
        continue

    current = path.read_text()
    verses = recover.extract_verses(current)
    nums = recover.ref_numbers(ref)

    if not nums:
        errors.append(f"BAD REF: {rel} {ref}")
        continue

    missing = [n for n in nums if n not in verses]
    if missing:
        errors.append(f"MISSING VERSE(S): {rel} {ref} -> {missing}")
        continue

    existing = recover.parse_note_entries(current)
    sigs = {body_sig(e) for e in existing}
    candidate = make_entry(ref, note_text)

    if body_sig(candidate) in sigs:
        skipped_existing += 1
        continue

    planned.setdefault(rel, []).append(candidate)

print(f"Mode: {'APPLY' if APPLY else 'DRY RUN'}")
print(f"Candidate additions defined: {len(ADDITIONS)}")
print(f"Already present/skipped: {skipped_existing}")
print(f"New notes planned: {sum(len(v) for v in planned.values())}")
print(f"Files to change: {len(planned)}")

if errors:
    print("\nVALIDATION ERRORS:")
    for err in errors:
        print("  " + err)
    raise SystemExit("\nNo files changed because validation failed.")

for rel in sorted(planned):
    print(f"\n{rel}: {len(planned[rel])} notes")
    for e in planned[rel]:
        print(f"  {e.ref}: {body_sig(e)[:100]}")

if not APPLY:
    print("\nDry run only. Re-run with --apply after the totals and targets look correct.")
    raise SystemExit(0)

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup_root = Path("audit/final_note_patch_backups") / stamp

for rel, new_entries in planned.items():
    path = Path(rel)
    current = path.read_text()
    existing = recover.parse_note_entries(current)
    merged = existing + new_entries

    def sort_key(entry):
        nums = recover.ref_numbers(entry.ref)
        return nums[0] if nums else 9999

    merged.sort(key=sort_key)
    new_text = recover.replace_notes_section(current, merged)

    if without_notes(current) != without_notes(new_text):
        raise RuntimeError(f"Safety invariant failed for {rel}")

    backup_path = backup_root / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)
    path.write_text(new_text)

print(f"\nApplied {sum(len(v) for v in planned.values())} notes to {len(planned)} files.")
print(f"Backups: {backup_root}")
