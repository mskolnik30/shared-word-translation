"""Source identity, structure and recorded risk checks, not scholarly approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='66da508924ee7a0491749f718a9c16e72ab57841'
sys.path.insert(0,str(ROOT/'tools'));from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*a):
 p=subprocess.run(a,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);a=p.parse_args();sd=a.source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];paths=set()
 for sc in q['completed_draft_scopes']:
  book=sc['scope'].split()[0].lower();s=sd/(book+'-pinned-'+('greek.txt' if book=='james' else 'hebrew.xml'))
  audits.append({'ledger':sc['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',sc['ledger'],'--source-text',str(s)))})
  l=json.loads((ROOT/sc['ledger']).read_text())
  for c in l['chapters']:assert c['path'] not in paths;paths.add(c['path'])
 assert len(audits)==46 and len(paths)==200 and sum(x['verses'] for x in audits)==6146
 l=json.loads((BATCH/'joshua-verse-review.json').read_text());verses={x['reference']:x for x in l['verses']};structural=[]
 for c in l['chapters']:
  t=(ROOT/c['path']).read_text();m=t.split('---',2)[2].split('## Notes')[0];inside=False
  for line in m.splitlines():
   if line=='<p>':assert not inside;inside=True
   elif line=='</p>':assert inside;inside=False
   elif line.strip() and not line.startswith('## '):assert inside,(c['chapter'],line)
  assert not inside and m.count('“')==m.count('”'),c['chapter']
  for para in m.split('</p>')[:-1]:assert not para.rstrip().endswith((',',':',';','—')),(c['chapter'],para[-90:])
  rv=json.loads((ROOT/f'audit/exegetical-core/fluent-production/joshua/Joshua_{c["chapter"]:02}_review.json').read_text());assert rv['chapter_binding']==c and rv['publication_allowed'] is False
  structural.append({'chapter':c['chapter'],'verses':c['verse_count'],'sha256':c['after_sha256'],'headings':re.findall(r'^## (.*)$',m,re.M)})
 checks={'1:8':['lips','day and night','everything written'],'1:14':['wives','little ones','livestock','fellow Israelites'],'2:1':['two men','prostitute','Rahab'],'2:13':['father and mother','brothers and sisters'],'2:19':['blood','own head','our heads'],'3:4':['about two thousand cubits'],'3:10':['Canaanites, Hittites, Hivites, Perizzites, Girgashites, Amorites, and Jebusites'],'3:16':['at Adam','Zarethan','Salt Sea','Jericho'],'4:9':['twelve stones','middle of the Jordan'],'4:13':['About forty thousand'],'4:16':['ark of the testimony'],'4:19':['tenth day','first month'],'4:20':['Gilgal','twelve stones'],'4:23':['before you','before us'],'5:1':['until they crossed'],'5:2':['flint knives','second time'],'5:6':['forty years','give us'],'5:10':['fourteenth day','evening'],'5:14':['“No,”','commander'],'6:4':['Seven priests','seven ram’s horns','seventh day','seven times'],'6:17':['destruction','Rahab','everyone with her'],'6:19':['silver','gold','bronze','iron','treasury'],'6:21':['men and women','young and old','cattle, sheep, and donkeys'],'6:26':['firstborn','youngest'],'7:1':['Carmi','Zabdi','Zerah','Judah'],'7:3':['two or three thousand'],'7:4':['About three thousand'],'7:5':['about thirty-six','Shebarim','turned to water'],'7:6':['elders of Israel','until evening','dust'],'7:17':['man by man','Zabdi'],'7:21':['Shinar','two hundred shekels','fifty shekels','tongue-shaped','coveted'],'7:24':['sons and daughters','Achor'],'7:25':['stoned him','burned them','pelted them'],'8:3':['thirty thousand'],'8:12':['about five thousand'],'8:13':['north','west','That night'],'8:17':['Ai or Bethel'],'8:25':['men and women','twelve thousand'],'8:29':['tree','sunset','body'],'8:31':['whole stones','iron tool','burnt offerings','peace offerings'],'8:33':['Gerizim','Ebal','Resident foreigners'],'8:35':['women','little ones','resident foreigners']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in verses['Joshua '+ref]['after'].casefold(),(ref,term)
 # Preserve old ledgers and all non-Joshua wording, including TSW and later chapters.
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{c['path'] for c in l['chapters']}|{f'audit/exegetical-core/fluent-production/joshua/Joshua_{c:02}_review.json' for c in range(1,9)}|{'audit/exegetical-core/fluent-production/joshua/'+n for n in ['JOSHUA_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']}
 assert all(n in allowed or n.startswith(str(BATCH.relative_to(ROOT))+'/') for n in changed),changed
 rd='audit/exegetical-core/fluent-production/joshua/'
 old=json.loads(run('git','show',BASE+':'+rd+'BOOK_VERSE_REVIEW_LEDGER.json'));new=json.loads((ROOT/rd/'BOOK_VERSE_REVIEW_LEDGER.json').read_text())
 for prev,now in zip(old['entries'],new['entries']):
  assert all(now[k]==v for k,v in prev.items())
  if prev['chapter']>8:assert prev==now
  else:assert now['status']=='SUPERSEDED'
 assert q['next_work'][0]['scope']=='Joshua 9–12'
 # Record the 23 Hebrew/draft pairs reread for focused risks after first drafting.
 selected=['1:14','2:13','3:16','4:9','4:13','4:19','5:1','5:6','6:18','6:21','7:6','7:17','7:21','7:24','7:25','8:3','8:12','8:13','8:14','8:17','8:25','8:32','8:35'];raw={}
 for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/'joshua-pinned-hebrew.xml').read_text(),re.S):
  e=E.fromstring(s);bk,c,v=e.attrib['osisID'].split('.');raw[f'Joshua {c}:{v}']=(s,e)
 focused=[]
 for ref in selected:
  key='Joshua '+ref;s,e=raw[key];v=verses[key];assert sha(s.encode())==v['source_verse_sha256'];focused.append({'reference':key,'source_verse_sha256':v['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext()) for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode') for x in e if x.tag=='note'],'after':v['after']})
 (BATCH/'focused-comparisons.json').write_text(json.dumps({'qualification':'Authoring self-check after complete first reading of all 186 source verses. No independent review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Joshua 1–8 source binding, structure, selected risk assertions and cumulative ledger preservation','revision_audits':audits,'cumulative_coverage':{'chapters':200,'verses':6146},'structural_chapters':structural,'first_source_reading_verses':186,'focused_source_reread_verses':23,'focused_assertions':checks,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':46,'chapters':8,'new_verses':186,'cumulative_verses':6146}))
if __name__=='__main__':main()
