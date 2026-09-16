#!/usr/bin/env python3
"""Structural/preservation checks, separate from documented authoring judgment."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from audit_fluent_revision import audit

R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('scope_directory',type=Path)
    ap.add_argument('--source-directory',required=True,type=Path)
    ap.add_argument('--bind-focused-records',action='store_true')
    a=ap.parse_args(); A=a.scope_directory.resolve(); rel=str(A.relative_to(R))
    cfg=json.loads((A/'config.json').read_text()); parent=cfg['parent_commit']
    def old(p):return subprocess.check_output(['git','show',parent+':'+p],cwd=R)
    q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text())
    oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'))
    assert q['completed_draft_scopes'][:-1]==oq['completed_draft_scopes']
    assert q['next_work'][1:]==oq['next_work'][1:]
    prior=set(); prior_verses=0
    for sc in oq['completed_draft_scopes']:
        assert (R/sc['ledger']).read_bytes()==old(sc['ledger']),sc['ledger']
        l=json.loads((R/sc['ledger']).read_text())
        for ch in l['chapters']:
            assert ch['path'] not in prior
            prior.add(ch['path']); prior_verses+=ch['verse_count']
            assert (R/ch['path']).read_bytes()==old(ch['path']),ch['path']
            assert sha((R/ch['path']).read_bytes())==ch['after_sha256']
            assert sha((R/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
    assert (len(prior),prior_verses)==(965,24428)
    L=json.loads((A/'mark-verse-review.json').read_text())
    sb=(a.source_directory/cfg['source_filename']).read_bytes()
    errors=audit(R,L,sb); assert not errors,errors
    # Re-audit the immediately preceding Gospel source ledgers, unchanged.
    affected=[]
    for p,b in [('audit/fluent-revision/2026-09-16-mark-1-3/mark-verse-review.json','mark'),('audit/fluent-revision/2026-09-16-matthew-24-28/matthew-verse-review.json','matthew')]:
        errs=audit(R,json.loads((R/p).read_text()),(a.source_directory/(b+'-pinned-greek.txt')).read_bytes())
        assert not errs,errs
        affected.append(p)
    src={line.split('\t',1)[0]:line.split('\t',1)[1] for line in sb.decode().splitlines() if '\t' in line}
    rows={v['reference']:v for v in L['verses']}
    refs=set(cfg['f3'])|set('4:8 4:20 5:13 5:25 5:41 5:42 6:30 6:37 6:38 6:40 6:41 6:43 6:44 6:45 6:53 7:10 7:11 7:21 7:24 7:29 7:31 7:33 7:35 8:6 8:7 8:8 8:9 8:19 8:20 8:26 8:29 8:33'.split())
    focus=[{**v,'exact_source_record':src[v['source_reference']]} for v in L['verses'] if v['reference'].split()[1] in refs]
    assert len(focus)==75
    record=dict(status='AUTHORING_REREAD_COMPLETED',review_type='Drafting assistant self-reread, not human or independent scholarly review',authoring_record_sha256=sha((A/'authoring-reread.md').read_bytes()),rows=focus)
    if a.bind_focused_records:dump(A/'focused-comparisons.json',record)
    else:assert json.loads((A/'focused-comparisons.json').read_text())==record
    vv={k.split()[1]:v['after'] for k,v in rows.items()}
    checks={
      'yield_numbers':all(x in vv['4:8'] and x in vv['4:20'] for x in ['thirty','sixty','hundred']),
      'unqualified_smallest':'smallest of all' in vv['4:31'] and 'among' not in vv['4:31'],
      'legion_shifts':'My name' in vv['5:9'] and 'we are many' in vv['5:9'] and 'send them' in vv['5:10'],
      'pigs_count':'about two thousand' in vv['5:13'],
      'two_twelves':'twelve years' in vv['5:25'] and 'twelve years' in vv['5:42'],
      'family_names':all(x in vv['6:3'] for x in ['Mary','James','Joses','Judas','Simon','sisters']),
      'no_harmonized_staff':'except a staff' in vv['6:8'] and 'wear sandals' in vv['6:9'],
      'herodias_identity':'Herodias’s own daughter' in vv['6:22'],
      'apostles_source_present':'ἀπόστολοι' in src['Mark 6:30'] and 'apostles' in vv['6:30'],
      'first_feeding':all(x in vv[k].lower() for k,x in [('6:37','two hundred'),('6:38','five'),('6:38','two fish'),('6:40','hundred'),('6:40','fifty'),('6:43','twelve'),('6:44','men'),('6:44','five thousand')]),
      'route_names':'Bethsaida' in vv['6:45'] and 'Gennesaret' in vv['6:53'],
      'pass_by_and_self_identification':'intended to pass by' in vv['6:48'] and 'It is I' in vv['6:50'],
      'couches_present':'κλινῶν' in src['Mark 7:4'] and 'dining couches' in vv['7:4'],
      'omitted_7_16':'Mark 7:16' not in rows and 'Mark 7:16' not in src,
      'adultery_verse_location':'μοιχεῖαι' in src['Mark 7:22'] and 'adultery' not in vv['7:21'] and vv['7:22'].startswith('adultery'),
      'tyre_sidon_route':'Sidon' not in vv['7:24'] and all(x in vv['7:31'] for x in ['Tyre','Sidon','Decapolis']),
      'reply_without_yes':'yes' not in vv['7:28'].lower() and 'even the dogs' in vv['7:28'],
      'no_added_immediately_7_35':'immediately' not in vv['7:35'].lower() and 'at once' not in vv['7:35'].lower(),
      'second_feeding':all(x in vv[k].lower() for k,x in [('8:6','seven'),('8:7','few small fish'),('8:8','seven large baskets'),('8:9','about four thousand')]) and 'men' not in vv['8:9'],
      'recollection_counts':all(x in vv['8:19'].lower() for x in ['five loaves','five thousand','twelve']) and all(x in vv['8:20'].lower() for x in ['seven loaves','four thousand','seven']),
      'two_stage_sight':'trees walking' in vv['8:24'] and 'again' in vv['8:25'],
      'short_village_prohibition':'tell' not in vv['8:26'] and 'Do not even go' in vv['8:26'],
      'passion_sequence':all(x in vv['8:31'] for x in ['must','elders','chief priests','scribes','be killed','after three days']),
      'life_repetition':all('life' in vv['8:'+str(v)] for v in [35,36,37])
    }
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    allowed={'audit/fluent-revision/WORK_QUEUE.json','tools/build_fluent_mark_checkpoint.py','tools/verify_fluent_mark_checkpoint.py','tools/package_fluent_checkpoint.py'}
    for ch in L['chapters']:
        allowed.add(ch['path']); assert ch['path'] not in prior
        p=f'audit/exegetical-core/fluent-production/mark/Mark_{ch["chapter"]:02}_review.json'
        allowed.add(p); d=json.loads((R/p).read_text());assert d['chapter_binding']==ch and d['publication_allowed'] is False
        text=(R/ch['path']).read_text(); inside=False
        for line in text.split('---',2)[2].split('## Notes')[0].splitlines():
            if line=='<p>':assert not inside;inside=True
            elif line=='</p>':assert inside;inside=False
            elif line.strip() and not line.startswith('## '):assert inside,(ch['path'],line)
        assert not inside
        maximum=ch['verse_count']+len(ch.get('source_omitted_public_labels',[]))
        for ref in re.findall(r'^v([\d,–\- ]+):',text.split('## Notes')[1],re.M):assert all(1<=int(x)<=maximum for x in re.findall(r'\d+',ref))
    for fn in ['MARK_FLUENT_BOOK_QA.json','MARK_SOURCE_BINDINGS.json']:
        p='audit/exegetical-core/fluent-production/mark/'+fn;allowed.add(p)
        d=json.loads((R/p).read_text());od=json.loads(old(p))
        assert d['revision_batches'][:-1]==od['revision_batches'] and d['source']==od['source']
        assert d['editorial_review_pending_chapters']==list(range(1,9)) and not d['publication_allowed']
        if 'bindings' in od:assert d['bindings']==od['bindings']
    changed=subprocess.check_output(['git','diff','--name-only',parent],cwd=R).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R).decode().splitlines()
    assert all(p in allowed or p.startswith(rel+'/') for p in changed),[p for p in changed if p not in allowed and not p.startswith(rel+'/')]
    assert not subprocess.check_output(['git','diff',parent,'--','books','companions'],cwd=R).strip()
    subprocess.run(['git','diff','--check',parent],cwd=R,check=True)
    family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=R).decode()
    chapters=[c for sc in q['completed_draft_scopes'] for c in json.loads((R/sc['ledger']).read_text())['chapters']]
    assert len({c['path'] for c in chapters})==len(chapters)==970
    assert sum(c['verse_count'] for c in chapters)==24642 and len(q['completed_draft_scopes'])==109
    block=q['active_fifty_chapter_block'];assert (block['status'],block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==('IN_PROGRESS',13,37,580)
    result=dict(status='PASSED',qa_scope='structural',parent_commit=parent,new_chapters=5,new_verses=214,
      cumulative_coverage=dict(ledgers=109,chapters=970,verses=24642),prior_preservation=dict(ledgers_byte_identical=108,chapters_byte_identical=965,tsw_and_companion_unchanged=True),
      source_binding_audit='PASSED; all exact payloads, whole-file SHA-256 and Git blob identity',additional_affected_ledgers_passed=affected,
      source_sensitive_checks=checks,focused_authoring_reread_count=len(focus),translation_family=family,block_progress=block,
      independent_editorial_review='REVIEW_PENDING',reader_testing='PENDING',companion_reconciliation='PENDING; no quotations or bindings changed',publication_allowed=False)
    dump(A/'verification.json',result)
    print(json.dumps({k:result[k] for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
