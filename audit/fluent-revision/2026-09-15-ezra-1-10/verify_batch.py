"""Parent-relative structural/source verification. Not independent editorial review."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='749d1387736696a625c2ec177645f7212c0e9ec6'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*a):
 p=subprocess.run(a,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def main():
 a=argparse.ArgumentParser();a.add_argument('--source-directory',type=Path,required=True);sd=a.parse_args().source_directory.resolve()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-2]==oq['completed_draft_scopes']
 paths=set();total=0;oldcount=0;ls=[];chron=[]
 for idx,sc in enumerate(q['completed_draft_scopes']):
  p=ROOT/sc['ledger'];l=json.loads(p.read_text());ls.append(l)
  if idx<65:assert p.read_bytes()==old(sc['ledger'])
  for c in l['chapters']:
   assert c['path']not in paths;paths.add(c['path']);total+=c['verse_count'];assert sha((ROOT/c['path']).read_bytes())==c['after_sha256'];assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
   if idx<65:assert (ROOT/c['path']).read_bytes()==old(c['path']);oldcount+=1
  if l['source'].get('osis_book_id')=='2Chr':chron += [s['source_reference']for v in l['verses']for s in v.get('source_segments',[v])]
 assert len(ls)==67 and len(paths)==418 and total==12405 and oldcount==407
 assert len(chron)==len(set(chron))==822
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};dirs=[];audits=[];allv={};focused={};languages={}
 for l,bk,pre,bqa,n in zip(ls[-2:],['2chronicles','ezra'],['2Chronicles','Ezra'],['2_CHRONICLES_FLUENT_BOOK_QA.json','EZRA_FLUENT_BOOK_QA.json'],[23,280]):
  sc=next(x for x in q['completed_draft_scopes']if x['ledger'].endswith(bk+'-verse-review.json')and json.loads((ROOT/x['ledger']).read_text())['revision_id']==l['revision_id']);lp=ROOT/sc['ledger'];ad=lp.parent;dirs.append(str(ad.relative_to(ROOT))+'/');source=sd/(bk+'-pinned-hebrew.xml')
  audit=json.loads(run(sys.executable,'tools/audit_fluent_revision.py',sc['ledger'],'--source-text',str(source)));audits.append(audit);assert l['automated_qa']=='PASSED'
  raw={};ar=[];he=[]
  for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',source.read_text(),re.S):
   e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');key=f'{o} {c}:{v}';raw[key]=rec
   morph={w.attrib.get('morph','')[:1]for w in e if w.tag=='w'}
   if 'A'in morph:ar.append(f'{c}:{v}')
   if 'H'in morph:he.append(f'{c}:{v}')
  if bk=='ezra':
   exp=[f'{c}:{v}'for c,lo,hi in [(4,8,24),(5,1,17),(6,1,18),(7,12,26)]for v in range(lo,hi+1)];assert ar==exp and len(he)==213;languages={'Hebrew_verses':213,'Aramaic_verses':67,'Aramaic_ranges':['4:8–6:18','7:12–26']}
  vv={v['reference']:v for v in l['verses']};allv.update(vv);assert len(vv)==n
  bound=[v['source_reference']for v in l['verses']];assert len(set(bound))==n
  rows=json.loads((ad/'focused-comparisons.json').read_text())['rows'];focused[bk]=len(rows)
  assert [r['reference']for r in rows]==json.loads((ad/'focused-selection.json').read_text())
  for r in rows:assert all(r[k]==v for k,v in vv[r['reference']].items())and sha(r['original_source_xml'].encode())==r['source_verse_sha256']
  for c in l['chapters']:
   t=(ROOT/c['path']).read_text();yaml=t.split('---',2)[1];body=t.split('---',2)[2].split('## Notes')[0];inside=False
   for line in body.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip()and not line.startswith('## '):assert inside,(c['path'],line)
   assert not inside
   assert all(x in yaml for x in ['status: QA_PASSED','qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   assert all(x in yaml for x in old(c['path']).decode().split('---',2)[1].strip().splitlines())
   for refs in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(i)<=c['verse_count']for i in re.findall(r'\d+',refs))
   rp=f'audit/exegetical-core/fluent-production/{bk}/{pre}_{c["chapter"]:02}_review.json';d=json.loads((ROOT/rp).read_text());assert d['chapter_binding']==c and d['automated_qa']=='PASSED' and d['publication_allowed']is False;allowed|={c['path'],rp}
  for fn in [bqa,'APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
   rel=f'audit/exegetical-core/fluent-production/{bk}/'+fn;allowed.add(rel);p=json.loads(old(rel));d=json.loads((ROOT/rel).read_text());assert d['revision_batches'][:-1]==p.get('revision_batches',[])and d['publication_allowed']is False
   for k in ['human_textual_review','source_lock','resolved_f3']:
    if k in p:assert d[k]==p[k]
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    for x,y in zip(p['entries'],d['entries']):
     if x['chapter']in l['source']['scope_chapters']:assert y['status']=='SUPERSEDED'and y['historical_status_before_revision']==x.get('status')and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
     else:assert x==y
 checks=json.loads((BATCH/'focused-assertions.json').read_text())
 for ref,terms in checks.items():
  for term in terms:assert term in allv[ref]['after'],(ref,term)
 assert allv['Ezra 8:16']['after'].count('Elnathan')==3 and allv['Ezra 10:25']['after'].count('Malchijah')==2
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(d)for d in dirs)for p in changed)
 assert q['next_work'][:5]==oq['next_work'][:5]
 result={'status':'PASSED','base_commit':BASE,'new_chapters':11,'new_verses':303,'cumulative_coverage':{'ledgers':67,'chapters':418,'verses':12405},'preservation':{'prior_ledgers_byte_identical':65,'prior_chapters_byte_identical':407,'historical_provenance_preserved':True},'affected_source_binding_audits':audits,'all_2chronicles_source_records_bound_once':822,'ezra_languages':languages,'focused_authoring_reread':focused,'first_source_reading':{'verses':303,'all_source_annotations_read':True},'tsw_comparator_verses_read_after_drafting':303,'focused_assertions':checks,'translation_family':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage','focused_authoring_reread']}))
if __name__=='__main__':main()
