#!/usr/bin/env python3
"""Structural and preservation checks, separate from documented authoring judgment."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from audit_fluent_revision import audit

R = Path(__file__).resolve().parents[3]
sha = lambda b: hashlib.sha256(b).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scope_directory", type=Path)
    parser.add_argument("--source-directory", required=True, type=Path)
    parser.add_argument("--bind-focused-records", action="store_true")
    args = parser.parse_args()
    scope = args.scope_directory.resolve()
    rel = str(scope.relative_to(R))
    cfg = json.loads((scope / "config.json").read_text())
    parent = cfg["parent_commit"]

    def old(path):
        return subprocess.check_output(["git", "show", parent + ":" + path], cwd=R)

    queue = json.loads((R / "audit/fluent-revision/WORK_QUEUE.json").read_text())
    old_queue = json.loads(old("audit/fluent-revision/WORK_QUEUE.json"))
    assert queue["completed_draft_scopes"][:-1] == old_queue["completed_draft_scopes"]
    assert queue["next_work"][1:] == old_queue["next_work"][1:]

    prior = set()
    prior_verses = 0
    for completed in old_queue["completed_draft_scopes"]:
        assert (R / completed["ledger"]).read_bytes() == old(completed["ledger"]), completed["ledger"]
        prior_ledger = json.loads((R / completed["ledger"]).read_text())
        for chapter in prior_ledger["chapters"]:
            assert chapter["path"] not in prior
            prior.add(chapter["path"])
            prior_verses += chapter["verse_count"]
            assert (R / chapter["path"]).read_bytes() == old(chapter["path"]), chapter["path"]
            assert sha((R / chapter["path"]).read_bytes()) == chapter["after_sha256"]
            assert sha((R / chapter["tsw_comparator_path"]).read_bytes()) == chapter["tsw_comparator_sha256"]
    assert (len(prior), prior_verses) == (982, 25207)

    ledger = json.loads((scope / "luke-verse-review.json").read_text())
    source_bytes = (args.source_directory / cfg["source_filename"]).read_bytes()
    errors = audit(R, ledger, source_bytes)
    assert not errors, errors

    affected = []
    for path, source_name in [
        ("audit/fluent-revision/2026-09-16-luke-1-4/luke-verse-review.json", "luke-pinned-greek.txt"),
        ("audit/fluent-revision/2026-09-16-mark-13-16/mark-verse-review.json", "mark-pinned-greek.txt"),
    ]:
        preceding_errors = audit(R, json.loads((R / path).read_text()), (args.source_directory / source_name).read_bytes())
        assert not preceding_errors, preceding_errors
        affected.append(path)

    source = {
        line.split("\t", 1)[0]: line.split("\t", 1)[1]
        for line in source_bytes.decode().splitlines()
        if "\t" in line
    }
    rows = {verse["reference"]: verse for verse in ledger["verses"]}
    focus = [{**verse, "exact_source_record": source[verse["source_reference"]]} for verse in ledger["verses"]]
    assert len(focus) == 194
    record = {
        "status": "AUTHORING_REREAD_COMPLETED",
        "review_type": "Drafting assistant self-reread, not human or independent scholarly review",
        "authoring_record_sha256": sha((scope / "authoring-reread.md").read_bytes()),
        "rows": focus,
    }
    if args.bind_focused_records:
        dump(scope / "focused-comparisons.json", record)
        dump(scope / "focused-selection.json", focus)
    else:
        assert json.loads((scope / "focused-comparisons.json").read_text()) == record
        assert json.loads((scope / "focused-selection.json").read_text()) == focus

    verse = {key.split()[1]: value["after"] for key, value in rows.items()}
    checks = {
        "gennesaret_two_boats": "Lake Gennesaret" in verse["5:1"] and "two boats" in verse["5:2"],
        "failed_night_and_word": all(x in verse["5:5"] for x in ["all night", "caught nothing", "because you say so"]),
        "nets_and_two_boats": "nets began to tear" in verse["5:6"] and all(x in verse["5:7"] for x in ["partners", "both boats", "began to sink"]),
        "peter_james_john": all(x in verse["5:10"] for x in ["James", "John", "Zebedee", "Simon", "catching people alive"]),
        "cleansing_moses_testimony": all(x in verse["5:14"] for x in ["priest", "Moses", "cleansing", "testimony to them"]),
        "plural_faith": "their faith" in verse["5:20"],
        "son_of_man_authority": all(x in verse["5:24"] for x in ["Son of Man", "authority on earth", "forgive sins", "mat", "go home"]),
        "levi_everything": "Levi" in verse["5:27"] and "left everything" in verse["5:28"],
        "repentance": "sinners to repentance" in verse["5:32"],
        "bridegroom_removed": "bridegroom is taken away" in verse["5:35"],
        "garment_wineskins_old_wine": "new garment" in verse["5:36"] and "new wine" in verse["5:37"] and "The old is good" in verse["5:39"],
        "sabbath_grain_actions": all(x in verse["6:1"] for x in ["Sabbath", "picking", "rubbing", "eating"]),
        "consecrated_bread_priests": "consecrated bread" in verse["6:4"] and "priests" in verse["6:4"],
        "right_hand": "right hand" in verse["6:6"],
        "save_destroy": "save a life or to destroy it" in verse["6:9"],
        "senseless_rage": "senseless rage" in verse["6:11"],
        "night_prayer": "whole night" in verse["6:12"] and "prayer to God" in verse["6:12"],
        "twelve_apostles": "twelve" in verse["6:13"] and "apostles" in verse["6:13"],
        "twelve_names_and_traitor": all(name in " ".join(verse[f"6:{n}"] for n in range(14, 17)) for name in ["Peter", "Andrew", "James", "John", "Philip", "Bartholomew", "Matthew", "Thomas", "Alphaeus", "Zealot", "Judas Iscariot", "traitor"]),
        "level_place_geography": all(x in verse["6:17"] for x in ["level place", "Judea", "Jerusalem", "Tyre", "Sidon"]),
        "lukan_blessings": "poor" in verse["6:20"] and "in spirit" not in verse["6:20"] and all(x in verse["6:21"] for x in ["hunger now", "weep now", "filled", "laugh"]),
        "lukan_woes": "rich" in verse["6:24"] and all(x in verse["6:25"] for x in ["well fed now", "hunger", "laugh now", "mourn", "weep"]),
        "enemy_love": "Love your enemies" in verse["6:27"] and "bless" in verse["6:28"] and "pray" in verse["6:28"],
        "garment_distinction": "outer garment" in verse["6:29"] and "tunic" in verse["6:29"],
        "credit_repetition": all("what credit is that to you?" in verse[x] for x in ["6:32", "6:33", "6:34"]),
        "most_high_kindness": all(x in verse["6:35"] for x in ["Most High", "ungrateful", "evil"]),
        "mercy_not_perfection": "merciful" in verse["6:36"] and "perfect" not in verse["6:36"],
        "judge_condemn_forgive": all(x in verse["6:37"] for x in ["judge", "condemn", "Forgive"]),
        "lap_measure": all(x in verse["6:38"] for x in ["pressed down", "shaken together", "overflowing", "lap", "measure"]),
        "speck_beam_brother": all(x in verse["6:42"] for x in ["Brother", "speck", "beam", "Hypocrite"]),
        "heart_overflow": "heart’s good treasure" in verse["6:45"] and "overflow of the heart" in verse["6:45"],
        "house_foundation": all(x in verse["6:48"] for x in ["dug down deep", "foundation on rock", "flood", "built well"]) and all(x in verse["6:49"] for x in ["without a foundation", "immediately collapsed", "great"]),
        "centurion_slave": all("slave" in verse[x] for x in ["7:2", "7:3", "7:8", "7:10"]) and "servant" in verse["7:7"],
        "authority_chain": all(x in verse["7:8"] for x in ["under authority", "soldiers under me", "Go", "Come", "Do this"]),
        "jesus_marveled": "marveled" in verse["7:9"] and "Israel" in verse["7:9"],
        "nain_widow_only_son": all(x in verse["7:12"] for x in ["only son", "widow", "town"]),
        "lord_compassion": "the Lord" in verse["7:13"] and "compassion" in verse["7:13"],
        "dead_man_restored": "dead man" in verse["7:15"] and "gave him to his mother" in verse["7:15"],
        "visitation": "God has visited his people" in verse["7:16"],
        "coming_one_question": "one who is to come" in verse["7:19"] and "someone else" in verse["7:19"],
        "six_signs": all(x in verse["7:22"] for x in ["blind", "lame", "leprosy", "deaf", "dead", "poor"]),
        "john_comparison": "more than a prophet" in verse["7:26"] and "least in the kingdom" in verse["7:28"],
        "baptism_responses": "God was just" in verse["7:29"] and "God’s purpose for themselves" in verse["7:30"],
        "children_games": all(x in verse["7:32"] for x in ["marketplace", "flute", "dance", "funeral song", "weep"]),
        "john_and_son_accusations": all(x in verse["7:33"] for x in ["bread", "wine", "demon"]) and all(x in verse["7:34"] for x in ["glutton", "drunkard", "tax collectors", "sinners"]),
        "wisdom_children": "wisdom is vindicated by all her children" in verse["7:35"],
        "woman_unnamed": "woman" in verse["7:37"] and "Mary" not in verse["7:37"] and "alabaster jar" in verse["7:37"],
        "tears_hair_kisses_perfume": all(x in verse["7:38"] for x in ["tears", "hair", "kissing", "perfume"]),
        "debts_numbers": "five hundred denarii" in verse["7:41"] and "fifty" in verse["7:41"],
        "forgiveness_love": all(x in verse["7:47"] for x in ["many sins", "forgiven", "loved much", "loves little"]),
        "faith_saved_peace": all(x in verse["7:50"] for x in ["faith", "saved", "peace"]),
        "women_named_and_support": all(x in " ".join(verse[f"8:{n}"] for n in range(1, 4)) for x in ["Mary", "Magdalene", "seven", "Joanna", "Chuza", "Herod", "Susanna", "own resources"]),
        "sower_details": "trampled" in verse["8:5"] and "moisture" in verse["8:6"] and "choked" in verse["8:7"] and "hundred" in verse["8:8"],
        "purpose_quote": "seeing they may not see" in verse["8:10"] and "hearing they may not understand" in verse["8:10"],
        "temporary_belief": all(x in verse["8:13"] for x in ["joy", "no root", "believe", "testing", "fall away"]),
        "fruit_contrast": "never matures" in verse["8:14"] and "with endurance" in verse["8:15"],
        "how_listen": "how you listen" in verse["8:18"] and "think they have" in verse["8:18"],
        "family_hear_do": "hear the word of God and do it" in verse["8:21"],
        "storm_danger": all(x in verse["8:23"] for x in ["windstorm", "filling", "danger"]),
        "gerasenes": "Gerasenes" in verse["8:26"] and "Γερασηνῶν" in source["Luke 8:26"],
        "man_harm": all(x in verse["8:27"] for x in ["no clothes", "house", "tombs"]) and all(x in verse["8:29"] for x in ["chains", "shackles", "break", "deserted places"]),
        "legion_many": "Legion" in verse["8:30"] and "many demons" in verse["8:30"],
        "restored_posture": all(x in verse["8:35"] for x in ["Jesus’ feet", "clothed", "right mind"]),
        "god_jesus_correspondence": "God has done" in verse["8:39"] and "Jesus had done" in verse["8:39"],
        "two_twelves": "twelve years old" in verse["8:42"] and "twelve years" in verse["8:43"],
        "woman_cost": "whole livelihood" in verse["8:43"] and "physicians" in verse["8:43"],
        "public_testimony": "all the people" in verse["8:47"] and "healed immediately" in verse["8:47"],
        "daughter_saved": all(x in verse["8:48"] for x in ["Daughter", "faith", "saved", "peace"]),
        "girl_death_and_rescue": "has died" in verse["8:49"] and "only believe" in verse["8:50"] and "made well" in verse["8:50"],
        "spirit_food": "spirit returned" in verse["8:55"] and "something to eat" in verse["8:55"],
    }
    assert all(checks.values()), [key for key, value in checks.items() if not value]

    allowed = {
        "audit/fluent-revision/WORK_QUEUE.json",
        "tools/build_fluent_mark_checkpoint.py",
        "tools/verify_fluent_mark_checkpoint.py",
        "tools/package_fluent_checkpoint.py",
    }
    for chapter in ledger["chapters"]:
        allowed.add(chapter["path"])
        assert chapter["path"] not in prior
        review_path = f'audit/exegetical-core/fluent-production/luke/Luke_{chapter["chapter"]:02}_review.json'
        allowed.add(review_path)
        review = json.loads((R / review_path).read_text())
        assert review["chapter_binding"] == chapter and review["publication_allowed"] is False
        chapter_text = (R / chapter["path"]).read_text()
        main_text = chapter_text.split("## Notes")[0]
        assert main_text.count("“") == main_text.count("”"), chapter["path"]
        inside = False
        for line in chapter_text.split("---", 2)[2].split("## Notes")[0].splitlines():
            if line == "<p>":
                assert not inside
                inside = True
            elif line == "</p>":
                assert inside
                inside = False
            elif line.strip() and not line.startswith("## "):
                assert inside, (chapter["path"], line)
        assert not inside
        maximum = chapter["verse_count"]
        for note_ref in re.findall(r"^v([\d,–\- ]+):", chapter_text.split("## Notes")[1], re.M):
            assert all(1 <= int(number) <= maximum for number in re.findall(r"\d+", note_ref))

    for filename in cfg["book_record_files"]:
        path = "audit/exegetical-core/fluent-production/luke/" + filename
        allowed.add(path)
        current = json.loads((R / path).read_text())
        previous = json.loads(old(path))
        assert current["revision_batches"][:-1] == previous.get("revision_batches", []) and current["source"] == previous["source"]
        assert current["editorial_review_pending_chapters"] == list(range(1, 9)) and not current["publication_allowed"]
        if "entries" in previous:
            assert len(current["entries"]) == len(previous["entries"])
            for entry, prior_entry in zip(current["entries"], previous["entries"]):
                if entry["chapter"] in cfg["chapters"]:
                    assert entry["status"] == "SUPERSEDED" and entry["superseded_by_verse_ledger"] == rel + "/luke-verse-review.json"
                    assert all(entry[key] == value for key, value in prior_entry.items())
                else:
                    assert entry == prior_entry
            assert current["summary"] == previous["summary"]

    changed = subprocess.check_output(["git", "diff", "--name-only", parent], cwd=R).decode().splitlines()
    changed += subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=R).decode().splitlines()
    assert all(path in allowed or path.startswith(rel + "/") for path in changed), [path for path in changed if path not in allowed and not path.startswith(rel + "/")]
    assert not subprocess.check_output(["git", "diff", parent, "--", "books", "companions"], cwd=R).strip()
    subprocess.run(["git", "diff", "--check", parent], cwd=R, check=True)
    family = subprocess.check_output([sys.executable, "tools/audit_translation_family.py"], cwd=R).decode()

    chapters = [chapter for completed in queue["completed_draft_scopes"] for chapter in json.loads((R / completed["ledger"]).read_text())["chapters"]]
    assert len({chapter["path"] for chapter in chapters}) == len(chapters) == 986
    assert sum(chapter["verse_count"] for chapter in chapters) == 25401
    assert len(queue["completed_draft_scopes"]) == 113
    block = queue["active_fifty_chapter_block"]
    assert (block["status"], block["completed_chapters"], block["remaining_chapters"], block["completed_verses"]) == ("IN_PROGRESS", 29, 21, 1339)

    result = {
        "status": "PASSED",
        "qa_scope": "structural",
        "parent_commit": parent,
        "new_chapters": 4,
        "new_verses": 194,
        "cumulative_coverage": {"ledgers": 113, "chapters": 986, "verses": 25401},
        "prior_preservation": {"ledgers_byte_identical": 112, "chapters_byte_identical": 982, "tsw_and_companion_unchanged": True},
        "source_binding_audit": "PASSED; all exact payloads, whole-file SHA-256 and Git blob identity",
        "additional_affected_ledgers_passed": affected,
        "source_sensitive_checks": checks,
        "focused_authoring_reread_count": len(focus),
        "translation_family": family,
        "block_progress": block,
        "independent_editorial_review": "REVIEW_PENDING",
        "reader_testing": "PENDING",
        "companion_reconciliation": "PENDING; no quotations or bindings changed",
        "publication_allowed": False,
    }
    dump(scope / "verification.json", result)
    print(json.dumps({key: result[key] for key in ["status", "new_chapters", "new_verses", "cumulative_coverage"]}))


if __name__ == "__main__":
    main()
