"""Source/structural checks, not editorial approval."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys,re,copy,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;BASE='bba235669797602d28cbd2ee0e3521b59fdc87c6'
sys.path.insert(0,str(ROOT/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def public(b,c,v):
 if b=='nahum'and c==2:return (1,15)if v==1 else(2,v-1)
 if b=='zechariah'and c==2:return (1,v+17)if v<=4 else(2,v-4)
 if b=='malachi'and c==3 and v>=19:return 4,v-18
 return c,v
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));parts=json.loads((B/'batch.json').read_text());assert len(parts)==7
 assert q['completed_draft_scopes'][:-7]==oq['completed_draft_scopes'];assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:]
 prior=set();pv=0
 for sc in oq['completed_draft_scopes']:
  assert(ROOT/sc['ledger']).read_bytes()==old(sc['ledger']);l=json.loads((ROOT/sc['ledger']).read_text())
  for ch in l['chapters']:
   assert ch['path']not in prior;prior.add(ch['path']);pv+=ch['verse_count'];assert(ROOT/ch['path']).read_bytes()==old(ch['path']);assert sha((ROOT/ch['path']).read_bytes())==ch['after_sha256'];assert sha((ROOT/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert(len(prior),pv)==(907,22820)
 allowed={'audit/fluent-revision/WORK_QUEUE.json','tools/audit_fluent_revision.py'};prefixes=[str(B.relative_to(ROOT))+'/'];counts={};focus_count=0;allrows={}
 for part in parts:
  b=part['book'];a=ROOT/part['rel'];prefixes.append(part['rel']+'/');l=json.loads((a/(b+'-verse-review.json')).read_text());sb=(sd/(b+('-pinned-greek.txt'if b=='matthew'else'-pinned-hebrew.xml'))).read_bytes();assert not audit(ROOT,l,sb),audit(ROOT,l,sb)
  raw={};els={}
  if b=='matthew':
   for line in sb.decode().splitlines():
    m=re.fullmatch(r'(Matt \d+:\d+)\t(.*)',line)
    if m:raw[m[1]]=m[2]
  else:
   for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
    e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';raw[ref]=rec;els[ref]=e
  vv={v['reference']:v for v in l['verses']};allrows.update(vv);assert len(vv)==part['verses'];counts[b]=len(vv)
  for row in vv.values():
   assert sha(raw[row['source_reference']].encode())==row['source_verse_sha256'];c,v=map(int,row['source_reference'].split()[-1].split(':'));pc,pn=public(b,c,v);assert row['reference']==f'{b.title()} {pc}:{pn}'
   if b!='matthew':
    lemmas=[w.attrib.get('lemma','').split('/')[-1]for w in els[row['source_reference']]if w.tag=='w'];assert sum(x in ['3068','3069']for x in lemmas)==len(re.findall(r'\b(?:LORD|GOD)\b',row['after'])),row['reference'];assert lemmas.count('3050')==len(re.findall(r'\bYAH\b',row['after'])),row['reference']
  f=json.loads((a/'focused-comparisons.json').read_text());sel=json.loads((a/'focused-selection.json').read_text());assert f['status']=='AUTHORING_REREAD_COMPLETED';assert sel==[r['reference']for r in f['rows']];focus_count+=len(sel)
  for row in f['rows']:assert all(row[k]==v for k,v in vv[row['reference']].items())and row['exact_source_record']==raw[row['source_reference']]
  for ch in l['chapters']:
   assert ch['path']not in prior;t=(ROOT/ch['path']).read_text();assert '\\'not in t.split('## Notes')[0];rp=f'audit/exegetical-core/fluent-production/{b}/{b.title()}_{ch["chapter"]:02}_review.json';d=json.loads((ROOT/rp).read_text());assert d['chapter_binding']==ch and d['status']=='REVIEW_PENDING'and d['publication_allowed']is False;allowed|={rp,ch['path']}
   for ref in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(x)<=ch['verse_count']+len(ch.get('source_omitted_public_labels',[]))for x in re.findall(r'\d+',ref))
  for fn in ([b.upper()+'_FLUENT_BOOK_QA.json','MATTHEW_SOURCE_BINDINGS.json']if b=='matthew'else[b.upper()+'_FLUENT_BOOK_QA.json','APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']):
   rp=f'audit/exegetical-core/fluent-production/{b}/{fn}';allowed.add(rp);d=json.loads((ROOT/rp).read_text());od=json.loads(old(rp));assert d['revision_batches'][:-1]==od.get('revision_batches',[]);assert d['publication_allowed']is False
   for k in ['source','curated_f3_decisions','deployment_audit','summary']:
    if k in od:assert d[k]==od[k]
  if b=='matthew':ml,ms=l,sb
 assert focus_count==157,focus_count
 # Exercise the newly supported partial-book Greek scope and comparator omissions.
 regressions={}
 def reject(name,edit):
  d=copy.deepcopy(ml);edit(d);errs=audit(ROOT,d,ms);assert errs,name;regressions[name]='REJECTED'
 reject('wrong source chapter scope',lambda d:d['source'].update(scope_chapters=list(range(1,25))))
 reject('wrong source book',lambda d:d['source'].update(osis_book_id='Mark'))
 reject('missing source-bound verse',lambda d:d['verses'].pop())
 reject('undeclared comparator gap',lambda d:d['chapters'][16].pop('tsw_omitted_public_labels'))
 reject('wrong comparator gap',lambda d:d['chapters'][16].update(tsw_omitted_public_labels=[20]))
 assert audit(ROOT,ml,ms+b'\n');regressions['tampered full source']='REJECTED'
 # Ensure prior whole-book Greek behavior still passes without a chapter scope.
 js=next(sc for sc in oq['completed_draft_scopes']if sc['scope'].startswith('James'));jl=json.loads((ROOT/js['ledger']).read_text());jfiles=list(sd.glob('*james*'))
 assert jfiles,'James pinned source required for regression';assert any(not audit(ROOT,jl,f.read_bytes())for f in jfiles);regressions['prior James full-book audit']='PASSED'
 cumulative=[ch for sc in q['completed_draft_scopes']for ch in json.loads((ROOT/sc['ledger']).read_text())['chapters']];assert len(q['completed_draft_scopes'])==106 and len(cumulative)==957 and sum(ch['verse_count']for ch in cumulative)==24062
 changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT).decode().splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),[p for p in changed if p not in allowed and not any(p.startswith(x)for x in prefixes)]
 assert not subprocess.check_output(['git','diff',BASE,'--','books'],cwd=ROOT).strip();subprocess.run(['git','diff','--check'],cwd=ROOT,check=True);family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=ROOT).decode()
 result={'status':'PASSED','base_commit':BASE,'new_chapters':50,'new_verses':1242,'source_records_by_scope':counts,'cumulative_coverage':{'ledgers':106,'chapters':957,'verses':24062},'prior_preservation':{'ledgers_byte_identical':99,'chapters_byte_identical':907,'verses':22820,'tsw_and_companion_unchanged':True},'source_binding_audit':'PASSED seven ledgers','divine_names':'Hebrew LORD/GOD/YAH counts passed verse by verse','focused_authoring_reread':focus_count,'complete_English_and_apparatus_read':True,'recovery_qualification':'Recovered unfinished drafts; this turn does not independently establish the earlier drafting sequence or claim full original-language reading before recovery.','checker_regressions':regressions,'translation_family':family,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_consistency_reviews':'Pending; prior queue preserved','publication_allowed':False};(B/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
