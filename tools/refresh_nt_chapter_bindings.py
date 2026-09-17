#!/usr/bin/env python3
"""Refresh after-SHA bindings after whitespace-only chapter normalization."""
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1]
SCOPES=[
 ("2026-09-17-colossians-1-4","colossians"),("2026-09-17-1thessalonians-1-5","1thessalonians"),
 ("2026-09-17-2thessalonians-1-3","2thessalonians"),("2026-09-17-1timothy-1-6","1timothy"),
 ("2026-09-17-2timothy-1-4","2timothy"),("2026-09-17-titus-1-3","titus"),
 ("2026-09-17-philemon-1-1","philemon"),("2026-09-17-hebrews-1-13","hebrews"),
 ("2026-09-17-1peter-1-5","1peter"),("2026-09-17-2peter-1-1","2peter")]
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")
for dirname,slug in SCOPES:
    lp=R/"audit/fluent-revision"/dirname/f"{slug}-verse-review.json";ledger=json.loads(lp.read_text())
    for chapter in ledger["chapters"]:
        chapter["after_sha256"]=sha((R/chapter["path"]).read_bytes())
        rp=R/f"audit/exegetical-core/fluent-production/{slug}"/(Path(chapter["path"]).stem+"_review.json")
        review=json.loads(rp.read_text());review["chapter_binding"]=chapter;dump(rp,review)
    dump(lp,ledger)
