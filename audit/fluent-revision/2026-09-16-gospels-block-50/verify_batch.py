"""Verify an intermediate eight-chapter checkpoint within a fifty-chapter block."""
from pathlib import Path
import argparse,json,hashlib,re,sys,subprocess
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;BASE='cd51fb21efb0b9967dc4fc4ccd7e5fe2bc8f5781'
sys.path.insert(0,str(R/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=R)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory
 q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-2]==oq['completed_draft_scopes'];prior=set();pv=0
 for sc in oq['completed_draft_scopes']:
  assert(R/sc['ledger']).read_bytes()==old(sc['ledger']);l=json.loads((R/sc['ledger']).read_text())
  for ch in l['chapters']:
   assert ch['path']not in prior;prior.add(ch['path']);pv+=ch['verse_count'];assert(R/ch['path']).read_bytes()==old(ch['path']);assert sha((R/ch['path']).read_bytes())==ch['after_sha256'];assert sha((R/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert(len(prior),pv)==(957,24062)
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};prefixes=[str(B.relative_to(R))+'/'];focus_count=0;vv={};summaries={}
 for b,lo,hi,N,F in [('matthew',24,28,258,37),('mark',1,3,108,27)]:
  rel=f'audit/fluent-revision/2026-09-16-{b}-{lo}-{hi}';A=R/rel;prefixes.append(rel+'/');l=json.loads((A/f'{b}-verse-review.json').read_text());sb=(sd/f'{b}-pinned-greek.txt').read_bytes();errors=audit(R,l,sb);assert not errors,errors;assert len(l['verses'])==N;raw={}
  for line in sb.decode().splitlines():
   m=re.fullmatch(r'(\S+ \d+:\d+)\t(.*)',line)
   if m:raw[m[1]]=m[2]
  byref={v['reference']:v for v in l['verses']};vv.update(byref)
  assert len({v['source_reference']for v in l['verses']})==N
  for v in l['verses']:assert sha(raw[v['source_reference']].encode())==v['source_verse_sha256']and v['rationale'].strip()
  f=json.loads((A/'focused-comparisons.json').read_text());sel=json.loads((A/'focused-selection.json').read_text());assert f['status']=='AUTHORING_REREAD_COMPLETED'and len(sel)==F;assert sel==[v['reference']for v in f['rows']];focus_count+=len(sel)
  for v in f['rows']:assert all(v[k]==x for k,x in byref[v['reference']].items())and v['exact_source_record']==raw[v['source_reference']]
  for ch in l['chapters']:
   assert ch['path']not in prior;allowed.add(ch['path']);t=(R/ch['path']).read_text();body=t.split('## Notes')[0];assert '\\'not in body and '## Vocabulary'not in body;inside=False
   for line in body.split('---',2)[2].splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip()and not line.startswith('## '):assert inside,(ch['path'],line)
   assert not inside
   for ref in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(x)<=ch['verse_count']for x in re.findall(r'\d+',ref)),ref
   rp=f'audit/exegetical-core/fluent-production/{b}/{b.title()}_{ch["chapter"]:02}_review.json';allowed.add(rp);d=json.loads((R/rp).read_text());assert d['chapter_binding']==ch and d['status']=='REVIEW_PENDING'and d['publication_allowed']is False
  for fn in [b.upper()+'_FLUENT_BOOK_QA.json',b.upper()+'_SOURCE_BINDINGS.json']:
   rp=f'audit/exegetical-core/fluent-production/{b}/{fn}';allowed.add(rp);d=json.loads((R/rp).read_text());od=json.loads(old(rp));assert d['publication_allowed']is False and d['status']=='REVIEW_PENDING';assert d['revision_batches'][:-1]==od.get('revision_batches',[]);assert d['source']==od['source']
   if b=='mark'and fn.endswith('SOURCE_BINDINGS.json'):assert d['bindings']==od['bindings']
  summaries[b]=l['summary']
 # Concrete source-sensitive regressions found in this authoring pass.
 assert 'apostles'not in vv['Mark 3:14']['after'].lower();assert 'ἀποστόλους'not in raw.get('Mark 3:14','')
 assert 'anger'in vv['Mark 1:41']['after']and 'Jesus Barabbas'in vv['Matthew 27:16']['after']and 'nor the Son'in vv['Matthew 24:36']['after']
 assert vv['Matthew 25:15']['after'].endswith('At once,')and vv['Matthew 25:16']['after'].startswith('the servant');assert 'Jesus’ resurrection'in vv['Matthew 27:53']['after']
 assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:];block=q['active_fifty_chapter_block'];assert(block['status'],block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==('IN_PROGRESS',8,42,366)
 cumulative=[c for sc in q['completed_draft_scopes']for c in json.loads((R/sc['ledger']).read_text())['chapters']];assert len(q['completed_draft_scopes'])==108 and len(cumulative)==965 and sum(c['verse_count']for c in cumulative)==24428
 changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=R).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R).decode().splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),[p for p in changed if p not in allowed and not any(p.startswith(x)for x in prefixes)]
 assert not subprocess.check_output(['git','diff',BASE,'--','books'],cwd=R).strip();subprocess.run(['git','diff','--check'],cwd=R,check=True);family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=R).decode()
 result={'status':'PASSED','base_commit':BASE,'new_chapters':8,'new_verses':366,'cumulative_coverage':{'ledgers':108,'chapters':965,'verses':24428},'prior_preservation':{'ledgers_byte_identical':106,'chapters_byte_identical':957,'verses':24062,'tsw_and_companion_unchanged':True},'source_binding_audit':'PASSED both ledgers and all 366 source records','focused_authoring_reread':focus_count,'source_reading':'All 366 Greek records read before authoring. Prior Fluent consulted after source reading for Matthew24–25; other chapters drafted before reading prior Fluent. TSW compared after authoring.','summaries':summaries,'translation_family':family,'block_progress':block,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False};(B/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
