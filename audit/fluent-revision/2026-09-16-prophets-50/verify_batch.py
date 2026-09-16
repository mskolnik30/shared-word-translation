"""Reproducible structural/source checks; no independent editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='a1e6a02b972f845b0b13f0ab4f0bcc9078b5b5d5'
sys.path.insert(0,str(ROOT/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
C=[('isaiah','Isaiah','Isaiah',2,24,66,851,140),('jeremiah','Jeremiah','Jeremiah',2,1,7,207,22)]
def qa_name(b):return ('SONG_OF_SONGS'if b=='songofsongs'else b.upper())+'_FLUENT_BOOK_QA.json'

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-2]==oq['completed_draft_scopes'];assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:]
 priorpaths=set();total=0
 for sc in oq['completed_draft_scopes']:
  p=ROOT/sc['ledger'];assert p.read_bytes()==old(sc['ledger']);l=json.loads(p.read_text())
  for ch in l['chapters']:
   assert ch['path']not in priorpaths;priorpaths.add(ch['path']);total+=ch['verse_count'];assert(ROOT/ch['path']).read_bytes()==old(ch['path']);assert sha((ROOT/ch['path']).read_bytes())==ch['after_sha256'];assert sha((ROOT/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert len(oq['completed_draft_scopes'])==82 and len(priorpaths)==707 and total==18203
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};prefixes=[str(BATCH.relative_to(ROOT))+'/'];allvv={};allbooks={};sourcecounts={}
 for b,name,pre,width,lo,hi,N,F in C:
  rel=f'audit/fluent-revision/2026-09-16-{b}-{lo}-{hi}';a=ROOT/rel;prefixes.append(rel+'/');l=json.loads((a/f'{b}-verse-review.json').read_text());sb=(sd/f'{b}-pinned-hebrew.xml').read_bytes();errors=audit(ROOT,l,sb);assert not errors,errors
  assert len(l['chapters'])==hi-lo+1 and len(l['verses'])==N
  raw={};selected={}
  for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
   e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';raw[ref]=rec
   if lo<=int(c)<=hi:selected[ref]=e
  assert len(raw)==l['source']['book_verse_count']and len(selected)==N-(1 if b=='isaiah'else 0)
  refs=[v['source_reference']for v in l['verses']];assert len(refs)==N and set(refs)==set(selected);assert len(set(refs))==len(selected);sourcecounts[b]=len(selected)
  vv={v['reference']:v for v in l['verses']};allvv.update(vv);allbooks[b]=l
  for row in l['verses']:
   e=selected[row['source_reference']];assert sha(raw[row['source_reference']].encode())==row['source_verse_sha256'];assert row['rationale'].strip()
   ws=[w for w in e if w.tag=='w'];part=row.get('source_partition');ws=ws[part['word_start']-1:part['word_end']]if part else ws;lemmas=[w.attrib.get('lemma','').split('/')[-1]for w in ws]
   assert sum(x in ['3068','3069']for x in lemmas)==len(re.findall(r'\b(?:LORD|GOD)\b',row['after'])),row['reference']
   assert lemmas.count('3050')==len(re.findall(r'\bYAH\b',row['after'])),row['reference']
  focus=json.loads((a/'focused-comparisons.json').read_text());sel=json.loads((a/'focused-selection.json').read_text());assert len(sel)==F and [x['reference']for x in focus['rows']]==sel
  for row in focus['rows']:
   assert all(row[k]==v for k,v in vv[row['reference']].items());assert row['original_source_xml']==raw[row['source_reference']]
  for ch in l['chapters']:
   path=ch['path'];assert path not in priorpaths;t=(ROOT/path).read_text();yaml=t.split('---',2)[1];body=t.split('---',2)[2].split('## Notes')[0];inside=False
   for line in body.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip()and not line.startswith('## '):assert inside,(path,line)
   assert not inside and '\\'not in body
   assert all(x in yaml for x in old(path).decode().split('---',2)[1].strip().splitlines());assert all(x in yaml for x in ['status: QA_PASSED','qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   for ref in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(x)<=ch['verse_count']for x in re.findall(r'\d+',ref)),(path,ref)
   rp=f'audit/exegetical-core/fluent-production/{b}/{pre}_{ch["chapter"]:0{width}}_review.json';d=json.loads((ROOT/rp).read_text());assert d['chapter_binding']==ch and d['publication_allowed']is False and d['status']=='REVIEW_PENDING';allowed|={path,rp}
  for fn in [qa_name(b),'APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
   rp=f'audit/exegetical-core/fluent-production/{b}/{fn}';allowed.add(rp);d=json.loads((ROOT/rp).read_text());p=json.loads(old(rp));assert d['revision_batches'][:-1]==p.get('revision_batches',[]);assert d['publication_allowed']is False
   for k in ['source','curated_f3_decisions','deployment_audit','summary']:
    if k in p:assert d[k]==p[k]
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(d['entries'])==len(p['entries'])
    for x,y in zip(p['entries'],d['entries']):
     if lo<=x['chapter']<=hi:assert y['status']=='SUPERSEDED'and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
     else:assert x==y
 # Focused mechanical guards support, but do not replace, the recorded source/English reread.
 checks={'Isaiah 26:3':['peace'],'Isaiah 26:4':['YAH','LORD'],'Isaiah 27:1':['Leviathan'],'Isaiah 29:1':['Ariel'],'Isaiah 30:26':['seven times brighter','seven days'],'Isaiah 36:1':['fourteenth'],'Isaiah 36:8':['two thousand'],'Isaiah 37:36':['185,000'],'Isaiah 38:5':['fifteen'],'Isaiah 38:8':['ten'],'Isaiah 38:11':['YAH'],'Isaiah 44:28':['Cyrus'],'Isaiah 45:1':['Cyrus','anointed'],'Isaiah 48:10':['chosen'],'Isaiah 49:3':['Israel'],'Isaiah 56:3':['eunuch'],'Isaiah 60:17':['gold','silver','bronze','iron'],'Isaiah 62:5':['sons'],'Isaiah 63:17':['wander'],'Isaiah 64:6':['menstrual'],'Isaiah 65:20':['hundred'],'Isaiah 66:24':['corpses','worm','fire'],'Jeremiah 1:2':['thirteenth'],'Jeremiah 1:3':['eleventh','fifth'],'Jeremiah 1:10':['uproot','tear down','destroy','overthrow','build','plant'],'Jeremiah 2:13':['two evils'],'Jeremiah 2:34':['You did not find them breaking in'],'Jeremiah 3:14':['one','two'],'Jeremiah 4:10':['deceived'],'Jeremiah 4:23':['unformed and empty'],'Jeremiah 6:14':['Peace, peace'],'Jeremiah 7:31':['sons','daughters','fire'],'Jeremiah 7:32':['for lack of room elsewhere']}
 for ref,terms in checks.items():
  for term in terms:assert term.lower() in allvv[ref]['after'].lower(),(ref,term)
 assert 'light'not in allvv['Isaiah 53:11']['after'].lower()
 assert allvv['Isaiah 29:1']['after'].count('Ariel')==2
 assert allvv['Isaiah 38:11']['after'].count('YAH')==2
 assert allvv['Jeremiah 7:4']['after'].count('LORD')==3
 assert allvv['Isaiah 35:10']['after']==allvv['Isaiah 51:11']['after']
 assert allvv['Isaiah 63:19']['source_reference']==allvv['Isaiah 64:1']['source_reference']=='Isa 63:19'
 assert allvv['Isaiah 63:19']['source_partition']['word_end']==9 and allvv['Isaiah 64:1']['source_partition']['word_start']==10
 for v in range(2,13):assert allvv[f'Isaiah 64:{v}']['source_reference']==f'Isa 64:{v-1}'
 assert len(q['completed_draft_scopes'])==84
 cumulative=[ch for sc in q['completed_draft_scopes']for ch in json.loads((ROOT/sc['ledger']).read_text())['chapters']]
 assert len(cumulative)==757 and sum(ch['verse_count']for ch in cumulative)==19261
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip();family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':50,'new_verses':1058,'unique_original_source_records':sourcecounts,'cumulative_coverage':{'ledgers':84,'chapters':757,'verses':19261},'prior_preservation':{'ledgers_byte_identical':82,'chapters_byte_identical':707,'verses':18203,'tsw_unchanged':True,'historical_provenance_preserved':True},'source_binding_audit':'PASSED for both affected ledgers','divine_names':'PASSED verse by verse, including LORD/GOD and YAH separately','focused_assertions':checks,'versification':'Public Isaiah 63:19 and 64:1 partition original Isa 63:19; both retain the exact complete original XML hash. Public 64:2–12 bind Isa 64:1–11. All other selected labels match.','repeated_refrains':'Isaiah 35:10 and 51:11 match; YAH, Ariel, and temple-name repetitions checked. Other repetitions inspected during authoring reread.','focused_authoring_reread':162,'translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_consistency_reviews':'Prior pending reviews preserved; continuous whole-book Isaiah review queued.','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
