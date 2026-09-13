"""Whole-book structure and selected source comparisons, not independent editorial approval."""
from pathlib import Path
import argparse,json,re,hashlib,subprocess,sys,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='6b5a732173ce09788c58c715ae039e01eba7fea2'
sys.path.insert(0,str(ROOT/'tools'));from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
def main():
 p=argparse.ArgumentParser()
 for b in ['genesis','exodus','leviticus','numbers','deuteronomy','james']:p.add_argument('--'+b+'-source',type=Path,required=True)
 a=p.parse_args();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];deut=[];allpaths=set()
 for scope in q['completed_draft_scopes']:
  lp=scope['ledger'];l=json.loads((ROOT/lp).read_text());book=scope['scope'].split()[0]
  audits.append({'ledger':lp,**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',lp,'--source-text',str(getattr(a,book.lower()+'_source').resolve())))})
  for c in l['chapters']:assert c['path'] not in allpaths;allpaths.add(c['path'])
  if book=='Deuteronomy':deut.append((lp,l))
 assert len(audits)==45 and len(allpaths)==192 and sum(x['verses'] for x in audits)==5960
 data=a.deuteronomy_source.read_bytes();assert sha(data)=='aad16a6a2dcbdc6ee36d7d051e80a63bfeb69ecaae19f775ec5b6aa67fe22355'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()=='5317431fd1d1fb5848d7f9f1d22d0753152f9991'
 raw={f'Deut {c}:{v}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',data.decode(),re.S) for c,v in [re.search(r'osisID="Deut\.(\d+)\.(\d+)"',s).groups()]}
 public={v['reference']:v for lp,l in deut for v in l['verses']};refs=[v['source_reference'] for v in public.values()];assert len(deut)==5 and len(public)==len(refs)==len(set(refs))==len(raw)==959 and set(refs)==set(raw)
 structural=[]
 for lp,l in deut:
  for c in l['chapters']:
   b=(ROOT/c['path']).read_bytes();t=b.decode();m=t.split('---',2)[2].split('## Notes')[0]
   assert sha(b)==c['after_sha256'] and re.findall(r'^v(\d\d):',m,re.M)==[f'{v:02}' for v in range(1,c['verse_count']+1)]
   assert m.count('“')==m.count('”'),c['chapter']
   inside=False
   for line in m.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['chapter'],line)
   assert not inside
   for para in m.split('</p>')[:-1]:assert not para.rstrip().endswith((',',':',';','—'))
   assert all(x in t for x in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   cr=json.loads((ROOT/f'audit/exegetical-core/fluent-production/deuteronomy/Deuteronomy_{c["chapter"]:02}_review.json').read_text());assert cr['chapter_binding']==c and cr['publication_allowed'] is False
   structural.append({'chapter':c['chapter'],'verses':c['verse_count'],'sha256':sha(b),'headings':re.findall(r'^## (.*)$',m,re.M)})
 assert sorted(c['chapter'] for c in structural)==list(range(1,35))
 mapping={v['reference']:v['source_reference'] for v in public.values() if v['source_reference']!=v['reference'].replace('Deuteronomy ','Deut ')}
 expected={'Deuteronomy 12:32':'Deut 13:1','Deuteronomy 22:30':'Deut 23:1','Deuteronomy 29:1':'Deut 28:69'}
 expected.update({f'Deuteronomy 13:{v}':f'Deut 13:{v+1}' for v in range(1,19)});expected.update({f'Deuteronomy 23:{v}':f'Deut 23:{v+1}' for v in range(1,26)});expected.update({f'Deuteronomy 29:{v}':f'Deut 29:{v-1}' for v in range(2,30)});assert mapping==expected
 co=json.loads((BATCH/'concordance.json').read_text());fo=json.loads((BATCH/'focused-comparisons.json').read_text());changes=json.loads((BATCH/'changes.json').read_text());selected=co['rows']+fo['rows']
 assert len(co['rows'])==94 and len(fo['rows'])==160 and len({x['reference'] for x in selected})==250
 expectedco={ref for ref,s in raw.items() if {i for w in E.fromstring(s).findall('w') for i in re.findall(r'\d+',w.get('lemma',''))}&set(co['lemmas'])};assert {x['source_reference'] for x in co['rows']}==expectedco
 for row in selected:
  v=public[row['reference']];assert row['source_reference']==v['source_reference'] and row['fluent']==v['after'] and row['source_verse_sha256']==v['source_verse_sha256']==sha(raw[v['source_reference']].encode())
  e=E.fromstring(raw[v['source_reference']]);assert row['hebrew']==' '.join(''.join(w.itertext()) for w in e if w.tag in ('w','seg'));assert row['annotations']==[E.tostring(w,encoding='unicode') for w in e if w.tag=='note']
 text=lambda ref:public['Deuteronomy '+ref]['after']
 checks={'1:2':['eleven-day'],'1:3':['fortieth','first day','eleventh month'],'2:14':['Thirty-eight'],'3:11':['nine cubits','four cubits'],'5:14':['male and female slaves may rest'],'5:15':['slave in Egypt'],'6:4':['LORD is one'],'6:7':['children','sit at home','walk along the road','lie down','get up'],'10:5':['tablets in the ark'],'10:6':['Moserah','Aaron','Eleazar'],'10:16':['Circumcise your hearts'],'10:19':['love the resident foreigner'],'12:15':['unclean and the clean'],'12:23':['blood is the life'],'14:21':['give it to the resident foreigner','sell it to a foreigner'],'15:1':['seven years'],'15:4':['no poor'],'15:11':['always be poor'],'15:12':['six years','seventh year'],'17:6':['two or three','one witness'],'17:16':['Egypt','horses'],'19:4':['unintentionally'],'19:6':['does not deserve death'],'19:11':['hates','lies in wait','kills'],'19:15':['two or three'],'20:11':['forced labor'],'20:13':['all its males'],'20:14':['women, children, livestock'],'20:16':['nothing that breathes'],'21:14':['free','not sell','slave','humiliated'],'22:25':['rapes','only the man'],'22:26':['Do nothing','no offense'],'22:28':['seizes'],'23:15':['Do not hand a slave back'],'23:16':['chooses','Do not mistreat'],'24:16':['own sin'],'25:3':['Forty','no more'],'27:20':['father’s garment'],'28:20':['forsaking me'],'28:63':['rejoiced','will rejoice'],'29:4':['has not given'],'30:6':['circumcise your heart'],'30:14':['mouth','heart','carry it out'],'31:7':['go with'],'31:23':['bring the Israelites'],'31:26':['beside the ark'],'32:8':['children of Israel'],'32:13':['The LORD made Jacob','Jacob ate','The LORD let him suck'],'32:44':['Hoshea'],'33:17':['Ephraim’s ten thousands','Manasseh’s thousands'],'34:7':['hundred and twenty','vigor'],'34:8':['thirty days'],'34:10':['Since then','whom the LORD knew'],'34:11':['No prophet has matched'],'34:12':['mighty hand','great terror','all Israel']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in text(ref).casefold(),(ref,term)
 changedrefs={x['reference'] for x in changes};assert changedrefs=={'Deuteronomy 27:20','Deuteronomy 32:13','Deuteronomy 34:10','Deuteronomy 34:11','Deuteronomy 34:12'}
 for x in changes:
  b=subprocess.check_output(['git','show',BASE+':'+x['chapter_path']],cwd=ROOT);assert sha(b)==x['before_chapter_sha256'];assert verse_texts(b.decode())[x['reference'].split(':')[1].zfill(2)]==x['before'];assert public[x['reference']]['after']==x['after'];assert sha((ROOT/x['chapter_path']).read_bytes())==x['after_chapter_sha256']
 for lp,l in deut:
  old=json.loads(run('git','show',BASE+':'+lp));ov={v['reference']:v for v in old['verses']};assert l['base_commit']==old['base_commit'] and l['source']==old['source']
  for v in l['verses']:
   if v['reference'] not in changedrefs:assert v==ov[v['reference']]
   else:
    for k in ['before','source_reference','source_verse_sha256','tsw_comparator','delta']:assert v[k]==ov[v['reference']][k]
  for c in l['chapters']:
   if c['chapter'] not in [27,32,34]:assert c==next(x for x in old['chapters'] if x['chapter']==c['chapter'])
 rd='audit/exegetical-core/fluent-production/deuteronomy/';names=['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{x['chapter_path'] for x in changes}|{x['verse_ledger'] for x in changes}|{rd+f'Deuteronomy_{c:02}_review.json' for c in [27,32,34]}|{rd+n for n in names}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or p.startswith(str(BATCH.relative_to(ROOT))+'/') for p in changed),changed
 for n in names:
  old=json.loads(run('git','show',BASE+':'+rd+n));new=json.loads((ROOT/rd/n).read_text());assert all(new[k]==v for k,v in old.items());assert new['publication_allowed'] is False
 assert q['next_work'][0]['scope']=='Joshua 1–12'
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'All 34 chapters structurally scanned; 250 selected source/English comparisons reread','revision_audits':audits,'cumulative_coverage':{'chapters':192,'verses':5960},'deuteronomy_source_records':959,'all_source_records_bound_once':True,'structural_chapters':structural,'public_source_numbering_differences':mapping,'concordance_rows':94,'focused_rows':160,'unique_selected_verses':250,'focused_assertions':checks,'corrected_references':sorted(changedrefs),'prior_provenance_and_unaffected_work_preserved':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':45,'chapters_scanned':34,'selected_verses':250,'refined_verses':len(changes),'mapping_differences':len(mapping)},indent=2))
if __name__=='__main__':main()
