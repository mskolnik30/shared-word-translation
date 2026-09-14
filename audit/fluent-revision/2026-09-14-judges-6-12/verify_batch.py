"""Source identity, structure and recorded risk checks, not scholarly approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='641fa1935c2f970e3c842694a01d85356b31f342'
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
 assert len(audits)==50 and len(paths)==228 and sum(x['verses'] for x in audits)==6993
 l=json.loads((BATCH/'judges-verse-review.json').read_text());verses={x['reference']:x for x in l['verses']};structural=[]
 for c in l['chapters']:
  t=(ROOT/c['path']).read_text();m=t.split('---',2)[2].split('## Notes')[0];inside=False
  for line in m.splitlines():
   if line=='<p>':assert not inside;inside=True
   elif line=='</p>':assert inside;inside=False
   elif line.strip() and not line.startswith('## '):assert inside,(c['chapter'],line)
  assert not inside and m.count('“')==m.count('”'),c['chapter']
  for para in m.split('</p>')[:-1]:assert not para.rstrip().endswith((',',':',';','—')),(c['chapter'],para[-90:])
  rv=json.loads((ROOT/f'audit/exegetical-core/fluent-production/judges/Judges_{c["chapter"]:02}_review.json').read_text());assert rv['chapter_binding']==c and rv['publication_allowed'] is False
  structural.append({'chapter':c['chapter'],'verses':c['verse_count'],'sha256':c['after_sha256'],'headings':re.findall(r'^## (.*)$',m,re.M)})
 checks={'6:4': ['Gaza', 'sheep', 'ox', 'donkey'], '6:13': ['abandoned us'], '6:19': ['ephah', 'broth'], '6:25': ['second bull', 'seven years'], '6:34': ['clothed himself with Gideon'], '6:37': ['dew', 'dry'], '6:40': ['dry', 'dew'], '7:3': ['Gilead', 'twenty-two thousand', 'ten thousand'], '7:6': ['three hundred', 'hand'], '7:13': ['barley'], '7:18': ['For the LORD and for Gideon'], '7:20': ['left', 'right', 'sword'], '7:22': ['Beth-shittah', 'Zererah', 'Abel-meholah', 'Tabbath'], '8:2': ['gleanings', 'Abiezer'], '8:7': ['thresh your flesh'], '8:10': ['fifteen thousand', 'One hundred twenty thousand'], '8:14': ['seventy-seven'], '8:16': ['taught', 'thorns'], '8:17': ['killed'], '8:19': ['mother’s sons'], '8:24': ['Ishmaelites'], '8:26': ['one thousand seven hundred', 'shekels'], '8:27': ['ephod', 'prostituted', 'snare'], '8:30': ['seventy sons'], '8:31': ['concubine', 'Abimelech'], '9:1': ['mother’s father'], '9:4': ['seventy shekels', 'Baal-berith'], '9:5': ['seventy sons', 'Jotham', 'survived'], '9:9': ['gods and people'], '9:13': ['gods and people'], '9:15': ['shade', 'fire', 'cedars'], '9:18': ['slave woman'], '9:23': ['God sent an evil spirit'], '9:34': ['four companies'], '9:43': ['three companies'], '9:44': ['companies with him', 'other two'], '9:45': ['salt'], '9:46': ['El-berith'], '9:49': ['thousand men and women'], '9:53': ['woman', 'upper millstone', 'skull'], '9:54': ['A woman killed him'], '10:2': ['twenty-three'], '10:4': ['thirty sons', 'thirty donkeys', 'thirty towns'], '10:6': ['Baals', 'Ashtaroth', 'Aram', 'Sidon', 'Moab', 'Ammonites', 'Philistines'], '10:8': ['That year', 'eighteen years'], '10:12': ['Maon'], '10:16': ['misery'], '11:1': ['prostitute', 'Gilead was his father'], '11:11': ['head and commander'], '11:13': ['Arnon', 'Jabbok', 'Jordan'], '11:24': ['Chemosh', 'land of all those', 'driven out'], '11:25': ['Balak son of Zippor'], '11:26': ['three hundred years'], '11:27': ['Judge, judge'], '11:29': ['Spirit', 'Mizpeh'], '11:31': ['doors', 'and I will offer', 'burnt offering'], '11:33': ['twenty towns', 'Minnith', 'Abel-keramim'], '11:34': ['only child', 'son or daughter'], '11:35': ['You have brought me', 'cannot take it back'], '11:37': ['two months', 'virginity'], '11:39': ['he did to her what he had vowed', 'never known a man'], '11:40': ['daughters', 'four days'], '12:1': ['northward', 'burn'], '12:4': ['fugitives', 'Ephraim and Manasseh'], '12:6': ['Shibboleth', 'Sibboleth', 'slaughtered', 'Forty-two thousand'], '12:7': ['six years', 'one of Gilead’s towns'], '12:9': ['thirty sons and thirty daughters', 'thirty daughters from outside', 'seven years'], '12:12': ['Aijalon', 'Zebulun'], '12:14': ['forty sons', 'thirty grandsons', 'seventy donkeys', 'eight years'], '12:15': ['Amalekites']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in verses['Judges '+ref]['after'].casefold(),(ref,term)
 # Preserve old ledgers and all non-Judges wording, including TSW and later chapters.
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{c['path'] for c in l['chapters']}|{f'audit/exegetical-core/fluent-production/judges/Judges_{c:02}_review.json' for c in range(6,13)}|{'audit/exegetical-core/fluent-production/judges/'+n for n in ['JUDGES_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']}
 assert all(n in allowed or n.startswith(str(BATCH.relative_to(ROOT))+'/') for n in changed),changed
 rd='audit/exegetical-core/fluent-production/judges/'
 old=json.loads(run('git','show',BASE+':'+rd+'BOOK_VERSE_REVIEW_LEDGER.json'));new=json.loads((ROOT/rd/'BOOK_VERSE_REVIEW_LEDGER.json').read_text())
 for prev,now in zip(old['entries'],new['entries']):
  assert all(now[k]==v for k,v in prev.items())
  if prev['chapter'] not in range(6,13):assert prev==now
  else:assert now['status']=='SUPERSEDED'
 assert q['next_work'][0]['scope']=='Judges 13–21'
 # Record the 107 Hebrew/draft pairs reread for focused risks after first drafting.
 selected=['6:2', '6:4', '6:5', '6:8', '6:13', '6:14', '6:15', '6:19', '6:25', '6:26', '6:31', '6:34', '6:37', '6:39', '6:40', '7:3', '7:4', '7:5', '7:6', '7:7', '7:8', '7:13', '7:18', '7:20', '7:22', '7:25', '8:2', '8:6', '8:7', '8:10', '8:14', '8:16', '8:18', '8:19', '8:20', '8:21', '8:24', '8:26', '8:27', '8:30', '8:31', '8:35', '9:1', '9:2', '9:4', '9:5', '9:6', '9:9', '9:13', '9:15', '9:16', '9:18', '9:19', '9:20', '9:23', '9:24', '9:28', '9:31', '9:37', '9:43', '9:44', '9:46', '9:48', '9:49', '9:51', '9:53', '9:54', '9:56', '10:4', '10:6', '10:8', '10:11', '10:12', '10:16', '11:1', '11:8', '11:9', '11:10', '11:11', '11:13', '11:17', '11:19', '11:24', '11:25', '11:26', '11:27', '11:29', '11:30', '11:31', '11:32', '11:33', '11:34', '11:35', '11:36', '11:37', '11:38', '11:39', '11:40', '12:1', '12:4', '12:5', '12:6', '12:7', '12:9', '12:12', '12:14', '12:15'];raw={}
 for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/'judges-pinned-hebrew.xml').read_text(),re.S):
  e=E.fromstring(s);bk,c,v=e.attrib['osisID'].split('.');raw[f'Judges {c}:{v}']=(s,e)
 focused=[]
 for ref in selected:
  key='Judges '+ref;s,e=raw[key];v=verses[key];assert sha(s.encode())==v['source_verse_sha256'];focused.append({'reference':key,'source_verse_sha256':v['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext()) for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode') for x in e if x.tag=='note'],'after':v['after']})
 (BATCH/'focused-comparisons.json').write_text(json.dumps({'qualification':'Authoring self-check after complete first reading of all 230 source verses. No independent review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Judges 6–12 source binding, structure, selected risk assertions and cumulative ledger preservation','revision_audits':audits,'cumulative_coverage':{'chapters':228,'verses':6993},'structural_chapters':structural,'first_source_reading_verses':230,'focused_source_reread_verses':107,'focused_assertions':checks,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':50,'chapters':7,'new_verses':230,'cumulative_verses':6993}))
if __name__=='__main__':main()
