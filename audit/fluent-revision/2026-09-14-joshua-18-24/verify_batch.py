"""Source identity, structure and recorded risk checks, not scholarly approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='7116136c16308f2e58843ca64b33c5b6b8dfa177'
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
 assert len(audits)==48 and len(paths)==216 and sum(x['verses'] for x in audits)==6618
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
 checks={'18:2': ['seven'], '18:4': ['three men'], '18:7': ['priestly service', 'half'], '18:15': ['west'], '18:18': ['Arabah'], '18:24': ['Chephar-ammonah', 'twelve'], '18:28': ['Gibeath, and Kiriath', 'fourteen'], '19:2': ['Beer-sheba, Sheba'], '19:6': ['thirteen'], '19:15': ['twelve'], '19:22': ['Shahazimah', 'sixteen'], '19:34': ['Judah at the Jordan'], '19:38': ['nineteen'], '19:47': ['slipped from their grasp', 'put it to the sword'], '20:3': ['accidentally', 'without intending'], '20:5': ['not previously hated the victim'], '20:6': ['until standing', 'and until the death'], '20:9': ['resident foreigners', 'before standing'], '21:12': ['fields and villages', 'Caleb'], '21:25': ['Gath-rimmon', 'two towns'], '21:36': ['Bezer', 'Jahaz'], '21:37': ['Kedemoth', 'Mephaath', 'four towns'], '21:41': ['forty-eight'], '21:43': ['all the land'], '21:45': ['Not one word failed', 'It all came to pass'], '22:14': ['Ten leaders', 'each'], '22:19': ['If', 'unclean', 'among us'], '22:20': ['Achan son of Zerah', 'did not die alone'], '22:22': ['The Mighty One, God, the LORD! The Mighty One, God, the LORD!', 'do not save us today'], '22:23': ['burnt offerings', 'grain offerings', 'peace-offering sacrifices'], '22:25': ['no share in the LORD'], '22:27': ['witness', 'generations', 'no share in the LORD'], '22:31': ['from the LORD’s hand'], '22:34': ['Witness'], '23:4': ['remaining nations', 'all the nations I cut off'], '23:7': ['have oaths sworn'], '23:10': ['One', 'thousand'], '23:13': ['trap', 'snare', 'whips', 'sides', 'thorns', 'eyes'], '23:14': ['going the way of all the earth', 'not one word has failed'], '23:15': ['all the harm', 'destroys you'], '24:7': ['he put darkness', 'what I did'], '24:9': ['Balak', 'fought against Israel'], '24:11': ['Amorites, Perizzites, Canaanites, Hittites, Girgashites, Hivites, and Jebusites'], '24:12': ['hornet', 'two Amorite kings', 'not your sword or your bow'], '24:19': ['cannot serve', 'will not forgive'], '24:23': ['foreign gods among you'], '24:26': ['God’s instruction', 'terebinth', 'in the LORD’s sanctuary'], '24:27': ['against us', 'has heard', 'against you'], '24:29': ['one hundred ten'], '24:32': ['one hundred qesitahs', 'sons of Hamor'], '24:33': ['given to his son Phinehas']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in verses['Joshua '+ref]['after'].casefold(),(ref,term)
 # Preserve old ledgers and all non-Joshua wording, including TSW and later chapters.
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{c['path'] for c in l['chapters']}|{f'audit/exegetical-core/fluent-production/joshua/Joshua_{c:02}_review.json' for c in range(18,25)}|{'audit/exegetical-core/fluent-production/joshua/'+n for n in ['JOSHUA_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']}
 assert all(n in allowed or n.startswith(str(BATCH.relative_to(ROOT))+'/') for n in changed),changed
 rd='audit/exegetical-core/fluent-production/joshua/'
 old=json.loads(run('git','show',BASE+':'+rd+'BOOK_VERSE_REVIEW_LEDGER.json'));new=json.loads((ROOT/rd/'BOOK_VERSE_REVIEW_LEDGER.json').read_text())
 for prev,now in zip(old['entries'],new['entries']):
  assert all(now[k]==v for k,v in prev.items())
  if prev['chapter'] not in range(18,25):assert prev==now
  else:assert now['status']=='SUPERSEDED'
 for name in ['JOSHUA_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']:
  prev=json.loads(run('git','show',BASE+':'+rd+name));now=json.loads((ROOT/rd/name).read_text());assert now['revision_batches'][:-1]==prev['revision_batches'];assert now['editorial_review_pending_chapters']==list(range(1,25))
 assert q['next_work'][0]['scope']=='Joshua whole-book consistency review'
 # Record the 56 Hebrew/draft pairs actually reread after drafting.
 selected=['18:7', '18:14', '18:15', '18:18', '18:24', '18:28', '19:2', '19:6', '19:13', '19:22', '19:27', '19:29', '19:33', '19:34', '19:38', '19:47', '20:3', '20:5', '20:6', '20:9', '21:12', '21:25', '21:36', '21:37', '21:41', '21:45', '22:10', '22:11', '22:14', '22:19', '22:20', '22:22', '22:23', '22:25', '22:27', '22:31', '22:34', '23:4', '23:5', '23:7', '23:10', '23:13', '23:14', '23:15', '24:2', '24:7', '24:8', '24:9', '24:11', '24:12', '24:19', '24:23', '24:26', '24:27', '24:32', '24:33'];raw={}
 for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/'joshua-pinned-hebrew.xml').read_text(),re.S):
  e=E.fromstring(s);bk,c,v=e.attrib['osisID'].split('.');raw[f'Joshua {c}:{v}']=(s,e)
 focused=[]
 for ref in selected:
  key='Joshua '+ref;s,e=raw[key];v=verses[key];assert sha(s.encode())==v['source_verse_sha256'];focused.append({'reference':key,'source_verse_sha256':v['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext()) for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode') for x in e if x.tag=='note'],'after':v['after']})
 (BATCH/'focused-comparisons.json').write_text(json.dumps({'qualification':'Authoring self-check after complete first reading of all 216 source verses. No independent review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 # Preserve each Levitical town-and-pasture grant, including both Reubenite verses.
 name_checks=[]
 groups=[(13,18,13),(21,25,10),(27,32,13),(34,39,12)]
 for start,end,count in groups:
  refs=[f'Joshua 21:{v}' for v in range(start,end+1)]
  assert sum(verses[x]['after'].count('with its pasturelands') for x in refs)==count
  name_checks.append({'references':refs,'town_and_pasture_pairs':count})
 assert sum(x[2] for x in groups)==48
 for ref in ['18:24','19:22','20:8','21:27','24:8']:
  assert 'x-qere' in raw['Joshua '+ref][0],ref
 assert 'Shahazumah' not in verses['Joshua 19:22']['after']
 assert 'Beth-arabah' not in verses['Joshua 18:18']['after']
 assert verses['Joshua 23:14']['after'].count('not one word has failed')==2
 # The source's stated totals remain even where the list does not reconcile.
 for ref,total in [('18:24','twelve'),('18:28','fourteen'),('19:6','thirteen'),('19:15','twelve'),('19:22','sixteen'),('19:30','twenty-two'),('19:38','nineteen')]:
  assert total in verses['Joshua '+ref]['after']

 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Joshua 18–24 source binding, structure, selected risk assertions and cumulative ledger preservation','revision_audits':audits,'cumulative_coverage':{'chapters':216,'verses':6618},'structural_chapters':structural,'first_source_reading_verses':216,'focused_source_reread_verses':56,'focused_assertions':checks,'name_and_tally_checks':name_checks,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':48,'chapters':7,'new_verses':216,'cumulative_verses':6618}))
if __name__=='__main__':main()
