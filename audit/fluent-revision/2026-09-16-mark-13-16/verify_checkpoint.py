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
        ledger = json.loads((R / completed["ledger"]).read_text())
        for chapter in ledger["chapters"]:
            assert chapter["path"] not in prior
            prior.add(chapter["path"])
            prior_verses += chapter["verse_count"]
            assert (R / chapter["path"]).read_bytes() == old(chapter["path"]), chapter["path"]
            assert sha((R / chapter["path"]).read_bytes()) == chapter["after_sha256"]
            assert sha((R / chapter["tsw_comparator_path"]).read_bytes()) == chapter["tsw_comparator_sha256"]
    assert (len(prior), prior_verses) == (974, 24818)

    ledger = json.loads((scope / "mark-verse-review.json").read_text())
    source_bytes = (args.source_directory / cfg["source_filename"]).read_bytes()
    errors = audit(R, ledger, source_bytes)
    assert not errors, errors

    affected = []
    for path, book in [
        ("audit/fluent-revision/2026-09-16-mark-9-12/mark-verse-review.json", "mark"),
        ("audit/fluent-revision/2026-09-16-mark-4-8/mark-verse-review.json", "mark"),
        ("audit/fluent-revision/2026-09-16-mark-1-3/mark-verse-review.json", "mark"),
        ("audit/fluent-revision/2026-09-16-matthew-24-28/matthew-verse-review.json", "matthew"),
    ]:
        preceding_errors = audit(
            R,
            json.loads((R / path).read_text()),
            (args.source_directory / (book + "-pinned-greek.txt")).read_bytes(),
        )
        assert not preceding_errors, preceding_errors
        affected.append(path)

    source = {
        line.split("\t", 1)[0]: line.split("\t", 1)[1]
        for line in source_bytes.decode().splitlines()
        if "\t" in line
    }
    rows = {verse["reference"]: verse for verse in ledger["verses"]}
    refs = set(cfg["f3"]) | set(cfg["focused_extra_references"])
    focus = [
        {**verse, "exact_source_record": source[verse["source_reference"]]}
        for verse in ledger["verses"]
        if verse["reference"].split()[1] in refs
    ]
    assert len(refs) == len(focus) == 175
    record = {
        "status": "AUTHORING_REREAD_COMPLETED",
        "review_type": "Drafting assistant self-reread, not human or independent scholarly review",
        "authoring_record_sha256": sha((scope / "authoring-reread.md").read_bytes()),
        "rows": focus,
    }
    if args.bind_focused_records:
        dump(scope / "focused-comparisons.json", record)
    else:
        assert json.loads((scope / "focused-comparisons.json").read_text()) == record

    verse = {key.split()[1]: value["after"] for key, value in rows.items()}
    checks = {
        "olivet_witnesses": all(x in verse["13:3"] for x in ["Mount of Olives", "temple", "Peter", "James", "John", "Andrew"]),
        "wars_not_end": "end is not yet" in verse["13:7"],
        "birth_pains": all(x in verse["13:8"] for x in ["nation", "kingdom", "earthquakes", "famines", "birth pains"]),
        "all_nations": "all nations" in verse["13:10"],
        "abomination_and_aside": "standing" in verse["13:14"] and "reader understand" in verse["13:14"] and "ἑστηκότα" in source["Mark 13:14"],
        "chosen_repetition": "chosen" in verse["13:20"] and "chose" in verse["13:20"],
        "near_referent_open": "it is near" in verse["13:29"],
        "generation_retained": "this generation" in verse["13:30"],
        "son_does_not_know": "nor the Son" in verse["13:32"],
        "slaves_and_watches": "slaves" in verse["13:34"] and all(x in verse["13:35"] for x in ["evening", "midnight", "rooster", "dawn"]),
        "bethany_anointing": all(x in verse["14:3"] for x in ["Bethany", "Simon the leper", "nard", "head"]),
        "denarii_and_poor": "three hundred denarii" in verse["14:5"] and "poor" in verse["14:5"],
        "covenant_without_new": "blood of the covenant" in verse["14:24"] and "new covenant" not in verse["14:24"],
        "rooster_and_denials": "twice" in verse["14:30"] and "three times" in verse["14:30"] and "second time" in verse["14:72"],
        "abba_cup_and_will": all(x in verse["14:36"] for x in ["Abba", "Father", "cup", "what I want", "what you want"]),
        "difficult_transition": "Enough!" in verse["14:41"],
        "unnamed_assailant_and_slave": "high priest’s slave" in verse["14:47"] and "Peter" not in verse["14:47"] and "ear" in verse["14:47"],
        "naked_young_man": "young man" in verse["14:51"] and "linen cloth" in verse["14:51"] and "fled naked" in verse["14:52"],
        "handmade_contrast": "made by hands" in verse["14:58"] and "not made by hands" in verse["14:58"] and "three days" in verse["14:58"],
        "power_and_clouds": all(x in verse["14:62"] for x in ["I am", "Power", "clouds of heaven"]),
        "violence_explicit": all(x in verse["14:65"] for x in ["spit", "strike", "slaps"]),
        "first_rooster": "a rooster crowed" in verse["14:68"],
        "speech_resemblance_present": "your speech sounds like it" in verse["14:70"] and "ἡ λαλιά σου ὁμοιάζει" in source["Mark 14:70"],
        "barabbas_revolt_murder": all(x in verse["15:7"] for x in ["Barabbas", "rebels", "murder", "uprising"]),
        "pilate_crowd_and_harm": all(x in verse["15:15"] for x in ["satisfy the crowd", "flogged", "crucified"]),
        "simon_identity": all(x in verse["15:21"] for x in ["Simon", "Cyrene", "Alexander", "Rufus", "cross"]),
        "verse_28_absent": "Mark 15:28" not in rows and "Mark 15:28" not in source,
        "ancient_hours": "third hour" in verse["15:25"] and "sixth hour" in verse["15:33"] and "ninth hour" in verse["15:33"] and "ninth hour" in verse["15:34"],
        "aramaic_cry": "Eloi, Eloi, lema sabachthani" in verse["15:34"],
        "centurion_confession": "centurion" in verse["15:39"] and "God’s Son" in verse["15:39"],
        "women_named_and_serving": all(x in verse["15:40"] for x in ["Mary Magdalene", "James", "Joses", "Salome"]) and all(x in verse["15:41"] for x in ["followed", "served", "Many other women"]),
        "corpse_retained": "corpse" in verse["15:45"],
        "tomb_witnesses": all(x in verse["16:1"] for x in ["Mary Magdalene", "Mary", "James", "Salome", "spices"]),
        "first_day_sunrise": "first day" in verse["16:2"] and "sunrise" in verse["16:2"],
        "young_man_not_angel": "young man" in verse["16:5"] and "angel" not in verse["16:5"],
        "empty_tomb_message": all(x in verse["16:6"] for x in ["crucified", "raised", "not here"]),
        "peter_and_galilee": "Peter" in verse["16:7"] and "Galilee" in verse["16:7"],
        "main_ending_fear": all(x in verse["16:8"] for x in ["trembling", "astonishment", "nothing", "afraid"]),
        "shorter_ending_bracketed": "⟦" in source["Mark 16:8"] and "⟧" in source["Mark 16:8"] and "Πάντα" in source["Mark 16:8"],
        "longer_ending_bracketed": source["Mark 16:9"].startswith("⟦") and source["Mark 16:20"].rstrip().endswith("⟧"),
        "eleven_unbelief_hardness": all(x in verse["16:14"] for x in ["Eleven", "unbelief", "hardness of heart"]),
        "belief_baptism_unbelief": all(x in verse["16:16"] for x in ["believes", "baptized", "saved", "does not believe", "condemned"]),
        "danger_not_softened": all(x in verse["16:18"] for x in ["snakes", "deadly", "sick"]),
        "exaltation": all(x in verse["16:19"] for x in ["Lord Jesus", "heaven", "right hand"]),
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
        review_path = f'audit/exegetical-core/fluent-production/mark/Mark_{chapter["chapter"]:02}_review.json'
        allowed.add(review_path)
        review = json.loads((R / review_path).read_text())
        assert review["chapter_binding"] == chapter and review["publication_allowed"] is False
        chapter_text = (R / chapter["path"]).read_text()
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
        maximum = chapter["verse_count"] + len(chapter.get("source_omitted_public_labels", []))
        for note_ref in re.findall(r"^v([\d,–\- ]+):", chapter_text.split("## Notes")[1], re.M):
            assert all(1 <= int(number) <= maximum for number in re.findall(r"\d+", note_ref))

    for filename in ["MARK_FLUENT_BOOK_QA.json", "MARK_SOURCE_BINDINGS.json"]:
        path = "audit/exegetical-core/fluent-production/mark/" + filename
        allowed.add(path)
        current = json.loads((R / path).read_text())
        previous = json.loads(old(path))
        assert current["revision_batches"][:-1] == previous["revision_batches"] and current["source"] == previous["source"]
        assert current["editorial_review_pending_chapters"] == list(range(1, 17)) and not current["publication_allowed"]
        if "bindings" in previous:
            assert current["bindings"] == previous["bindings"]

    changed = subprocess.check_output(["git", "diff", "--name-only", parent], cwd=R).decode().splitlines()
    changed += subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=R).decode().splitlines()
    assert all(path in allowed or path.startswith(rel + "/") for path in changed), [path for path in changed if path not in allowed and not path.startswith(rel + "/")]
    assert not subprocess.check_output(["git", "diff", parent, "--", "books", "companions"], cwd=R).strip()
    subprocess.run(["git", "diff", "--check", parent], cwd=R, check=True)
    family = subprocess.check_output([sys.executable, "tools/audit_translation_family.py"], cwd=R).decode()

    chapters = [chapter for completed in queue["completed_draft_scopes"] for chapter in json.loads((R / completed["ledger"]).read_text())["chapters"]]
    assert len({chapter["path"] for chapter in chapters}) == len(chapters) == 978
    assert sum(chapter["verse_count"] for chapter in chapters) == 24993
    assert len(queue["completed_draft_scopes"]) == 111
    block = queue["active_fifty_chapter_block"]
    assert (block["status"], block["completed_chapters"], block["remaining_chapters"], block["completed_verses"]) == ("IN_PROGRESS", 21, 29, 931)

    result = {
        "status": "PASSED",
        "qa_scope": "structural",
        "parent_commit": parent,
        "new_chapters": 4,
        "new_verses": 175,
        "cumulative_coverage": {"ledgers": 111, "chapters": 978, "verses": 24993},
        "prior_preservation": {"ledgers_byte_identical": 110, "chapters_byte_identical": 974, "tsw_and_companion_unchanged": True},
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
