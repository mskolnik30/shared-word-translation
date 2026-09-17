#!/usr/bin/env python3
"""Verify this audit's exact corrections; no editorial certification."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
BASE='dc09c88b7080e042e915474fe50e92f56adeee3c'
sys.path.insert(0,str(R/'tools'))
from audit_fluent_revision import audit
from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=R)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);a=ap.parse_args()
 c=json.loads((A/'corrections.json').read_text());q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'))
 assert q['completed_draft_scopes']==oq['completed_draft_scopes'] and q['draft_coverage']==oq['draft_coverage']
 assert q['next_work'][1:]==oq['next_work']
 changes={x['path']:x for x in c['chapters']};assert len(changes)==31 and len(c['verse_changes'])==2
 sources={sha(p.read_bytes()):p for p in a.sources.iterdir() if p.suffix in ['.xml','.txt']}
 audits=[];paths=set();actual_versechanges=[];unchanged_ledgers=0;unchanged_chapters=0;allowed={'audit/fluent-revision/WORK_QUEUE.json'}
 for item in q['completed_draft_scopes']:
  p=item['ledger'];l=json.loads((R/p).read_text());previous=json.loads(old(p));assert l['source']==previous['source'] and l['base_commit']==previous['base_commit']
  sp=sources[l['source']['sha256']];errors=audit(R,l,sp.read_bytes());assert not errors,(p,errors)
  audits.append(dict(ledger=p,status='PASSED',chapters=len(l['chapters']),verses=len(l['verses'])))
  if p in c['affected_ledgers']:allowed.add(p)
  else:assert (R/p).read_bytes()==old(p);unchanged_ledgers+=1
  for ch in l['chapters']:
   pth=ch['path'];assert pth not in paths;paths.add(pth);b=old(pth);n=(R/pth).read_bytes()
   if pth not in changes:assert b==n;unchanged_chapters+=1;continue
   d=changes[pth];assert sha(b)==d['before_sha256'] and sha(n)==d['after_sha256']==ch['after_sha256'];allowed.add(pth)
   cp='audit/exegetical-core/fluent-production/'+Path(pth).parts[-2]+'/'+Path(pth).stem+'_review.json';allowed.add(cp);cr=json.loads((R/cp).read_text());assert cr['chapter_binding']==ch and cr['status']=='REVIEW_PENDING' and cr['publication_allowed'] is False
   bv,nv=verse_texts(b.decode()),verse_texts(n.decode());assert list(bv)==list(nv)
   for label in bv:
    if bv[label]!=nv[label]:actual_versechanges.append((pth,int(label),bv[label],nv[label]))
  for v,pv in zip(l['verses'],previous['verses']):
   for key in ['reference','before','source_reference','source_verse_sha256','tsw_comparator','delta','rationale']:
    assert v[key]==pv[key],(p,v['reference'],key)
 assert len(paths)==1189 and len(audits)==145 and sum(x['verses'] for x in audits)==31083
 expected={(v['path'],int(v['reference'].split(':')[-1]),v['before'],v['after']) for v in c['verse_changes']};assert set(actual_versechanges)==expected
 assert unchanged_ledgers==128 and unchanged_chapters==1158
 assert not subprocess.check_output(['git','diff',BASE,'--','books','companions'],cwd=R).strip()
 for x in json.loads((A/'criteria-bindings.json').read_text()):assert sha((A/x['file']).read_bytes())==x['sha256']
 summary=json.loads((A/'after/summary.json').read_text());assert summary['binding_errors']==0 and not summary['family_errors'] and summary['chapters']==1189 and summary['verses']==31083
 changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=R,text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
 for p in changed:assert p in allowed or p.startswith(str(A.relative_to(R))+'/'),p
 subprocess.run(['git','diff','--check',BASE],cwd=R,check=True)
 result=dict(status='PASSED',qa_scope='source bindings, structural checks, exact corrections and preservation only',base_commit=BASE,cumulative_coverage=dict(chapters=1189,verses=31083,ledgers=145),source_binding_audits=audits,corrections=dict(chapters=31,scripture_verses=2,joined_paragraph_boundaries=24),preservation=dict(unchanged_chapters=unchanged_chapters,unchanged_ledgers=unchanged_ledgers,tsw_unchanged=True,companion_unchanged=True,original_source_bindings_unchanged=True),targeted_source_comparisons=103,audit_judgment='DISTINCT_FROM_TSW; EDITORIAL_COMPLIANCE_REQUIRES_FURTHER_WORK',independent_editorial_review='REVIEW_PENDING',publication_allowed=False)
 (A/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_binding_audits'},indent=2))
if __name__=='__main__':main()
