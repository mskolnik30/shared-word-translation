"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='310bdad4b60bd136696665ee94d93362ffd51135';COUNTS={13:33,14:45,15:41,16:50,17:13,18:32}
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
 assert len(audits)==37 and len(chapters)==140 and sum(a['verses'] for a in audits)==4398
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':685}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 def binding(ref):
  c,v=map(int,ref.split(':'))
  return f'Num 17:{v-35}' if c==16 and v>=36 else f'Num 17:{v+15}' if c==17 else 'Num '+ref
 for ref,v in byref.items():
  sr=binding(ref)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==214
 annotated=[ref for ref in byref if '<note' in raw[binding(ref)]]
 assert annotated==['14:36','16:11','16:21','16:27']+[f'16:{i}' for i in range(36,51)]+[f'17:{i}' for i in range(1,14)]+['18:8']
 assert sum(raw[binding(ref)].count('<note') for ref in annotated)==34
 assert byref['16:36']['source_reference']=='Num 17:1'
 assert byref['16:50']['source_reference']=='Num 17:15'
 assert byref['17:1']['source_reference']=='Num 17:16'
 assert byref['17:13']['source_reference']=='Num 17:28'
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
 checks={'13:2': ['one man', 'ancestral tribe', 'leader'], '13:11': ['Joseph', 'Manasseh', 'Gaddi', 'Susi'], '13:16': ['Hoshea', 'Nun', 'Joshua'], '13:21': ['Zin', 'Rehob', 'Lebo-hamath'], '13:22': ['Ahiman', 'Sheshai', 'Talmai', 'seven years', 'Zoan'], '13:23': ['single cluster', 'Two men', 'pole', 'pomegranates', 'figs'], '13:25': ['forty days'], '13:26': ['Kadesh', 'Paran'], '13:29': ['Amalekites', 'Hittites', 'Jebusites', 'Amorites', 'Canaanites', 'Jordan'], '13:33': ['Nephilim', 'grasshoppers', 'own eyes'], '14:2': ['If only'], '14:3': ['wives', 'little ones', 'plunder', 'sword'], '14:7': ['very, very good'], '14:9': ['bread', 'shade', 'Do not fear'], '14:12': ['plague', 'disinherit', 'greater', 'stronger'], '14:14': ['eye to eye', 'cloud', 'day', 'fire', 'night'], '14:16': ['slaughtered'], '14:18': ['faithful love', 'guilt and rebellion', 'not clearing', 'fathers’ guilt', 'third', 'fourth'], '14:20': ['forgiven'], '14:22': ['ten times'], '14:24': ['Caleb', 'different spirit', 'descendants'], '14:25': ['tomorrow', 'Sea of Reeds'], '14:29': ['corpses', 'counted', 'twenty'], '14:30': ['raised my hand', 'Caleb', 'Jephunneh', 'Joshua', 'Nun'], '14:31': ['little ones', 'plunder', 'know'], '14:33': ['shepherds', 'forty years', 'prostitution'], '14:34': ['forty days', 'forty years', 'opposition'], '14:37': ['plague'], '14:38': ['Joshua', 'Caleb', 'alive'], '14:44': ['Neither Moses', 'ark', 'left the camp'], '14:45': ['Hormah'], '15:4': ['one-tenth', 'ephah', 'one-quarter', 'hin', 'oil'], '15:5': ['lamb', 'one-quarter', 'wine'], '15:6': ['ram', 'two-tenths', 'one-third', 'oil'], '15:7': ['one-third', 'wine'], '15:9': ['bull', 'three-tenths', 'half', 'oil'], '15:10': ['half', 'wine'], '15:15': ['one rule', 'foreigner', 'alike'], '15:20': ['cake', 'first', 'dough', 'threshing floor'], '15:24': ['one young bull', 'burnt offering', 'one male goat', 'sin offering'], '15:26': ['foreigner', 'forgiven'], '15:27': ['year-old female goat'], '15:30': ['raised hand', 'cut off'], '15:31': ['guilt remains'], '15:32': ['man', 'wood', 'Sabbath'], '15:35': ['put to death', 'whole community', 'outside'], '15:36': ['stoned him to death'], '15:38': ['tassels', 'corners', 'blue cord'], '15:39': ['scouting', 'heart', 'eyes', 'prostituting'], '16:1': ['Korah', 'Izhar', 'Kohath', 'Levi', 'Dathan', 'Abiram', 'Eliab', 'On', 'Peleth', 'Reuben'], '16:2': ['two hundred and fifty', 'men of standing'], '16:3': ['every one', 'holy', 'gone too far'], '16:7': ['tomorrow', 'gone too far'], '16:10': ['priesthood'], '16:12': ['We will not come up'], '16:13': ['milk and honey', 'kill us'], '16:14': ['milk and honey', 'gouge', 'eyes', 'We will not come up'], '16:15': ['one donkey', 'harmed'], '16:17': ['two hundred and fifty', 'Aaron', 'too'], '16:22': ['spirits of all flesh', 'one man', 'whole community'], '16:27': ['wives', 'sons', 'little ones'], '16:30': ['creates', 'mouth', 'alive', 'Sheol'], '16:32': ['households', 'Korah', 'possessions'], '16:35': ['LORD', 'two hundred and fifty'], '16:37': ['Eleazar', 'coals', 'censers are holy'], '16:39': ['bronze', 'altar'], '16:40': ['unauthorized', 'Aaron’s descendants'], '16:41': ['You have killed'], '16:46': ['fire from the altar', 'atonement', 'plague'], '16:48': ['between the dead and the living'], '16:49': ['Fourteen thousand seven hundred', 'besides'], '16:50': ['plague had stopped'], '17:2': ['twelve staffs', 'name'], '17:3': ['Aaron', 'Levi'], '17:6': ['twelve', 'among'], '17:8': ['buds', 'blossoms', 'almonds'], '17:10': ['back', 'testimony', 'not die'], '17:12': ['All of us are lost'], '17:13': ['Must we all die'], '18:1': ['ancestral house', 'sanctuary', 'sons', 'priesthood'], '18:3': ['furnishings', 'altar', 'both they and you'], '18:6': ['gift to you', 'given to the LORD'], '18:7': ['inside the curtain', 'gift of service', 'put to death'], '18:9': ['grain offerings', 'sin offerings', 'guilt offerings'], '18:10': ['Every male', 'most holy'], '18:11': ['sons', 'daughters', 'clean'], '18:12': ['oil', 'new wine', 'grain'], '18:14': ['irrevocably'], '18:15': ['redeem the firstborn humans', 'unclean animals'], '18:16': ['one month', 'five shekels', 'twenty gerahs'], '18:17': ['do not redeem', 'cattle', 'sheep', 'goats', 'blood', 'fat'], '18:18': ['breast', 'right thigh'], '18:19': ['sons', 'daughters', 'covenant of salt'], '18:20': ['no inheritance', 'I am your share'], '18:26': ['tithe of the tithe'], '18:28': ['Aaron the priest'], '18:29': ['finest'], '18:31': ['households', 'anywhere', 'payment'], '18:32': ['guilt', 'finest', 'profane', 'not die']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 names=[('4','Shammua','Zaccur','Reuben'),('5','Shaphat','Hori','Simeon'),('6','Caleb','Jephunneh','Judah'),('7','Igal','Joseph','Issachar'),('8','Hoshea','Nun','Ephraim'),('9','Palti','Raphu','Benjamin'),('10','Gaddiel','Sodi','Zebulun'),('11','Gaddi','Susi','Manasseh'),('12','Ammiel','Gemalli','Dan'),('13','Sethur','Michael','Asher'),('14','Nahbi','Vophsi','Naphtali'),('15','Geuel','Machi','Gad')]
 for v,*terms in names:
  for term in terms:assert term in byref['13:'+v]['after']
 assert byref['14:2']['after'].count('If only')==2
 assert byref['14:34']['after'].count('a year for each day')==2
 assert byref['15:41']['after'].count('I am the LORD your God')==2
 assert byref['17:13']['after'].count('who comes near')==2
 t14=(ROOT/'translations/fluent/OT/numbers/Numbers_14.md').read_text()
 assert 'anger,\nabounding' in t14 and 'rebellion,\nyet certainly' in t14
 for ref in ['14:36','16:11']:assert 'x-ketiv' in raw['Num '+ref] and 'x-qere' in raw['Num '+ref]
 assert 'KJV:Num.16.36' in raw['Num 17:1'] and 'KJV:Num.17.13' in raw['Num 17:28']
 assert q['next_work'][0]['scope']=='Numbers 19–24' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,19))
  assert len(new['revision_batches'])==7 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 13–18; 214 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 13–18; 214 verses','revision_audits':audits,'cumulative_coverage':{'chapters':140,'verses':4398},'source_record_count':1289,'public_source_mapping':'Public 13–15, 16:1–35 and 18 align directly; public 16:36–50 maps to Hebrew 17:1–15; public 17:1–13 maps to Hebrew 17:16–28. All 214 records are unique and complete, with 34 annotations across 33 records retained. Earlier books and their public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 214 selected pinned Hebrew verses were read before drafting. Supplemental NET grammatical and lexical notes were consulted on selected difficulties; all TSW comparators were read after drafting. Source-focused checks covered twelve scout names and fathers, competing claims, oath and forgiveness, ten tests and forty-day/year correspondence, exact offering quantities, equal resident-foreigner instructions, defiance and Sabbath execution, tassels and scouting wordplay, Korah’s opening syntax, household harm, 250 and 14,700 deaths, shifted source numbering, twelve staffs and almond progression, access boundaries, sons/daughters and clean status, firstborn redemption, five shekels/twenty gerahs, salt covenant and tithe of the tithe. Sacrificial terms were aligned with earlier revised chapters, without changing those chapters. This is an authoring self-check, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':37,'chapters':140,'verses':4398,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
