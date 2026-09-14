"""Source identity, structure and recorded risk checks, not scholarly approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='59b751f3aa3f763d7c2af6c3662f1e9cbe8b83dd'
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
 assert len(audits)==51 and len(paths)==237 and sum(x['verses'] for x in audits)==7236
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
 checks={'13:5': ['Nazirite', 'womb', 'begin to rescue'], '13:7': ['until the day he dies'], '13:14': ['grapevine', 'strong drink', 'unclean'], '13:19': ['The LORD did something wondrous'], '13:23': ['kill us', 'accepted', 'shown', 'told'], '13:25': ['Mahaneh-dan', 'Zorah', 'Eshtaol'], '14:3': ['uncircumcised', 'right in my eyes'], '14:4': ['LORD, who was seeking'], '14:6': ['Spirit', 'young goat', 'nothing in his hand'], '14:12': ['seven days', 'thirty linen', 'thirty changes'], '14:14': ['eater', 'strong', 'three days'], '14:15': ['seventh day', 'burn'], '14:17': ['seven days', 'seventh day'], '14:18': ['heifer', 'plowed'], '14:19': ['Spirit', 'Ashkelon', 'killed thirty'], '15:4': ['three hundred', 'tail to tail'], '15:5': ['stacked grain', 'standing crops', 'olive orchards'], '15:6': ['burned her and her father to death'], '15:8': ['hip and thigh', 'slaughter'], '15:11': ['Three thousand'], '15:16': ['heaps upon heaps', 'thousand'], '15:19': ['hollow at Lehi', 'spirit returned', 'En-hakkore'], '15:20': ['twenty years', 'Philistines'], '16:1': ['prostitute', 'slept with her'], '16:3': ['midnight', 'two posts', 'bar', 'facing Hebron'], '16:5': ['Each of us', 'eleven hundred'], '16:13': ['seven locks', 'loom—'], '16:17': ['all that was in his heart', 'Nazirite'], '16:18': ['all his heart'], '16:19': ['knees', 'had the seven locks', 'afflict'], '16:20': ['LORD had left him'], '16:21': ['gouged out his eyes', 'ground grain'], '16:24': ['multiplied our dead'], '16:27': ['On the roof', 'about three thousand men and women'], '16:28': ['one of my two eyes'], '16:30': ['Let me die', 'more people'], '16:31': ['twenty years'], '17:2': ['curse in my hearing', 'I took it'], '17:3': ['eleven hundred', 'LORD', 'carved image', 'cast image'], '17:4': ['two hundred'], '17:5': ['ephod', 'teraphim', 'sons'], '17:7': ['clan of Judah', 'Levite'], '17:10': ['father and priest', 'ten shekels', 'year'], '17:13': ['Micah said'], '18:1': ['no inheritance had fallen'], '18:6': ['before the LORD'], '18:7': ['power to oppress', 'no dealings with anyone'], '18:11': ['Six hundred'], '18:17': ['carved image', 'ephod', 'teraphim', 'cast image'], '18:18': ['carved image', 'ephod', 'teraphim', 'cast image'], '18:19': ['hand over your mouth', 'father and priest'], '18:27': ['quiet and secure', 'sword', 'burned'], '18:30': ['Jonathan', 'Gershom', 'Manasseh', 'exile'], '19:2': ['unfaithful'], '19:3': ['she brought him'], '19:18': ['house of the LORD'], '19:22': ['have sex with him'], '19:24': ['Violate them', 'good in your eyes'], '19:25': ['seized his concubine', 'raped', 'abused', 'all night'], '19:27': ['master', 'hands on the threshold'], '19:28': ['no answer'], '19:29': ['twelve pieces'], '20:4': ['murdered'], '20:5': ['kill me'], '20:10': ['ten men from every hundred', 'hundred from every thousand', 'thousand from every ten thousand', 'Geba'], '20:15': ['twenty-six thousand', 'seven hundred'], '20:16': ['left-handed', 'hair', 'not miss'], '20:18': ['Who should go up first', 'Judah first'], '20:21': ['twenty-two thousand'], '20:23': ['my brother Benjamin'], '20:25': ['eighteen thousand'], '20:28': ['Phinehas son of Eleazar, son of Aaron', 'before it', 'tomorrow'], '20:31': ['Bethel', 'Gibeah', 'About thirty'], '20:33': ['Baal-tamar', 'Geba'], '20:35': ['twenty-five thousand one hundred'], '20:39': ['turned back', 'about thirty'], '20:42': ['towns'], '20:43': ['resting place'], '20:45': ['gleaned five thousand', 'Gidom', 'two thousand'], '20:46': ['twenty-five thousand'], '20:47': ['Six hundred', 'four months'], '20:48': ['whole towns', 'livestock', 'every town'], '21:1': ['give his daughter'], '21:5': ['must be put to death'], '21:10': ['twelve thousand', 'women and children'], '21:11': ['devote to destruction', 'every male'], '21:12': ['four hundred', 'virgins', 'Shiloh', 'Canaan'], '21:14': ['gave them the women', 'not enough'], '21:15': ['LORD had made a breach'], '21:19': ['north of Bethel', 'east of the road', 'south of Lebonah'], '21:21': ['seize a wife'], '21:22': ['You did not give', 'otherwise'], '21:23': ['carried off']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in verses['Judges '+ref]['after'].casefold(),(ref,term)
 assert verses['Judges 17:6']['after']==verses['Judges 21:25']['after']
 assert 'cast image' not in verses['Judges 18:20']['after']
 assert 'dead' not in verses['Judges 19:28']['after']
 # Preserve old ledgers and all non-Judges wording, including TSW and later chapters.
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{c['path'] for c in l['chapters']}|{f'audit/exegetical-core/fluent-production/judges/Judges_{c:02}_review.json' for c in range(13,22)}|{'audit/exegetical-core/fluent-production/judges/'+n for n in ['JUDGES_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','APPROVE_QA.json']}
 assert all(n in allowed or n.startswith(str(BATCH.relative_to(ROOT))+'/') for n in changed),changed
 rd='audit/exegetical-core/fluent-production/judges/'
 old=json.loads(run('git','show',BASE+':'+rd+'BOOK_VERSE_REVIEW_LEDGER.json'));new=json.loads((ROOT/rd/'BOOK_VERSE_REVIEW_LEDGER.json').read_text())
 for prev,now in zip(old['entries'],new['entries']):
  assert all(now[k]==v for k,v in prev.items())
  if prev['chapter'] not in range(13,22):assert prev==now
  else:assert now['status']=='SUPERSEDED'
 assert q['next_work'][0]['scope']=='Judges whole-book consistency review'
 # Record the 125 Hebrew/draft pairs reread for focused risks after first drafting.
 selected=['13:3', '13:5', '13:7', '13:12', '13:14', '13:18', '13:19', '13:23', '13:25', '14:3', '14:4', '14:6', '14:7', '14:11', '14:14', '14:15', '14:17', '14:18', '14:19', '14:20', '15:3', '15:4', '15:5', '15:6', '15:8', '15:14', '15:16', '15:19', '15:20', '16:1', '16:3', '16:5', '16:7', '16:13', '16:14', '16:17', '16:18', '16:19', '16:20', '16:21', '16:24', '16:27', '16:28', '16:30', '17:2', '17:3', '17:4', '17:5', '17:6', '17:7', '17:10', '17:12', '17:13', '18:1', '18:3', '18:6', '18:7', '18:10', '18:17', '18:18', '18:19', '18:20', '18:24', '18:25', '18:27', '18:28', '18:30', '18:31', '19:2', '19:3', '19:8', '19:12', '19:18', '19:19', '19:22', '19:23', '19:24', '19:25', '19:26', '19:27', '19:28', '19:29', '19:30', '20:4', '20:5', '20:6', '20:9', '20:10', '20:12', '20:15', '20:16', '20:18', '20:21', '20:23', '20:25', '20:27', '20:28', '20:31', '20:33', '20:35', '20:36', '20:39', '20:42', '20:43', '20:45', '20:46', '20:47', '20:48', '21:1', '21:5', '21:7', '21:10', '21:11', '21:12', '21:14', '21:15', '21:16', '21:17', '21:18', '21:19', '21:20', '21:21', '21:22', '21:23', '21:25'];raw={}
 for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/'judges-pinned-hebrew.xml').read_text(),re.S):
  e=E.fromstring(s);bk,c,v=e.attrib['osisID'].split('.');raw[f'Judges {c}:{v}']=(s,e)
 focused=[]
 for ref in selected:
  key='Judges '+ref;s,e=raw[key];v=verses[key];assert sha(s.encode())==v['source_verse_sha256'];focused.append({'reference':key,'source_verse_sha256':v['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext()) for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode') for x in e if x.tag=='note'],'after':v['after']})
 (BATCH/'focused-comparisons.json').write_text(json.dumps({'qualification':'Authoring self-check after complete first reading of all 243 source verses. No independent review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Judges 13–21 source binding, structure, selected risk assertions and cumulative ledger preservation','revision_audits':audits,'cumulative_coverage':{'chapters':237,'verses':7236},'structural_chapters':structural,'first_source_reading_verses':243,'focused_source_reread_verses':125,'focused_assertions':checks,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':51,'chapters':9,'new_verses':243,'cumulative_verses':7236}))
if __name__=='__main__':main()
