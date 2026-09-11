"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='cae294fa8084b00288c53f7815ff889fe8c207d1';COUNTS={1:54,2:34}
sys.path.insert(0,str(ROOT/'tools'))
from audit_translation_overlap import words

def run(*args):
 r=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
 return r.stdout.strip()
def put(name,d):(BATCH/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser()
 for book in ['genesis','exodus','leviticus','numbers','james']:p.add_argument('--'+book+'-source',type=Path,required=True)
 args=p.parse_args();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];chapters=set();refs={}
 for s in q['completed_draft_scopes']:
  book=s['scope'].split()[0];l=json.loads((ROOT/s['ledger']).read_text())
  audits.append({'ledger':s['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',s['ledger'],'--source-text',str(getattr(args,book.lower()+'_source').resolve())))})
  for c in l['chapters']:assert c['path'] not in chapters;chapters.add(c['path'])
  rs=refs.setdefault(book,set())
  for v in l['verses']:assert v['source_reference'] not in rs;rs.add(v['source_reference'])
 assert len(audits)==31 and len(chapters)==124 and sum(a['verses'] for a in audits)==3801
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':88}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Num '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Num '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==88
 annotated=[ref for ref in byref if '<note' in raw['Num '+ref]];assert annotated==['1:16']
 assert sum(raw['Num '+ref].count('<note') for ref in byref)==1
 assert 'קריאי' in raw['Num 1:16'] and 'קְרוּאֵ֣י' in raw['Num 1:16']
 for c,n in COUNTS.items():
  t=(ROOT/f'translations/fluent/OT/numbers/Numbers_{c:02}.md').read_text();m=t.split('---',2)[2].split('## Notes')[0]
  assert re.findall(r'^v(\d\d):',m,re.M)==[f'{v:02}' for v in range(1,n+1)]
  assert m.count('“')==m.count('”')
  for s in m.split('</p>')[:-1]:assert not s.rstrip().endswith((',',':',';','—'))
  inside=False
  for line in m.splitlines():
   if line=='<p>':assert not inside;inside=True
   elif line=='</p>':assert inside;inside=False
   elif line.strip() and not line.startswith('## '):assert inside,(c,line)
  assert not inside
  assert all(s in t for s in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
 checks={'1:1': ['first day of the second month', 'second year', 'Egypt', 'Moses', 'Sinai', 'tent of meeting'], '1:2': ['whole Israelite community', 'clan', 'ancestral household', 'every male', 'one by one'], '1:3': ['twenty years old and upward', 'army', 'You and Aaron', 'military divisions'], '1:10': ['Joseph', 'Ephraim', 'Elishama son of Ammihud', 'Manasseh', 'Gamaliel son of Pedahzur'], '1:14': ['Eliasaph son of Deuel'], '1:16': ['called', 'community', 'ancestral tribes', 'thousands'], '1:18': ['first day of the second month', 'declared their ancestry', 'twenty years old and upward', 'one by one'], '1:20': ['Israel’s firstborn', 'every male', 'one by one'], '1:22': ['every male', 'one by one'], '1:44': ['Moses, Aaron', 'twelve leaders', 'ancestral household'], '1:47': ['Levites', 'not registered', 'ancestral tribe'], '1:49': ['Do not register', 'Levi', 'or include'], '1:50': ['tabernacle of the testimony', 'furnishings', 'carry', 'care for it', 'camp around'], '1:51': ['take it down', 'erect it', 'unauthorized person', 'put to death'], '1:53': ['wrath', 'keep charge'], '1:54': ['did everything', 'That is what they did'], '2:1': ['Moses and Aaron'], '2:2': ['standards', 'identifying signs', 'ancestral households', 'around', 'distance'], '2:3': ['east', 'sunrise'], '2:9': ['set out first'], '2:10': ['south'], '2:14': ['Eliasaph son of Reuel'], '2:16': ['set out second'], '2:17': ['tent of meeting', 'Levites', 'middle', 'march as they camp', 'assigned place'], '2:18': ['west'], '2:24': ['set out third'], '2:25': ['north'], '2:31': ['set out last', 'standards'], '2:33': ['Levites', 'not registered', 'other Israelites', 'commanded Moses'], '2:34': ['camped', 'standards', 'set out', 'clan', 'ancestral household']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 # Values transcribed from the Hebrew source, paired across the two lists.
 census=[('Reuben',21,11,46500),('Simeon',23,13,59300),('Gad',25,15,45650),('Judah',27,4,74600),('Issachar',29,6,54400),('Zebulun',31,8,57400),('Ephraim',33,19,40500),('Manasseh',35,21,32200),('Benjamin',37,23,35400),('Dan',39,26,62700),('Asher',41,28,41500),('Naphtali',43,30,53400)]
 for tribe,v1,v2,n in census:
  assert tribe in byref[f'1:{v1}']['after']
  for ref in [f'1:{v1}',f'2:{v2}']:assert re.findall(r'\d[\d,]*',byref[ref]['after'])==[f'{n:,}']
 camp_totals={9:186400,16:151450,24:108100,31:157600}
 for v,n in camp_totals.items():assert re.findall(r'\d[\d,]*',byref[f'2:{v}']['after'])==[f'{n:,}']
 tribal={x[0]:x[3] for x in census}
 for tribes,v in [(('Judah','Issachar','Zebulun'),9),(('Reuben','Simeon','Gad'),16),(('Ephraim','Manasseh','Benjamin'),24),(('Dan','Asher','Naphtali'),31)]:assert sum(tribal[t] for t in tribes)==camp_totals[v]
 assert sum(tribal.values())==sum(camp_totals.values())==603550
 assert all('603,550' in byref[ref]['after'] for ref in ['1:46','2:32'])
 names=[(5,10,'Elizur son of Shedeur'),(6,12,'Shelumiel son of Zurishaddai'),(7,3,'Nahshon son of Amminadab'),(8,5,'Nethanel son of Zuar'),(9,7,'Eliab son of Helon'),(10,18,'Elishama son of Ammihud'),(10,20,'Gamaliel son of Pedahzur'),(11,22,'Abidan son of Gideoni'),(12,25,'Ahiezer son of Ammishaddai'),(13,27,'Pagiel son of Ochran'),(15,29,'Ahira son of Enan')]
 for v1,v2,name in names:assert all(name in byref[ref]['after'] for ref in [f'1:{v1}',f'2:{v2}'])
 assert 'דְּעוּאֵֽל' in raw['Num 1:14'] and 'רְעוּאֵֽל' in raw['Num 2:14']
 assert byref['1:53']['after'].count('tabernacle of the testimony')==2
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==[1,2]
  assert len(new['revision_batches'])==1 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 1–2; 88 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 1–2; 88 verses','revision_audits':audits,'cumulative_coverage':{'chapters':124,'verses':3801},'source_record_count':1289,'public_source_mapping':'Numbers 1–2 aligns directly; all 88 records are unique and complete, including the original written/read annotation at 1:16. Earlier books and their public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'paired_census_counts':census,'camp_totals':camp_totals,'leader_pairs':names,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 88 pinned Hebrew verses and the 1:16 written/read annotation before drafting. NET comparison and selected translators’ notes were consulted after the Hebrew reading, with focused notes checked after drafting. All 88 TSW comparators were read after drafting. Self-checks cover all leader/patronymic pairs, Deuel/Reuel, twelve paired counts, four camp subtotals and the aggregate, military scope, kinship levels, named directions, marching order, repeated tabernacle terminology, the Levite exception and the unauthorized approach death penalty. These are authoring self-checks, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':31,'chapters':124,'verses':3801,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
