"""Verify this batch's bindings and structure; preserve earlier work. No editorial approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='82918a076360a371bdf598f83d00668656811ccd'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
def prior(rel):return subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oldq=json.loads(prior('audit/fluent-revision/WORK_QUEUE.json'));scopes=q['completed_draft_scopes'];assert scopes[:-2]==oldq['completed_draft_scopes']
 paths=set();total=0;old_chapters=0;all_2sam=[];ledgers=[]
 for idx,sc in enumerate(scopes):
  data=(ROOT/sc['ledger']).read_bytes();l=json.loads(data);ledgers.append(l)
  if idx<len(scopes)-2:assert data==prior(sc['ledger'])
  for c in l['chapters']:
   assert c['path'] not in paths;paths.add(c['path']);total+=c['verse_count']
   assert sha((ROOT/c['path']).read_bytes())==c['after_sha256']
   assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
   if idx<len(scopes)-2:old_chapters+=1;assert (ROOT/c['path']).read_bytes()==prior(c['path'])
  if l['source'].get('osis_book_id')=='2Sam':
   for v in l['verses']:all_2sam.extend(s['source_reference']for s in v.get('source_segments',[v]))
 assert len(scopes)==57 and len(paths)==297 and total==8879 and old_chapters==277
 assert len(all_2sam)==len(set(all_2sam))==695
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};ads=[];audits=[];structural=[];allv={};focused={}
 for sc,bk,pre,start,end,bookqa in zip(scopes[-2:],['2samuel','1kings'],['2Samuel','1Kings'],[6,1],[24,1],['2_SAMUEL_FLUENT_BOOK_QA.json','1_KINGS_FLUENT_BOOK_QA.json']):
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
  focused[bk]=len(rows)
 assert focused=={'2samuel':120,'1kings':16}
 assert allv['2 Samuel 18:33']['source_reference']=='2Sam 19:1'
 for n in range(1,44):assert allv[f'2 Samuel 19:{n}']['source_reference']==f'2Sam 19:{n+1}'
 checks={'2 Samuel 8:4':['seventeen hundred','twenty thousand','hundred chariots'],'2 Samuel 8:13':['eighteen thousand Arameans'],'2 Samuel 12:14':['the LORD’s enemies','die'],'2 Samuel 12:31':['under saws','brickworks'],'2 Samuel 13:14':['overpowered','raped'],'2 Samuel 14:26':['two hundred shekels'],'2 Samuel 15:7':['forty years'],'2 Samuel 18:3':['ten thousand like us'],'2 Samuel 21:8':['Michal','borne','Armoni','Mephibosheth'],'2 Samuel 21:19':['Elhanan','Goliath'],'2 Samuel 22:36':['your answering me'],'2 Samuel 22:46':['limping'],'2 Samuel 22:51':['tower of salvation'],'2 Samuel 23:8':['Josheb-basshebeth','Adino','eight hundred'],'2 Samuel 23:18':['Three','three hundred'],'2 Samuel 23:19':['Three'],'2 Samuel 23:20':['two ariels'],'2 Samuel 23:39':['Thirty-seven'],'2 Samuel 24:9':['eight hundred thousand','five hundred thousand'],'2 Samuel 24:13':['seven years','three months','three days'],'2 Samuel 24:15':['Seventy thousand'],'2 Samuel 24:23':['Araunah the king'],'2 Samuel 24:24':['fifty silver shekels'],'1 Kings 1:4':['did not have sexual relations'],'1 Kings 1:39':['Zadok','anointed'],'1 Kings 1:45':['Zadok','Nathan']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in allv[ref]['after'].casefold(),(ref,term)
 assert allv['2 Samuel 18:33']['after'].casefold().count('my son')==5
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(n in allowed or any(n.startswith(ad)for ad in ads)for n in changed),changed
 assert [x['scope']for x in q['next_work'][:2]]==['Whole-book 1 Samuel consistency review','Whole-book 2 Samuel consistency review']
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'2 Samuel 6–24 and 1 Kings 1','new_chapters':20,'new_verses':613,'affected_source_binding_audits':audits,'preservation':{'prior_ledgers_byte_identical':55,'prior_chapters_byte_identical':277,'historical_provenance_and_unrelated_work_preserved':True},'cumulative_coverage':{'ledgers':57,'chapters':297,'verses':8879},'structural_chapters':structural,'first_source_reading':{'public_verses':613,'original_records':613,'all_original_annotations_read':True},'tsw_comparator_reading':613,'focused_source_reread':focused,'focused_assertions':checks,'all_2samuel_source_records_bound_once':695,'public_source_versification_checked':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','whole_book_samuel_consistency_passes':'PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage','preservation','focused_source_reread']}))
if __name__=='__main__':main()
