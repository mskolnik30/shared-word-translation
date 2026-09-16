"""Reproducible structural/source checks; no independent editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='872b8c9d11bd167708d31b48d84ab6b07d544162'
sys.path.insert(0,str(ROOT/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
C=[('ecclesiastes','Ecclesiastes','Ecclesiastes',2,4,12,156,48),('songofsongs','Song of Songs','SongOfSongs',2,1,8,117,30),('isaiah','Isaiah','Isaiah',2,1,23,441,87)]
def qa_name(b):return ('SONG_OF_SONGS'if b=='songofsongs'else b.upper())+'_FLUENT_BOOK_QA.json'

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-3]==oq['completed_draft_scopes'];assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:]
 priorpaths=set();total=0
 for sc in oq['completed_draft_scopes']:
  p=ROOT/sc['ledger'];assert p.read_bytes()==old(sc['ledger']);l=json.loads(p.read_text())
  for ch in l['chapters']:
   assert ch['path']not in priorpaths;priorpaths.add(ch['path']);total+=ch['verse_count'];assert(ROOT/ch['path']).read_bytes()==old(ch['path']);assert sha((ROOT/ch['path']).read_bytes())==ch['after_sha256'];assert sha((ROOT/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert len(oq['completed_draft_scopes'])==79 and len(priorpaths)==667 and total==17489
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};prefixes=[str(BATCH.relative_to(ROOT))+'/'];allvv={};allbooks={};sourcecounts={}
 for b,name,pre,width,lo,hi,N,F in C:
  rel=f'audit/fluent-revision/2026-09-16-{b}-{lo}-{hi}';a=ROOT/rel;prefixes.append(rel+'/');l=json.loads((a/f'{b}-verse-review.json').read_text());sb=(sd/f'{b}-pinned-hebrew.xml').read_bytes();errors=audit(ROOT,l,sb);assert not errors,errors
  assert len(l['chapters'])==hi-lo+1 and len(l['verses'])==N
  raw={};selected={}
  for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
   e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';raw[ref]=rec
   if lo<=int(c)<=hi:selected[ref]=e
  assert len(raw)==l['source']['book_verse_count']and len(selected)==N
  refs=[v['source_reference']for v in l['verses']];assert len(refs)==len(set(refs))==N and set(refs)==set(selected);sourcecounts[b]=N
  vv={v['reference']:v for v in l['verses']};allvv.update(vv);allbooks[b]=l
  for row in l['verses']:
   e=selected[row['source_reference']];assert sha(raw[row['source_reference']].encode())==row['source_verse_sha256'];assert row['rationale'].strip()
   lemmas=[w.attrib.get('lemma','').split('/')[-1]for w in e if w.tag=='w']
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
 checks={'Ecclesiastes 4:12':['three strands'],'Ecclesiastes 6:3':['hundred','stillborn','burial'],'Ecclesiastes 6:6':['thousand years twice'],'Ecclesiastes 7:16':['excessively righteous'],'Ecclesiastes 7:28':['one man','thousand','no woman'],'Ecclesiastes 8:10':['forgotten'],'Ecclesiastes 8:12':['hundred'],'Ecclesiastes 9:5':['dead know nothing'],'Ecclesiastes 9:11':['Time and chance'],'Ecclesiastes 11:2':['seven','eight'],'Ecclesiastes 12:6':['silver cord','golden bowl','jar','wheel'],'Ecclesiastes 12:11':['one shepherd'],'Song of Songs 1:5':['black and beautiful'],'Song of Songs 3:7':['Sixty'],'Song of Songs 4:4':['thousand'],'Song of Songs 5:7':['struck','wounded','wrap'],'Song of Songs 6:13':['two camps'],'Song of Songs 7:9':['stirring the lips of sleepers'],'Song of Songs 8:6':['jealousy','Sheol','YAH'],'Song of Songs 8:12':['thousand','two hundred'],'Isaiah 5:10':['Ten yoke','bath','homer','ephah'],'Isaiah 6:2':['six wings'],'Isaiah 7:8':['sixty-five'],'Isaiah 7:14':['young woman','you will name him Immanuel'],'Isaiah 8:14':['sanctuary','stone','rock','trap','snare'],'Isaiah 9:6':['Wonderful Counselor','Mighty God','Everlasting Father','Prince of Peace'],'Isaiah 9:20':['his own arm'],'Isaiah 10:27':['fatness'],'Isaiah 11:6':['wolf','lamb','leopard','goat','Calf','lion','fattened'],'Isaiah 11:15':['seven streams','sandals'],'Isaiah 12:2':['YAH','LORD'],'Isaiah 13:16':['infants','dashed to pieces','raped'],'Isaiah 14:4':['extortion'],'Isaiah 14:12':['shining one','Dawn'],'Isaiah 16:4':['my outcasts','Moab'],'Isaiah 16:14':['three years'],'Isaiah 17:6':['two or three','four or five'],'Isaiah 19:18':['five cities','City of Destruction'],'Isaiah 19:25':['Egypt my people','Assyria the work of my hands','Israel my inheritance'],'Isaiah 20:1':['Sargon'],'Isaiah 20:3':['three years'],'Isaiah 20:4':['buttocks exposed'],'Isaiah 21:2':['Lay siege, Media'],'Isaiah 21:8':['like a lion'],'Isaiah 22:19':['I will','he will'],'Isaiah 22:25':['give way'],'Isaiah 23:15':['seventy years'],'Isaiah 23:17':['seventy years'],'Isaiah 23:18':['holy to the **LORD**','abundant food']}
 for ref,terms in checks.items():
  for term in terms:assert term in allvv[ref]['after'],(ref,term)
 refrain='For all this, his anger has not turned away; his hand is still stretched out.'
 for ref in ['5:25','9:12','9:17','9:21','10:4']:assert allvv['Isaiah '+ref]['after'].endswith(refrain)
 assert allvv['Song of Songs 2:7']['after']==allvv['Song of Songs 3:5']['after']
 assert 'gazelles'not in allvv['Song of Songs 8:4']['after']and '?'in allvv['Song of Songs 8:4']['after']
 assert allvv['Song of Songs 6:13']['after'].lower().count('return')==4
 assert allvv['Isaiah 6:3']['after'].lower().count('holy')==3
 assert allvv['Song of Songs 6:13']['source_reference']=='Song 7:1'
 for v in range(1,14):assert allvv[f'Song of Songs 7:{v}']['source_reference']==f'Song 7:{v+1}'
 assert allvv['Isaiah 9:1']['source_reference']=='Isa 8:23'
 for v in range(2,22):assert allvv[f'Isaiah 9:{v}']['source_reference']==f'Isa 9:{v-1}'
 assert [ch['verse_count']for ch in allbooks['ecclesiastes']['chapters'][:2]]==[17,19]
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip();family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':40,'new_verses':714,'source_records_bound_exactly_once':sourcecounts,'cumulative_coverage':{'ledgers':82,'chapters':707,'verses':18203},'prior_preservation':{'ledgers_byte_identical':79,'chapters_byte_identical':667,'verses':17489,'tsw_unchanged':True,'historical_provenance_preserved':True},'source_binding_audit':'PASSED for all three affected ledgers','divine_names':'PASSED verse by verse, including LORD/GOD and YAH separately','focused_assertions':checks,'versification':'Existing Ecclesiastes Hebrew numbering retained; Song and Isaiah offsets verified exactly.','repeated_refrains':'PASSED; Isaiah fivefold anger refrain; Song repeated oath and changed final oath.','focused_authoring_reread':165,'translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_consistency_reviews':'Prior pending reviews preserved; Ecclesiastes and Song of Songs continuous whole-book reviews queued.','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
