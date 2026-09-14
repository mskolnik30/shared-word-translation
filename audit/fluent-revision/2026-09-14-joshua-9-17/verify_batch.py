"""Source identity, structure and recorded risk checks, not scholarly approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='6600d692480e490e8ebccbadd51c716fe81fc037'
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
 assert len(audits)==47 and len(paths)==209 and sum(x['verses'] for x in audits)==6402
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
 checks={'9:4': ['posing as envoys', 'wineskins'], '9:14': ['took some', 'did not ask'], '9:17': ['Gibeon, Chephirah, Beeroth, and Kiriath-jearim', 'third day'], '9:23': ['cursed', 'slaves', 'always'], '9:24': ['destroy all its inhabitants', 'feared greatly for our lives'], '10:3': ['Hoham king of Hebron', 'Piram king of Jarmuth', 'Japhia king of Lachish', 'Debir king of Eglon'], '10:10': ['The LORD', 'He pursued'], '10:11': ['hailstones', 'More died'], '10:13': ['vengeance', 'Book of Jashar', 'about a full day'], '10:14': ['man’s voice'], '10:20': ['survivors', 'fortified towns'], '10:21': ['sharp tongue'], '10:24': ['feet', 'necks'], '10:26': ['killed them, then hung', 'five trees'], '10:27': ['sunset', 'cave'], '10:32': ['second day'], '10:37': ['king', 'dependent towns', 'everyone'], '10:40': ['everything that breathed', 'destruction'], '11:6': ['tomorrow', 'Hamstring their horses', 'burn their chariots'], '11:13': ['mounds', 'Hazor alone'], '11:14': ['livestock', 'all the people', 'no one breathing'], '11:20': ['LORD who hardened', 'without mercy'], '11:22': ['Gaza, Gath, and Ashdod'], '11:23': ['whole land', 'land rested from war'], '12:2': ['middle of the valley', 'half of Gilead', 'Jabbok'], '12:23': ['Goiim in Gilgal'], '12:24': ['Thirty-one kings'], '13:1': ['land still remains'], '13:3': ['Gaza, Ashdod, Ashkelon, Gath, and Ekron', 'Avvim'], '13:4': ['in the south', 'Mearah'], '13:7': ['nine tribes', 'half-tribe'], '13:13': ['did not drive out', 'Geshur', 'Maacath'], '13:14': ['offerings made by fire'], '13:21': ['Evi, Rekem, Zur, Hur, and Reba'], '13:22': ['Balaam son of Beor', 'diviner', 'killed'], '13:26': ['Lidbir'], '13:30': ['sixty towns'], '13:31': ['Half of Gilead', 'half of Machir’s'], '13:33': ['LORD, the God of Israel, is their inheritance'], '14:7': ['forty years'], '14:10': ['Forty-five', 'eighty-five'], '14:12': ['Perhaps', 'Anakim'], '15:14': ['Sheshai, Ahiman, and Talmai'], '15:17': ['Othniel son of Kenaz, Caleb’s brother'], '15:18': ['she urged Othniel', 'her father'], '15:19': ['blessing', 'upper springs', 'lower springs'], '15:32': ['twenty-nine'], '15:36': ['fourteen'], '15:40': ['Lahmas'], '15:47': ['Great Sea'], '15:49': ['Kiriath-sannah'], '15:53': ['Janum'], '15:63': ['could not drive out', 'Jebusites'], '16:2': ['From Bethel', 'to Luz'], '16:3': ['Lower Beth-horon'], '16:5': ['Upper Beth-horon'], '16:6': ['Michmethath', 'north', 'east', 'Janoah'], '16:10': ['did not drive out', 'forced labor'], '17:3': ['Mahlah, Noah, Hoglah, Milcah, and Tirzah'], '17:4': ['relatives', 'father’s brothers'], '17:5': ['Ten portions', 'besides'], '17:6': ['daughters', 'among his sons'], '17:7': ['opposite Shechem', 'south'], '17:9': ['South', 'Ephraim', 'north side'], '17:11': ['Beth-shean', 'Ibleam', 'Dor, En-dor, Taanach, and Megiddo', 'three heights'], '17:13': ['forced labor', 'still did not drive them out'], '17:16': ['iron chariots', 'Valley of Jezreel'], '17:18': ['clear it', 'even though']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in verses['Joshua '+ref]['after'].casefold(),(ref,term)
 # Preserve old ledgers and all non-Joshua wording, including TSW and later chapters.
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{c['path'] for c in l['chapters']}|{f'audit/exegetical-core/fluent-production/joshua/Joshua_{c:02}_review.json' for c in range(9,18)}|{'audit/exegetical-core/fluent-production/joshua/'+n for n in ['JOSHUA_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']}
 assert all(n in allowed or n.startswith(str(BATCH.relative_to(ROOT))+'/') for n in changed),changed
 rd='audit/exegetical-core/fluent-production/joshua/'
 old=json.loads(run('git','show',BASE+':'+rd+'BOOK_VERSE_REVIEW_LEDGER.json'));new=json.loads((ROOT/rd/'BOOK_VERSE_REVIEW_LEDGER.json').read_text())
 for prev,now in zip(old['entries'],new['entries']):
  assert all(now[k]==v for k,v in prev.items())
  if prev['chapter'] not in range(9,18):assert prev==now
  else:assert now['status']=='SUPERSEDED'
 for name in ['JOSHUA_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']:
  prev=json.loads(run('git','show',BASE+':'+rd+name));now=json.loads((ROOT/rd/name).read_text());assert now['revision_batches'][:-1]==prev['revision_batches'];assert now['editorial_review_pending_chapters']==list(range(1,18))
 assert q['next_work'][0]['scope']=='Joshua 18–24'
 # Record the 53 Hebrew/draft pairs actually reread after drafting.
 selected=['9:4', '9:14', '9:23', '10:10', '10:12', '10:13', '10:20', '10:21', '10:26', '10:37', '10:40', '11:6', '11:13', '11:14', '11:20', '11:22', '11:23', '12:2', '12:3', '12:18', '12:23', '13:3', '13:4', '13:8', '13:14', '13:23', '13:26', '13:30', '13:31', '13:33', '14:7', '14:10', '14:12', '15:17', '15:18', '15:19', '15:32', '15:36', '15:40', '15:47', '15:53', '16:2', '16:6', '16:10', '17:3', '17:4', '17:5', '17:6', '17:7', '17:9', '17:11', '17:13', '17:18'];raw={}
 for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/'joshua-pinned-hebrew.xml').read_text(),re.S):
  e=E.fromstring(s);bk,c,v=e.attrib['osisID'].split('.');raw[f'Joshua {c}:{v}']=(s,e)
 focused=[]
 for ref in selected:
  key='Joshua '+ref;s,e=raw[key];v=verses[key];assert sha(s.encode())==v['source_verse_sha256'];focused.append({'reference':key,'source_verse_sha256':v['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext()) for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode') for x in e if x.tag=='note'],'after':v['after']})
 (BATCH/'focused-comparisons.json').write_text(json.dumps({'qualification':'Authoring self-check after complete first reading of all 256 source verses. No independent review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 # Source tally: one for each king, including a single compound Shimron-meron.
 assert sum(verses[f'Joshua 12:{v}']['after'].count(', one') for v in range(9,25))==31
 assert sum(sum(w.attrib.get('lemma')=='259' for w in raw[f'Joshua 12:{v}'][1] if w.tag=='w') for v in range(9,25))==31
 assert verses['Joshua 10:15']['after']==verses['Joshua 10:43']['after']
 name_checks=[]
 for vv in range(21,63):
  if vv in (45,46,47):continue
  ref=f'Joshua 15:{vv}';item=verses[ref];before=item['tsw_comparator'];after=item['after']
  # A finite proper-name list is an appropriate comparator for order; it does not set the prose wording.
  names=re.findall(r"\b[A-Z][a-z]+(?:-[A-Z][a-z]+)*\b",before)
  names=[n for n in names if n not in {'The','In','City','Salt','Judah','Edom'}]
  if vv==21:names=names[names.index('Kabzeel'):]
  posn=0
  for name in names:
   expected={'Beersheba':'Beer-sheba','Lahmam':'Lahmas','Janim':'Janum'}.get(name,name).casefold()
   loc=after.casefold().find(expected,posn);assert loc>=0,(ref,name,expected,after);posn=loc+len(expected)
  name_checks.append({'reference':ref,'comparator_names_in_order':names,'source_spelling_exceptions':{'Beersheba':'Beer-sheba','Lahmam':'Lahmas','Janim':'Janum'} if vv in (28,40,53) else {}})
 # Every source note, including both written/read alternatives, remains in the hashed record.
 for ref,needle in [('15:47','x-qere'),('15:53','x-qere')]:assert needle in raw['Joshua '+ref][0]
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Joshua 9–17 source binding, structure, selected risk assertions and cumulative ledger preservation','revision_audits':audits,'cumulative_coverage':{'chapters':209,'verses':6402},'structural_chapters':structural,'first_source_reading_verses':256,'focused_source_reread_verses':53,'focused_assertions':checks,'name_and_tally_checks':name_checks,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':47,'chapters':9,'new_verses':256,'cumulative_verses':6402}))
if __name__=='__main__':main()
