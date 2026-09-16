"""Reproducible structural/source checks; no independent editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='f3479755c5b890a8d1d03254bd18a6eaa77c26e1'
sys.path.insert(0,str(ROOT/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
C=[('daniel', 'Daniel', 'Daniel', 2, 3, 12, 287, 30), ('hosea', 'Hosea', 'Hosea', 2, 1, 14, 197, 42), ('joel', 'Joel', 'Joel', 2, 1, 3, 73, 9), ('amos', 'Amos', 'Amos', 2, 1, 9, 146, 27), ('obadiah', 'Obadiah', 'Obadiah', 2, 1, 1, 21, 3), ('jonah', 'Jonah', 'Jonah', 2, 1, 4, 48, 11), ('micah', 'Micah', 'Micah', 2, 1, 7, 105, 21), ('nahum', 'Nahum', 'Nahum', 2, 1, 2, 28, 6)]
from versification import public

def qa_name(b):return ('SONG_OF_SONGS'if b=='songofsongs'else b.upper())+'_FLUENT_BOOK_QA.json'

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-8]==oq['completed_draft_scopes'];assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:]
 priorpaths=set();total=0
 for sc in oq['completed_draft_scopes']:
  p=ROOT/sc['ledger'];assert p.read_bytes()==old(sc['ledger']);l=json.loads(p.read_text())
  for ch in l['chapters']:
   assert ch['path']not in priorpaths;priorpaths.add(ch['path']);total+=ch['verse_count'];assert(ROOT/ch['path']).read_bytes()==old(ch['path']);assert sha((ROOT/ch['path']).read_bytes())==ch['after_sha256'];assert sha((ROOT/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert len(oq['completed_draft_scopes'])==91 and len(priorpaths)==857 and total==21915
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};prefixes=[str(BATCH.relative_to(ROOT))+'/'];allvv={};allbooks={};sourcecounts={}
 for b,name,pre,width,lo,hi,N,F in C:
  rel=f'audit/fluent-revision/2026-09-16-{b}-{lo}-{hi}';a=ROOT/rel;prefixes.append(rel+'/');l=json.loads((a/f'{b}-verse-review.json').read_text());sb=(sd/f'{b}-pinned-hebrew.xml').read_bytes();errors=audit(ROOT,l,sb);assert not errors,errors
  assert l['automated_qa']=='PASSED'
  assert len(l['chapters'])==hi-lo+1 and len(l['verses'])==N
  raw={};selected={}
  for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
   e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';raw[ref]=rec
   if lo<=public(b,int(c),int(v))[0]<=hi:selected[ref]=e
  assert len(raw)==l['source']['book_verse_count']and len(selected)==N
  refs=[v['source_reference']for v in l['verses']];assert len(refs)==N and set(refs)==set(selected);assert len(set(refs))==len(selected);sourcecounts[b]=len(selected)
  vv={v['reference']:v for v in l['verses']};allvv.update(vv);allbooks[b]=l
  for row in l['verses']:
   e=selected[row['source_reference']];assert sha(raw[row['source_reference']].encode())==row['source_verse_sha256'];assert row['rationale'].strip()
   ws=[w for w in e if w.tag=='w'];part=row.get('source_partition');ws=ws[part['word_start']-1:part['word_end']]if part else ws;lemmas=[w.attrib.get('lemma','').split('/')[-1]for w in ws]
   assert sum(x in ['3068','3069']for x in lemmas)==len(re.findall(r'\b(?:LORD|GOD)\b',row['after'])),row['reference']
   assert lemmas.count('3050')==len(re.findall(r'\bYAH\b',row['after'])),row['reference']
  focus=json.loads((a/'focused-comparisons.json').read_text());sel=json.loads((a/'focused-selection.json').read_text());assert focus['status']=='AUTHORING_REREAD_COMPLETED'
  assert len(sel)==F and [x['reference']for x in focus['rows']]==sel
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
  for fn in ([qa_name(b)]if b=='jonah'else[qa_name(b),'APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']):
   rp=f'audit/exegetical-core/fluent-production/{b}/{fn}';allowed.add(rp);d=json.loads((ROOT/rp).read_text());p=json.loads(old(rp));assert d['revision_batches'][:-1]==p.get('revision_batches',[]);assert d['publication_allowed']is False
   for k in ['source','curated_f3_decisions','deployment_audit','summary']:
    if k in p:assert d[k]==p[k]
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(d['entries'])==len(p['entries'])
    for x,y in zip(p['entries'],d['entries']):
     if lo<=x['chapter']<=hi:assert y['status']=='SUPERSEDED'and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
     else:assert x==y
 # Focused mechanical guards support, but do not replace, the recorded source/English reread.
 checks={'Daniel 3:1': ['sixty cubits', 'six cubits', 'Dura'], 'Daniel 3:25': ['son of the gods'], 'Daniel 4:16': ['seven times'], 'Daniel 5:31': ['sixty-two'], 'Daniel 7:13': ['son of man', 'Ancient of Days'], 'Daniel 8:14': ['2,300', 'evenings and mornings'], 'Daniel 9:25': ['seven sevens', 'sixty-two sevens'], 'Daniel 9:26': ['anointed one', 'cut off'], 'Daniel 9:27': ['wing of abominations'], 'Daniel 12:11': ['1,290'], 'Daniel 12:12': ['1,335'], 'Hosea 11:3': ['taking them by the arms'], 'Hosea 13:16': ['little children', 'pregnant women'], 'Joel 2:23': ['autumn rain in righteousness'], 'Joel 3:3': ['boy', 'girl', 'drank it'], 'Amos 9:12': ['Edom'], 'Jonah 4:11': ['120,000', 'many animals'], 'Micah 6:9': ['Hear the rod'], 'Nahum 2:7': ['slave women']}
 for ref,terms in checks.items():
  for term in terms:assert term.lower()in allvv[ref]['after'].lower(),(ref,term)
 for b,l in allbooks.items():
  for row in l['verses']:
   c,v=map(int,row['source_reference'].split()[-1].split(':'));pc,pv=public(b,c,v);assert row['reference']==b.title()+f' {pc}:{pv}'
 # Source morphology retains Aramaic through Daniel7; Hebrew begins in Daniel8.
 ds=(sd/'daniel-pinned-hebrew.xml').read_text()
 for chapter,language in [(3,'A'),(7,'A'),(8,'H'),(12,'H')]:
  de=E.fromstring(re.search(r'<verse osisID="Dan.'+str(chapter)+r'.1">.*?</verse>',ds,re.S)[0]);langs=[w.attrib['morph'][0]for w in de if w.tag=='w'];assert set(langs)=={language},(chapter,langs)
 assert allbooks['daniel']['source']['languages']==['Hebrew','Aramaic']

 assert len(q['completed_draft_scopes'])==99
 cumulative=[ch for sc in q['completed_draft_scopes']for ch in json.loads((ROOT/sc['ledger']).read_text())['chapters']]
 assert len(cumulative)==907 and sum(ch['verse_count']for ch in cumulative)==22820
 block=q['active_fifty_chapter_block'];assert block['status']=='DRAFT_COMPLETED'and block['completed_chapters']==50 and block['remaining_chapters']==0 and block['completed_verses']==905
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip();family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':50,'new_verses':905,'unique_original_source_records':sourcecounts,'cumulative_coverage':{'ledgers':99,'chapters':907,'verses':22820},'prior_preservation':{'ledgers_byte_identical':91,'chapters_byte_identical':857,'verses':21915,'tsw_unchanged':True,'historical_provenance_preserved':True},'source_binding_audit':'PASSED for all eight affected ledgers','divine_names':'PASSED verse by verse, including LORD/GOD and YAH separately','focused_assertions':checks,'versification':'905 unique exact original records; public/source numbering mapped for six books, retaining all annotations. Daniel3–7 is Aramaic and Daniel8–12 Hebrew.','repeated_refrains':'Divine-name repetitions checked verse by verse; recurring promise and judgment phrases reread.','focused_authoring_reread':149,'translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_consistency_reviews':'All prior pending reviews preserved.','active_fifty_chapter_block':block,'publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
