#!/usr/bin/env python3
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent;BASE='7caadac15c6cc7c76534069dd1d7d936d98f69a1'
sys.path.insert(0,str(R/'tools'))
from audit_fluent_revision import audit
from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=R)
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);args=ap.parse_args();c=json.loads((A/'corrections.json').read_text());sr=json.loads((A/'source-review.json').read_text());pr=json.loads((A/'priority-review.json').read_text())
 assert len(sr['records'])==267 and len({v['reference'] for v in sr['records']})==267 and len(pr['records'])==15
 sb=(args.sources/sr['source_file']).read_bytes();assert sha(sb)==sr['source_file_sha256']==pr['source_file_sha256']
 for v in sr['records']+pr['records']:
  ch,n=map(int,v['reference'].split()[1].split(':'));m=re.search(r'<verse\b[^>]*osisID="Gen\.'+str(ch)+r'\.'+str(n)+r'"[^>]*>.*?</verse>',sb.decode(),re.S);assert m and m[0]==v['exact_source_record'] and sha(m[0].encode())==v['source_verse_sha256']
  p=f'translations/fluent/OT/genesis/Genesis_{ch:02}.md';actual=verse_texts((R/p).read_text())[f'{n:02}']
  if v in sr['records']:assert v['before']==verse_texts(old(p).decode())[f'{n:02}'] and v['after']==actual
  else:assert v['fluent']==f'v{n:02}: '+actual
 q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());pq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes']==pq['completed_draft_scopes'] and q['draft_coverage']==pq['draft_coverage'];assert q['next_work'][1:]==pq['next_work'][1:]
 changed={x['path']:x for x in c['chapters']};expected={(v['path'],int(v['reference'].split(':')[-1]),v['before'],v['after']) for v in c['verse_changes']};assert len(changed)==4 and len(expected)==6 and len(c['affected_ledgers'])==1
 sources={sha(p.read_bytes()):p for p in args.sources.iterdir() if p.suffix in ['.xml','.txt']};audits=[];paths=set();actualchanges=[];allowed={'EDITORIAL_PROGRESS.json','audit/fluent-revision/WORK_QUEUE.json'};unchanged_ledgers=0;unchanged_chapters=0
 for scope in q['completed_draft_scopes']:
  p=scope['ledger'];l=json.loads((R/p).read_text());pl=json.loads(old(p));assert l['source']==pl['source'] and l['base_commit']==pl['base_commit']
  errors=audit(R,l,sources[l['source']['sha256']].read_bytes());assert not errors,(p,errors);audits.append(dict(ledger=p,status='PASSED',chapters=len(l['chapters']),verses=len(l['verses'])))
  if p in c['affected_ledgers']:allowed.add(p)
  else:assert (R/p).read_bytes()==old(p);unchanged_ledgers+=1
  for v,pv in zip(l['verses'],pl['verses']):
   for k in ['reference','before','source_reference','source_verse_sha256','tsw_comparator','delta','rationale']:assert v[k]==pv[k],(v['reference'],k)
   if v['reference'] not in {e['reference'] for e in c['verse_changes']}:assert v==pv
  for ch in l['chapters']:
   pth=ch['path'];assert pth not in paths;paths.add(pth);b=old(pth);n=(R/pth).read_bytes()
   if pth not in changed:assert b==n;unchanged_chapters+=1;continue
   rec=changed[pth];assert sha(b)==rec['before_sha256'] and sha(n)==rec['after_sha256']==ch['after_sha256'];allowed.add(pth)
   assert b.decode().split('## Notes',1)[1]==n.decode().split('## Notes',1)[1]
   bv,nv=verse_texts(b.decode()),verse_texts(n.decode());assert list(bv)==list(nv)
   for label in bv:
    if bv[label]!=nv[label]:actualchanges.append((pth,int(label),bv[label],nv[label]))
   cp='audit/exegetical-core/fluent-production/genesis/'+Path(pth).stem+'_review.json';allowed.add(cp);cr=json.loads((R/cp).read_text());assert cr['chapter_binding']==ch and cr['status']=='REVIEW_PENDING' and cr['publication_allowed'] is False
 assert len(paths)==1189 and len(audits)==145 and sum(x['verses'] for x in audits)==31083 and unchanged_ledgers==144 and unchanged_chapters==1185 and set(actualchanges)==expected
 assert not subprocess.check_output(['git','diff',BASE,'--','books','companions'],cwd=R).strip()
 reg=json.loads((R/'EDITORIAL_PROGRESS.json').read_text());assert len(reg['books'])==66 and reg['active_block']['source_reviewed_chapters']==list(range(1,11)) and reg['active_block']['next_source_chapter']==11 and reg['active_block']['full_bilingual_review_complete'] is False
 reg['criteria_status']['F10']='CURRENT_STRUCTURAL_CHECKS_PASSED; EDITORIAL_APPROVAL_NOT_CONFERRED';dump(R/'EDITORIAL_PROGRESS.json',reg)
 actualfiles=subprocess.check_output(['git','diff','--name-only',BASE],cwd=R,text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
 for p in actualfiles:assert p in allowed or p.startswith(str(A.relative_to(R))+'/'),p
 subprocess.run(['git','diff','--check',BASE],cwd=R,check=True)
 result=dict(status='PASSED',base_commit=BASE,qa_scope='source/verse/chapter bindings and exact corrections; not independent language review',cumulative_coverage=dict(chapters=1189,verses=31083,ledgers=145),source_binding_audits=audits,source_review=dict(complete_chapters=10,verses=267,additional_targeted_verses=15,independent_review=False),corrections=dict(chapters=4,scripture_verses=6),preservation=dict(unchanged_chapters=1185,unchanged_ledgers=144,tsw_unchanged=True,companion_unchanged=True,apparatus_unchanged=True,original_source_bindings_unchanged=True),full_genesis_review_complete=False,independent_editorial_review='REVIEW_PENDING',publication_allowed=False)
 dump(A/'verification.json',result);print(json.dumps({k:v for k,v in result.items() if k!='source_binding_audits'},indent=2))
if __name__=='__main__':main()
