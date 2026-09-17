#!/usr/bin/env python3
"""Structural/source verification for Acts 7–14."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from audit_fluent_revision import audit

PARENT = "e05e3debfb3fca3f21f12eb0c3dd797fa2b96d88"
REL = "audit/fluent-revision/2026-09-16-acts-7-14"
A = ROOT / REL
sha = lambda b: hashlib.sha256(b).hexdigest()

def old(path):
    return subprocess.check_output(["git", "show", PARENT + ":" + path], cwd=ROOT)

def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def records(data):
    out = {}
    for line in data.decode().splitlines():
        if "\t" in line:
            ref, payload = line.split("\t", 1)
            assert ref not in out
            out[ref] = payload
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-directory", type=Path, required=True)
    ap.add_argument("--bind-focused-records", action="store_true")
    args = ap.parse_args()

    cfg = json.loads((A / "config.json").read_text())
    source_bytes = (args.source_directory / "acts-pinned-greek.txt").read_bytes()
    assert sha(source_bytes) == cfg["source"]["sha256"]
    assert hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest() == cfg["source"]["git_blob_sha"]
    src = records(source_bytes)
    assert len(src) == 1002 and "Acts 8:37" not in src and "Acts 8:38" in src

    q = json.loads((ROOT / "audit/fluent-revision/WORK_QUEUE.json").read_text())
    oq = json.loads(old("audit/fluent-revision/WORK_QUEUE.json"))
    assert len(oq["completed_draft_scopes"]) == 118
    assert q["completed_draft_scopes"][:-1] == oq["completed_draft_scopes"]
    assert q["next_work"][1:] == oq["next_work"][1:]

    prior_paths = set()
    prior_verses = 0
    for scope in oq["completed_draft_scopes"]:
        ledger_path = scope["ledger"]
        assert (ROOT / ledger_path).read_bytes() == old(ledger_path), ledger_path
        ledger = json.loads((ROOT / ledger_path).read_text())
        for chapter in ledger["chapters"]:
            assert chapter["path"] not in prior_paths
            prior_paths.add(chapter["path"])
            prior_verses += chapter["verse_count"]
            assert (ROOT / chapter["path"]).read_bytes() == old(chapter["path"])
            assert sha((ROOT / chapter["path"]).read_bytes()) == chapter["after_sha256"]
            assert sha((ROOT / chapter["tsw_comparator_path"]).read_bytes()) == chapter["tsw_comparator_sha256"]
    assert (len(prior_paths), prior_verses) == (1029, 27213)

    ledger = json.loads((A / "acts-verse-review.json").read_text())
    errors = audit(ROOT, ledger, source_bytes)
    assert not errors, errors
    assert ledger["status"] == "REVIEW_PENDING"
    assert ledger["qa_scope"] == "structural"
    assert ledger["publication_allowed"] is False
    assert ledger["summary"]["verses_drafted"] == 325
    assert len(ledger["verses"]) == 325
    assert [c["chapter"] for c in ledger["chapters"]] == list(range(7, 15))
    assert ledger["chapters"][1]["source_omitted_public_labels"] == [37]

    focus = [{**v, "exact_source_record": src[v["source_reference"]]} for v in ledger["verses"]]
    record = {
        "status": "AUTHORING_REREAD_COMPLETED",
        "review_type": "Drafting assistant self-reread, not human or independent scholarly review",
        "authoring_record_sha256": sha((A / "authoring-reread.md").read_bytes()),
        "rows": focus,
    }
    if args.bind_focused_records:
        dump(A / "focused-selection.json", focus)
        dump(A / "focused-comparisons.json", record)
    else:
        assert json.loads((A / "focused-selection.json").read_text()) == focus
        assert json.loads((A / "focused-comparisons.json").read_text()) == record

    after = {v["reference"].split(" ", 1)[1]: v["after"] for v in ledger["verses"]}
    checks = {
        "acts_7_75_people": "seventy-five" in after["7:14"],
        "acts_7_burial_shechem": all(x in after["7:16"] for x in ["Shechem", "Abraham", "Hamor"]),
        "acts_7_infant_harm": all(x in after["7:19"] for x in ["infants", "would not survive"]),
        "acts_7_forty_forty": "forty years" in after["7:30"] and "forty years" in after["7:36"],
        "acts_7_living_words": "living words" in after["7:38"],
        "acts_7_moloch_rephan": all(x in after["7:43"] for x in ["Moloch", "Rephan", "Babylon"]),
        "acts_7_stoning_saul": all(x in after["7:58"] for x in ["stone him", "Saul"]),
        "acts_7_final_prayers": "receive my spirit" in after["7:59"] and "do not hold this sin" in after["7:60"],
        "acts_8_men_women": "both men and women" in after["8:12"],
        "acts_8_money_gift": all(x in after["8:20"] for x in ["silver", "God’s gift", "money"]),
        "acts_8_eunuch_identity": all(x in after["8:27"] for x in ["Ethiopian man", "eunuch", "Candace", "treasury"]),
        "acts_8_source_omission": "8:37" not in {v["reference"].split(" ", 1)[1] for v in ledger["verses"]},
        "acts_8_water_spirit": "water" in after["8:38"] and "Spirit of the Lord" in after["8:39"],
        "acts_9_men_women": "men or women" in after["9:2"],
        "acts_9_companions": "heard the voice" in after["9:7"] and "saw no one" in after["9:7"],
        "acts_9_chosen_suffer": "chosen instrument" in after["9:15"] and "must suffer" in after["9:16"],
        "acts_9_regions": all(x in after["9:31"] for x in ["Judea", "Galilee", "Samaria"]),
        "acts_9_tabitha_dorcas": all(x in after["9:36"] for x in ["disciple", "Tabitha", "Dorcas"]),
        "acts_9_widows_clothes": all(x in after["9:39"] for x in ["widows", "tunics", "clothing"]),
        "acts_10_italian_cohort": all(x in after["10:1"] for x in ["centurion", "Italian Cohort"]),
        "acts_10_three_times": "three times" in after["10:16"],
        "acts_10_human_application": all(x in after["10:28"] for x in ["any person", "defiled", "unclean"]),
        "acts_10_impartial_nations": "does not show favoritism" in after["10:34"] and "every nation" in after["10:35"],
        "acts_10_tree_third_day": "tree" in after["10:39"] and "third day" in after["10:40"],
        "acts_10_spirit_gentiles": "Gentiles" in after["10:45"] and "poured out" in after["10:45"],
        "acts_11_six_witnesses": "six brothers" in after["11:12"],
        "acts_11_life_rep": "repentance that leads to life" in after["11:18"],
        "acts_11_christians": "first called Christians" in after["11:26"],
        "acts_11_relief_means": "according to their means" in after["11:29"],
        "acts_12_james_sword": all(x in after["12:2"] for x in ["James", "John", "sword"]),
        "acts_12_four_squads": "four squads of four" in after["12:4"],
        "acts_12_rhoda": all(x in after["12:13"] for x in ["servant girl", "Rhoda"]),
        "acts_12_guards_execution": "guards" in after["12:19"] and "execution" in after["12:19"],
        "acts_12_herod_worms": "eaten by worms" in after["12:23"] and after["12:23"].endswith("died."),
        "acts_13_named_teachers": all(x in after["13:1"] for x in ["Barnabas", "Simeon", "Lucius", "Manaen", "Saul"]),
        "acts_13_seven_450": "seven nations" in after["13:19"] and "450 years" in after["13:20"],
        "acts_13_saul_40": all(x in after["13:21"] for x in ["Kish", "Benjamin", "forty years"]),
        "acts_13_forgive_justify": "forgiveness of sins" in after["13:38"] and "justified" in after["13:39"],
        "acts_13_appointed": "appointed to eternal life" in after["13:48"],
        "acts_13_influential_gender": all(x in after["13:50"] for x in ["women", "men"]),
        "acts_14_zeus_hermes": "Zeus" in after["14:12"] and "Hermes" in after["14:12"],
        "acts_14_bulls_wreaths": "bulls and wreaths" in after["14:13"],
        "acts_14_shared_humanity": "same nature as you" in after["14:15"],
        "acts_14_stoning": all(x in after["14:19"] for x in ["stoned Paul", "dragged him", "dead"]),
        "acts_14_many_troubles": "many troubles" in after["14:22"],
        "variant_markers_retained": "⸀" in src["Acts 7:1"] and "⸂" in src["Acts 13:20"],
    }
    assert all(checks.values()), [k for k, ok in checks.items() if not ok]

    affected_path = "audit/fluent-revision/2026-09-16-acts-1-6/acts-verse-review.json"
    affected_errors = audit(ROOT, json.loads((ROOT / affected_path).read_text()), source_bytes)
    assert not affected_errors, affected_errors

    for chapter in ledger["chapters"]:
        text = (ROOT / chapter["path"]).read_text()
        main = text.split("## Notes")[0]
        assert all(x in text for x in ["qa_scope: structural", "editorial_status: REVIEW_PENDING", "publication_allowed: false", "## Notes", "## Vocabulary"])
        assert len(re.findall(r"^v\d\d:", main, re.M)) == chapter["verse_count"]
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

    for name in cfg["book_record_files"]:
        path = f"audit/exegetical-core/fluent-production/acts/{name}"
        data = json.loads((ROOT / path).read_text())
        previous = json.loads(old(path))
        assert data["source"] == previous["source"]
        assert data["revision_batches"][:-1] == previous.get("revision_batches", [])
        assert data["revision_batches"][-1]["chapters"] == list(range(7, 15))
        assert data["revision_batches"][-1]["verse_ledger"] == REL + "/acts-verse-review.json"
        assert data["publication_allowed"] is False
        if "entries" in previous:
            assert len(data["entries"]) == len(previous["entries"])
            for entry, old_entry in zip(data["entries"], previous["entries"]):
                if entry["chapter"] in range(7, 15):
                    assert entry["status"] == "SUPERSEDED"
                    assert entry["superseded_by_verse_ledger"] == REL + "/acts-verse-review.json"
                    assert all(entry[k] == value for k, value in old_entry.items())
                else:
                    assert entry == old_entry
            assert data["summary"] == previous["summary"]

    subprocess.run(["git", "diff", "--check", PARENT], cwd=ROOT, check=True)
    assert not subprocess.check_output(["git", "diff", PARENT, "--", "books", "companions"], cwd=ROOT).strip()
    family = subprocess.check_output([sys.executable, "tools/audit_translation_family.py"], cwd=ROOT).decode()

    chapters = []
    for scope in q["completed_draft_scopes"]:
        chapters += json.loads((ROOT / scope["ledger"]).read_text())["chapters"]
    assert len(q["completed_draft_scopes"]) == 119
    assert len({c["path"] for c in chapters}) == len(chapters) == 1037
    assert sum(c["verse_count"] for c in chapters) == 27538
    block = q["active_fifty_chapter_block"]
    assert (block["completed_chapters"], block["remaining_chapters"], block["completed_verses"]) == (30, 20, 1184)

    allowed = {
        "audit/fluent-revision/WORK_QUEUE.json",
        "audit/exegetical-core/fluent-production/acts/ACTS_FLUENT_BOOK_QA.json",
        "audit/exegetical-core/fluent-production/acts/BOOK_VERSE_REVIEW_LEDGER.json",
    }
    allowed.update(subprocess.check_output(["find", REL, "-type", "f"], cwd=ROOT).decode().splitlines())
    for chapter in ledger["chapters"]:
        allowed.add(chapter["path"])
        allowed.add("audit/exegetical-core/fluent-production/acts/" + Path(chapter["path"]).name.replace(".md", "_review.json"))
    changed = subprocess.check_output(["git", "diff", "--name-only", PARENT], cwd=ROOT).decode().splitlines()
    changed += subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT).decode().splitlines()
    unexpected = [p for p in changed if p not in allowed and p != ".fluent-revision-writer.lock"]
    assert not unexpected, unexpected

    result = {
        "status": "PASSED",
        "qa_scope": "structural",
        "parent_commit": PARENT,
        "batch_scope": "Acts 7–14",
        "new_chapters": 8,
        "new_verses": 325,
        "cumulative_coverage": {"ledgers": 119, "chapters": 1037, "verses": 27538},
        "prior_preservation": {"ledgers_byte_identical": 118, "chapters_byte_identical": 1029, "tsw_and_companion_unchanged": True},
        "source_binding_audit": "PASSED; exact verse payload hashes, whole-file SHA-256, and Git blob identity verified",
        "additional_affected_source_audits": [affected_path],
        "source_sensitive_checks": checks,
        "focused_authoring_reread_count": 325,
        "translation_family": family,
        "block_progress": block,
        "independent_editorial_review": "REVIEW_PENDING",
        "reader_testing": "PENDING",
        "companion_reconciliation": "PENDING; no quotations or bindings changed",
        "publication_allowed": False,
    }
    dump(A / "verification.json", result)
    print(json.dumps({k: result[k] for k in ["status", "new_chapters", "new_verses", "cumulative_coverage"]}))

if __name__ == "__main__":
    main()
