"""Verify this batch's bindings and structure; preserve earlier work. No editorial approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='f7f1fd7eb2d7534b8667a1d243746b3d28b915f0'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
def prior(rel):return subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oldq=json.loads(prior('audit/fluent-revision/WORK_QUEUE.json'));scopes=q['completed_draft_scopes'];assert scopes[:-3]==oldq['completed_draft_scopes']
 paths=set();total=0;old_chapters=0;all_kings=[];ledgers=[]
 for idx,sc in enumerate(scopes):
  data=(ROOT/sc['ledger']).read_bytes();l=json.loads(data);ledgers.append(l)
  if idx<len(scopes)-3:assert data==prior(sc['ledger'])
  for c in l['chapters']:
   assert c['path'] not in paths;paths.add(c['path']);total+=c['verse_count']
   assert sha((ROOT/c['path']).read_bytes())==c['after_sha256']
   assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
   if idx<len(scopes)-3:old_chapters+=1;assert (ROOT/c['path']).read_bytes()==prior(c['path'])
  if l['source'].get('osis_book_id')=='1Kgs':
   for v in l['verses']:all_kings.extend(s['source_reference']for s in v.get('source_segments',[v]))
 assert len(scopes)==61 and len(paths)==347 and total==10537 and old_chapters==317
 assert len(all_kings)==len(set(all_kings))==817
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};ads=[];audits=[];structural=[];allv={};focused={}
 for sc,bk,pre,start,end,bookqa in zip(scopes[-3:],['1kings','2kings','1chronicles'],['1Kings','2Kings','1Chronicles'],[22,1,1],[22,25,4],['1_KINGS_FLUENT_BOOK_QA.json','2_KINGS_FLUENT_BOOK_QA.json','1_CHRONICLES_FLUENT_BOOK_QA.json']):
  lp=ROOT/sc['ledger'];ad=lp.parent;ads.append(str(ad.relative_to(ROOT))+'/');l=json.loads(lp.read_text());vv={v['reference']:v for v in l['verses']};allv.update(vv)
  audits.append({'ledger':sc['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',sc['ledger'],'--source-text',str(sd/(bk+'-pinned-hebrew.xml'))))})
  rd=f'audit/exegetical-core/fluent-production/{bk}/'
  for c in l['chapters']:
   t=(ROOT/c['path']).read_text();yaml=t.split('---',2)[1];body=t.split('---',2)[2].split('## Notes')[0];inside=False
   for line in body.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['path'],line)
   assert not inside
   assert all(s in yaml for s in ['status: QA_PASSED','qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   assert all(s in yaml for s in prior(c['path']).decode().split('---',2)[1].strip().splitlines())
   for refs in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):
    for n in re.findall(r'\d+',refs):assert 1<=int(n)<=c['verse_count']
   rp=rd+f'{pre}_{c["chapter"]:02}_review.json';rv=json.loads((ROOT/rp).read_text());assert rv['chapter_binding']==c and rv['publication_allowed'] is False and rv['status']=='REVIEW_PENDING' and rv['automated_qa']=='PASSED';allowed|={c['path'],rp};structural.append(c)
  for fn in [bookqa,'APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
   rel=rd+fn;allowed.add(rel);a=json.loads(prior(rel));b=json.loads((ROOT/rel).read_text());assert b['publication_allowed'] is False and b['current_revision']['editorial_status']=='REVIEW_PENDING';assert b['revision_batches'][:-1]==a.get('revision_batches',[])
   for k in ['human_textual_review','source_lock','resolved_f3']:
    if k in a:assert b[k]==a[k]
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(a['entries'])==len(b['entries'])
    for x,y in zip(a['entries'],b['entries']):
     if not start<=x['chapter']<=end:assert x==y
     else:assert all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by']) and y['status']=='SUPERSEDED' and y['historical_status_before_revision']==x.get('status')
  raw={}
  for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/(bk+'-pinned-hebrew.xml')).read_text(),re.S):
   e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');raw[f'{o} {int(c)}:{int(v)}']=rec
  rows=json.loads((ad/'focused-comparisons.json').read_text())['rows'];selected=json.loads((ad/'focused-selection.json').read_text());assert [v['reference']for v in rows]==selected
  for v in rows:
   orig=vv[v['reference']];assert all(v[k]==val for k,val in orig.items());assert sha(raw[v['source_reference']].encode())==v['source_verse_sha256']
   for seg in v.get('source_segments',[v]):assert sha(raw[seg['source_reference']].encode())==seg['source_verse_sha256']
  bound=[seg['source_reference']for v in l['verses']for seg in v.get('source_segments',[v])];assert len(bound)==len(set(bound))
  assert len(bound)=={'1kings':54,'2kings':719,'1chronicles':176}[bk]
  focused[bk]=len(rows)
 assert focused=={'1kings':20,'2kings':200,'1chronicles':44}
 assert [s['source_reference']for s in allv['1 Kings 22:43']['source_segments']]==['1Kgs 22:43','1Kgs 22:44']
 for n in range(44,54):assert allv[f'1 Kings 22:{n}']['source_reference']==f'1Kgs 22:{n+1}'
 assert allv['1 Kings 22:21']['source_reference']=='1Kgs 22:21'
 assert allv['2 Kings 11:21']['source_reference']=='2Kgs 12:1'
 for n in range(1,22):assert allv[f'2 Kings 12:{n}']['source_reference']==f'2Kgs 12:{n+1}'
 checks=json.loads((BATCH/'focused-assertions.json').read_text())
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in allv[ref]['after'].casefold(),(ref,term)
 assert 'fourth' not in allv['2 Kings 25:3']['after'].casefold()
 assert 'ashtoreth' not in allv['2 Kings 23:7']['after'].casefold()
 assert 'the descendants of abraham' not in allv['1 Chronicles 1:27']['after'].casefold()
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(n in allowed or any(n.startswith(ad)for ad in ads)for n in changed),changed
 assert [x['scope']for x in q['next_work'][:2]]==['Whole-book 1 Samuel consistency review','Whole-book 2 Samuel consistency review']
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'1 Kings 22; 2 Kings 1–25; 1 Chronicles 1–4','new_chapters':30,'new_verses':948,'affected_source_binding_audits':audits,'preservation':{'prior_ledgers_byte_identical':58,'prior_chapters_byte_identical':317,'historical_provenance_and_unrelated_work_preserved':True},'cumulative_coverage':{'ledgers':61,'chapters':347,'verses':10537},'structural_chapters':structural,'first_source_reading':{'public_verses':948,'original_records':949,'all_original_annotations_read':True},'tsw_comparator_reading':948,'focused_source_reread':focused,'focused_assertions':checks,'whole_1kings_source_records_bound_once':817,'whole_2kings_source_records_bound_once':719,'selected_1chronicles_source_records_bound_once':176,'public_source_versification_checked':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','whole_book_samuel_and_kings_consistency_passes':'PENDING','reader_testing':'PENDING','publication_allowed':False}

 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage','preservation','focused_source_reread']}))
if __name__=='__main__':main()
