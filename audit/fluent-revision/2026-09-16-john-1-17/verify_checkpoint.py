#!/usr/bin/env python3
"""Verify the Luke 12–24 / John 1–17 source-bound draft batch."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from audit_fluent_revision import audit

PARENT = "13e792cbd5e6d5ef1035d34f7bd0b08a62da172b"
SCOPES = [
    ("audit/fluent-revision/2026-09-16-luke-12-24", "luke", "luke-pinned-greek.txt", 583),
    ("audit/fluent-revision/2026-09-16-john-1-17", "john", "john-pinned-greek.txt", 740),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def old(path):
    return subprocess.check_output(["git", "show", PARENT + ":" + path], cwd=ROOT)


def source_records(source_bytes):
    rows = {}
    for line in source_bytes.decode().splitlines():
        match = re.fullmatch(r"([^\t]+)\t(.*)", line)
        if match:
            assert match[1] not in rows
            rows[match[1]] = match[2]
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-directory", required=True, type=Path)
    parser.add_argument("--bind-focused-records", action="store_true")
    args = parser.parse_args()

    queue_path = ROOT / "audit/fluent-revision/WORK_QUEUE.json"
    queue = json.loads(queue_path.read_text())
    old_queue = json.loads(old("audit/fluent-revision/WORK_QUEUE.json"))
    assert len(old_queue["completed_draft_scopes"]) == 114
    assert queue["completed_draft_scopes"][:-2] == old_queue["completed_draft_scopes"]
    assert queue["next_work"][1:] == old_queue["next_work"][1:]

    prior_paths = set()
    prior_verses = 0
    for scope in old_queue["completed_draft_scopes"]:
        ledger_path = scope["ledger"]
        assert (ROOT / ledger_path).read_bytes() == old(ledger_path), ledger_path
        ledger = json.loads((ROOT / ledger_path).read_text())
        for chapter in ledger["chapters"]:
            path = chapter["path"]
            assert path not in prior_paths
            prior_paths.add(path)
            prior_verses += chapter["verse_count"]
            assert (ROOT / path).read_bytes() == old(path), path
            assert sha((ROOT / path).read_bytes()) == chapter["after_sha256"]
            assert sha((ROOT / chapter["tsw_comparator_path"]).read_bytes()) == chapter["tsw_comparator_sha256"]
    assert (len(prior_paths), prior_verses) == (989, 25559)

    ledgers = []
    focused_total = 0
    for rel, slug, filename, expected in SCOPES:
        audit_dir = ROOT / rel
        cfg = json.loads((audit_dir / "config.json").read_text())
        source_bytes = (args.source_directory / filename).read_bytes()
        assert sha(source_bytes) == cfg["source"]["sha256"]
        git_blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
        assert git_blob == cfg["source"]["git_blob_sha"]
        ledger = json.loads((audit_dir / f"{slug}-verse-review.json").read_text())
        assert ledger["status"] == "REVIEW_PENDING"
        assert ledger["qa_scope"] == "structural"
        assert ledger["publication_allowed"] is False
        assert ledger["automated_qa"] == "PASSED"
        assert ledger["summary"]["verses_drafted"] == expected
        errors = audit(ROOT, ledger, source_bytes)
        assert not errors, errors
        exact = source_records(source_bytes)
        focus = [{**verse, "exact_source_record": exact[verse["source_reference"]]} for verse in ledger["verses"]]
        assert len(focus) == expected
        record = {
            "status": "AUTHORING_REREAD_COMPLETED",
            "review_type": "Drafting assistant self-reread, not human or independent scholarly review",
            "authoring_record_sha256": sha((audit_dir / "authoring-reread.md").read_bytes()),
            "rows": focus,
        }
        if args.bind_focused_records:
            dump(audit_dir / "focused-comparisons.json", record)
            dump(audit_dir / "focused-selection.json", focus)
        else:
            assert json.loads((audit_dir / "focused-comparisons.json").read_text()) == record
            assert json.loads((audit_dir / "focused-selection.json").read_text()) == focus
        ledgers.append(ledger)
        focused_total += len(focus)

    luke, john = ledgers
    affected_source_audits = []
    luke_source_bytes = (args.source_directory / "luke-pinned-greek.txt").read_bytes()
    for path in [
        "audit/fluent-revision/2026-09-16-luke-1-4/luke-verse-review.json",
        "audit/fluent-revision/2026-09-16-luke-5-8/luke-verse-review.json",
        "audit/fluent-revision/2026-09-16-luke-9-11/luke-verse-review.json",
    ]:
        errors = audit(ROOT, json.loads((ROOT / path).read_text()), luke_source_bytes)
        assert not errors, (path, errors)
        affected_source_audits.append(path)
    lv = {v["reference"].split(" ", 1)[1]: v["after"] for v in luke["verses"]}
    jv = {v["reference"].split(" ", 1)[1]: v["after"] for v in john["verses"]}
    ls = source_records((args.source_directory / "luke-pinned-greek.txt").read_bytes())
    js = source_records((args.source_directory / "john-pinned-greek.txt").read_bytes())

    sensitive = {
        "luke_watchful_servants": all(term in lv["12:37"] for term in ["recline", "serve"]),
        "luke_division_not_peace": "division" in lv["12:51"] and "peace" in lv["12:51"],
        "luke_siloam_eighteen": "eighteen" in lv["13:4"] and "tower in Siloam" in lv["13:4"],
        "luke_disabled_guests": all(term in lv["14:13"] for term in ["poor", "disabled", "lame", "blind"]),
        "luke_hate_idiom_retained": all(term in lv["14:26"] for term in ["hate", "father", "mother", "wife", "children", "brothers", "sisters", "life"]),
        "luke_three_lost": all(term in " ".join(lv[f"15:{n}"] for n in range(4, 33)) for term in ["hundred sheep", "ten silver coins", "two sons"]),
        "luke_dishonest_wealth": "dishonest wealth" in lv["16:9"] and "eternal dwellings" in lv["16:9"],
        "luke_lazarus_named": "Lazarus" in lv["16:20"] and "Abraham’s side" in lv["16:22"],
        "luke_public_17_36_absent": "Luke 17:36" not in ls and "v36:" not in (ROOT / "translations/fluent/NT/luke/Luke_17.md").read_text().split("## Notes", 1)[0],
        "luke_two_women": "Two women" in lv["17:35"] and "one will be taken" in lv["17:35"],
        "luke_vultures": "body" in lv["17:37"] and "vultures" in lv["17:37"],
        "luke_widow_harm": "neither feared God nor respected people" in lv["18:2"] and "justice" in lv["18:3"],
        "luke_children": "infants" in lv["18:15"] and "children" in lv["18:16"] and "kingdom of God" in lv["18:16"],
        "luke_zacchaeus_restitution": "four times" in lv["19:8"] and "poor" in lv["19:8"],
        "luke_mina_numbers": "ten of his servants" in lv["19:13"] and "ten minas" in lv["19:13"],
        "luke_denarius_caesar": "denarius" in lv["20:24"] and "Caesar’s" in lv["20:24"],
        "luke_resurrection_gender": all(term in lv["20:35"] for term in ["marry", "given in marriage"]),
        "luke_widow_two_coins": "two small coins" in lv["21:2"],
        "luke_passover_speakers": "Peter and John" in lv["22:8"] and "Passover" in lv["22:8"],
        "luke_swords": all(term in lv["22:36"] for term in ["purse", "bag", "sword", "cloak"]),
        "luke_bracketed_agony": lv["22:43"].startswith("[") and lv["22:44"].endswith("]") and "ἀπʼ οὐρανοῦ" in ls["Luke 22:43"],
        "luke_three_denials": "three times" in lv["22:34"] and "rooster" in lv["22:34"],
        "luke_bracketed_forgiveness": lv["23:34"].startswith("[") and "]" in lv["23:34"] and "κλήρους" in ls["Luke 23:34"],
        "luke_paradise_today": all(term in lv["23:43"] for term in ["today", "with me", "paradise"]),
        "luke_women_witnesses": all(term in lv["24:10"] for term in ["Mary Magdalene", "Joanna", "Mary the mother of James", "others with them"]),
        "luke_bracketed_peter": lv["24:12"].startswith("[") and lv["24:12"].endswith("]"),
        "luke_embodied_appearance": all(term in lv["24:39"] for term in ["hands", "feet", "flesh", "bones"]),
        "luke_bracketed_ascension": "[and was carried up into heaven]" in lv["24:51"],
        "john_word_deity": "the Word was God" in jv["1:1"],
        "john_unique_god": "one-of-a-kind God" in jv["1:18"],
        "john_birth_above": "born from above" in jv["3:3"],
        "john_samaritan_identity": "Samaritan woman" in jv["4:9"] and "Jewish people" in jv["4:9"],
        "john_public_5_4_absent": "John 5:4" not in js and "v04:" not in (ROOT / "translations/fluent/NT/john/John_05.md").read_text().split("## Notes", 1)[0],
        "john_bread_flesh_blood": all(term in jv["6:53"] for term in ["flesh", "blood", "life"]),
        "john_seventy_two_not_imported": "seventy" not in " ".join(jv.values()),
        "john_variant_festival_timing": "not going up to this festival now" in jv["7:8"] and "⸀οὐκ" in js["John 7:8"],
        "john_living_water": "rivers of living water" in jv["7:38"] and "Spirit" in jv["7:39"],
        "john_bracketed_tradition": jv["7:53"].startswith("⟦") and jv["8:11"].endswith("⟧") and "⟦" in js["John 7:53"],
        "john_absolute_i_am": jv["8:58"].endswith("I am.”") and "ἐγὼ εἰμί" in js["John 8:58"],
        "john_blindness_not_blame": "Neither this man nor his parents sinned" in jv["9:3"],
        "john_we_must_work": jv["9:4"].startswith("We must") and "ἡμᾶς" in js["John 9:4"],
        "john_one_flock": "one flock, one shepherd" in jv["10:16"],
        "john_psalm_gods": "you are gods" in jv["10:34"],
        "john_jesus_wept": jv["11:35"] == "Jesus wept.",
        "john_caiaphas_calculation": "one man die for the people" in jv["11:50"],
        "john_judas_theft": all(term in jv["12:6"] for term in ["thief", "money box", "stole"]),
        "john_lifted_up": "lifted up" in jv["12:32"] and "kind of death" in jv["12:33"],
        "john_love_to_end": "loved them to the very end" in jv["13:1"],
        "john_heel": "lifted his heel" in jv["13:18"],
        "john_night": jv["13:30"].endswith("it was night."),
        "john_variant_13_32": jv["13:32"].startswith("If God has been glorified") and "⸂" in js["John 13:32"],
        "john_dwellings_not_mansions": "dwelling places" in jv["14:2"] and "mansions" not in jv["14:2"].lower(),
        "john_way_truth_life": all(term in jv["14:6"] for term in ["the way", "the truth", "the life"]),
        "john_variant_ask_me": "ask me" in jv["14:14"] and "⸀με" in js["John 14:14"],
        "john_advocate": "Advocate" in jv["14:16"] and "Holy Spirit" in jv["14:26"],
        "john_branch_choice": "he removes" in jv["15:2"] and "he prunes" in jv["15:2"],
        "john_slave_friend": all(term in jv["15:15"] for term in ["slaves", "friends", "Father"]),
        "john_synagogue_killing": "expel you from the synagogues" in jv["16:2"] and "kills you" in jv["16:2"],
        "john_spirit_exposes": all(term in jv["16:8"] for term in ["sin", "righteousness", "judgment"]),
        "john_childbirth_body": all(term in jv["16:21"] for term in ["woman", "giving birth", "pain", "child"]),
        "john_affliction_victory": "affliction" in jv["16:33"] and "overcome the world" in jv["16:33"],
        "john_eternal_life": all(term in jv["17:3"] for term in ["only true God", "Jesus the Messiah", "sent"]),
        "john_precreation_glory": "before the world existed" in jv["17:5"],
        "john_sanctify_truth": "Sanctify them in the truth" in jv["17:17"],
        "john_unity_witness": "may all be one" in jv["17:21"] and "world may believe" in jv["17:21"],
        "john_precreation_love": "before the foundation of the world" in jv["17:24"],
    }
    assert all(sensitive.values()), [name for name, passed in sensitive.items() if not passed]

    # Translation files retain required frontmatter, labels, headings, paragraphs, and apparatus.
    new_paths = set()
    for ledger in ledgers:
        for chapter in ledger["chapters"]:
            assert chapter["path"] not in prior_paths
            new_paths.add(chapter["path"])
            text = (ROOT / chapter["path"]).read_text()
            assert "qa_scope: structural" in text
            assert "editorial_status: REVIEW_PENDING" in text
            assert "publication_allowed: false" in text
            assert "## Notes" in text and "## Vocabulary" in text
            main = text.split("## Notes", 1)[0]
            labels = re.findall(r"^v(\d\d):", main, re.M)
            assert len(labels) == chapter["verse_count"]
            inside = False
            for line in main.split("---", 2)[2].splitlines():
                if line == "<p>":
                    assert not inside
                    inside = True
                elif line == "</p>":
                    assert inside
                    inside = False
                elif line.strip() and not line.startswith("## "):
                    assert inside, (chapter["path"], line)
            assert not inside

    # Book-level records append the new batch and preserve prior history/source.
    for slug, names, chapters, ledger_rel in [
        ("luke", ["LUKE_FLUENT_BOOK_QA.json", "BOOK_VERSE_REVIEW_LEDGER.json"], list(range(12, 25)), SCOPES[0][0] + "/luke-verse-review.json"),
        ("john", ["JOHN_FLUENT_BOOK_QA.json", "BOOK_VERSE_REVIEW_LEDGER.json"], list(range(1, 18)), SCOPES[1][0] + "/john-verse-review.json"),
    ]:
        for name in names:
            path = f"audit/exegetical-core/fluent-production/{slug}/{name}"
            current = json.loads((ROOT / path).read_text())
            previous = json.loads(old(path))
            assert current["source"] == previous["source"]
            assert current["revision_batches"][:-1] == previous.get("revision_batches", [])
            assert current["revision_batches"][-1]["verse_ledger"] == ledger_rel
            assert current["revision_batches"][-1]["chapters"] == chapters
            assert current["publication_allowed"] is False
            assert current["editorial_review_pending_chapters"] == sorted(set(previous.get("editorial_review_pending_chapters", [])) | set(chapters))
            if "entries" in previous:
                assert len(current["entries"]) == len(previous["entries"])
                for new, prior in zip(current["entries"], previous["entries"]):
                    if new["chapter"] in chapters:
                        assert new["status"] == "SUPERSEDED"
                        assert new["superseded_by_verse_ledger"] == ledger_rel
                        assert all(new[key] == value for key, value in prior.items())
                    else:
                        assert new == prior
                assert current["summary"] == previous["summary"]

    assert not subprocess.check_output(["git", "diff", PARENT, "--", "books", "companions"], cwd=ROOT).strip()
    subprocess.run(["git", "diff", "--check", PARENT], cwd=ROOT, check=True)
    family = subprocess.check_output([sys.executable, "tools/audit_translation_family.py"], cwd=ROOT).decode()

    all_chapters = []
    for item in queue["completed_draft_scopes"]:
        all_chapters.extend(json.loads((ROOT / item["ledger"]).read_text())["chapters"])
    assert len(queue["completed_draft_scopes"]) == 116
    assert len({c["path"] for c in all_chapters}) == len(all_chapters) == 1019
    assert sum(c["verse_count"] for c in all_chapters) == 26882
    block = queue["active_fifty_chapter_block"]
    assert (block["scope"], block["status"], block["completed_chapters"], block["remaining_chapters"], block["completed_verses"]) == (
        "John 6–21; Acts 1–28; Romans 1–6", "IN_PROGRESS", 12, 38, 528
    )
    completed = queue["completed_fifty_chapter_blocks"][-1]
    assert (completed["status"], completed["chapters"], completed["verses"]) == ("DRAFT_COMPLETED", 50, 2292)

    allowed = {"audit/fluent-revision/WORK_QUEUE.json", "tools/package_fluent_checkpoint.py"}
    for rel, slug, _, _ in SCOPES:
        allowed.update(path for path in subprocess.check_output(["find", rel, "-type", "f"], cwd=ROOT).decode().splitlines())
        ledger = json.loads((ROOT / rel / f"{slug}-verse-review.json").read_text())
        for chapter in ledger["chapters"]:
            allowed.add(chapter["path"])
            allowed.add(f"audit/exegetical-core/fluent-production/{slug}/{chapter['path'].split('/')[-1].replace('.md', '_review.json')}")
        cfg = json.loads((ROOT / rel / "config.json").read_text())
        allowed.update(f"audit/exegetical-core/fluent-production/{slug}/{name}" for name in cfg["book_record_files"])
    changed = subprocess.check_output(["git", "diff", "--name-only", PARENT], cwd=ROOT).decode().splitlines()
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT).decode().splitlines()
    unexpected = [path for path in changed + untracked if path not in allowed and path != ".fluent-revision-writer.lock"]
    assert not unexpected, unexpected

    boundary = {
        "status": "PASSED",
        "scope": "Matthew 24–28; Mark 1–16; Luke 1–24; John 1–5",
        "chapters": 50,
        "verses": 2292,
        "newly_completed_in_this_batch": {"scope": "Luke 12–24; John 1–5", "chapters": 18, "verses": 795},
        "completed_before_next_block_started": True,
        "next_block_started_with": {"scope": "John 6–17", "chapters": 12, "verses": 528},
        "qualification": "Draft coverage and structural QA complete; independent editorial and whole-book review pending.",
        "publication_allowed": False,
    }
    dump(ROOT / SCOPES[1][0] / "block-boundary-verification.json", boundary)

    result = {
        "status": "PASSED",
        "qa_scope": "structural",
        "parent_commit": PARENT,
        "batch_scope": "Luke 12–24; John 1–17",
        "new_chapters": 30,
        "new_verses": 1323,
        "cumulative_coverage": {"ledgers": 116, "chapters": 1019, "verses": 26882},
        "prior_preservation": {"ledgers_byte_identical": 114, "chapters_byte_identical": 989, "tsw_and_companion_unchanged": True},
        "source_binding_audit": "PASSED; exact verse payload hashes, whole-file SHA-256, and Git blob identities verified",
        "additional_affected_source_audits": affected_source_audits,
        "source_sensitive_checks": sensitive,
        "focused_authoring_reread_count": focused_total,
        "translation_family": family,
        "completed_block": boundary,
        "block_progress": block,
        "independent_editorial_review": "REVIEW_PENDING",
        "whole_book_review": "PENDING",
        "reader_testing": "PENDING",
        "companion_reconciliation": "PENDING; no quotations or bindings changed",
        "publication_allowed": False,
    }
    dump(ROOT / SCOPES[1][0] / "verification.json", result)
    print(json.dumps({key: result[key] for key in ["status", "new_chapters", "new_verses", "cumulative_coverage"]}))


if __name__ == "__main__":
    main()
