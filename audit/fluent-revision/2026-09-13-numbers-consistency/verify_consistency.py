"""Verify complete Numbers structure and explicitly selected authoring comparisons."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='8d8159775ff46f862be51e6a91a4a0f33e7d743c'
sys.path.insert(0,str(ROOT/'tools'))
from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
def main():
 p=argparse.ArgumentParser()
 for b in ['genesis','exodus','leviticus','numbers','james']:p.add_argument('--'+b+'-source',type=Path,required=True)
 a=p.parse_args();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];num=[];allpaths=set()
 for s in q['completed_draft_scopes']:
  l=json.loads((ROOT/s['ledger']).read_text());book=s['scope'].split()[0]
  audits.append({'ledger':s['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',s['ledger'],'--source-text',str(getattr(a,book.lower()+'_source').resolve())))})
  for c in l['chapters']:assert c['path'] not in allpaths;allpaths.add(c['path'])
  if book=='Numbers':num.append((s['ledger'],l))
 assert len(audits)==40 and len(allpaths)==158 and sum(x['verses'] for x in audits)==5001
 data=a.numbers_source.read_bytes();assert sha(data)=='5be7f0c196a84eacc39c0ef751c5cdba82218d41cf9ed4e6107ae5ac715ffccf'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()=='2e7252db3bd33d510d2361a8b5016ac680b27dbb'
 raw={f'Num {c}:{v}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',data.decode(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 public={v['reference']:v for lp,l in num for v in l['verses']};refs=[seg['source_reference'] for v in public.values() for seg in v.get('source_segments',[v])]
 assert len(public)==1288 and len(refs)==len(set(refs))==len(raw)==1289 and set(refs)==set(raw)
 structural=[]
 for lp,l in num:
  for c in l['chapters']:
   b=(ROOT/c['path']).read_bytes();t=b.decode();m=t.split('---',2)[2].split('## Notes')[0]
   assert sha(b)==c['after_sha256'] and re.findall(r'^v(\d\d):',m,re.M)==[f'{v:02}' for v in range(1,c['verse_count']+1)]
   assert m.count('“')==m.count('”')
   inside=False
   for line in m.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['chapter'],line)
   assert not inside
   for para in m.split('</p>')[:-1]:assert not para.rstrip().endswith((',',':',';','—'))
   assert all(x in t for x in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   cr=json.loads((ROOT/f'audit/exegetical-core/fluent-production/numbers/Numbers_{c["chapter"]:02}_review.json').read_text());assert cr['chapter_binding']==c and cr['publication_allowed'] is False
   structural.append({'chapter':c['chapter'],'public_verses':c['verse_count'],'current_sha256':sha(b)})
 assert sorted(x['chapter'] for x in structural)==list(range(1,37))
 mapping={v['reference']:[s['source_reference'] for s in v.get('source_segments',[v])] for v in public.values() if [s['source_reference'] for s in v.get('source_segments',[v])]!=[v['reference'].replace('Numbers ','Num ')]}
 assert mapping['Numbers 26:1']==['Num 25:19','Num 26:1']
 assert mapping['Numbers 29:40']==['Num 30:1'] and mapping['Numbers 30:16']==['Num 30:17']
 selected=json.loads((BATCH/'focused-comparisons.json').read_text());review=json.loads((BATCH/'review.json').read_text())
 assert len(selected['rows'])==len({x['reference'] for x in selected['rows']})==153
 for row in selected['rows']:
  v=public[row['reference']];assert row['fluent']==v['after']
  assert row['source_segments']==[{k:s[k] for k in ['source_reference','source_verse_sha256']} for s in v.get('source_segments',[v])]
  for seg in row['source_segments']:assert sha(raw[seg['source_reference']].encode())==seg['source_verse_sha256']
 text=lambda ref:public['Numbers '+ref]['after']
 checks={'1:3':['twenty years'],'1:46':['603,550'],'3:39':['22,000'],'3:43':['22,273'],'3:46':['273'],'3:47':['five shekels','twenty gerahs'],'3:50':['1,365'],'4:3':['thirty','fifty'],'8:24':['twenty-five'],'8:25':['fifty'],'8:26':['may assist','must not perform'],'11:25':['seventy elders','did not do so again'],'13:8':['Hoshea'],'13:16':['Hoshea','Joshua'],'16:22':['God of the spirits of all flesh'],'27:16':['God of the spirits of all flesh'],'27:18':['your hand'],'27:23':['his hands'],'5:8':['family redeemer'],'9:11':['fourteenth','second month'],'9:14':['one rule','resident foreigner','native-born'],'15:30':['raised hand','cut off'],'19:18':['all the articles in it'],'19:19':['third and seventh','at evening'],'19:21':['sprinkles','wash their clothes','touches','unclean until evening'],'31:19':['third and seventh','captives'],'31:23':['also','water for removing impurity'],'35:12':['before standing trial'],'35:15':['foreigner and settler'],'35:24':['community must judge'],'35:25':['must rescue','high priest'],'35:27':['no bloodguilt'],'35:30':['commits murder','on the testimony of witnesses','single witness cannot'],'35:31':['Do not accept a ransom'],'35:32':['do not accept a ransom','before the priest dies'],'35:33':['blood pollutes','No atonement'],'26:51':['six hundred and one thousand seven hundred and thirty'],'26:62':['twenty-three thousand','one month'],'27:7':['daughters are right','Transfer'],'27:8':['without a son','daughter'],'27:9':['no daughter','brothers'],'27:10':['no brothers','father’s brothers'],'27:11':['nearest relative'],'32:30':['if they do not','holding among you in Canaan'],'36:6':['whomever they think best','but only'],'36:8':['Every daughter who inherits'],'36:11':['Mahlah, Tirzah, Hoglah, Milcah and Noah','father’s brothers'],'28:7':['fermented drink'],'28:14':['wine'],'29:7':['Humble yourselves'],'30:13':['humble herself']}
 for ref,terms in checks.items():
  for t in terms:assert t.casefold() in text(ref).casefold(),(ref,t)
 assert 22273-22000==273 and 273*5==1365
 changedrefs={x['reference'] for x in review['changes']};assert changedrefs=={'Numbers 19:18','Numbers 35:30'}
 for x in review['changes']:
  old=run('git','show',BASE+':'+x['chapter_path']);assert verse_texts(old)[x['reference'].split(':')[1].zfill(2)]==x['before']
  assert text(x['reference'].replace('Numbers ',''))==x['after'] and x['editorial_status']=='REVIEW_PENDING'
  original=subprocess.check_output(['git','show',BASE+':'+x['chapter_path']],cwd=ROOT);assert sha(original)==x['before_chapter_sha256'];assert sha((ROOT/x['chapter_path']).read_bytes())==x['after_chapter_sha256']
 for lp,l in num:
  old=json.loads(run('git','show',BASE+':'+lp));oldv={v['reference']:v for v in old['verses']};assert l['base_commit']==old['base_commit'] and l['source']==old['source']
  for v in l['verses']:
   if v['reference'] not in changedrefs:assert v==oldv[v['reference']]
   else:
    for key in ['before','source_reference','source_verse_sha256','tsw_comparator']:assert v[key]==oldv[v['reference']][key]
  for c in l['chapters']:
   if c['chapter'] not in [19,35]:assert c==next(x for x in old['chapters'] if x['chapter']==c['chapter'])
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{x['chapter_path'] for x in review['changes']}|{x['verse_ledger'] for x in review['changes']}|{reviewdir+f'Numbers_{c:02}_review.json' for c in [19,35]}|{reviewdir+n for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or p.startswith(str(BATCH.relative_to(ROOT))+'/') for p in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text());assert all(new[k]==v for k,v in old.items());assert new['publication_allowed'] is False
 assert q['next_work'][0]['scope']=='Deuteronomy 1–6'
 out={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers whole-book structural and selected thematic authoring self-check','revision_audits':audits,'cumulative_coverage':{'chapters':158,'verses':5001},'numbers_public_verses':1288,'numbers_source_records':1289,'structural_chapters':structural,'public_source_numbering_differences':mapping,'selected_source_comparisons':153,'focused_assertions':checks,'corrected_references':sorted(changedrefs),'prior_provenance_and_unaffected_work_preserved':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':40,'Numbers_chapters':36,'source_records':1289,'selected_comparisons':153,'corrections':sorted(changedrefs),'numbering_differences':len(mapping)},indent=2))
if __name__=='__main__':main()
