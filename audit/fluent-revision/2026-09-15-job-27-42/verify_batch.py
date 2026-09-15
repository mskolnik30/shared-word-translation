"""Reproducible structural/source checks; not independent editorial approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,collections
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='6479d27235b909d76b1eaf5160d45855a1342113'
sys.path.insert(0,str(ROOT/'tools'))
from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*a):
 p=subprocess.run(a,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def main():
 a=argparse.ArgumentParser();a.add_argument('--source-directory',type=Path,required=True);sd=a.parse_args().source_directory.resolve()
 sources={sha(p.read_bytes()):p.read_bytes()for p in sd.rglob('*')if p.is_file()}
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-2]==oq['completed_draft_scopes']
 paths=set();total=0;oldcount=0;ls=[];jobreferences=[];audits=[]
 for idx,sc in enumerate(q['completed_draft_scopes']):
  p=ROOT/sc['ledger'];l=json.loads(p.read_text());ls.append(l)
  if idx<71:assert p.read_bytes()==old(sc['ledger'])
  for c in l['chapters']:
   assert c['path']not in paths;paths.add(c['path']);total+=c['verse_count'];assert sha((ROOT/c['path']).read_bytes())==c['after_sha256'];assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
   if idx<71:assert (ROOT/c['path']).read_bytes()==old(c['path']);oldcount+=1
  if l['source'].get('osis_book_id')=='Job':jobreferences += [s['source_reference']for v in l['verses']for s in v.get('source_segments',[v])]
  # The shared audit tool changed to support explicitly partitioned source records.
  # Check every existing ledger for backward compatibility and unchanged bindings.
  errors=audit(ROOT,l,sources[l['source']['sha256']]);assert not errors,(sc['ledger'],errors)
  audits.append({'ledger':sc['ledger'],'status':'PASSED','chapters':len(l['chapters']),'verses':len(l['verses'])})
 assert len(ls)==73 and len(paths)==507 and total==14359 and oldcount==467
 assert len(jobreferences)==len(set(jobreferences))==1070
 allowed={'audit/fluent-revision/WORK_QUEUE.json','tools/audit_fluent_revision.py'};dirs=[];allv={};focused={};recordcounts={}
 for l,bk,pre,bqa,n in zip(ls[-2:],['job','psalms'],['Job','Psalm'],['JOB_FLUENT_BOOK_QA.json','PSALMS_FLUENT_BOOK_QA.json'],[458,312]):
  sc=next(x for x in q['completed_draft_scopes']if x['ledger'].endswith(bk+'-verse-review.json')and json.loads((ROOT/x['ledger']).read_text())['revision_id']==l['revision_id']);lp=ROOT/sc['ledger'];ad=lp.parent;dirs.append(str(ad.relative_to(ROOT))+'/');assert l['automated_qa']=='PASSED'
  sb=sources[l['source']['sha256']];raw={};he=[]
  for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
   e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');key=f'{o} {c}:{v}';raw[key]=rec
   morph={w.attrib.get('morph','')[:1]for w in e if w.tag=='w'};assert 'A'not in morph
   if 'H'in morph:he.append(key)
  assert len(he)==(1070 if bk=='job' else 2527)
  vv={v['reference']:v for v in l['verses']};allv.update(vv);assert len(vv)==n
  bound=[s['source_reference']for v in l['verses']for s in v.get('source_segments',[v])];recordcounts[bk]=len(set(bound))
  if bk=='job':assert len(bound)==len(set(bound))==458
  else:
   assert len(bound)==326 and len(set(bound))==325
   assert {r:k for r,k in collections.Counter(bound).items()if k>1}=={'Ps 13:6':2}
   assert sum('source_segments'in v for v in l['verses'])==14
  rows=json.loads((ad/'focused-comparisons.json').read_text())['rows'];focused[bk]=len(rows)
  assert [r['reference']for r in rows]==json.loads((ad/'focused-selection.json').read_text())
  for r in rows:
   assert all(r[k]==v for k,v in vv[r['reference']].items())
   for ev in r['source_evidence']:assert ev['original_source_xml']==raw[ev['source_reference']]and sha(ev['original_source_xml'].encode())==ev['source_verse_sha256']
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
   rp=f'audit/exegetical-core/fluent-production/{bk}/{pre}_{c["chapter"]:0{3 if bk=="psalms" else 2}}_review.json';d=json.loads((ROOT/rp).read_text());assert d['chapter_binding']==c and d['automated_qa']=='PASSED' and d['publication_allowed']is False;allowed|={c['path'],rp}
  for fn in [bqa,'APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
   rel=f'audit/exegetical-core/fluent-production/{bk}/'+fn;allowed.add(rel);p=json.loads(old(rel));d=json.loads((ROOT/rel).read_text());assert d['revision_batches'][:-1]==p.get('revision_batches',[])and d['publication_allowed']is False
   for k in ['human_textual_review','source_lock','resolved_f3']:
    if k in p:assert d[k]==p[k]
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(p['entries'])==len(d['entries'])
    for x,y in zip(p['entries'],d['entries']):
     if x['chapter']in l['source']['scope_chapters']:assert y['status']=='SUPERSEDED'and y['historical_status_before_revision']==x.get('status')and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
     else:assert x==y
 checks=json.loads((BATCH/'focused-assertions.json').read_text())
 for ref,terms in checks.items():
  for term in terms:assert term in allv[ref]['after'],(ref,term)
 for c in [27,29,34,35,36,38,42]:assert allv[f'Job {c}:2']['after'].startswith('“')
 for c in [28,30,31,33,37,39,41]:assert not allv[f'Job {c}:1']['after'].startswith('“')
 for c,n in [(28,28),(33,33),(34,37),(35,16),(37,24),(39,30),(41,34),(42,6)]:assert allv[f'Job {c}:{n}']['after'].endswith('”')
 assert '” The words of Job were ended.'in allv['Job 31:40']['after']
 for v in [2,4,7]:assert allv[f'Job 40:{v}']['after'].startswith('“')
 for v in [2,5]:assert allv[f'Job 40:{v}']['after'].endswith('”')
 # Explicit chapter boundary mapping, including all eight Hebrew 40 records.
 for v in range(1,35):assert allv[f'Job 41:{v}']['source_reference']==(f'Job 40:{v+24}'if v<=8 else f'Job 41:{v-8}')
 for ref,start,end in [('Psalms 13:5',1,6),('Psalms 13:6',7,11)]:
  assert allv[ref]['source_reference']=='Ps 13:6';assert allv[ref]['source_partition']['word_start']==start and allv[ref]['source_partition']['word_end']==end
 assert q['next_work'][1:]==oq['next_work'][1:]
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(d)for d in dirs)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip()
 psad=ROOT/'audit/fluent-revision/2026-09-15-psalms-1-24';pssource=next(p for p in sd.rglob('*')if p.is_file()and sha(p.read_bytes())==ls[-1]['source']['sha256'])
 regression=run(sys.executable,str(psad/'test_source_partitions.py'),'--source-text',str(pssource))
 result={'status':'PASSED','base_commit':BASE,'new_chapters':40,'new_verses':770,'cumulative_coverage':{'ledgers':73,'chapters':507,'verses':14359},'preservation':{'prior_ledgers_byte_identical':71,'prior_chapters_byte_identical':467,'historical_provenance_preserved':True,'tsw_unchanged':True},'cumulative_source_binding_audits':audits,'all_job_original_records_bound_once':1070,'selected_original_records':recordcounts,'focused_authoring_reread':focused,'first_source_reading':{'original_records':783,'all_source_annotations_read':True},'tsw_comparator_verses_read_after_drafting':770,'focused_assertions':checks,'speaker_boundaries_poetry_containment_and_public_source_mapping':'PASSED','partition_regression':json.loads(regression),'translation_family':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'whole_book_job_consistency_review':'PENDING; forty selected chapters received source drafting and focused authoring checks. Earlier chapters 1–26 were not reread continuously in this batch.','independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage','focused_authoring_reread']}))
if __name__=='__main__':main()
