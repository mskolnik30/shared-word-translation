#!/usr/bin/env python3
"""Structural and exact-source verification for Romans 7–15."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from audit_fluent_revision import audit

PARENT = "cfbf791e640c869b958d5456051b6febbc208b02"
REL = "audit/fluent-revision/2026-09-16-romans-7-15"
SCOPE = ROOT / REL
LEDGER_PATH = REL + "/romans-verse-review.json"
SOURCE_NAME = "romans-pinned-greek.txt"
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
    cfg = json.loads((SCOPE / "config.json").read_text())
    source_bytes = (args.source_directory / SOURCE_NAME).read_bytes()
    assert sha(source_bytes) == cfg["source"]["sha256"]
    blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
    assert blob == cfg["source"]["git_blob_sha"]
    source = records(source_bytes)
    assert len(source) == cfg["source"]["book_verse_count"] == 430
    ledger = json.loads((SCOPE / "romans-verse-review.json").read_text())
    errors = audit(ROOT, ledger, source_bytes)
    assert not errors, errors
    assert len(ledger["verses"]) == ledger["summary"]["verses_drafted"] == 245
    assert ledger["status"] == "REVIEW_PENDING" and ledger["qa_scope"] == "structural"
    assert ledger["publication_allowed"] is False

    queue = json.loads((ROOT / "audit/fluent-revision/WORK_QUEUE.json").read_text())
    old_queue = json.loads(old("audit/fluent-revision/WORK_QUEUE.json"))
    assert len(old_queue["completed_draft_scopes"]) == 121
    assert queue["completed_draft_scopes"][:-1] == old_queue["completed_draft_scopes"]
    assert queue["completed_draft_scopes"][-1] == {"scope": "Romans 7–15", "verses": 245, "ledger": LEDGER_PATH}
    assert queue["next_work"][1:] == old_queue["next_work"][1:]

    prior_paths, prior_verses = set(), 0
    for item in old_queue["completed_draft_scopes"]:
        path = item["ledger"]
        assert (ROOT / path).read_bytes() == old(path), path
        prior = json.loads((ROOT / path).read_text())
        for chapter in prior["chapters"]:
            assert chapter["path"] not in prior_paths
            prior_paths.add(chapter["path"])
            prior_verses += chapter["verse_count"]
            assert (ROOT / chapter["path"]).read_bytes() == old(chapter["path"])
            assert sha((ROOT / chapter["path"]).read_bytes()) == chapter["after_sha256"]
            assert sha((ROOT / chapter["tsw_comparator_path"]).read_bytes()) == chapter["tsw_comparator_sha256"]
    assert (len(prior_paths), prior_verses) == (1057, 28183)

    focus = [{**v, "exact_source_record": source[v["source_reference"]]} for v in ledger["verses"]]
    reread = {
        "status": "AUTHORING_REREAD_COMPLETED",
        "review_type": "Drafting assistant self-reread, not human or independent scholarly review",
        "authoring_record_sha256": sha((SCOPE / "authoring-reread.md").read_bytes()),
        "rows": focus,
    }
    if args.bind_focused_records:
        dump(SCOPE / "focused-selection.json", focus)
        dump(SCOPE / "focused-comparisons.json", reread)
    else:
        assert json.loads((SCOPE / "focused-selection.json").read_text()) == focus
        assert json.loads((SCOPE / "focused-comparisons.json").read_text()) == reread

    after = {v["reference"]: v["after"] for v in ledger["verses"]}
    checks = {
        "rom_7_law_not_sin": all(x in after["Romans 7:7"] for x in ["law sin", "Absolutely not", "Do not covet"]),
        "rom_7_inner_captivity": all(x in after["Romans 7:22"] + after["Romans 7:23"] for x in ["inner self", "taking me captive"]),
        "rom_7_body_of_death": "body of death" in after["Romans 7:24"],
        "rom_8_no_added_clause": after["Romans 8:1"].endswith("Christ Jesus.") and "walk" not in after["Romans 8:1"],
        "rom_8_sons_children": "God's sons" in after["Romans 8:14"] and "God's children" in after["Romans 8:16"],
        "rom_8_creation_groans": all(x in after["Romans 8:22"] + after["Romans 8:23"] for x in ["creation", "labor pains", "groan", "redemption of our bodies"]),
        "rom_8_all_things": "all things work together" in after["Romans 8:28"],
        "rom_8_real_harms": all(x in after["Romans 8:35"] for x in ["persecution", "famine", "nakedness", "sword"]),
        "rom_9_israel_privileges": all(x in after["Romans 9:4"] for x in ["Israelites", "covenants", "law", "worship", "promises"]),
        "rom_9_jacob_esau": all(x in after["Romans 9:13"] for x in ["Jacob", "loved", "Esau", "hated"]),
        "rom_9_mercy_hardening": all(x in after["Romans 9:18"] for x in ["mercy", "hardens"]),
        "rom_9_potter_clay": all(x in after["Romans 9:21"] for x in ["potter", "clay", "same lump", "dishonored"]),
        "rom_10_culmination": "culmination of the law" in after["Romans 10:4"],
        "rom_10_confess_believe": all(x in after["Romans 10:9"] for x in ["Jesus is Lord", "believe", "raised him from the dead"]),
        "rom_10_word_christ": "word of Christ" in after["Romans 10:17"],
        "rom_11_seven_thousand": "seven thousand men" in after["Romans 11:4"],
        "rom_11_root_supports": "the root supports you" in after["Romans 11:18"],
        "rom_11_own_tree": "their own olive tree" in after["Romans 11:24"],
        "rom_11_all_israel": "all Israel will be saved" in after["Romans 11:26"],
        "rom_11_beloved": all(x in after["Romans 11:28"] for x in ["enemies", "beloved", "patriarchs"]),
        "rom_11_all_mercy": after["Romans 11:32"].count("everyone") == 2,
        "rom_12_bodies_sacrifice": all(x in after["Romans 12:1"] for x in ["bodies", "living sacrifice"]),
        "rom_12_enemy_care": all(x in after["Romans 12:20"] for x in ["enemy", "feed", "drink", "burning coals"]),
        "rom_13_sword": all(x in after["Romans 13:4"] for x in ["sword", "avenger", "wrath"]),
        "rom_13_love_no_harm": "Love does no harm to a neighbor" in after["Romans 13:10"],
        "rom_14_god_judgment_seat": "God's judgment seat" in after["Romans 14:10"],
        "rom_14_meat_wine_three_harms": all(x in after["Romans 14:21"] for x in ["meat", "wine", "stumble", "ensnared", "weak"]),
        "rom_15_priestly": all(x in after["Romans 15:16"] for x in ["priestly service", "Gentiles", "offering", "Holy Spirit"]),
        "rom_15_geography": all(x in after["Romans 15:19"] for x in ["Jerusalem", "Illyricum"]),
        "rom_15_contribution": all(x in after["Romans 15:26"] for x in ["Macedonia", "Achaia", "poor", "Jerusalem"]),
        "rom_15_danger_acceptance": all(x in after["Romans 15:31"] for x in ["rescued", "Judea", "acceptable", "saints"]),
        "variant_markers_retained": "⸀" in source["Rom 7:13"] and "⸂" in source["Rom 8:11"],
    }
    assert all(checks.values()), [k for k, ok in checks.items() if not ok]

    affected_path = "audit/fluent-revision/2026-09-16-romans-1-6/romans-verse-review.json"
    affected_errors = audit(ROOT, json.loads((ROOT / affected_path).read_text()), source_bytes)
    assert not affected_errors, affected_errors

    for chapter in ledger["chapters"]:
        text = (ROOT / chapter["path"]).read_text()
        main = text.split("## Notes")[0]
        assert all(x in text for x in ["qa_scope: structural", "editorial_status: REVIEW_PENDING", "publication_allowed: false", "## Notes", "## Vocabulary"])
        assert len(re.findall(r"^v\d\d:", main, re.M)) == chapter["verse_count"]
        assert sha((ROOT / chapter["path"]).read_bytes()) == chapter["after_sha256"]

    for name in cfg["book_record_files"]:
        path = f"audit/exegetical-core/fluent-production/romans/{name}"
        data, previous = json.loads((ROOT / path).read_text()), json.loads(old(path))
        assert data["source"] == previous["source"]
        assert data["revision_batches"][:-1] == previous.get("revision_batches", [])
        assert data["revision_batches"][-1]["chapters"] == cfg["chapters"]
        assert data["revision_batches"][-1]["verse_ledger"] == LEDGER_PATH
        assert data["publication_allowed"] is False
        if "entries" in previous:
            assert len(data["entries"]) == len(previous["entries"])
            for entry, prior in zip(data["entries"], previous["entries"]):
                if entry["chapter"] in cfg["chapters"]:
                    assert entry["status"] == "SUPERSEDED"
                    assert entry["superseded_by_verse_ledger"] == LEDGER_PATH
                    assert all(entry[k] == value for k, value in prior.items())
                else:
                    assert entry == prior
            assert data["summary"] == previous["summary"]

    subprocess.run(["git", "diff", "--check", PARENT], cwd=ROOT, check=True)
    assert not subprocess.check_output(["git", "diff", PARENT, "--", "books", "companions"], cwd=ROOT).strip()
    family = subprocess.check_output([sys.executable, "tools/audit_translation_family.py"], cwd=ROOT).decode()

    chapters = []
    for item in queue["completed_draft_scopes"]:
        chapters += json.loads((ROOT / item["ledger"]).read_text())["chapters"]
    assert len(queue["completed_draft_scopes"]) == 122
    assert len({c["path"] for c in chapters}) == len(chapters) == 1066
    assert sum(c["verse_count"] for c in chapters) == 28428
    block = queue["active_fifty_chapter_block"]
    assert (block["completed_chapters"], block["remaining_chapters"], block["completed_verses"]) == (9, 41, 245)
    assert block["status"] == "IN_PROGRESS" and block["completed_scope"] == "Romans 7–15"

    allowed = {"audit/fluent-revision/WORK_QUEUE.json", "tools/package_fluent_checkpoint.py"}
    allowed.update(subprocess.check_output(["find", REL, "-type", "f"], cwd=ROOT).decode().splitlines())
    allowed.update(f"audit/exegetical-core/fluent-production/romans/{name}" for name in cfg["book_record_files"])
    for chapter in ledger["chapters"]:
        allowed.add(chapter["path"])
        allowed.add("audit/exegetical-core/fluent-production/romans/" + Path(chapter["path"]).name.replace(".md", "_review.json"))
    changed = subprocess.check_output(["git", "diff", "--name-only", PARENT], cwd=ROOT).decode().splitlines()
    changed += subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT).decode().splitlines()
    unexpected = [p for p in changed if p not in allowed and p != ".fluent-revision-writer.lock"]
    assert not unexpected, unexpected

    result = {
        "status": "PASSED", "qa_scope": "structural", "parent_commit": PARENT,
        "batch_scope": "Romans 7–15", "new_chapters": 9, "new_verses": 245,
        "cumulative_coverage": {"ledgers": 122, "chapters": 1066, "verses": 28428},
        "prior_preservation": {"ledgers_byte_identical": 121, "chapters_byte_identical": 1057, "tsw_and_companion_unchanged": True},
        "source_binding_audit": "PASSED; all exact verse payload hashes, whole-file SHA-256, and Git blob identity verified",
        "additional_affected_source_audits": [affected_path],
        "source_sensitive_checks": checks,
        "focused_authoring_reread_count": 245,
        "translation_family": family,
        "block_progress": block,
        "block_status": "IN_PROGRESS; this checkpoint is not a completed fifty-chapter block",
        "next_scope": cfg["next_scope"],
        "independent_editorial_review": "REVIEW_PENDING",
        "whole_book_review": "PENDING",
        "reader_testing": "PENDING",
        "companion_reconciliation": "PENDING; no quotations or bindings changed",
        "publication_allowed": False,
    }
    dump(SCOPE / "verification.json", result)
    print(json.dumps({k: result[k] for k in ["status", "new_chapters", "new_verses", "cumulative_coverage", "block_status"]}))

if __name__ == "__main__":
    main()
