"""Source identity, structure and recorded risk checks, not scholarly approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='1bee833986b0aff270b3f5f50f26357f29783223'
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
 assert len(audits)==49 and len(paths)==221 and sum(x['verses'] for x in audits)==6763
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
 checks={'1:4': ['ten thousand'], '1:6': ['thumbs', 'big toes'], '1:7': ['Seventy', 'under my table'], '1:13': ['Othniel son of Kenaz', 'younger brother', 'Achsah'], '1:16': ['Kenite', 'City of Palms', 'Negev', 'Arad'], '1:18': ['Gaza and its territory', 'Ashkelon and its territory', 'Ekron and its territory'], '1:19': ['LORD was with Judah', 'could not drive out', 'iron chariots'], '1:21': ['Benjamin', 'Jebusites'], '1:27': ['Beth-shean', 'Taanach', 'Dor', 'Ibleam', 'Megiddo'], '1:31': ['Acco, Sidon, Ahlab, Achzib, Helbah, Aphik, or Rehob'], '1:32': ['Asher’s people lived among the Canaanites'], '1:35': ['Mount Heres, Aijalon, and Shaalbim', 'heavy hand', 'forced labor'], '2:3': ['thorns in your sides', 'snare'], '2:6': ['Joshua had sent', 'inheritance'], '2:8': ['one hundred ten'], '2:9': ['Timnath-heres', 'Gaash'], '2:13': ['Ashtaroth'], '2:17': ['prostituted themselves'], '2:18': ['groaning', 'compassion'], '3:3': ['five Philistine rulers', 'Sidonians', 'Hivites', 'Baal-hermon', 'Lebo-hamath'], '3:6': ['daughters as wives', 'daughters to those peoples’ sons'], '3:7': ['Asheroth'], '3:8': ['Aram-naharaim', 'eight years'], '3:10': ['Spirit', 'judged Israel', 'king of Aram'], '3:11': ['forty years'], '3:14': ['eighteen years'], '3:15': ['left-handed', 'Benjaminite'], '3:16': ['double-edged', 'gomed', 'right thigh'], '3:21': ['left hand', 'right thigh', 'belly'], '3:22': ['hilt', 'fat', 'excrement'], '3:24': ['relieving himself'], '3:29': ['about ten thousand', 'Not one escaped'], '3:30': ['eighty years'], '3:31': ['six hundred', 'oxgoad'], '4:3': ['nine hundred', 'twenty years'], '4:4': ['prophetess', 'wife of Lappidoth', 'judging Israel'], '4:6': ['ten thousand', 'Naphtali and Zebulun'], '4:9': ['sell Sisera into a woman’s hand'], '4:11': ['Hobab', 'Zaanannim'], '4:13': ['nine hundred iron chariots'], '4:16': ['not one man remained'], '4:20': ['Is a man here?'], '4:21': ['temple into the ground', 'fast asleep', 'He died'], '5:8': ['forty thousand'], '5:10': ['female donkeys'], '5:12': ['Awake, awake, Deborah!', 'Awake, awake!'], '5:15': ['resolves of heart', 'sent into the valley'], '5:16': ['searchings of heart'], '5:20': ['stars fought', 'courses'], '5:21': ['ancient wadi', 'my soul'], '5:22': ['galloping, galloping'], '5:26': ['right hand', 'crushed his head', 'pierced his temple'], '5:27': ['Between her feet', 'destroyed'], '5:30': ['a womb, two wombs', 'plunder', 'necks'], '5:31': ['your enemies', 'love him', 'forty years']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in verses['Judges '+ref]['after'].casefold(),(ref,term)
 # Preserve old ledgers and all non-Judges wording, including TSW and later chapters.
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{c['path'] for c in l['chapters']}|{f'audit/exegetical-core/fluent-production/judges/Judges_{c:02}_review.json' for c in range(1,6)}|{'audit/exegetical-core/fluent-production/judges/'+n for n in ['JUDGES_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']}
 assert all(n in allowed or n.startswith(str(BATCH.relative_to(ROOT))+'/') for n in changed),changed
 rd='audit/exegetical-core/fluent-production/judges/'
 old=json.loads(run('git','show',BASE+':'+rd+'BOOK_VERSE_REVIEW_LEDGER.json'));new=json.loads((ROOT/rd/'BOOK_VERSE_REVIEW_LEDGER.json').read_text())
 for prev,now in zip(old['entries'],new['entries']):
  assert all(now[k]==v for k,v in prev.items())
  if prev['chapter']>5:assert prev==now
  else:assert now['status']=='SUPERSEDED'
 assert q['next_work'][0]['scope']=='Judges 6–12'
 # Record the 88 Hebrew/draft pairs reread for focused risks after first drafting.
 selected=['1:6', '1:7', '1:13', '1:14', '1:16', '1:18', '1:19', '1:21', '1:27', '1:31', '1:32', '1:33', '1:35', '1:36', '2:1', '2:3', '2:6', '2:9', '2:13', '2:17', '2:18', '2:22', '3:2', '3:3', '3:6', '3:7', '3:8', '3:9', '3:10', '3:11', '3:14', '3:15', '3:16', '3:19', '3:20', '3:21', '3:22', '3:23', '3:24', '3:29', '3:30', '3:31', '4:2', '4:3', '4:4', '4:6', '4:7', '4:9', '4:10', '4:11', '4:13', '4:15', '4:16', '4:17', '4:20', '4:21', '4:24', '5:1', '5:2', '5:3', '5:4', '5:5', '5:6', '5:7', '5:8', '5:9', '5:10', '5:11', '5:12', '5:13', '5:14', '5:15', '5:16', '5:17', '5:18', '5:19', '5:20', '5:21', '5:22', '5:23', '5:24', '5:25', '5:26', '5:27', '5:28', '5:29', '5:30', '5:31'];raw={}
 for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/'judges-pinned-hebrew.xml').read_text(),re.S):
  e=E.fromstring(s);bk,c,v=e.attrib['osisID'].split('.');raw[f'Judges {c}:{v}']=(s,e)
 focused=[]
 for ref in selected:
  key='Judges '+ref;s,e=raw[key];v=verses[key];assert sha(s.encode())==v['source_verse_sha256'];focused.append({'reference':key,'source_verse_sha256':v['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext()) for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode') for x in e if x.tag=='note'],'after':v['after']})
 (BATCH/'focused-comparisons.json').write_text(json.dumps({'qualification':'Authoring self-check after complete first reading of all 145 source verses. No independent review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Judges 1–5 source binding, structure, selected risk assertions and cumulative ledger preservation','revision_audits':audits,'cumulative_coverage':{'chapters':221,'verses':6763},'structural_chapters':structural,'first_source_reading_verses':145,'focused_source_reread_verses':88,'focused_assertions':checks,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':49,'chapters':5,'new_verses':145,'cumulative_verses':6763}))
if __name__=='__main__':main()
