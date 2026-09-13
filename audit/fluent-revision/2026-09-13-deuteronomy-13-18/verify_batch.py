"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='4b36f1b8b5908970c19ff8440212ac221051b5f2';COUNTS={13:18,14:29,15:23,16:22,17:20,18:22}
sys.path.insert(0,str(ROOT/'tools'))
from audit_translation_overlap import words

def run(*args):
 r=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
 return r.stdout.strip()
def put(name,d):(BATCH/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser()
 for book in ['genesis','exodus','leviticus','numbers','deuteronomy','james']:p.add_argument('--'+book+'-source',type=Path,required=True)
 args=p.parse_args();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];chapters=set();refs={}
 for s in q['completed_draft_scopes']:
  book=s['scope'].split()[0];l=json.loads((ROOT/s['ledger']).read_text())
  audits.append({'ledger':s['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',s['ledger'],'--source-text',str(getattr(args,book.lower()+'_source').resolve())))})
  for c in l['chapters']:assert c['path'] not in chapters;chapters.add(c['path'])
  rs=refs.setdefault(book,set())
  for v in l['verses']:
   for segment in v.get('source_segments',[v]):
    ref=segment['source_reference'];assert ref not in rs;rs.add(ref)
 assert len(audits)==43 and len(chapters)==176 and sum(a['verses'] for a in audits)==5515
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':1289,'Deuteronomy':514}
 raw={f'Deut {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.deuteronomy_source.read_text(),re.S) for c,v in [re.search(r'osisID="Deut\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==959
 l=json.loads((BATCH/'deuteronomy-verse-review.json').read_text());byref={v['reference'].replace('Deuteronomy ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 source_refs=[]
 for ref,v in byref.items():
  sr='Deut 13:'+str(int(ref.split(':')[1])+1) if ref.startswith('13:') else 'Deut '+ref;source_refs.append(sr)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len(source_refs)==len(set(source_refs))==134
 assert set(source_refs)=={ref for ref in raw if 13<=int(ref.split()[1].split(':')[0])<=18 and ref!='Deut 13:1'}
 assert refs['Deuteronomy']=={r for r in raw if int(r.split()[1].split(':')[0])<=18}
 annotated=[ref for ref in source_refs if '<note' in raw[ref]]
 assert annotated==[f'Deut 13:{v}' for v in range(2,20)]+['Deut 14:24','Deut 16:3','Deut 17:8','Deut 18:14']
 assert 'x-ketiv' in raw['Deut 13:16'] and 'x-qere' in raw['Deut 13:16']
 for v in range(1,19):assert f'KJV:Deut.13.{v}<' in raw[f'Deut 13:{v+1}']
 for c,n in COUNTS.items():
  t=(ROOT/f'translations/fluent/OT/deuteronomy/Deuteronomy_{c:02}.md').read_text();m=t.split('---',2)[2].split('## Notes')[0]
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
 checks={'13:2': ['comes true', 'other gods'], '13:3': ['testing', 'to know', 'all your heart', 'all your soul'], '13:4': ['Follow', 'fear', 'Keep', 'listen', 'serve', 'hold fast'], '13:5': ['put to death', 'rebellion', 'redeemed', 'house of slavery', 'purge'], '13:6': ["mother's son", 'son or daughter', 'wife', 'own life', 'secretly'], '13:9': ['Your hand', 'first', 'kill', 'all the people'], '13:10': ['Stone', 'to death'], '13:14': ['inquire', 'investigate', 'question thoroughly', 'true', 'established'], '13:15': ['inhabitants', 'sword', 'livestock', 'destruction'], '13:16': ['plunder', 'square', 'Burn', 'whole offering', 'forever', 'never to be rebuilt'], '13:17': ['cling to your hand', 'mercy', 'compassion', 'increase'], '14:1': ['children', 'cut yourselves', 'above your eyes', 'dead'], '14:5': ['deer, gazelle, fallow deer, wild goat, antelope, wild ox, and mountain sheep'], '14:7': ['camel', 'hare', 'hyrax', 'They chew the cud'], '14:8': ['pig', 'carcasses'], '14:9': ['fins and scales'], '14:10': ['both fins and scales'], '14:13': ['kite', 'falcon', 'dayyah'], '14:18': ['heron', 'hoopoe', 'bat'], '14:21': ['found dead', 'resident foreigner', 'sell', 'foreigner', "mother's milk"], '14:23': ['grain, new wine, and oil', 'firstborn', 'learn to fear'], '14:25': ['silver', 'hand'], '14:26': ['sheep and goats', 'wine, strong drink', 'household'], '14:28': ['three years', "that year's", 'towns'], '14:29': ['Levite', 'resident foreigner', 'fatherless', 'widow', 'eat their fill'], '15:1': ['seven years', 'release'], '15:2': ['creditor', 'release the claim', 'not press'], '15:3': ['foreigner', 'fellow Israelite'], '15:4': ['no poor'], '15:5': ['if only'], '15:6': ['lend', 'borrow', 'rule'], '15:7': ['harden your heart', 'close your hand'], '15:8': ['Open your hand wide', 'Lend enough'], '15:9': ['seventh year', 'give nothing', 'cry', 'sin'], '15:11': ['always be poor', 'open your hand'], '15:12': ['Hebrew man or woman', 'sold', 'six years', 'seventh year'], '15:14': ['flock', 'threshing floor', 'winepress'], '15:15': ['slave', 'redeemed'], '15:17': ['awl', 'ear', 'door', 'slave permanently', 'female slave'], '15:18': ['six years', 'twice the wages'], '15:19': ['firstborn male', 'work', 'shear'], '15:22': ['unclean and the clean together', 'gazelle or deer'], '15:23': ['blood', 'ground like water'], '16:1': ['Abib', 'night'], '16:2': ['flocks and herds'], '16:3': ['seven days', 'bread of affliction', 'haste'], '16:4': ['seven days', 'first day', 'morning'], '16:6': ['evening at sunset'], '16:7': ['Cook', 'morning', 'tents'], '16:8': ['six days', 'seventh day', 'assembly', 'no work'], '16:9': ['seven weeks', 'sickle', 'standing grain'], '16:11': ['son and daughter', 'male and female slave', 'Levite', 'resident foreigner', 'fatherless', 'widow'], '16:14': ['son and daughter', 'male and female slave', 'Levite', 'resident foreigner', 'fatherless', 'widow'], '16:16': ['Three times', 'all your males', 'Unleavened Bread', 'Weeks', 'Booths', 'empty-handed'], '16:19': ['bribe', 'blinds the eyes', 'twists the words'], '16:20': ['Justice, justice'], '16:21': ['plant', 'tree', 'Asherah', 'altar'], '16:22': ['standing stone', 'hates'], '17:3': ['sun', 'moon', 'host of heaven', 'I have not commanded'], '17:4': ['investigate', 'true and established'], '17:5': ['man or woman', 'town gates', 'to death'], '17:6': ['two or three witnesses', 'just one witness'], '17:7': ['witnesses', 'first', 'all the people'], '17:8': ['bloodshed', 'legal claims', 'injuries'], '17:9': ['Levitical priests', 'judge'], '17:11': ['right', 'left'], '17:12': ['presumptuously', 'refusing', 'priest', 'judge', 'must die'], '17:15': ['chooses', 'foreigner'], '17:16': ['horses', 'Egypt', 'never go back'], '17:17': ['wives', 'heart', 'silver and gold'], '17:18': ['write', 'scroll', 'copy', 'Levitical priests'], '17:19': ['read', 'all the days of his life', 'fear'], '17:20': ['heart', 'above', 'right', 'left', 'sons'], '18:1': ['Levitical priests', 'whole tribe', 'no share', 'offerings by fire'], '18:2': ['LORD is his inheritance'], '18:3': ['foreleg', 'two cheeks', 'stomach'], '18:4': ['grain, new wine, and oil', 'wool'], '18:6': ["heart's desire"], '18:8': ['equal share', 'ancestral property'], '18:10': ['son or daughter', 'fire', 'divination', 'fortunes', 'omens', 'sorcery'], '18:11': ['spells', 'medium', 'spiritist', 'dead'], '18:13': ['wholehearted'], '18:15': ['prophet like me', 'fellow Israelites', 'listen'], '18:16': ['Horeb', 'assembly', 'my God', 'I will die'], '18:18': ['prophet like you', 'my words in his mouth'], '18:19': ['I myself', 'hold accountable'], '18:20': ['not commanded', 'other gods', 'must die'], '18:22': ['does not come true or happen', 'has not spoken', 'presumptuously', 'Do not be afraid']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['13:1']['source_reference']=='Deut 13:2' and byref['13:18']['source_reference']=='Deut 13:19'
 assert q['next_work'][0]['scope']=='Deuteronomy 19–26' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/deuteronomy/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/deuteronomy/Deuteronomy_{c:02}.md' for c in COUNTS}|{reviewdir+f'Deuteronomy_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,19))
  assert len(new['revision_batches'])==3 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  assert new['current_revision']['not_yet_revised_chapters']==list(range(19,35))
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Deuteronomy 13–18; 134 public verses / 134 source records','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Deuteronomy 13–18; 134 public verses / 134 source records','revision_audits':audits,'cumulative_coverage':{'chapters':176,'verses':5515},'source_record_count':959,'public_source_mapping':'Public Deuteronomy 13:1–18 binds the complete Hebrew 13:2–19 records. Chapters 14–18 align directly; Hebrew 13:1 is already bound to public 12:32 in the preceding batch. Other books retain their earlier mappings, including the two-record Numbers 26:1 binding.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 134 selected Hebrew records were read before drafting, and all 134 TSW comparator verses afterward. NET translators’ notes on chapters 14, 15 and 18 were consulted for selected difficulties; the earlier Fluent Leviticus 11 animal names were checked for lexical consistency. The authoring self-check covered true signs leading to other gods; explicit execution, collective killing and destruction; close kinship; all animal-list entries and uncertain identifications; resident foreigner versus foreigner; annual and third-year tithes; seven-year debt release and six-year slave service; the scope of female-slave provisions; firstborn males and blemishes; festival times, foods and participants; witnesses and judicial authority; royal limits and lifelong reading; priestly portions and ancestral resources; the practices prohibited in chapter 18; and the voices of Moses, the people and the LORD. Assertions check selected risks and exact XML coverage; they are not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':43,'chapters':176,'verses':5515,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
