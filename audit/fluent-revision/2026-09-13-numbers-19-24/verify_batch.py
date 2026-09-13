"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='a627130e373ee31df863c7be0f78d080a8df7b6f';COUNTS={19:22,20:29,21:35,22:41,23:30,24:25}
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
 assert len(audits)==38 and len(chapters)==146 and sum(a['verses'] for a in audits)==4580
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':867}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 def binding(ref):return 'Num '+ref
 for ref,v in byref.items():
  sr=binding(ref)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==182
 annotated=[ref for ref in byref if '<note' in raw[binding(ref)]]
 assert annotated==['19:21','20:8','20:19','21:13','21:30','21:32','23:13']
 assert sum(raw[binding(ref)].count('<note') for ref in annotated)==7
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
 checks={'19:2': ['red cow', 'without defect', 'never carried a yoke'], '19:3': ['Eleazar', 'outside', 'in his presence'], '19:4': ['finger', 'seven times', 'toward'], '19:5': ['hide', 'flesh', 'blood', 'dung'], '19:6': ['cedarwood', 'hyssop', 'scarlet'], '19:7': ['enter the camp', 'unclean until evening'], '19:9': ['clean man', 'outside', 'purification offering'], '19:10': ['foreigner'], '19:12': ['third day', 'seventh day'], '19:13': ['cut off', 'tabernacle'], '19:16': ['sword', 'bone', 'grave', 'seven days'], '19:19': ['third and seventh', 'wash', 'bathe', 'evening'], '19:21': ['sprinkles', 'wash', 'touches', 'evening'], '20:1': ['first month', 'Zin', 'Kadesh', 'Miriam', 'buried'], '20:5': ['grain', 'figs', 'vines', 'pomegranates', 'no water'], '20:8': ['Take the staff', 'Speak to the rock', 'livestock'], '20:10': ['Moses said', 'we'], '20:11': ['twice', 'livestock'], '20:12': ['Moses and Aaron', 'trust', 'holiness', 'not bring'], '20:16': ['angel', 'Kadesh'], '20:17': ['fields', 'vineyards', 'wells', 'King’s Highway', 'right nor left'], '20:19': ['If', 'livestock', 'pay', 'on foot'], '20:24': ['gathered to his people', 'you both', 'Meribah'], '20:28': ['Eleazar', 'Aaron died', 'Moses and Eleazar'], '20:29': ['thirty days'], '21:1': ['Arad', 'Negev', 'Atharim', 'captive'], '21:3': ['them and their cities', 'destruction', 'Hormah'], '21:4': ['Sea of Reeds', 'Edom'], '21:6': ['fiery snakes', 'died'], '21:9': ['bronze', 'pole', 'looked', 'lived'], '21:11': ['Iye-abarim', 'sunrise'], '21:14': ['Waheb', 'Suphah', 'Arnon'], '21:15': ['Ar', 'Moab'], '21:18': ['ruler’s staff', 'walking sticks', 'Mattanah'], '21:19': ['Nahaliel', 'Bamoth'], '21:20': ['Pisgah'], '21:24': ['Arnon', 'Jabbok', 'strong'], '21:29': ['Chemosh', 'sons', 'fugitives', 'daughters', 'captives'], '21:30': ['shot', 'Dibon', 'Nophah', 'Medeba'], '21:32': ['They captured', 'Moses drove out'], '21:35': ['sons', 'all his people', 'no survivor'], '22:2': ['Balak', 'Zippor'], '22:4': ['Midian', 'ox', 'grass'], '22:5': ['Balaam', 'Beor', 'Pethor', 'River', 'his people'], '22:6': ['we can strike', 'I can drive', 'bless', 'curse'], '22:7': ['divination'], '22:12': ['Do not go', 'Do not curse', 'blessed'], '22:13': ['LORD has refused'], '22:14': ['Balaam refuses'], '22:18': ['silver and gold', 'my God', 'small or great'], '22:20': ['If', 'go with them', 'do only'], '22:22': ['angry because', 'adversary', 'two young servants'], '22:23': ['sword', 'She turned', 'struck'], '22:25': ['foot', 'again'], '22:26': ['right or left'], '22:28': ['opened', 'three times'], '22:29': ['sword', 'kill you'], '22:30': ['No'], '22:31': ['uncovered', 'sword', 'facedown'], '22:33': ['If she had not', 'killed you', 'let her live'], '22:34': ['sinned', 'did not know', 'turn back'], '22:38': ['word God puts in my mouth'], '22:40': ['cattle', 'sheep', 'portions'], '22:41': ['Bamoth-baal', 'edge'], '23:1': ['seven altars', 'seven bulls', 'seven rams'], '23:2': ['Balak and Balaam', 'each altar'], '23:3': ['Perhaps', 'bare height'], '23:7': ['Aram', 'eastern mountains', 'Jacob', 'Israel'], '23:10': ['dust', 'quarter', 'upright'], '23:13': ['only part', 'not all'], '23:14': ['Zophim', 'Pisgah', 'seven', 'each altar'], '23:19': ['not a man', 'not a human being', 'fail to do', 'fail to fulfill'], '23:21': ['misfortune', 'misery', 'king’s shout'], '23:22': ['them out of Egypt', 'wild ox'], '23:23': ['enchantment', 'divination', 'God has done'], '23:24': ['lioness', 'lion', 'blood of the slain'], '23:28': ['Peor', 'wasteland'], '24:1': ['omens', 'wilderness'], '24:2': ['tribe by tribe', 'spirit of God'], '24:4': ['Almighty', 'falling down', 'eyes uncovered'], '24:6': ['valleys', 'gardens', 'aloes', 'cedars'], '24:7': ['buckets', 'seed', 'Agag', 'kingdom'], '24:8': ['him out of Egypt', 'wild ox', 'bones', 'arrows'], '24:9': ['Blessed are those who bless you', 'cursed are those who curse you'], '24:10': ['three times'], '24:13': ['silver and gold', 'good or bad', 'on my own'], '24:14': ['your people', 'days to come'], '24:16': ['Most High', 'Almighty'], '24:17': ['not now', 'not near', 'star', 'scepter', 'Moab', 'Sheth'], '24:18': ['Edom', 'Seir', 'possession'], '24:19': ['survivors', 'city'], '24:20': ['Amalek', 'first', 'end'], '24:22': ['Kain', 'Asshur', 'captive'], '24:24': ['Kittim', 'Asshur', 'Eber', 'he too'], '24:25': ['Balaam', 'Balak']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['23:1']['after']==byref['23:29']['after']
 assert byref['24:3']['after'].split('The declaration',1)[1]==byref['24:15']['after'].split('The declaration',1)[1]
 assert 'blessed' not in byref['22:13']['after'] and 'LORD' not in byref['22:14']['after']
 assert 'year' not in byref['20:1']['after'] and 'Satan' not in byref['22:22']['after']
 for ref in ['21:32','23:13']:assert 'x-ketiv' in raw['Num '+ref] and 'x-qere' in raw['Num '+ref]
 assert 'Vqw3ms' in raw['Num 21:32'] and 'Vhw3ms' in raw['Num 21:32']
 assert '\u05c4' in raw['Num 21:30']
 assert q['next_work'][0]['scope']=='Numbers 25–30' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,25))
  assert len(new['revision_batches'])==8 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 19–24; 182 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 19–24; 182 verses','revision_audits':audits,'cumulative_coverage':{'chapters':146,'verses':4580},'source_record_count':1289,'public_source_mapping':'Public Numbers 19–24 aligns directly with the 182 selected pinned Hebrew records. Seven annotations across seven records, including both written/read notes and the extraordinary point at 21:30, remain hashed exactly. Earlier books and public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 182 selected pinned Hebrew verses were read before drafting; all TSW comparators were read afterward. Supplemental NET notes were consulted for selected lexical and grammatical difficulties. Source-focused self-check covered red-cow requirements, purification days and agents, Miriam and Aaron, two rock strikes, Edom’s refusal, exact itinerary and conflict scope, written/read verb stems at 21:32, narrative permission/anger tension, donkey/angel sight and three blows, partial views, three sets of seven altars and animals, repeated oracle language, violent images, and consequential ambiguities in the poems. Standard checks do not establish independent fidelity, originality or reader comprehension; this is an authoring self-check, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':38,'chapters':146,'verses':4580,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
