#!/usr/bin/env python3
"""Verify the Genesis apparatus checkpoint; not an editorial certification."""
import argparse,hashlib,json,re,subprocess,sys
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
BASE='4d1c207f3645412e01c725431cb4bfc11e2ed655'
sys.path.insert(0,str(R/'tools'))
from audit_fluent_revision import audit
from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=R)
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);args=ap.parse_args()
 d=json.loads((A/'apparatus-decisions.json').read_text());c=json.loads((A/'corrections.json').read_text());inputs=json.loads((A/'input-chapters.json').read_text());bindings=json.loads((A/'input-bindings.json').read_text())
 assert len(inputs)==50 and sorted(x['chapter'] for x in inputs)==list(range(1,51))
 assert len(d['entries'])==577
 for section,total,counts in [('Notes',337,{'KEEP':194,'REWRITE':95,'REMOVE':48}),('Vocabulary',240,{'KEEP':226,'REWRITE':14})]:
  items=[e for e in d['entries'] if e['section']==section];assert len(items)==total and dict(Counter(x['decision'] for x in items))==counts
 for ch in inputs:
  before=old(ch['path']);after=(R/ch['path']).read_bytes();assert before.decode()==ch['text'];assert sha(before)==next(x['sha256'] for x in bindings['chapters'] if x['path']==ch['path'])
  assert before.decode().split('## Notes',1)[0]==after.decode().split('## Notes',1)[0]
  assert verse_texts(before.decode())==verse_texts(after.decode())
  bnotes,bvoc=before.decode().split('## Notes',1)[1].split('## Vocabulary',1);anotes,avoc=after.decode().split('## Notes',1)[1].split('## Vocabulary',1)
  for sec,b,a in [('Notes',bnotes,anotes),('Vocabulary',bvoc,avoc)]:
   es=[x for x in d['entries'] if x['path']==ch['path'] and x['section']==sec]
   assert re.split(r'\n\s*\n',b.strip())==[e['before'] for e in es]
   assert re.split(r'\n\s*\n',a.strip())==[e['after'] for e in es if e['after'] is not None]
   for e in es:
    assert e['decision']==('REMOVE' if e['after'] is None else 'KEEP' if e['before']==e['after'] else 'REWRITE')
   for line in a.splitlines():
    if line.startswith('v'):assert not re.match(r'^v\d:',line)
  assert not re.search(r'\b(?:draft|pinned)\b|bound to.*source',anotes,re.I)
 evidence=json.loads((A/'targeted-source-evidence.json').read_text())['records'];assert len(evidence)==10 and len({e['reference'] for e in evidence})==10
 for e in evidence:
  sb=(args.sources/e['source_file']).read_bytes();assert sha(sb)==e['source_file_sha256'];m=re.search(r'<verse\b[^>]*osisID="'+re.escape(e['reference'])+r'"[^>]*>.*?</verse>',sb.decode(),re.S);assert m and m[0]==e['exact_source_record'] and sha(m[0].encode())==e['source_record_sha256']
 q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());pq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes']==pq['completed_draft_scopes'] and q['draft_coverage']==pq['draft_coverage'];assert q['next_work'][1:]==pq['next_work']
 sources={sha(p.read_bytes()):p for p in args.sources.iterdir() if p.suffix in ['.xml','.txt']};audits=[];paths=set();unchanged_ledgers=0;unchanged_chapters=0;changed={x['path']:x for x in c['chapters']}
 allowed={'FLUENT_EDITORIAL_STANDARD.md','FLUENT_READER_GUIDANCE.md','EDITORIAL_PROGRESS.json','audit/fluent-revision/WORK_QUEUE.json'}
 assert len(changed)==48 and len(c['affected_ledgers'])==8 and c['verse_changes']==[]
 for scope in q['completed_draft_scopes']:
  p=scope['ledger'];l=json.loads((R/p).read_text());pl=json.loads(old(p));assert l['source']==pl['source'] and l['base_commit']==pl['base_commit'] and l['verses']==pl['verses']
  errors=audit(R,l,sources[l['source']['sha256']].read_bytes());assert not errors,(p,errors);audits.append(dict(ledger=p,status='PASSED',chapters=len(l['chapters']),verses=len(l['verses'])))
  if p in c['affected_ledgers']:allowed.add(p)
  else:assert (R/p).read_bytes()==old(p);unchanged_ledgers+=1
  for ch in l['chapters']:
   pth=ch['path'];assert pth not in paths;paths.add(pth);before=old(pth);after=(R/pth).read_bytes();assert verse_texts(before.decode())==verse_texts(after.decode())
   if pth not in changed:assert before==after;unchanged_chapters+=1;continue
   r=changed[pth];assert sha(before)==r['before_sha256'] and sha(after)==r['after_sha256']==ch['after_sha256'];allowed.add(pth)
   cp='audit/exegetical-core/fluent-production/genesis/'+Path(pth).stem+'_review.json';allowed.add(cp);cr=json.loads((R/cp).read_text());assert cr['chapter_binding']==ch and cr['status']=='REVIEW_PENDING' and cr['publication_allowed'] is False
 assert len(paths)==1189 and len(audits)==145 and sum(x['verses'] for x in audits)==31083 and unchanged_ledgers==137 and unchanged_chapters==1141
 assert not subprocess.check_output(['git','diff',BASE,'--','books','companions'],cwd=R).strip()
 prior=R/'audit/fluent-revision/2026-09-17-full-corpus-audit'
 for x in json.loads((prior/'criteria-bindings.json').read_text()):assert sha((prior/x['file']).read_bytes())==x['sha256']
 reg=json.loads((R/'EDITORIAL_PROGRESS.json').read_text());assert len(reg['books'])==66 and sum(b['chapters'] for b in reg['books'])==1189 and reg['active_block']['full_bilingual_review_complete'] is False
 reg['criteria_status']['F10']='CURRENT_STRUCTURAL_CHECKS_PASSED; EDITORIAL_APPROVAL_NOT_CONFERRED';dump(R/'EDITORIAL_PROGRESS.json',reg)
 changedfiles=subprocess.check_output(['git','diff','--name-only',BASE],cwd=R,text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
 for p in changedfiles:assert p in allowed or p.startswith(str(A.relative_to(R))+'/'),p
 subprocess.run(['git','diff','--check',BASE],cwd=R,check=True)
 result=dict(status='PASSED',qa_scope='exact apparatus edits, source and chapter bindings, complete coverage, Scripture and comparator preservation',base_commit=BASE,cumulative_coverage=dict(chapters=1189,verses=31083,ledgers=145),source_binding_audits=audits,reviewed_apparatus=dict(chapters=50,notes=337,vocabulary=240),corrections=dict(chapters=48,notes_rewritten=95,notes_removed=48,vocabulary_revised=14,scripture_verses=0),targeted_source_records=10,preservation=dict(unchanged_chapters=1141,unchanged_ledgers=137,all_scripture_unchanged=True,tsw_unchanged=True,companion_unchanged=True,original_source_bindings_unchanged=True),full_bilingual_review_complete=False,independent_editorial_review='REVIEW_PENDING',publication_allowed=False)
 dump(A/'verification.json',result);print(json.dumps({k:v for k,v in result.items() if k!='source_binding_audits'},indent=2))
if __name__=='__main__':main()
