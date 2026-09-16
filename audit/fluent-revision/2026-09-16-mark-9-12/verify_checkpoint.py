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
    assert (len(prior),prior_verses)==(970,24642)
    L=json.loads((A/'mark-verse-review.json').read_text())
    sb=(a.source_directory/cfg['source_filename']).read_bytes()
    errors=audit(R,L,sb); assert not errors,errors
    # Re-audit the immediately preceding Gospel source ledgers, unchanged.
    affected=[]
    for p,b in [('audit/fluent-revision/2026-09-16-mark-4-8/mark-verse-review.json','mark'),('audit/fluent-revision/2026-09-16-mark-1-3/mark-verse-review.json','mark'),('audit/fluent-revision/2026-09-16-matthew-24-28/matthew-verse-review.json','matthew')]:
        errs=audit(R,json.loads((R/p).read_text()),(a.source_directory/(b+'-pinned-greek.txt')).read_bytes())
        assert not errs,errs
        affected.append(p)
    src={line.split('\t',1)[0]:line.split('\t',1)[1] for line in sb.decode().splitlines() if '\t' in line}
    rows={v['reference']:v for v in L['verses']}
    refs=set(cfg['f3'])|set(cfg['focused_extra_references'])
    focus=[{**v,'exact_source_record':src[v['source_reference']]} for v in L['verses'] if v['reference'].split()[1] in refs]
    assert len(focus)==99
    record=dict(status='AUTHORING_REREAD_COMPLETED',review_type='Drafting assistant self-reread, not human or independent scholarly review',authoring_record_sha256=sha((A/'authoring-reread.md').read_bytes()),rows=focus)
    if a.bind_focused_records:dump(A/'focused-comparisons.json',record)
    else:assert json.loads((A/'focused-comparisons.json').read_text())==record
    vv={k.split()[1]:v['after'] for k,v in rows.items()}
    checks={
      'transfiguration_witnesses':all(x in vv['9:2'] for x in ['Six days','Peter','James','John']),
      'two_arguing_parties':'with them' in vv['9:16'],
      'belief_unbelief':'I believe! Help my unbelief!' in vv['9:24'],
      'most_not_merely_many':'most of the people' in vv['9:26'],
      'prayer_without_fasting':'prayer' in vv['9:29'] and 'fasting' not in vv['9:29'],
      'human_hands_and_three_days':all(x in vv['9:31'] for x in ['handed over','human hands','three days']),
      'outsider_boundary':'following us' in vv['9:38'] and vv['9:40'].count('us')==2,
      'omitted_labels':all('Mark '+x not in rows and 'Mark '+x not in src for x in ['9:44','9:46','11:26']),
      'short_fire_salt':'sacrifice' not in vv['9:49'] and 'salted with fire' in vv['9:49'],
      'unnamed_questioners':'Pharisees' not in vv['10:2'] and 'Φαρισαῖοι' not in src['Mark 10:2'],
      'joining_clause_present':'προσκολληθήσεται' in src['Mark 10:7'] and 'be joined to his wife' in vv['10:7'],
      'mutual_divorce_subjects':'against her' in vv['10:11'] and 'a woman divorces her husband' in vv['10:12'],
      'wealth_not_added_to_10_24':'rich' not in vv['10:24'] and 'wealth' not in vv['10:24'],
      'hundredfold_with_persecution':all(x in vv['10:30'] for x in ['hundred','mothers','persecutions','eternal life']) and 'fathers' not in vv['10:30'],
      'passion_order':all(x in vv['10:34'] for x in ['mock','spit','flog','kill','Three days']),
      'servant_slave_distinction':'servant' in vv['10:43'] and 'slave' in vv['10:44'],
      'ransom_without_added_recipient':'ransom for many' in vv['10:45'],
      'repeated_request_question':all('What do you want me to do for you?' in vv[x] for x in ['10:36','10:51']),
      'bartimaeus_identity':all(x in vv['10:46'] for x in ['Bartimaeus','Timaeus','blind beggar','Jericho']),
      'two_villages':all(x in vv['11:1'] for x in ['Bethphage','Bethany','Mount of Olives','two']),
      'fig_season_tension':'not the season for figs' in vv['11:13'],
      'all_nations':'all nations' in vv['11:17'],
      'received_tense':'have received' in vv['11:24'],
      'deliberation_question_present':'Τί εἴπωμεν' in src['Mark 11:31'] and 'What should we say?' in vv['11:31'],
      'slave_status':'slave' in vv['12:2'] and 'slave' in vv['12:4'],
      'killed_before_thrown':vv['12:8'].index('killed')<vv['12:8'].index('threw'),
      'tax_question_numbering':'Should we pay' in vv['12:14'] and 'Should we pay' not in vv['12:15'] and 'δῶμεν' in src['Mark 12:14'],
      'give_back_to_both':'Give back' in vv['12:17'] and 'Caesar' in vv['12:17'] and 'God' in vv['12:17'],
      'seven_brothers':all('seven' in vv[x] for x in ['12:20','12:22','12:23']),
      'rise_clause_present':'ὅταν ἀναστῶσιν' in src['Mark 12:23'] and 'when they rise' in vv['12:23'],
      'angels_comparison':'like angels' in vv['12:25'] and 'become angels' not in vv['12:25'],
      'four_terms_three_terms':all(x in vv['12:30'] for x in ['heart','soul','mind','strength']) and all(x in vv['12:33'] for x in ['heart','understanding','strength']) and 'soul' not in vv['12:33'],
      'enemies_beneath_feet':'beneath your feet' in vv['12:36'] and 'footstool' not in vv['12:36'],
      'coin_value_retained':'κοδράντης' in src['Mark 12:42'] and 'two' in vv['12:42'] and 'quadrans' in vv['12:42'],
      'widow_totality':'everything she had' in vv['12:44'] and 'whole livelihood' in vv['12:44']
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
        assert d['editorial_review_pending_chapters']==list(range(1,13)) and not d['publication_allowed']
        if 'bindings' in od:assert d['bindings']==od['bindings']
    changed=subprocess.check_output(['git','diff','--name-only',parent],cwd=R).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R).decode().splitlines()
    assert all(p in allowed or p.startswith(rel+'/') for p in changed),[p for p in changed if p not in allowed and not p.startswith(rel+'/')]
    assert not subprocess.check_output(['git','diff',parent,'--','books','companions'],cwd=R).strip()
    subprocess.run(['git','diff','--check',parent],cwd=R,check=True)
    family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=R).decode()
    chapters=[c for sc in q['completed_draft_scopes'] for c in json.loads((R/sc['ledger']).read_text())['chapters']]
    assert len({c['path'] for c in chapters})==len(chapters)==974
    assert sum(c['verse_count'] for c in chapters)==24818 and len(q['completed_draft_scopes'])==110
    block=q['active_fifty_chapter_block'];assert (block['status'],block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==('IN_PROGRESS',17,33,756)
    result=dict(status='PASSED',qa_scope='structural',parent_commit=parent,new_chapters=4,new_verses=176,
      cumulative_coverage=dict(ledgers=110,chapters=974,verses=24818),prior_preservation=dict(ledgers_byte_identical=109,chapters_byte_identical=970,tsw_and_companion_unchanged=True),
      source_binding_audit='PASSED; all exact payloads, whole-file SHA-256 and Git blob identity',additional_affected_ledgers_passed=affected,
      source_sensitive_checks=checks,focused_authoring_reread_count=len(focus),translation_family=family,block_progress=block,
      independent_editorial_review='REVIEW_PENDING',reader_testing='PENDING',companion_reconciliation='PENDING; no quotations or bindings changed',publication_allowed=False)
    dump(A/'verification.json',result)
    print(json.dumps({k:result[k] for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
