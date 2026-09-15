"""Verify this batch's bindings and structure; preserve earlier work. No editorial approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='89f0893c0abd136c80d4a194ca42b090ae6f6274'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
def prior(rel):return subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oldq=json.loads(prior('audit/fluent-revision/WORK_QUEUE.json'));scopes=q['completed_draft_scopes'];assert scopes[:-2]==oldq['completed_draft_scopes']
 paths=set();total=0;old_chapters=0;all_chronicles=[];ledgers=[]
 for idx,sc in enumerate(scopes):
  data=(ROOT/sc['ledger']).read_bytes();l=json.loads(data);ledgers.append(l)
  if idx<len(scopes)-2:assert data==prior(sc['ledger'])
  for c in l['chapters']:
   assert c['path'] not in paths;paths.add(c['path']);total+=c['verse_count']
   assert sha((ROOT/c['path']).read_bytes())==c['after_sha256']
   assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
   if idx<len(scopes)-2:old_chapters+=1;assert (ROOT/c['path']).read_bytes()==prior(c['path'])
  if l['source'].get('osis_book_id')=='1Chr':
   for v in l['verses']:all_chronicles.extend(s['source_reference']for s in v.get('source_segments',[v]))
 assert len(scopes)==63 and len(paths)==377 and total==11391 and old_chapters==347
 assert len(all_chronicles)==len(set(all_chronicles))==943
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};ads=[];audits=[];structural=[];allv={};focused={}
 for sc,bk,pre,start,end,bookqa in zip(scopes[-2:],['1chronicles','2chronicles'],['1Chronicles','2Chronicles'],[5,1],[29,5],['1_CHRONICLES_FLUENT_BOOK_QA.json','2_CHRONICLES_FLUENT_BOOK_QA.json']):
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
  assert len(bound)=={'1chronicles':767,'2chronicles':88}[bk]
  focused[bk]=len(rows)
 assert focused=={'1chronicles':225,'2chronicles':44}
 for n in range(1,16):assert allv[f'1 Chronicles 6:{n}']['source_reference']==f'1Chr 5:{n+26}'
 for n in range(16,82):assert allv[f'1 Chronicles 6:{n}']['source_reference']==f'1Chr 6:{n-15}'
 assert [x['source_reference']for x in allv['1 Chronicles 12:4']['source_segments']]==['1Chr 12:4','1Chr 12:5']
 for n in range(5,41):assert allv[f'1 Chronicles 12:{n}']['source_reference']==f'1Chr 12:{n+1}'
 assert allv['2 Chronicles 2:1']['source_reference']=='2Chr 1:18'
 for n in range(2,19):assert allv[f'2 Chronicles 2:{n}']['source_reference']==f'2Chr 2:{n-1}'
 checks=json.loads((BATCH/'focused-assertions.json').read_text())
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in allv[ref]['after'].casefold(),(ref,term)
 assert 'twenty cubits high' not in allv['2 Chronicles 4:1']['after']
 assert 'Gibeah' not in allv['1 Chronicles 6:60']['after']
 assert 'Shitrai' not in allv['1 Chronicles 27:29']['after']
 assert 'his sons' not in allv['1 Chronicles 24:23']['after']
 for c,lo,hi in [(12,18,18),(16,8,36)]:
  text=(ROOT/f'translations/fluent/OT/1chronicles/1Chronicles_{c:02}.md').read_text()
  for v in range(lo,hi+1):
   verse=re.search(rf'^v{v:02}: (.*?)(?=^v\d+:|^</p>)',text,re.M|re.S).group(1)
   assert '\n' in verse.rstrip(),(c,v,'poetry lineation')
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(n in allowed or any(n.startswith(ad)for ad in ads)for n in changed),changed
 assert [x['scope']for x in q['next_work'][:4]]==['Whole-book 1 Samuel consistency review','Whole-book 2 Samuel consistency review','Whole-book 1 Kings consistency review','Whole-book 2 Kings consistency review']
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'1 Chronicles 5–29; 2 Chronicles 1–5','new_chapters':30,'new_verses':854,'affected_source_binding_audits':audits,'preservation':{'prior_ledgers_byte_identical':61,'prior_chapters_byte_identical':347,'historical_provenance_and_unrelated_work_preserved':True},'cumulative_coverage':{'ledgers':63,'chapters':377,'verses':11391},'structural_chapters':structural,'first_source_reading':{'public_verses':854,'original_records':855,'all_original_annotations_read':True},'tsw_comparator_reading':854,'focused_source_reread':focused,'focused_assertions':checks,'whole_1chronicles_source_records_bound_once':943,'selected_2chronicles_source_records_bound_once':88,'public_source_versification_checked':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','whole_book_samuel_kings_and_1chronicles_consistency_passes':'PENDING','reader_testing':'PENDING','publication_allowed':False}

 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage','preservation','focused_source_reread']}))
if __name__=='__main__':main()
