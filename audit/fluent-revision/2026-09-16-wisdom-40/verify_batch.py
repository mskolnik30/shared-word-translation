"""Reproducible structural/source checks; no independent editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='1e0d2add96250b83f5278fca0a72eb277fa60cb9'
sys.path.insert(0,str(ROOT/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
C=[('psalms','Psalms','Psalm',3,145,150,80,29),('proverbs','Proverbs','Proverbs',2,1,31,915,216),('ecclesiastes','Ecclesiastes','Ecclesiastes',2,1,3,66,31)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-3]==oq['completed_draft_scopes'];assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:]
 priorpaths=set();total=0
 for sc in oq['completed_draft_scopes']:
  p=ROOT/sc['ledger'];assert p.read_bytes()==old(sc['ledger']);l=json.loads(p.read_text())
  for ch in l['chapters']:
   assert ch['path']not in priorpaths;priorpaths.add(ch['path']);total+=ch['verse_count'];assert(ROOT/ch['path']).read_bytes()==old(ch['path']);assert sha((ROOT/ch['path']).read_bytes())==ch['after_sha256'];assert sha((ROOT/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert len(oq['completed_draft_scopes'])==76 and len(priorpaths)==627 and total==16428
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
   e=selected[row['source_reference']];assert row['reference'].split()[-1]==row['source_reference'].split()[-1];assert sha(raw[row['source_reference']].encode())==row['source_verse_sha256'];assert row['rationale'].strip()
   for lemma,term in [('3068','LORD'),('3050','YAH'),('5542','Selah')]:
    n=sum(w.attrib.get('lemma','').split('/')[-1]==lemma for w in e if w.tag=='w');assert len(re.findall(r'\b'+term+r'\b',row['after']))==n,(row['reference'],term,n)
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
  for fn in [b.upper()+'_FLUENT_BOOK_QA.json','APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
   rp=f'audit/exegetical-core/fluent-production/{b}/{fn}';allowed.add(rp);d=json.loads((ROOT/rp).read_text());p=json.loads(old(rp));assert d['revision_batches'][:-1]==p.get('revision_batches',[]);assert d['publication_allowed']is False
   for k in ['source','curated_f3_decisions','deployment_audit','summary']:
    if k in p:assert d[k]==p[k]
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(d['entries'])==len(p['entries'])
    for x,y in zip(p['entries'],d['entries']):
     if lo<=x['chapter']<=hi:assert y['status']=='SUPERSEDED'and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
     else:assert x==y
 # Focused mechanical guards support, but do not replace, the recorded source/English reread.
 checks={'Psalms 145:1':['David'],'Psalms 145:12':['his mighty','his kingdom'],'Psalms 146:9':['resident foreigners','fatherless','widow'],'Psalms 147:19':['words','Jacob','Israel'],'Psalms 148:14':['horn'],'Psalms 149:5':['beds'],'Psalms 149:7':['vengeance'],'Psalms 150:6':['everything that breathes'], 'Proverbs 1:1':['Solomon','David','Israel'],'Proverbs 6:16':['six','seven'],'Proverbs 6:31':['sevenfold'],'Proverbs 8:22':['acquired'],'Proverbs 8:30':['master worker','playing'],'Proverbs 13:23':['injustice'],'Proverbs 17:10':['hundred'],'Proverbs 17:27':['noble spirit'],'Proverbs 19:7':['not there'],'Proverbs 21:6':['seeking death'],'Proverbs 22:6':['his way'],'Proverbs 22:20':['excellent sayings'],'Proverbs 23:14':['rod','Sheol'],'Proverbs 23:26':['keep watch'],'Proverbs 24:16':['seven'],'Proverbs 25:1':['Hezekiah','Judah'],'Proverbs 26:2':['does not'],'Proverbs 26:16':['seven'],'Proverbs 30:1':['Agur','Jakeh','Ithiel','Ucal'],'Proverbs 30:15':['two','Three','four'],'Proverbs 30:33':['pressing milk','pressing a nose','pressing anger'],'Proverbs 31:1':['Lemuel','mother'],'Proverbs 31:4':['Where'],'Proverbs 31:21':['scarlet'],'Proverbs 31:24':['sells','merchant'],'Ecclesiastes 1:1':['David','Jerusalem'],'Ecclesiastes 2:7':['male and female slaves'],'Ecclesiastes 2:25':['apart from me'],'Ecclesiastes 3:18':['they themselves are animals'],'Ecclesiastes 3:21':['Who knows whether','?']}
 for ref,terms in checks.items():
  for term in terms:assert term in allvv[ref]['after'],(ref,term)
 for x,y in [('9:4','9:16'),('14:12','16:25'),('18:8','26:22'),('21:9','25:24'),('6:10','24:33'),('6:11','24:34')]:assert allvv['Proverbs '+x]['after']==allvv['Proverbs '+y]['after']
 assert allvv['Proverbs 26:4']['after'].startswith('Do not answer')and allvv['Proverbs 26:5']['after'].startswith('Answer')
 assert sum(allvv[f'Ecclesiastes 3:{v}']['after'].count('a time')for v in range(2,9))==28
 # Alphabetic ending: all 22 successive initial Hebrew letters are retained as 22 verse units.
 sb=(sd/'proverbs-pinned-hebrew.xml').read_text();pr={E.fromstring(x).get('osisID'):E.fromstring(x)for x in re.findall(r'<verse\b[^>]*>.*?</verse>',sb,re.S)}
 first=''.join(re.sub('[^\u05d0-\u05ea]','',''.join(pr[f'Prov.31.{v}'].find('w').itertext()))[0]for v in range(10,32));assert first=='אבגדהוזחטיכלמנסעפצקרשת',first
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip();family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':40,'new_verses':1061,'source_records_bound_exactly_once':sourcecounts,'cumulative_coverage':{'ledgers':79,'chapters':667,'verses':17489},'prior_preservation':{'ledgers_byte_identical':76,'chapters_byte_identical':627,'verses':16428,'tsw_unchanged':True,'historical_provenance_preserved':True},'source_binding_audit':'PASSED for all three affected ledgers','divine_names_selah':'PASSED verse by verse','focused_assertions':checks,'acrostic_31_10_31':'22 successive Hebrew initials verified','ecclesiastes_time_pairs':14,'repeated_sayings':'PASSED','focused_authoring_reread':276,'translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_psalms_proverbs_reviews':'PENDING; focused rereading and structural checks completed, not a full continuous reread.','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
