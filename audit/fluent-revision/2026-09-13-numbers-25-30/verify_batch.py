"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='139400ef537e1121695f777f836cd16cc2afffa8';COUNTS={25:18,26:65,27:23,28:31,29:40,30:16}
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
  for v in l['verses']:
   for segment in v.get('source_segments',[v]):
    ref=segment['source_reference'];assert ref not in rs;rs.add(ref)
 assert len(audits)==39 and len(chapters)==152 and sum(a['verses'] for a in audits)==4773
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':1061}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 def binding(ref):
  c,v=map(int,ref.split(':'))
  return f'Num 30:{v+1}' if c==30 else 'Num 30:1' if c==29 and v==40 else 'Num '+ref
 source_refs=[]
 for ref,v in byref.items():
  sr=binding(ref)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
  for segment in v.get('source_segments',[v]):
   sr=segment['source_reference'];source_refs.append(sr)
   assert segment['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len(source_refs)==len(set(source_refs))==194
 assert set(source_refs)=={ref for ref in raw if 25<=int(ref.split()[1].split(':')[0])<=30}
 assert [v['source_reference'] for v in byref['26:1']['source_segments']]==['Num 25:19','Num 26:1']
 annotated=[ref for ref in source_refs if '<note' in raw[ref]]
 assert annotated==['Num 25:2','Num 25:19','Num 26:7','Num 26:9','Num 27:5','Num 27:9','Num 29:15']+[f'Num 30:{v}' for v in range(1,18)]
 assert sum(raw[ref].count('<note') for ref in annotated)==25
 assert 'x-ketiv' in raw['Num 26:9'] and 'x-qere' in raw['Num 26:9']
 assert '\u05c4' in raw['Num 29:15']
 # Exercise the newly required multi-record binding failures with real source bytes.
 import copy
 from audit_fluent_revision import audit
 mutations={}
 for case in ['missing_segment','changed_hash','duplicate_segment','reversed_segments','unknown_segment','invalid_shape','primary_not_in_segments']:
  bad=copy.deepcopy(l);v=next(x for x in bad['verses'] if x['reference']=='Numbers 26:1')
  if case=='missing_segment':del v['source_segments']
  elif case=='changed_hash':v['source_segments'][0]['source_verse_sha256']='0'*64
  elif case=='duplicate_segment':v['source_segments'].append(copy.deepcopy(v['source_segments'][0]))
  elif case=='reversed_segments':v['source_segments'].reverse()
  elif case=='unknown_segment':v['source_segments'][0]['source_reference']='Num 99:1'
  elif case=='invalid_shape':v['source_segments']={}
  else:v['source_reference']='Num 26:2';v['source_verse_sha256']=hashlib.sha256(raw['Num 26:2'].encode()).hexdigest()
  errors=audit(ROOT,bad,args.numbers_source.read_bytes());assert errors,case
  mutations[case]=errors
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
 checks={'25:1': ['Shittim', 'prostitute', 'women of Moab'], '25:2': ['The women invited', 'ate', 'bowed'], '25:3': ['yoked', 'Baal of Peor'], '25:4': ['all the leaders', 'hang them up', 'broad daylight'], '25:5': ['Each of you', 'kill'], '25:6': ['Midianite', 'full view', 'weeping'], '25:7': ['Phinehas', 'Eleazar', 'Aaron', 'spear'], '25:8': ['both of them', 'abdomen', 'plague'], '25:9': ['Twenty-four thousand'], '25:11': ['my own zeal', 'my zeal'], '25:12': ['covenant of peace'], '25:13': ['descendants', 'priesthood', 'atonement'], '25:14': ['Zimri', 'Salu', 'Simeonites'], '25:15': ['Cozbi', 'Zur', 'ancestral house'], '25:18': ['kinswoman', 'Peor'], '26:1': ['After the plague', 'Eleazar', 'Aaron'], '26:2': ['twenty years', 'ancestral house', 'army'], '26:9': ['Nemuel', 'Dathan', 'Abiram', 'Korah'], '26:10': ['mouth', 'Korah', 'two hundred and fifty'], '26:11': ['sons did not die'], '26:33': ['no sons', 'Mahlah, Noah, Hoglah, Milcah and Tirzah'], '26:46': ['Serah'], '26:54': ['larger', 'smaller', 'census total'], '26:55': ['by lot', 'ancestral tribes'], '26:59': ['Jochebed', 'born to Levi in Egypt', 'Aaron', 'Moses', 'Miriam'], '26:61': ['Nadab', 'Abihu', 'unauthorized fire'], '26:62': ['twenty-three thousand males', 'one month', 'not counted', 'no inheritance'], '26:65': ['Caleb', 'Jephunneh', 'Joshua', 'Nun'], '27:1': ['Hepher', 'Gilead', 'Machir', 'Manasseh', 'Joseph', 'Mahlah, Noah, Hoglah, Milcah and Tirzah'], '27:2': ['leaders and the whole community'], '27:3': ['own sin', 'no sons'], '27:4': ['name', 'landholding', 'father’s brothers'], '27:7': ['daughters are right', 'Transfer', 'to them'], '27:8': ['without a son', 'daughter'], '27:9': ['no daughter', 'brothers'], '27:10': ['no brothers', 'father’s brothers'], '27:11': ['nearest relative', 'clan'], '27:12': ['Abarim'], '27:13': ['gathered to your people', 'Aaron'], '27:14': ['you both', 'Meribah', 'Kadesh', 'Zin'], '27:16': ['spirits of all flesh'], '27:17': ['go out before', 'come in before', 'lead them out', 'bring them in', 'sheep without a shepherd'], '27:18': ['Joshua', 'Nun', 'spirit', 'your hand'], '27:20': ['some of your authority'], '27:21': ['Eleazar', 'Urim', 'At his word'], '27:23': ['his hands', 'through Moses'], '28:2': ['my food', 'appointed time'], '28:3': ['two year-old male lambs', 'without defect', 'each day'], '28:4': ['morning', 'twilight'], '28:5': ['one-tenth', 'ephah', 'one-quarter', 'hin', 'beaten olives'], '28:6': ['Mount Sinai'], '28:7': ['one-quarter', 'each lamb', 'fermented drink', 'holy place'], '28:9': ['two year-old male lambs', 'two-tenths'], '28:10': ['in addition'], '28:11': ['two young bulls', 'one ram', 'seven year-old male lambs'], '28:12': ['each bull', 'three-tenths', 'ram two-tenths'], '28:13': ['each lamb', 'one-tenth'], '28:14': ['wine', 'half a hin', 'one-third', 'one-quarter'], '28:15': ['one male goat', 'sin offering'], '28:16': ['fourteenth', 'first month', 'Passover'], '28:17': ['fifteenth', 'seven days', 'unleavened'], '28:18': ['ordinary work'], '28:19': ['two young bulls', 'one ram', 'seven year-old male lambs'], '28:20': ['three-tenths', 'two-tenths'], '28:21': ['one-tenth', 'seven lambs'], '28:22': ['one male goat', 'atonement'], '28:23': ['morning'], '28:24': ['each day for seven days', 'in addition'], '28:25': ['seventh day', 'ordinary work'], '28:26': ['firstfruits', 'Weeks'], '28:27': ['two young bulls', 'one ram', 'seven year-old male lambs'], '28:28': ['three-tenths', 'two-tenths'], '28:29': ['one-tenth', 'seven lambs'], '28:30': ['male goat', 'atonement'], '28:31': ['drink offerings', 'in addition', 'without defect'], '29:1': ['first day', 'seventh month', 'blasts', 'ordinary work'], '29:2': ['one young bull', 'one ram', 'seven year-old male lambs'], '29:3': ['three-tenths', 'two-tenths'], '29:4': ['one-tenth', 'seven lambs'], '29:5': ['one male goat', 'atonement'], '29:6': ['monthly burnt offering', 'regular burnt offering'], '29:7': ['tenth day', 'Humble yourselves', 'no work at all'], '29:8': ['one young bull', 'one ram', 'seven year-old male lambs'], '29:9': ['three-tenths', 'two-tenths'], '29:10': ['one-tenth', 'seven lambs'], '29:11': ['one male goat', 'sin offering of atonement', 'regular burnt offering'], '29:12': ['fifteenth', 'seventh month', 'seven days'], '29:14': ['three-tenths', 'thirteen bulls', 'two-tenths', 'two rams'], '29:15': ['one-tenth', 'fourteen lambs'], '29:35': ['eighth day', 'solemn gathering'], '29:36': ['one bull', 'one ram', 'seven year-old male lambs'], '29:39': ['vowed', 'freewill', 'burnt offerings', 'grain offerings', 'drink offerings', 'peace offerings'], '29:40': ['Moses told', 'everything'], '30:2': ['a man', 'vow', 'oath', 'must not break'], '30:3': ['young woman', 'father’s house'], '30:4': ['father hears', 'says nothing', 'vows stand'], '30:5': ['day he hears', 'none', 'forgive'], '30:6': ['marries', 'still binding', 'rashly'], '30:7': ['day he hears', 'vows stand'], '30:8': ['day he hears', 'cancels', 'rash words', 'forgive'], '30:9': ['widow', 'divorced', 'binding on her'], '30:10': ['husband’s house', 'oath'], '30:11': ['does not forbid', 'vows stand'], '30:12': ['day he hears', 'nothing', 'forgive'], '30:13': ['confirm or cancel', 'humble herself'], '30:14': ['day to day', 'day he heard'], '30:15': ['after he has heard', 'bear her guilt'], '30:16': ['husband and wife', 'young daughter', 'father’s house']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 census={7:(43730,'forty-three thousand seven hundred and thirty'),14:(22200,'twenty-two thousand two hundred'),18:(40500,'forty thousand five hundred'),22:(76500,'seventy-six thousand five hundred'),25:(64300,'sixty-four thousand three hundred'),27:(60500,'sixty thousand five hundred'),34:(52700,'fifty-two thousand seven hundred'),37:(32500,'thirty-two thousand five hundred'),41:(45600,'forty-five thousand six hundred'),43:(64400,'sixty-four thousand four hundred'),47:(53400,'fifty-three thousand four hundred'),50:(45400,'forty-five thousand four hundred')}
 for v,(n,t) in census.items():assert t in byref[f'26:{v}']['after']
 assert sum(n for n,t in census.values())==601730
 assert 'six hundred and one thousand seven hundred and thirty' in byref['26:51']['after']
 founders={5:['Hanoch','Pallu'],6:['Hezron','Carmi'],12:['Nemuel','Jamin','Jachin'],13:['Zerah','Shaul'],15:['Zephon','Haggi','Shuni'],16:['Ozni','Eri'],17:['Arod','Areli'],20:['Shelah','Perez','Zerah'],21:['Hezron','Hamul'],23:['Tola','Puvah','Punite'],24:['Jashub','Shimron'],26:['Sered','Elon','Jahleel'],29:['Machir','Gilead'],30:['Iezer','Helek'],31:['Asriel','Shechem'],32:['Shemida','Hepher'],35:['Shuthelah','Becher','Tahan'],36:['Eran'],38:['Bela','Ashbel','Ahiram'],39:['Shephupham','Shuphamite','Hupham'],40:['Ard','Naaman','Naamite'],42:['Shuham'],44:['Imnah','Ishvi','Beriah'],45:['Heber','Malchiel'],48:['Jahzeel','Guni'],49:['Jezer','Shillem'],57:['Gershon','Kohath','Merari'],58:['Libnite','Hebronite','Mahlite','Mushite','Korahite','Amram']}
 for v,names in founders.items():
  for name in names:assert name in byref[f'26:{v}']['after'],(v,name)
 bulls=[(13,13,'thirteen'),(17,12,'twelve'),(20,11,'eleven'),(23,10,'ten'),(26,9,'nine'),(29,8,'eight'),(32,7,'seven')]
 for v,n,word in bulls:
  t=byref[f'29:{v}']['after'];assert word in t and 'two rams' in t and 'fourteen year-old male lambs' in t and 'without defect' in t
 assert sum(n for v,n,w in bulls)==70
 for v in [16,19,22,25,28,31,34,38]:
  assert 'one male goat' in byref[f'29:{v}']['after'] and 'in addition' in byref[f'29:{v}']['after']
 assert q['next_work'][0]['scope']=='Numbers 31–36' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json','tools/audit_fluent_revision.py'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,31))
  assert len(new['revision_batches'])==9 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 25–30; 193 public verses / 194 source records','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 25–30; 193 public verses / 194 source records','revision_audits':audits,'cumulative_coverage':{'chapters':152,'verses':4773},'source_record_count':1289,'public_source_mapping':'Public 26:1 combines Hebrew 25:19 and 26:1 in separate source_segments; public 29:40 binds Hebrew 30:1; public 30:1–16 binds Hebrew 30:2–17. Other selected verses align directly. All 194 original records, with 25 annotations in 24 records, are bound exactly to 193 public verses.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'census_totals':census,'clan_name_checks':founders,'festival_bull_sequence':bulls,'multi_record_negative_tests':mutations,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 194 selected pinned Hebrew records were read before drafting; all 193 TSW comparator verses were read afterward. Supplemental NET translators’ notes were consulted on selected difficulties in Numbers 25, 27 and 30. Source-focused self-check covered Peor violence and covenant language, clan names and all census totals, named women and inheritance priority, Korah’s surviving sons, military versus Levite census thresholds, Joshua’s public commission, exact offering quantities and seventy-bull sequence, daily/monthly additions, work restrictions, vow conditions, gender and household status, silence and later cancellation. The multi-record audit extension rejects seven tested corruption and omission cases while preserving all earlier single-record ledger checks. This is authoring and structural QA, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':39,'chapters':152,'verses':4773,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
