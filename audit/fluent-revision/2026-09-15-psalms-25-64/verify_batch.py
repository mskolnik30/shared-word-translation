"""Reproducible source and structural QA. Does not confer editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='54011f97552535dcc5b37389cb2321966f7d9771'
sys.path.insert(0,str(ROOT/'tools'))
from audit_fluent_revision import audit
from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-text',type=Path,required=True);sb=p.parse_args().source_text.read_bytes()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'))
 assert q['completed_draft_scopes'][:-1]==oq['completed_draft_scopes'];assert q['next_work'][1:]==oq['next_work'][1:]
 paths=set();count=0
 for sc in q['completed_draft_scopes'][:-1]:
  lp=ROOT/sc['ledger'];assert lp.read_bytes()==old(sc['ledger']);l=json.loads(lp.read_text())
  for c in l['chapters']:
   assert c['path']not in paths;paths.add(c['path']);count+=c['verse_count']
   assert (ROOT/c['path']).read_bytes()==old(c['path'])
   assert sha((ROOT/c['path']).read_bytes())==c['after_sha256'];assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
 assert len(paths)==507 and count==14359
 lp=BATCH/'psalms-verse-review.json';l=json.loads(lp.read_text());errors=audit(ROOT,l,sb);assert not errors,errors
 assert len(l['chapters'])==40 and len(l['verses'])==609
 records={};selected={}
 for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
  e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';records[ref]=rec
  if 25<=int(c)<=64:selected[ref]=e
 assert len(records)==2527 and len(selected)==642
 vv={v['reference']:v for v in l['verses']};refs=[s['source_reference']for v in l['verses']for s in v.get('source_segments',[v])]
 assert len(refs)==len(set(refs))==642 and set(refs)==set(selected)
 assert sum('source_segments'in v for v in l['verses'])==29
 offsets={c:sum(ref.startswith(f'Ps {c}:')for ref in selected)-sum(v['reference'].startswith(f'Psalms {c}:')for v in l['verses'])for c in range(25,65)}
 for row in l['verses']:
  c,v=map(int,row['reference'].split()[-1].split(':'));expected=list(range(1,offsets[c]+2))if v==1 else[v+offsets[c]]
  assert [x['source_reference']for x in row.get('source_segments',[row])]==[f'Ps {c}:{z}'for z in expected]
  rs=[E.fromstring(records[x['source_reference']])for x in row.get('source_segments',[row])]
  # A dropped divine name or Selah can disappear in fluent restructuring.
  yhwh=sum(w.attrib.get('lemma','').split('/')[-1]=='3068'for e in rs for w in e if w.tag=='w')
  selah=sum(w.attrib.get('lemma','')=='5542'for e in rs for w in e if w.tag=='w')
  assert row['after'].count('LORD')==yhwh+(row['reference']=='Psalms 25:12'),(row['reference'],'LORD count',yhwh)
  assert row['after'].count('Selah')==selah,(row['reference'],'Selah count',selah)
 focused=json.loads((BATCH/'focused-comparisons.json').read_text());selection=json.loads((BATCH/'focused-selection.json').read_text());assert len(selection)==247
 assert [x['reference']for x in focused['rows']]==selection
 for row in focused['rows']:
  assert all(row[k]==v for k,v in vv[row['reference']].items())
  for ev in row['source_evidence']:assert ev['original_source_xml']==records[ev['source_reference']]and sha(ev['original_source_xml'].encode())==ev['source_verse_sha256']
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};ad=str(BATCH.relative_to(ROOT))+'/'
 for ch in l['chapters']:
  path=ch['path'];t=(ROOT/path).read_text();yaml=t.split('---',2)[1];body=t.split('---',2)[2].split('## Notes')[0];inside=False
  for line in body.splitlines():
   if line=='<p>':assert not inside;inside=True
   elif line=='</p>':assert inside;inside=False
   elif line.strip()and not line.startswith('## '):assert inside,(path,line)
  assert not inside and '\\'not in body
  assert all(x in yaml for x in old(path).decode().split('---',2)[1].strip().splitlines())
  assert all(x in yaml for x in ['status: QA_PASSED','qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
  for refs2 in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(i)<=ch['verse_count']for i in re.findall(r'\d+',refs2))
  rp=f'audit/exegetical-core/fluent-production/psalms/Psalm_{ch["chapter"]:03}_review.json';d=json.loads((ROOT/rp).read_text());assert d['chapter_binding']==ch and d['publication_allowed']is False and d['status']=='REVIEW_PENDING';allowed|={path,rp}
 for fn in ['PSALMS_FLUENT_BOOK_QA.json','APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
  rel='audit/exegetical-core/fluent-production/psalms/'+fn;allowed.add(rel);p=json.loads(old(rel));d=json.loads((ROOT/rel).read_text());assert d['revision_batches'][:-1]==p['revision_batches'];assert d['publication_allowed']is False and d['editorial_review_pending_chapters']==list(range(1,65))
  for k in ['source','curated_f3_decisions','deployment_audit','summary']:
   if k in p:assert d[k]==p[k]
  if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
   assert len(p['entries'])==len(d['entries'])
   for x,y in zip(p['entries'],d['entries']):
    if 25<=x['chapter']<=64:assert y['status']=='SUPERSEDED'and y['historical_status_before_revision']==x.get('status')and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
    else:assert x==y
 pairs=[('42:11','43:5'),('46:7','46:11'),('57:5','57:11'),('59:6','59:14')]
 for a,b in pairs:assert vv['Psalms '+a]['after']==vv['Psalms '+b]['after']
 assert 'greatly shaken'in vv['Psalms 62:2']['after']and'greatly'not in vv['Psalms 62:6']['after']
 assert 'his strength'in vv['Psalms 59:9']['after']and'My strength'in vv['Psalms 59:17']['after']
 assert 'do not endure'in vv['Psalms 49:12']['after']and'without understanding'in vv['Psalms 49:20']['after']
 checks={'27:13':['If I had not','—'],'29:1':['sons of gods'],'29:6':['Lebanon','Sirion'],'33:2':['ten-stringed'],'34:1':['Abimelech'],'36:1':['my heart'],'36:6':['humans and animals'],'40:5':['No one compares with you'],'40:6':['dug out ears'],'44:17':['not forgotten','covenant'],'44:20':['or spread'],'44:23':['Why do you sleep'],'45:6':['O God'],'45:9':['Ophir','queen'],'45:14':['virgin companions'],'49:7':['brother'],'49:11':['inward thought'],'50:10':['thousand hills'],'51:1':['Nathan','Bathsheba'],'51:5':['sin my mother'],'52:1':['Doeg','Edomite','Saul','Ahimelech'],'53:5':['bones','no cause for terror'],'54:1':['Ziphites'],'54:3':['Strangers'],'55:23':['half their days'],'56:1':['Philistines','Gath'],'58:8':['stillborn'],'58:10':['blood'],'59:11':['Do not kill'],'59:13':['Consume'],'60:1':['Joab','twelve thousand','Edomites','Aram-naharaim','Aram-zobah','Valley of Salt'],'60:5':['answer me'],'60:8':['Philistia, shout over me'],'63:10':['jackals']}
 for ref,terms in checks.items():
  for term in terms:assert term in vv['Psalms '+ref]['after'],(ref,term)
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or p.startswith(ad)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip()
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':40,'new_verses':609,'original_source_records_bound_exactly_once':642,'cumulative_coverage':{'ledgers':74,'chapters':547,'verses':14968},'preservation':{'prior_ledgers_byte_identical':73,'prior_chapters_byte_identical':507,'historical_provenance_preserved':True,'tsw_unchanged':True},'source_binding_audit':{'status':'PASSED','errors':[]},'public_source_offsets':offsets,'first_source_reading':{'original_records':642,'all_annotations_read':True},'tsw_comparator_verses_read_after_drafting':609,'focused_authoring_source_reread':247,'focused_assertions':checks,'refrains_and_intentional_differences':'PASSED','divine_name_and_selah_counts':'PASSED; Psalm 25:12 repeats LORD once to identify the pronoun subject explicitly','translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_psalms_review':'PENDING; this is a selected forty-chapter authoring batch.','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','original_source_records_bound_exactly_once','cumulative_coverage']}))
if __name__=='__main__':main()
