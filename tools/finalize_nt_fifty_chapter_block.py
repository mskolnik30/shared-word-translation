#!/usr/bin/env python3
"""Finalize the completed 50-chapter NT block and prepare the final remainder.

This performs only deterministic bookkeeping and provisional F3 classification
for already-authored verse decisions. It does not create translation wording.
"""
from collections import Counter
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
PARENT = "9ba4fd64124c93cf9e1b7c9a422701a2705f404c"
SCOPE = "Ephesians 6; Philippians 1–4; Colossians 1–4; 1 Thessalonians 1–5; 2 Thessalonians 1–3; 1 Timothy 1–6; 2 Timothy 1–4; Titus 1–3; Philemon 1; Hebrews 1–13; 1 Peter 1–5; 2 Peter 1"
NEXT = "2 Peter 2–3; 1 John 1–5; 2 John 1; 3 John 1; Jude 1; Revelation 1–22"
SCOPES = [
    ("2026-09-17-colossians-1-4", "colossians", "colossians-pinned-greek.txt"),
    ("2026-09-17-1thessalonians-1-5", "1thessalonians", "1thessalonians-pinned-greek.txt"),
    ("2026-09-17-2thessalonians-1-3", "2thessalonians", "2thessalonians-pinned-greek.txt"),
    ("2026-09-17-1timothy-1-6", "1timothy", "1timothy-pinned-greek.txt"),
    ("2026-09-17-2timothy-1-4", "2timothy", "2timothy-pinned-greek.txt"),
    ("2026-09-17-titus-1-3", "titus", "titus-pinned-greek.txt"),
    ("2026-09-17-philemon-1-1", "philemon", "philemon-pinned-greek.txt"),
    ("2026-09-17-hebrews-1-13", "hebrews", "hebrews-pinned-greek.txt"),
    ("2026-09-17-1peter-1-5", "1peter", "1peter-pinned-greek.txt"),
    ("2026-09-17-2peter-1-1", "2peter", "2peter-pinned-greek.txt"),
]
F3 = {
 "1timothy": "1:9 1:10 1:13 1:20 2:4 2:5 2:6 2:8 2:9 2:11 2:12 2:13 2:14 2:15 3:1 3:2 3:4 3:5 3:6 3:11 3:12 3:16 4:7 4:10 4:16 5:3 5:6 5:8 5:9 5:11 5:12 5:13 5:14 5:16 5:17 5:20 5:22 6:1 6:2 6:9 6:10 6:13 6:15 6:16 6:17".split(),
 "2timothy": "1:5 1:7 1:8 1:9 1:10 1:12 1:15 2:3 2:9 2:11 2:12 2:13 2:15 2:17 2:18 2:24 2:26 3:6 3:8 3:11 3:12 3:15 3:16 4:1 4:6 4:7 4:8 4:10 4:13 4:14 4:16 4:17 4:18".split(),
 "titus": "1:1 1:6 1:7 1:10 1:11 1:12 1:13 1:14 2:3 2:4 2:5 2:9 2:10 2:11 2:13 2:14 3:1 3:5 3:6 3:7 3:10".split(),
 "philemon": "1:8 1:9 1:10 1:11 1:12 1:13 1:14 1:15 1:16 1:17 1:18 1:19 1:20 1:21 1:22".split(),
 "hebrews": "1:2 1:3 1:5 1:6 1:8 1:9 1:13 2:1 2:3 2:6 2:7 2:8 2:9 2:10 2:11 2:14 2:15 2:17 3:1 3:2 3:3 3:5 3:6 3:8 3:10 3:11 3:12 3:14 3:16 3:17 3:18 4:2 4:3 4:7 4:8 4:9 4:12 4:13 4:15 5:2 5:3 5:5 5:6 5:7 5:8 5:9 6:4 6:5 6:6 6:8 6:12 6:18 6:19 6:20 7:1 7:2 7:3 7:5 7:9 7:10 7:11 7:12 7:14 7:16 7:18 7:19 7:22 7:25 7:27 8:5 8:7 8:8 8:9 8:10 8:11 8:12 8:13 9:4 9:7 9:8 9:9 9:11 9:12 9:13 9:14 9:15 9:16 9:17 9:19 9:22 9:23 9:26 9:27 9:28 10:1 10:4 10:5 10:9 10:10 10:12 10:14 10:19 10:20 10:22 10:24 10:25 10:26 10:27 10:28 10:29 10:30 10:31 10:33 10:34 10:37 10:38 10:39 11:1 11:3 11:4 11:5 11:7 11:8 11:9 11:11 11:12 11:13 11:16 11:17 11:18 11:19 11:21 11:22 11:23 11:24 11:25 11:26 11:27 11:28 11:29 11:30 11:31 11:32 11:35 11:36 11:37 11:38 11:40 12:1 12:2 12:4 12:5 12:6 12:7 12:8 12:9 12:10 12:11 12:13 12:15 12:16 12:17 12:18 12:19 12:20 12:21 12:22 12:23 12:24 12:25 12:26 12:27 12:28 12:29 13:2 13:3 13:4 13:5 13:7 13:9 13:10 13:11 13:12 13:13 13:14 13:17 13:20 13:21 13:23 13:24".split(),
 "1peter": "1:1 1:2 1:3 1:6 1:7 1:9 1:11 1:12 1:13 1:17 1:18 1:19 1:22 1:23 2:4 2:5 2:6 2:7 2:8 2:9 2:10 2:11 2:12 2:13 2:14 2:15 2:16 2:17 2:18 2:19 2:20 2:21 2:23 2:24 2:25 3:1 3:2 3:3 3:4 3:5 3:6 3:7 3:9 3:12 3:14 3:15 3:16 3:17 3:18 3:19 3:20 3:21 3:22 4:1 4:3 4:4 4:5 4:6 4:12 4:13 4:14 4:15 4:16 4:17 4:18 4:19 5:1 5:2 5:3 5:4 5:5 5:8 5:9 5:10 5:12 5:13 5:14".split(),
 "2peter": "1:1 1:3 1:4 1:5 1:6 1:7 1:10 1:11 1:13 1:14 1:15 1:16 1:17 1:18 1:19 1:20 1:21".split(),
}

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

def main():
    ledgers = []
    for dirname, slug, _ in SCOPES:
        directory = R/"audit/fluent-revision"/dirname
        cfg_path = directory/"config.json"
        cfg = json.loads(cfg_path.read_text())
        refs = set(cfg.get("f3", [])) | set(F3.get(slug, []))
        cfg["f3"] = sorted(refs, key=lambda x: tuple(map(int, x.split(":"))))
        dump(cfg_path, cfg)
        ledger_path = directory/f"{slug}-verse-review.json"
        ledger = json.loads(ledger_path.read_text())
        for verse in ledger["verses"]:
            ref = verse["reference"].split()[-1]
            if ref in refs:
                verse["delta"] = "F3"
        ledger["summary"]["delta_counts"] = dict(Counter(v["delta"] for v in ledger["verses"]))
        dump(ledger_path, ledger)
        ledgers.append(str(ledger_path.relative_to(R)))
        for chapter in ledger["chapters"]:
            review_path = R/f"audit/exegetical-core/fluent-production/{slug}"/(Path(chapter["path"]).stem+"_review.json")
            review = json.loads(review_path.read_text())
            prefix = review["book"]+f" {chapter['chapter']}:"
            review["key_decisions"] = [v for v in ledger["verses"] if v["reference"].startswith(prefix) and v["delta"] == "F3"]
            dump(review_path, review)

    qpath = R/"audit/fluent-revision/WORK_QUEUE.json"
    q = json.loads(qpath.read_text())
    block = q["active_fifty_chapter_block"]
    assert block["scope"] == SCOPE
    assert (block["completed_chapters"], block["completed_verses"], block["remaining_chapters"]) == (50, 1055, 0)
    q["completed_fifty_chapter_blocks"].append({
        "scope": SCOPE, "status": "DRAFT_COMPLETED", "chapters": 50, "verses": 1055,
        "completion_evidence": "audit/fluent-revision/2026-09-17-2peter-1-1/block-boundary-verification.json",
        "qualification": "Source-based revision draft coverage and structural QA are complete. Independent editorial review, whole-book review, reader testing, and Companion reconciliation remain pending."
    })
    q["active_fifty_chapter_block"] = {
        "scope": NEXT, "status": "IN_PROGRESS", "chapters_target": 32,
        "completed_chapters": 0, "completed_scope": "None", "completed_verses": 0,
        "remaining_scope": NEXT, "remaining_chapters": 32,
        "qualification": "Final project remainder: 0 of 32 chapters drafted in this block; 32 remain. Independent editorial review and reader testing remain pending."
    }
    reviews = ["Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "1 Peter"]
    q["next_work"][0] = {"scope": NEXT, "action": "Continue the final 32-chapter remainder without routine approval. Read every verified pinned Greek verse before authoring."}
    existing = {x["scope"] for x in q["next_work"]}
    insert = []
    for book in reviews:
        name = f"Whole-book {book} consistency review"
        if name not in existing:
            insert.append({"scope": name, "action": "Read the complete revised book and apparatus continuously; review argument flow, repeated language, names, relationships, source variants and cross-batch consistency. Rebind any changes. Independent editorial review remains pending."})
    q["next_work"][1:1] = insert
    dump(qpath, q)

    final_cfg_path = R/"audit/fluent-revision/2026-09-17-2peter-1-1/config.json"
    cfg = json.loads(final_cfg_path.read_text())
    cfg.update({
        "batch_scope": "Colossians 1–4; 1 Thessalonians 1–5; 2 Thessalonians 1–3; 1 Timothy 1–6; 2 Timothy 1–4; Titus 1–3; Philemon 1; Hebrews 1–13; 1 Peter 1–5; 2 Peter 1",
        "batch_chapters": 45, "batch_verses": 927, "batch_source_records": 927,
        "batch_reader_filename": "Fluent-Colossians-1-2Peter-1.md",
        "batch_ledgers": ledgers, "active_block_ranges": [],
        "new_source_files": [x[2] for x in SCOPES],
        "additional_source_bindings": {}
    })
    for dirname, slug, source_name in SCOPES:
        source = json.loads((R/"audit/fluent-revision"/dirname/"config.json").read_text())["source"]
        cfg["additional_source_bindings"][slug] = {**source, "source_filename": source_name}
    dump(final_cfg_path, cfg)

if __name__ == "__main__":
    main()
