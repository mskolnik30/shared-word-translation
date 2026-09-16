#!/usr/bin/env python3
"""Structural/preservation checks, separate from documented authoring judgment."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'tools'))
from audit_fluent_revision import audit

R=Path(__file__).resolve().parents[3]
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
    assert (len(prior),prior_verses)==(978,24993)
    L=json.loads((A/'luke-verse-review.json').read_text())
    sb=(a.source_directory/cfg['source_filename']).read_bytes()
    errors=audit(R,L,sb); assert not errors,errors
    # Re-audit the immediately preceding Gospel source ledger, unchanged.
    affected=['audit/fluent-revision/2026-09-16-mark-13-16/mark-verse-review.json']
    for p in affected:
        errs=audit(R,json.loads((R/p).read_text()),(a.source_directory/'mark-pinned-greek.txt').read_bytes())
        assert not errs,errs
    src={line.split('\t',1)[0]:line.split('\t',1)[1] for line in sb.decode().splitlines() if '\t' in line}
    rows={v['reference']:v for v in L['verses']}
    refs=set(cfg['f3'])|set(cfg['focused_extra_references'])
    focus=[{**v,'exact_source_record':src[v['source_reference']]} for v in L['verses'] if v['reference'].split()[1] in refs]
    assert len(focus)==137
    record=dict(status='AUTHORING_REREAD_COMPLETED',review_type='Drafting assistant self-reread, not human or independent scholarly review',authoring_record_sha256=sha((A/'authoring-reread.md').read_bytes()),rows=focus)
    if a.bind_focused_records:
        dump(A/'focused-comparisons.json',record)
        dump(A/'focused-selection.json',focus)
    else:assert json.loads((A/'focused-comparisons.json').read_text())==record
    vv={k.split()[1]:v['after'] for k,v in rows.items()}
    checks={
      'fathers_hearts':"fathers' hearts" in vv['1:17'],
      'word_promise':'no word from God will fail' in vv['1:37'],
      'slave_servant_distinction':'slave' in vv['1:38'] and 'servant' in vv['1:54'],
      'future_dawn':'will visit' in vv['1:78'],
      'first_registration_when':'first registration, when Quirinius' in vv['2:2'],
      'birth_and_lodging':all(x in vv['2:7'] for x in ['firstborn son','manger','guest room']),
      'army_speaking':'army' in vv['2:13'] and 'saying' in vv['2:13'],
      'favor_reading':'those he favors' in vv['2:14'],
      'plural_purification':'their purification' in vv['2:22'],
      'father_and_mother':'His father and mother' in vv['2:33'],
      'rulers':all(x in vv['3:1'] for x in ['fifteenth','Tiberius Caesar','Pontius Pilate','Herod','Philip','Iturea','Trachonitis','Lysanias','Abilene']),
      'both_soldier_prohibitions':'extort money or accuse anyone falsely' in vv['3:14'],
      'age_and_supposition':'about thirty' in vv['3:23'] and 'as people supposed' in vv['3:23'],
      'source_genealogy_names':all(x in vv['3:32'] for x in ['Jesse','Jobel','Boaz','Sala','Nahshon']) and 'Ἰωβὴλ' in src['Luke 3:32'],
      'six_names_3_33':vv['3:33'].count('son of')==6 and all(x in vv['3:33'] for x in ['Amminadab','Admin','Arni','Hezron','Perez','Judah']),
      'two_cainans':all('Cainan' in vv[x] for x in ['3:36','3:37']),
      'genealogy_ending':'son of Enosh, son of Seth, son of Adam, son of God.'==vv['3:38'],
      'short_bread_quote':'bread alone' in vv['4:4'] and 'every word' not in vv['4:4'],
      'no_added_mountain':'mountain' not in vv['4:5'],
      'no_added_dismissal':'behind' not in vv['4:8'],
      'no_added_brokenhearted':'brokenhearted' not in vv['4:18'],
      'judea_retained':'Judea' in vv['4:44'] and 'Ἰουδαίας' in src['Luke 4:44']
    }
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    allowed={'audit/fluent-revision/WORK_QUEUE.json','tools/build_fluent_mark_checkpoint.py','tools/verify_fluent_mark_checkpoint.py','tools/package_fluent_checkpoint.py'}
    for ch in L['chapters']:
        allowed.add(ch['path']); assert ch['path'] not in prior
        p=f'audit/exegetical-core/fluent-production/luke/Luke_{ch["chapter"]:02}_review.json'
        allowed.add(p); d=json.loads((R/p).read_text());assert d['chapter_binding']==ch and d['publication_allowed'] is False
        text=(R/ch['path']).read_text(); inside=False
        for line in text.split('---',2)[2].split('## Notes')[0].splitlines():
            if line=='<p>':assert not inside;inside=True
            elif line=='</p>':assert inside;inside=False
            elif line.strip() and not line.startswith('## '):assert inside,(ch['path'],line)
        assert not inside
        maximum=ch['verse_count']+len(ch.get('source_omitted_public_labels',[]))
        for ref in re.findall(r'^v([\d,–\- ]+):',text.split('## Notes')[1],re.M):assert all(1<=int(x)<=maximum for x in re.findall(r'\d+',ref))
    for fn in cfg['book_record_files']:
        p='audit/exegetical-core/fluent-production/luke/'+fn;allowed.add(p)
        d=json.loads((R/p).read_text());od=json.loads(old(p))
        assert d['revision_batches'][:-1]==od.get('revision_batches',[]) and d['source']==od['source']
        assert d['editorial_review_pending_chapters']==[1,2,3,4] and not d['publication_allowed']
        if 'entries' in od:
            assert len(d['entries'])==len(od['entries'])
            for entry,prior_entry in zip(d['entries'],od['entries']):
                if entry['chapter'] in cfg['chapters']:
                    assert entry['status']=='SUPERSEDED' and entry['superseded_by_verse_ledger']==rel+'/luke-verse-review.json'
                    assert all(entry[k]==v for k,v in prior_entry.items())
                else:assert entry==prior_entry
            assert d['summary']==od['summary']
    changed=subprocess.check_output(['git','diff','--name-only',parent],cwd=R).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R).decode().splitlines()
    assert all(p in allowed or p.startswith(rel+'/') for p in changed),[p for p in changed if p not in allowed and not p.startswith(rel+'/')]
    assert not subprocess.check_output(['git','diff',parent,'--','books','companions'],cwd=R).strip()
    subprocess.run(['git','diff','--check',parent],cwd=R,check=True)
    family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=R).decode()
    chapters=[c for sc in q['completed_draft_scopes'] for c in json.loads((R/sc['ledger']).read_text())['chapters']]
    assert len({c['path'] for c in chapters})==len(chapters)==982
    assert sum(c['verse_count'] for c in chapters)==25207 and len(q['completed_draft_scopes'])==112
    block=q['active_fifty_chapter_block'];assert (block['status'],block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==('IN_PROGRESS',25,25,1145)
    result=dict(status='PASSED',qa_scope='structural',parent_commit=parent,new_chapters=4,new_verses=214,
      cumulative_coverage=dict(ledgers=112,chapters=982,verses=25207),prior_preservation=dict(ledgers_byte_identical=111,chapters_byte_identical=978,tsw_and_companion_unchanged=True),
      source_binding_audit='PASSED; all exact payloads, whole-file SHA-256 and Git blob identity',additional_affected_ledgers_passed=affected,
      source_sensitive_checks=checks,focused_authoring_reread_count=len(focus),translation_family=family,block_progress=block,
      independent_editorial_review='REVIEW_PENDING',reader_testing='PENDING',companion_reconciliation='PENDING; no quotations or bindings changed',publication_allowed=False)
    dump(A/'verification.json',result)
    print(json.dumps({k:result[k] for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
