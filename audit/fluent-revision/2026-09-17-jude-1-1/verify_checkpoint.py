#!/usr/bin/env python3
"""Verify the 10 newly authored chapters in the final 32-chapter remainder.

Structural and source-binding QA only. This is not independent editorial review
and cannot grant publication approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[3]
PARENT = "f12d5d5a2039ec1a086a1b80cc94c65874368a8a"
SCOPES = [('2026-09-17-2peter-2-3', '2peter', '2peter-pinned-greek.txt'), ('2026-09-17-1john-1-5', '1john', '1john-pinned-greek.txt'), ('2026-09-17-2john-1-1', '2john', '2john-pinned-greek.txt'), ('2026-09-17-3john-1-1', '3john', '3john-pinned-greek.txt'), ('2026-09-17-jude-1-1', 'jude', 'jude-pinned-greek.txt')]
sha=lambda b:hashlib.sha256(b).hexdigest()

def dump(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")
def old(path): return subprocess.check_output(["git","show",PARENT+":"+path],cwd=R)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source-directory",required=True,type=Path);ap.add_argument("--bind-focused-records",action="store_true");a=ap.parse_args()
    source_dir=a.source_directory.resolve();sys.path.insert(0,str(R/"tools"));from audit_fluent_revision import audit
    qpath="audit/fluent-revision/WORK_QUEUE.json";q=json.loads((R/qpath).read_text());oq=json.loads(old(qpath))
    assert q["completed_draft_scopes"][:len(oq["completed_draft_scopes"])]==oq["completed_draft_scopes"]
    assert len(oq["completed_draft_scopes"])==139 and len(q["completed_draft_scopes"])==144
    prior_paths=set();prior_verses=0
    for scope in oq["completed_draft_scopes"]:
        lp=scope["ledger"];assert (R/lp).read_bytes()==old(lp),lp
        ledger=json.loads((R/lp).read_text())
        for ch in ledger["chapters"]:
            p=ch["path"];assert p not in prior_paths;prior_paths.add(p);prior_verses+=ch["verse_count"]
            assert (R/p).read_bytes()==old(p),p
            assert sha((R/p).read_bytes())==ch["after_sha256"]
            assert sha((R/ch["tsw_comparator_path"]).read_bytes())==ch["tsw_comparator_sha256"]
    assert (len(prior_paths),prior_verses)==(1157,30481)

    allowed={qpath,"tools/audit_fluent_revision.py","tools/build_fluent_mark_checkpoint.py","tools/package_fluent_checkpoint.py","tools/prepare_remaining_nt_scopes.py","tools/finalize_nt_fifty_chapter_block.py","tools/refresh_nt_chapter_bindings.py"}
    ledgers=[];source_audits=[];focus_count=0;new_paths=set()
    for dirname,slug,source_name in SCOPES:
        directory=R/"audit/fluent-revision"/dirname;cfg=json.loads((directory/"config.json").read_text())
        lp=directory/f"{slug}-verse-review.json";ledger=json.loads(lp.read_text());sb=(source_dir/source_name).read_bytes()
        assert sha(sb)==cfg["source"]["sha256"]==ledger["source"]["sha256"]
        blob=hashlib.sha1(b"blob "+str(len(sb)).encode()+b"\0"+sb).hexdigest();assert blob==cfg["source"]["git_blob_sha"]==ledger["source"]["git_blob_sha"]
        errors=audit(R,ledger,sb);assert not errors,(slug,errors)
        ledgers.append(ledger);rows={line.split("\t",1)[0]:line.split("\t",1)[1] for line in sb.decode().splitlines() if "\t" in line}
        focus=[{**v,"exact_source_record":rows[v["source_reference"]]} for v in ledger["verses"] if v["delta"]=="F3"]
        reread=directory/"authoring-reread.md";assert "not human or independent scholarly review" in reread.read_text()
        record={"status":"AUTHORING_REREAD_COMPLETED","review_type":"Drafting-assistant bilingual self-reread; not human or independent scholarly review","authoring_record_sha256":sha(reread.read_bytes()),"rows":focus}
        fp=directory/"focused-comparisons.json"
        if a.bind_focused_records:dump(fp,record)
        else:assert json.loads(fp.read_text())==record
        focus_count+=len(focus);source_audits.append({"ledger":str(lp.relative_to(R)),"status":"PASSED","public_verses":len(ledger["verses"]),"unique_source_records":len({v["source_reference"] for v in ledger["verses"]})})
        allowed.update(str(p.relative_to(R)) for p in directory.rglob("*") if p.is_file())
        for ch in ledger["chapters"]:
            p=ch["path"];assert p not in prior_paths and p not in new_paths;new_paths.add(p);allowed.add(p)
            review=f"audit/exegetical-core/fluent-production/{slug}/"+Path(p).name.replace(".md","_review.json");allowed.add(review)
            rd=json.loads((R/review).read_text());assert rd["chapter_binding"]==ch and rd["status"]=="REVIEW_PENDING" and rd["publication_allowed"] is False
            text=(R/p).read_text();assert text.count("## Notes\n")==1 and text.count("## Vocabulary\n")==1
            body=text.split("## Notes")[0];opened=False
            for line in body.splitlines():
                if line=="<p>":assert not opened;opened=True
                elif line=="</p>":assert opened;opened=False
                elif re.match(r"^v\d+:",line):assert opened,(p,line)
            assert not opened
        for fn in cfg["book_record_files"]:
            p=f"audit/exegetical-core/fluent-production/{slug}/{fn}";allowed.add(p);cur=json.loads((R/p).read_text());prev=json.loads(old(p))
            assert cur["status"]=="REVIEW_PENDING" and cur["publication_allowed"] is False and cur["source"]==prev["source"]
            assert cur["revision_batches"][:-1]==prev.get("revision_batches",[])
            if "entries" in prev:
                assert len(cur["entries"])==len(prev["entries"])
                for x,y in zip(cur["entries"],prev["entries"]):
                    if y["chapter"] in cfg["chapters"]: assert all(x[k]==v for k,v in y.items()) and x["status"]=="SUPERSEDED"
                    else:assert x==y

    assert len(new_paths)==10 and sum(len(x["verses"]) for x in ledgers)==198
    assert sum(x["unique_source_records"] for x in source_audits)==198
    assert all(x["status"]=="REVIEW_PENDING" and x["qa_scope"]=="structural" and not x["publication_allowed"] for x in ledgers)
    after={v["reference"]:v["after"] for l in ledgers for v in l["verses"]}
    checks={
      "peter_names": "Bosor" in after["2Peter 2:15"] and "seven others" in after["2Peter 2:5"],
      "peter_variants": "chains" in after["2Peter 2:4"] and "before the Lord" not in after["2Peter 2:11"] and "deceptions" in after["2Peter 2:13"] and "exposed" in after["2Peter 3:10"],
      "peter_harm": "slaves" in after["2Peter 2:19"] and "under punishment" in after["2Peter 2:9"],
      "john_boundary": "children" not in after["1John 2:13"] and after["1John 2:14"].startswith("I have written to you, children"),
      "john_sin": "cannot sin" in after["1John 3:9"] and "slaughtered his brother" in after["1John 3:12"],
      "john_witnesses": after["1John 5:7"]=="For there are three who bear witness:" and "Spirit, the water and the blood" in after["1John 5:8"],
      "john_variants": after["1John 4:19"]=="We love because he first loved us." and "keeps that person safe" in after["1John 5:18"] and "This is the true God" in after["1John 5:20"],
      "second_john": "your joy" in after["2John 1:12"] and "what we have worked" in after["2John 1:8"],
      "third_john": "Diotrephes" in after["3John 1:9"] and "Demetrius" in after["3John 1:12"] and "by name" in after["3John 1:15"],
      "jude_variants": "Jesus saved" in after["Jude 1:5"] and "other flesh" in after["Jude 1:7"] and "Lord came" in after["Jude 1:14"],
      "jude_names": all(x in after["Jude 1:11"] for x in ["Cain","Balaam","Korah"]) and "seventh from Adam" in after["Jude 1:14"],
      "jude_end": "those who doubt" in after["Jude 1:22"] and "snatching" in after["Jude 1:23"] and "before all time" in after["Jude 1:25"],
    }
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    chapters=[c for s in q["completed_draft_scopes"] for c in json.loads((R/s["ledger"]).read_text())["chapters"]]
    assert len({c["path"] for c in chapters})==len(chapters)==1167 and sum(c["verse_count"] for c in chapters)==30679
    block=q["active_fifty_chapter_block"];assert (block["chapters_target"],block["completed_chapters"],block["remaining_chapters"],block["completed_verses"])==(32,10,22,198)
    assert q["completed_fifty_chapter_blocks"][-1]["chapters"]==50 and q["completed_fifty_chapter_blocks"][-1]["verses"]==1055
    changed=subprocess.check_output(["git","diff","--name-only",PARENT],cwd=R).decode().splitlines()+subprocess.check_output(["git","ls-files","--others","--exclude-standard"],cwd=R).decode().splitlines()
    for p in changed:
        if p==".fluent-revision-writer.lock":continue
        assert p in allowed,p
    assert not subprocess.check_output(["git","diff",PARENT,"--","books","companions"],cwd=R).strip()
    subprocess.run(["git","diff","--check",PARENT],cwd=R,check=True)
    family=subprocess.check_output([sys.executable,"tools/audit_translation_family.py"],cwd=R).decode()
    result={"status":"PASSED","qa_scope":"structural","parent_commit":PARENT,"new_chapters":10,"new_verses":198,"unique_original_source_records":198,"cumulative_coverage":{"ledgers":144,"chapters":1167,"verses":30679},"prior_preservation":{"ledgers_byte_identical":139,"chapters_byte_identical":1157,"verses":30481,"tsw_and_companion_unchanged":True},"source_binding_audits":source_audits,"source_sensitive_checks":checks,"focused_authoring_reread_count":focus_count,"translation_family":family,"completed_fifty_chapter_block":q["completed_fifty_chapter_blocks"][-1],"active_fifty_chapter_block":block,"independent_editorial_review":"REVIEW_PENDING","whole_book_reviews":"PENDING; five completed books newly queued","reader_testing":"PENDING","companion_reconciliation":"PENDING; no quotations or bindings changed","publication_allowed":False}
    out=Path(__file__).with_name("verification.json");dump(out,result)
    boundary={k:result[k] for k in ["status","qa_scope","parent_commit","new_chapters","new_verses","unique_original_source_records","cumulative_coverage","source_sensitive_checks","focused_authoring_reread_count","completed_fifty_chapter_block","active_fifty_chapter_block","independent_editorial_review","publication_allowed"]};dump(Path(__file__).with_name("block-boundary-verification.json"),boundary)
    print(json.dumps({"status":"PASSED","new_chapters":10,"new_verses":198,"coverage":result["cumulative_coverage"],"focused_rereads":focus_count}))

if __name__=="__main__":main()
