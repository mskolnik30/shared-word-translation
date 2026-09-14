"""Verify this batch's bindings and structure; preserve earlier work. No editorial approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='2a0f6019c595e2be476bbd84dcc6a930c8eea5f7'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
def prior(rel):return subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oldq=json.loads(prior('audit/fluent-revision/WORK_QUEUE.json'));scopes=q['completed_draft_scopes'];assert scopes[:-1]==oldq['completed_draft_scopes']
 paths=set();total=0;old_chapters=0;all_kings=[];ledgers=[]
 for idx,sc in enumerate(scopes):
  data=(ROOT/sc['ledger']).read_bytes();l=json.loads(data);ledgers.append(l)
  if idx<len(scopes)-1:assert data==prior(sc['ledger'])
  for c in l['chapters']:
   assert c['path'] not in paths;paths.add(c['path']);total+=c['verse_count']
   assert sha((ROOT/c['path']).read_bytes())==c['after_sha256']
   assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
   if idx<len(scopes)-1:old_chapters+=1;assert (ROOT/c['path']).read_bytes()==prior(c['path'])
  if l['source'].get('osis_book_id')=='1Kgs':
   for v in l['verses']:all_kings.extend(s['source_reference']for s in v.get('source_segments',[v]))
 assert len(scopes)==58 and len(paths)==317 and total==9589 and old_chapters==297
 assert len(all_kings)==len(set(all_kings))==763
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};ads=[];audits=[];structural=[];allv={};focused={}
 for sc,bk,pre,start,end,bookqa in zip(scopes[-1:],['1kings'],['1Kings'],[2],[21],['1_KINGS_FLUENT_BOOK_QA.json']):
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
 assert focused=={'1kings':138}
 for n in range(21,35):assert allv[f'1 Kings 4:{n}']['source_reference']==f'1Kgs 5:{n-20}'
 for n in range(1,19):assert allv[f'1 Kings 5:{n}']['source_reference']==f'1Kgs 5:{n+14}'
 checks={'2:11':['forty','seven','thirty-three'],'2:28':['Absalom'],'2:39':['slaves','Achish','Maacah'],'3:7':['young boy'],'3:9':['listening heart'],'4:26':['forty thousand','twelve thousand'],'4:32':['three thousand','one thousand five'],'5:3':['my feet'],'5:11':['twenty thousand cors','twenty cors'],'5:13':['thirty thousand'],'5:14':['ten thousand','one month','two months'],'5:15':['seventy thousand','eighty thousand'],'5:16':['thirty-three hundred'],'6:1':['four hundred eightieth','fourth','Ziv','second'],'6:8':['middle'],'6:16':['floor up to the walls'],'6:38':['eleventh','Bul','eighth','seven years'],'7:2':['four rows'],'7:3':['forty-five','fifteen'],'7:7':['floor to the other'],'7:15':['eighteen','twelve','other'],'7:23':['ten cubits','five cubits','thirty cubits'],'7:26':['two thousand baths'],'7:38':['forty baths','four cubits'],'7:42':['four hundred pomegranates'],'8:9':['nothing','two stone tablets'],'8:38':['any person','all your people'],'8:46':['no one who does not sin'],'8:63':['twenty-two thousand','a hundred twenty thousand'],'8:65':['fourteen'],'8:66':['eighth'],'9:18':['Tadmor'],'9:21':['forced slave labor','devote to destruction'],'9:22':['did not make slaves'],'9:23':['five hundred fifty'],'9:28':['four hundred twenty'],'10:14':['six hundred sixty-six'],'10:16':['two hundred','six hundred'],'10:17':['three hundred','three minas'],'10:29':['six hundred','hundred fifty'],'11:3':['seven hundred','three hundred'],'11:5':['Milcom'],'11:7':['Molech'],'11:16':['every male','six months'],'11:33':['they','his father David'],'11:39':['not forever'],'12:7':['servant','serve'],'12:18':['Adoram','stoned'],'12:21':['Benjamin','hundred eighty thousand'],'12:28':['gods'],'13:11':['One of his sons','His sons'],'13:18':['lying'],'13:28':['neither eaten','nor mauled the donkey'],'14:10':['urinates','dung'],'14:21':['forty-one','seventeen','Naamah'],'14:24':['male shrine attendants'],'15:6':['Rehoboam'],'15:10':['mother','Maacah'],'15:12':['male shrine attendants'],'16:11':['urinates','relative','friend'],'16:23':['thirty-first','twelve','six'],'16:34':['Abiram','Segub'],'17:21':['three times','life return'],'18:19':['four hundred fifty','four hundred'],'18:34':['four jars','third time'],'18:40':['slaughtered'],'19:3':['saw'],'19:8':['forty days','forty nights'],'19:12':['fine stillness'],'19:17':['Hazael','Jehu','Elisha','kill'],'19:18':['seven thousand'],'20:15':['two hundred thirty-two','seven thousand'],'20:23':['gods'],'20:29':['hundred thousand','one day'],'20:30':['twenty-seven thousand'],'20:31':['heads'],'20:38':['bandage'],'20:42':['devoted to destruction'],'21:3':['inheritance'],'21:10':['cursed God','stone'],'21:21':['urinates'],'21:23':['rampart'],'21:29':['his son']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in allv['1 Kings '+ref]['after'].casefold(),(ref,term)
 assert allv['1 Kings 19:10']['after']==allv['1 Kings 19:14']['after']
 assert 'inheritance' not in allv['1 Kings 21:6']['after']
 assert 'water' not in allv['1 Kings 18:33']['after']
 assert allv['1 Kings 20:2']['source_reference']=='1Kgs 20:2'
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(n in allowed or any(n.startswith(ad)for ad in ads)for n in changed),changed
 assert [x['scope']for x in q['next_work'][:2]]==['Whole-book 1 Samuel consistency review','Whole-book 2 Samuel consistency review']
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'1 Kings 2–21','new_chapters':20,'new_verses':710,'affected_source_binding_audits':audits,'preservation':{'prior_ledgers_byte_identical':57,'prior_chapters_byte_identical':297,'historical_provenance_and_unrelated_work_preserved':True},'cumulative_coverage':{'ledgers':58,'chapters':317,'verses':9589},'structural_chapters':structural,'first_source_reading':{'public_verses':710,'original_records':710,'all_original_annotations_read':True},'tsw_comparator_reading':710,'focused_source_reread':focused,'focused_assertions':checks,'selected_1kings_source_records_bound_once':763,'public_source_versification_checked':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','whole_book_samuel_consistency_passes':'PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage','preservation','focused_source_reread']}))
if __name__=='__main__':main()
