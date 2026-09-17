#!/usr/bin/env python3
"""Structural and exact-source verification for Acts 15–28 and Romans 1–6."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from audit_fluent_revision import audit

PARENT = "378de0f20726b72ab3ba8ff7240e833f640337bd"
SCOPES = [
    ("audit/fluent-revision/2026-09-16-acts-15-28", "acts", "acts-pinned-greek.txt", 484),
    ("audit/fluent-revision/2026-09-16-romans-1-6", "romans", "romans-pinned-greek.txt", 161),
]
FINAL = ROOT / SCOPES[1][0]
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
    ap.add_argument("--additional-source-directory", type=Path, required=True)
    ap.add_argument("--bind-focused-records", action="store_true")
    args = ap.parse_args()

    sources = {}
    ledgers = {}
    for rel, slug, filename, count in SCOPES:
        scope = ROOT / rel
        cfg = json.loads((scope / "config.json").read_text())
        base = args.source_directory if slug == "acts" else args.additional_source_directory
        source_bytes = (base / filename).read_bytes()
        assert sha(source_bytes) == cfg["source"]["sha256"]
        blob = hashlib.sha1(b"blob " + str(len(source_bytes)).encode() + b"\0" + source_bytes).hexdigest()
        assert blob == cfg["source"]["git_blob_sha"]
        src = records(source_bytes)
        assert len(src) == cfg["source"]["book_verse_count"]
        ledger = json.loads((scope / f"{slug}-verse-review.json").read_text())
        errors = audit(ROOT, ledger, source_bytes)
        assert not errors, errors
        assert len(ledger["verses"]) == ledger["summary"]["verses_drafted"] == count
        assert ledger["status"] == "REVIEW_PENDING" and ledger["qa_scope"] == "structural"
        assert ledger["publication_allowed"] is False
        sources[slug] = src
        ledgers[slug] = ledger

    acts_refs = {v["reference"].split(" ", 1)[1] for v in ledgers["acts"]["verses"]}
    assert all(ref not in acts_refs for ref in ["15:34", "19:41", "24:7", "28:29"])
    assert all(ref in acts_refs for ref in ["15:33", "15:35", "19:40", "24:6", "24:8", "28:28", "28:30"])
    assert ledgers["acts"]["chapters"][4]["source_omitted_public_labels"] == [41]

    queue = json.loads((ROOT / "audit/fluent-revision/WORK_QUEUE.json").read_text())
    old_queue = json.loads(old("audit/fluent-revision/WORK_QUEUE.json"))
    assert len(old_queue["completed_draft_scopes"]) == 119
    assert queue["completed_draft_scopes"][:-2] == old_queue["completed_draft_scopes"]
    assert [x["scope"] for x in queue["completed_draft_scopes"][-2:]] == ["Acts 15–28", "Romans 1–6"]
    assert queue["next_work"][1:] == old_queue["next_work"][1:]

    prior_paths, prior_verses = set(), 0
    for item in old_queue["completed_draft_scopes"]:
        ledger_path = item["ledger"]
        assert (ROOT / ledger_path).read_bytes() == old(ledger_path), ledger_path
        ledger = json.loads((ROOT / ledger_path).read_text())
        for chapter in ledger["chapters"]:
            assert chapter["path"] not in prior_paths
            prior_paths.add(chapter["path"])
            prior_verses += chapter["verse_count"]
            assert (ROOT / chapter["path"]).read_bytes() == old(chapter["path"])
            assert sha((ROOT / chapter["path"]).read_bytes()) == chapter["after_sha256"]
            assert sha((ROOT / chapter["tsw_comparator_path"]).read_bytes()) == chapter["tsw_comparator_sha256"]
    assert (len(prior_paths), prior_verses) == (1037, 27538)

    focused_total = 0
    for rel, slug, _, _ in SCOPES:
        scope = ROOT / rel
        ledger = ledgers[slug]
        focus = [{**v, "exact_source_record": sources[slug][v["source_reference"]]} for v in ledger["verses"]]
        record = {
            "status": "AUTHORING_REREAD_COMPLETED",
            "review_type": "Drafting assistant self-reread, not human or independent scholarly review",
            "authoring_record_sha256": sha((scope / "authoring-reread.md").read_bytes()),
            "rows": focus,
        }
        if args.bind_focused_records:
            dump(scope / "focused-selection.json", focus)
            dump(scope / "focused-comparisons.json", record)
        else:
            assert json.loads((scope / "focused-selection.json").read_text()) == focus
            assert json.loads((scope / "focused-comparisons.json").read_text()) == record
        focused_total += len(focus)
    assert focused_total == 645

    after = {v["reference"]: v["after"] for l in ledgers.values() for v in l["verses"]}
    checks = {
        "acts_15_four_requirements": all(x in after["Acts 15:29"] for x in ["idols", "blood", "strangled", "sexual immorality"]),
        "acts_16_enslaved_exploited": all(x in after["Acts 16:16"] + after["Acts 16:19"] for x in ["slave girl", "owners", "profit"]),
        "acts_16_citizenship_beating": all(x in after["Acts 16:37"] for x in ["Roman citizens", "publicly", "without a trial"]),
        "acts_17_athens_names": all(x in after["Acts 17:34"] for x in ["Dionysius", "Damaris"]),
        "acts_18_priscilla_first": after["Acts 18:26"].index("Priscilla") < after["Acts 18:26"].index("Aquila"),
        "acts_19_fifty_thousand": "fifty thousand" in after["Acts 19:19"],
        "acts_20_eutychus_dead_alive": "dead" in after["Acts 20:9"] and "alive" in after["Acts 20:12"],
        "acts_20_blood_own": "blood of his own Son" in after["Acts 20:28"],
        "acts_21_four_daughters": all(x in after["Acts 21:9"] for x in ["four", "daughters", "prophesied"]),
        "acts_22_flogging_citizen": all(x in after["Acts 22:25"] for x in ["flog", "Roman citizen", "not been condemned"]),
        "acts_23_troop_numbers": all(x in after["Acts 23:23"] for x in ["two hundred", "seventy", "two hundred"]),
        "acts_24_source_omission": "Acts 24:7" not in after,
        "acts_25_appeal": "I appeal to Caesar" in after["Acts 25:11"],
        "acts_26_goads": "kick against the goads" in after["Acts 26:14"],
        "acts_27_people_number": "276" in after["Acts 27:37"],
        "acts_27_prisoner_harm": "kill the prisoners" in after["Acts 27:42"],
        "acts_28_source_omission": "Acts 28:29" not in after,
        "rom_1_female_male": all(x in after["Romans 1:26"] + after["Romans 1:27"] for x in ["females", "males", "natural"]),
        "rom_2_judging_turn": all(x in after["Romans 2:1"] for x in ["without excuse", "judges", "condemn yourself"]),
        "rom_3_faithfulness": "faithfulness of Jesus Christ" in after["Romans 3:22"],
        "rom_3_atoning": "atoning sacrifice" in after["Romans 3:25"],
        "rom_4_sarah": all(x in after["Romans 4:19"] for x in ["hundred", "Sarah's womb"]),
        "rom_5_indicative_peace": "we have peace with God" in after["Romans 5:1"],
        "rom_5_because_all": "because all sinned" in after["Romans 5:12"],
        "rom_5_one_many": "one man" in after["Romans 5:19"] and "the many" in after["Romans 5:19"],
        "rom_6_slavery_retained": all(x in after["Romans 6:16"] + after["Romans 6:18"] for x in ["slaves", "enslaved", "righteousness"]),
        "variant_markers_retained": "⸀" in sources["acts"]["Acts 15:1"] and "⸂" in sources["romans"]["Rom 1:1"],
    }
    assert all(checks.values()), [k for k, ok in checks.items() if not ok]

    affected = []
    acts_bytes = (args.source_directory / "acts-pinned-greek.txt").read_bytes()
    for path in [
        "audit/fluent-revision/2026-09-16-acts-1-6/acts-verse-review.json",
        "audit/fluent-revision/2026-09-16-acts-7-14/acts-verse-review.json",
    ]:
        errors = audit(ROOT, json.loads((ROOT / path).read_text()), acts_bytes)
        assert not errors, (path, errors)
        affected.append(path)

    for rel, slug, _, _ in SCOPES:
        ledger = ledgers[slug]
        for chapter in ledger["chapters"]:
            text = (ROOT / chapter["path"]).read_text()
            main = text.split("## Notes")[0]
            assert all(x in text for x in ["qa_scope: structural", "editorial_status: REVIEW_PENDING", "publication_allowed: false", "## Notes", "## Vocabulary"])
            assert len(re.findall(r"^v\d\d:", main, re.M)) == chapter["verse_count"]

        cfg = json.loads((ROOT / rel / "config.json").read_text())
        for name in cfg["book_record_files"]:
            path = f"audit/exegetical-core/fluent-production/{slug}/{name}"
            data, previous = json.loads((ROOT / path).read_text()), json.loads(old(path))
            assert data["source"] == previous["source"]
            assert data["revision_batches"][:-1] == previous.get("revision_batches", [])
            assert data["revision_batches"][-1]["chapters"] == cfg["chapters"]
            assert data["revision_batches"][-1]["verse_ledger"] == rel + f"/{slug}-verse-review.json"
            assert data["publication_allowed"] is False
            if "entries" in previous:
                assert len(data["entries"]) == len(previous["entries"])
                for entry, prior in zip(data["entries"], previous["entries"]):
                    if entry["chapter"] in cfg["chapters"]:
                        assert entry["status"] == "SUPERSEDED"
                        assert entry["superseded_by_verse_ledger"] == rel + f"/{slug}-verse-review.json"
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
    assert len(queue["completed_draft_scopes"]) == 121
    assert len({c["path"] for c in chapters}) == len(chapters) == 1057
    assert sum(c["verse_count"] for c in chapters) == 28183
    completed = queue["completed_fifty_chapter_blocks"][-1]
    assert (completed["scope"], completed["status"], completed["chapters"], completed["verses"]) == (
        "John 6–21; Acts 1–28; Romans 1–6", "DRAFT_COMPLETED", 50, 1829)
    block = queue["active_fifty_chapter_block"]
    assert (block["completed_chapters"], block["remaining_chapters"], block["completed_verses"]) == (0, 50, 0)

    allowed = {"audit/fluent-revision/WORK_QUEUE.json", "tools/build_fluent_mark_checkpoint.py", "tools/audit_fluent_revision.py", "translations/registry.json"}
    for rel, slug, _, _ in SCOPES:
        allowed.update(subprocess.check_output(["find", rel, "-type", "f"], cwd=ROOT).decode().splitlines())
        cfg = json.loads((ROOT / rel / "config.json").read_text())
        allowed.update(f"audit/exegetical-core/fluent-production/{slug}/{name}" for name in cfg["book_record_files"])
        for chapter in ledgers[slug]["chapters"]:
            allowed.add(chapter["path"])
            allowed.add(f"audit/exegetical-core/fluent-production/{slug}/" + Path(chapter["path"]).name.replace(".md", "_review.json"))
    changed = subprocess.check_output(["git", "diff", "--name-only", PARENT], cwd=ROOT).decode().splitlines()
    changed += subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT).decode().splitlines()
    unexpected = [p for p in changed if p not in allowed and p != ".fluent-revision-writer.lock"]
    assert not unexpected, unexpected

    boundary = {
        "status": "PASSED",
        "scope": "John 6–21; Acts 1–28; Romans 1–6",
        "chapters": 50,
        "verses": 1829,
        "newly_completed_in_this_batch": {"scope": "Acts 15–28; Romans 1–6", "chapters": 20, "verses": 645},
        "completed_before_next_block_started": True,
        "next_block_started_with": None,
        "qualification": "Draft coverage and structural QA complete; independent editorial and whole-book review pending.",
        "publication_allowed": False,
    }
    dump(FINAL / "block-boundary-verification.json", boundary)
    result = {
        "status": "PASSED", "qa_scope": "structural", "parent_commit": PARENT,
        "batch_scope": "Acts 15–28; Romans 1–6", "new_chapters": 20, "new_verses": 645,
        "cumulative_coverage": {"ledgers": 121, "chapters": 1057, "verses": 28183},
        "prior_preservation": {"ledgers_byte_identical": 119, "chapters_byte_identical": 1037, "tsw_and_companion_unchanged": True},
        "source_binding_audit": "PASSED; exact verse payload hashes, whole-file SHA-256, and Git blob identities verified",
        "additional_affected_source_audits": affected,
        "source_sensitive_checks": checks,
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
    dump(FINAL / "verification.json", result)
    dump(ROOT / SCOPES[0][0] / "verification.json", {
        "status": "PASSED", "qa_scope": "structural", "scope": "Acts 15–28",
        "new_chapters": 14, "new_verses": 484,
        "combined_batch_verification": SCOPES[1][0] + "/verification.json",
        "independent_editorial_review": "REVIEW_PENDING", "publication_allowed": False,
    })
    print(json.dumps({k: result[k] for k in ["status", "new_chapters", "new_verses", "cumulative_coverage"]}))

if __name__ == "__main__":
    main()
