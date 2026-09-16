"""Reproducible structural/source checks; no independent editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='5e54ee1d98ad89c2fc37d3927004dca07acd406a'
sys.path.insert(0,str(ROOT/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
C=[('jeremiah','Jeremiah','Jeremiah',2,21,40,517,194)]
def qa_name(b):return ('SONG_OF_SONGS'if b=='songofsongs'else b.upper())+'_FLUENT_BOOK_QA.json'

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-1]==oq['completed_draft_scopes'];assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:]
 priorpaths=set();total=0
 for sc in oq['completed_draft_scopes']:
  p=ROOT/sc['ledger'];assert p.read_bytes()==old(sc['ledger']);l=json.loads(p.read_text())
  for ch in l['chapters']:
   assert ch['path']not in priorpaths;priorpaths.add(ch['path']);total+=ch['verse_count'];assert(ROOT/ch['path']).read_bytes()==old(ch['path']);assert sha((ROOT/ch['path']).read_bytes())==ch['after_sha256'];assert sha((ROOT/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert len(oq['completed_draft_scopes'])==85 and len(priorpaths)==770 and total==19548
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
 checks={'Jeremiah 21:1': ['Pashhur', 'Malchijah', 'Zephaniah', 'Maaseiah'], 'Jeremiah 22:30': ['childless', 'David'], 'Jeremiah 23:6': ['righteousness'], 'Jeremiah 25:1': ['fourth', 'first'], 'Jeremiah 25:3': ['twenty-three', 'thirteenth'], 'Jeremiah 25:11': ['seventy'], 'Jeremiah 27:1': ['Jehoiakim'], 'Jeremiah 27:3': ['Zedekiah'], 'Jeremiah 27:7': ['grandson'], 'Jeremiah 28:1': ['fourth', 'fifth'], 'Jeremiah 28:3': ['two'], 'Jeremiah 28:17': ['seventh'], 'Jeremiah 29:10': ['seventy', 'Babylon'], 'Jeremiah 30:9': ['David'], 'Jeremiah 31:9': ['Ephraim', 'firstborn'], 'Jeremiah 31:22': ['woman', 'man'], 'Jeremiah 31:31': ['Israel', 'Judah'], 'Jeremiah 31:32': ['husband'], 'Jeremiah 31:40': ['corpses', 'ashes'], 'Jeremiah 32:1': ['tenth', 'eighteenth'], 'Jeremiah 32:9': ['seventeen'], 'Jeremiah 32:12': ['Hanamel', 'Baruch', 'Neriah', 'Mahseiah'], 'Jeremiah 32:35': ['sons', 'daughters', 'sacrifice'], 'Jeremiah 32:44': ['Shephelah', 'Negeb'], 'Jeremiah 33:16': ['she', 'righteousness'], 'Jeremiah 34:7': ['Lachish', 'Azekah'], 'Jeremiah 34:14': ['seven', 'six'], 'Jeremiah 34:18': ['calf'], 'Jeremiah 35:8': ['wives', 'sons', 'daughters'], 'Jeremiah 35:11': ['Chaldean', 'Aramean'], 'Jeremiah 36:1': ['fourth'], 'Jeremiah 36:9': ['fifth', 'ninth'], 'Jeremiah 36:23': ['three', 'four'], 'Jeremiah 36:32': ['added'], 'Jeremiah 37:3': ['Jehucal'], 'Jeremiah 38:1': ['Jucal'], 'Jeremiah 38:10': ['thirty'], 'Jeremiah 38:12': ['armpits'], 'Jeremiah 38:28': ['captured'], 'Jeremiah 39:1': ['ninth', 'tenth'], 'Jeremiah 39:2': ['eleventh', 'ninth', 'fourth'], 'Jeremiah 39:6': ['sons'], 'Jeremiah 39:7': ['blinded', 'bronze']}
 for ref,terms in checks.items():
  for term in terms:assert term.lower()in allvv[ref]['after'].lower(),(ref,term)
 assert all(row['source_reference']==row['reference'].replace('Jeremiah','Jer')for row in allbooks['jeremiah']['verses'])
 assert len(q['completed_draft_scopes'])==86
 cumulative=[ch for sc in q['completed_draft_scopes']for ch in json.loads((ROOT/sc['ledger']).read_text())['chapters']]
 assert len(cumulative)==790 and sum(ch['verse_count']for ch in cumulative)==20065
 block=q['active_fifty_chapter_block'];assert block['status']=='IN_PROGRESS'and block['completed_chapters']==33 and block['remaining_chapters']==17
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip();family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':20,'new_verses':517,'unique_original_source_records':sourcecounts,'cumulative_coverage':{'ledgers':86,'chapters':790,'verses':20065},'prior_preservation':{'ledgers_byte_identical':85,'chapters_byte_identical':770,'verses':19548,'tsw_unchanged':True,'historical_provenance_preserved':True},'source_binding_audit':'PASSED for affected Jeremiah ledger','divine_names':'PASSED verse by verse, including LORD/GOD and YAH separately','focused_assertions':checks,'versification':'All 517 public labels match original Hebrew records. Final capture clause is inside 38:28.','repeated_refrains':'Divine-name repetitions checked verse by verse; recurring promise and judgment phrases reread.','focused_authoring_reread':194,'translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_consistency_reviews':'All prior pending reviews preserved.','active_fifty_chapter_block':block,'publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
