"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='24e3c69fc18a31ba55e93eeaf3a48c5f85bd3c21';COUNTS={1:46,2:37,3:29,4:49,5:33,6:25}
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
 assert len(audits)==41 and len(chapters)==164 and sum(a['verses'] for a in audits)==5220
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':1289,'Deuteronomy':219}
 raw={f'Deut {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.deuteronomy_source.read_text(),re.S) for c,v in [re.search(r'osisID="Deut\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==959
 l=json.loads((BATCH/'deuteronomy-verse-review.json').read_text());byref={v['reference'].replace('Deuteronomy ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 source_refs=[]
 for ref,v in byref.items():
  sr='Deut '+ref;source_refs.append(sr)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len(source_refs)==len(set(source_refs))==219
 assert set(source_refs)=={ref for ref in raw if 1<=int(ref.split()[1].split(':')[0])<=6}
 assert refs['Deuteronomy']==set(source_refs)
 annotated=[ref for ref in source_refs if '<note' in raw[ref]]
 assert len(annotated)==26
 for ref in ['Deut 2:33','Deut 5:10']:assert 'x-ketiv' in raw[ref] and 'x-qere' in raw[ref]
 assert all('alternative' in raw['Deut 5:'+str(v)] for v in (6,7,8,9,10,12,13,14,15,17,18,19))
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
 checks={'1:1': ['Suph', 'Paran, Tophel, Laban, Hazeroth, and Dizahab'], '1:2': ['eleven-day', 'Horeb', 'Kadesh-barnea', 'Mount Seir'], '1:3': ['fortieth year', 'first day', 'eleventh month'], '1:4': ['Sihon', 'Heshbon', 'Og', 'Ashtaroth', 'Edrei'], '1:7': ['Arabah', 'lowlands', 'Negev', 'coast', 'Lebanon', 'Euphrates'], '1:8': ['Abraham, Isaac, and Jacob', 'descendants'], '1:11': ['thousand times'], '1:13': ['wise, discerning, respected men'], '1:15': ['thousands, hundreds, fifties, and tens'], '1:16': ['judge fairly', 'resident foreigner'], '1:17': ['small and the great', 'judgment belongs to God'], '1:23': ['twelve men', 'one from each tribe'], '1:27': ['LORD hates us'], '1:28': ['hearts melt', 'fortified up to the heavens', 'Anakim'], '1:31': ['man carries his son'], '1:33': ['fire by night', 'cloud by day'], '1:36': ['Caleb son of Jephunneh', 'his sons'], '1:37': ['because of you', 'not enter'], '1:38': ['Joshua son of Nun'], '1:39': ['little ones', 'plunder', 'good from evil'], '1:40': ['Sea of Reeds'], '1:41': ['sinned', 'easy'], '1:44': ['bees', 'Seir', 'Hormah'], '2:5': ['sole of a foot', 'given Mount Seir to Esau'], '2:6': ['food', 'water', 'silver'], '2:7': ['forty years', 'lacked nothing'], '2:8': ['Elath', 'Ezion-geber'], '2:9': ['Ar', 'descendants of Lot'], '2:10': ['Emim', 'Anakim'], '2:11': ['Rephaim', 'Emim'], '2:12': ['Horites', 'just as Israel did'], '2:14': ['Thirty-eight years', 'Kadesh-barnea', 'Wadi Zered'], '2:15': ["LORD's hand was against"], '2:19': ['Ammonite land', 'descendants of Lot'], '2:20': ['Zamzummim'], '2:23': ['Avvim', 'Gaza', 'Caphtorim', 'Caphtor'], '2:24': ['Wadi Arnon', 'Sihon', 'Heshbon', 'battle'], '2:26': ['Kedemoth', 'words of peace'], '2:28': ['on foot'], '2:29': ["Esau's descendants", 'Moabites', 'Ar'], '2:30': ['hardened his spirit', 'heart unyielding'], '2:32': ['Jahaz'], '2:33': ['his sons'], '2:34': ['men, women, and little children', 'no survivor'], '2:35': ['livestock', 'spoil'], '2:36': ['Aroer', 'town in the wadi', 'Gilead'], '2:37': ['Ammonite', 'Jabbok', 'forbidden'], '3:4': ['sixty towns', 'Argob'], '3:5': ['walls, gates, and bars', 'unwalled'], '3:6': ['men, women, and little children'], '3:9': ['Sidonians', 'Sirion', 'Amorites', 'Senir'], '3:10': ['Salecah', 'Edrei'], '3:11': ['bed', 'iron', 'Rabbah', 'nine cubits long', 'four cubits wide', 'ordinary human cubit'], '3:12': ['Reubenites and Gadites', 'half'], '3:13': ['half-tribe of Manasseh'], '3:14': ['Jair', 'Geshurites and Maacathites', 'Havvoth-jair'], '3:15': ['Machir'], '3:16': ['middle of the wadi', 'Jabbok', 'Ammonite'], '3:17': ['Chinnereth', 'Salt Sea', 'Pisgah', 'east'], '3:19': ['wives, little ones, and livestock'], '3:20': ['rest', 'Then each of you may return'], '3:24': ['Lord GOD', 'strong hand'], '3:26': ['because of you', 'Enough'], '3:27': ['west, north, south, and east', 'will not cross'], '3:28': ['Commission Joshua', 'land you will see'], '3:29': ['Beth-peor'], '4:2': ['Do not add', 'take anything away'], '4:4': ['cling'], '4:7': ['god so near'], '4:9': ['children and grandchildren'], '4:11': ['heart of the heavens', 'darkness, cloud, and thick gloom'], '4:12': ['no form', 'only a voice'], '4:13': ['Ten Words', 'two stone tablets'], '4:16': ['male or female'], '4:19': ['sun, moon, and stars', 'host of heaven', 'allotted'], '4:20': ['iron furnace', 'inheritance'], '4:21': ['because of you'], '4:24': ['consuming fire', 'jealous God'], '4:26': ['heaven and earth', 'utterly destroyed'], '4:28': ['see, hear, eat, or smell'], '4:29': ['all your heart and all your soul'], '4:31': ['merciful', 'not abandon', 'destroy', 'forget'], '4:34': ['trials, signs, wonders, war, a strong hand, an outstretched arm, and great terrors'], '4:37': ['their descendants', 'his presence'], '4:41': ['three towns', 'sunrise'], '4:42': ['unintentionally', 'without having hated'], '4:43': ['Bezer', 'Reubenites', 'Ramoth', 'Gadites', 'Golan', 'Manassites'], '4:48': ['Mount Sion', 'Hermon'], '5:3': ['did not make this covenant with our fathers', 'but with us'], '5:4': ['face to face'], '5:6': ['house of slavery'], '5:7': ['no other gods before me'], '5:9': ["fathers' guilt", 'third and fourth'], '5:10': ['thousands', 'my commands'], '5:11': ['name', 'falsehood'], '5:12': ['Observe the Sabbath', 'keep it holy'], '5:14': ['son or daughter', 'male or female slave', 'ox or donkey', 'resident foreigner', 'rest as you do'], '5:15': ['slave in Egypt', 'strong hand', 'outstretched arm', 'That is why'], '5:17': ['not murder'], '5:21': ['covet', "neighbor's wife", 'desire', 'house or field', 'male or female slave', 'ox or donkey'], '5:22': ['He added no more', 'two stone tablets'], '5:27': ['listen and do'], '5:29': ['If only', 'heart', 'children forever'], '5:32': ['right', 'left'], '5:33': ['Walk', 'whole way'], '6:2': ['your son', 'your grandson'], '6:3': ['milk and honey'], '6:4': ['Hear, Israel', 'LORD is one'], '6:5': ['all your heart, all your soul, and all your strength'], '6:6': ['on your heart'], '6:7': ['again and again', 'sit at home', 'walk along the road', 'lie down', 'get up'], '6:8': ['hand', 'between your eyes'], '6:9': ['doorposts', 'gates'], '6:10': ['Abraham, Isaac, and Jacob', 'did not build'], '6:11': ['did not fill', 'did not hew', 'did not plant'], '6:12': ['not to forget', 'house of slavery'], '6:13': ['Fear', 'serve', 'swear'], '6:15': ['jealous God', 'destroy'], '6:16': ['Massah'], '6:21': ["Pharaoh's slaves"], '6:22': ['great and terrible', 'whole household'], '6:23': ['out of there to bring us in'], '6:25': ['righteousness', 'if', 'whole commandment']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert 'only' not in byref['5:3']['after']
 assert byref['5:21']['after'].index('wife') < byref['5:21']['after'].index('house') < byref['5:21']['after'].index('field')
 assert q['next_work'][0]['scope']=='Deuteronomy 7–12' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/deuteronomy/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/deuteronomy/Deuteronomy_{c:02}.md' for c in COUNTS}|{reviewdir+f'Deuteronomy_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,7))
  assert len(new['revision_batches'])==1 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  assert new['current_revision']['not_yet_revised_chapters']==list(range(7,35))
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Deuteronomy 1–6; 219 public verses / 219 source records','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Deuteronomy 1–6; 219 public verses / 219 source records','revision_audits':audits,'cumulative_coverage':{'chapters':164,'verses':5220},'source_record_count':959,'public_source_mapping':'All 219 public verses in Deuteronomy 1–6 align directly with the 219 corresponding original Hebrew records. Other books retain their earlier mappings, including the two-record Numbers 26:1 binding.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 219 selected pinned Hebrew records were read before drafting; all 219 TSW comparator verses were read afterward. Supplemental NET translators’ notes were consulted on Deuteronomy 6 before drafting and 1, 3, and 5 during the post-draft self-check. Focused comparisons covered chronology, geographical and people names, kinship and grants to Esau and Lot, explicit killing, divine hardening, exact written/read forms, dimensions and directions, inheritance and rest, Moses’ retrospective attribution of his exclusion, hearing versus visible form, covenant and generations, Sabbath wording and rationale distinct from Exodus, explicit slavery, the desire verbs and list, the one/alone ambiguity, embodied teaching and daily repetition, and conditional righteousness language. This is authoring and structural QA, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':41,'chapters':164,'verses':5220,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
