"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='0e819eb7bc1e0d5cf636e4237c2fa30e654c1b18';COUNTS={27:26,28:68,29:29,30:20,31:30,32:52,33:29,34:12}
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
 assert len(audits)==45 and len(chapters)==192 and sum(a['verses'] for a in audits)==5960
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':1289,'Deuteronomy':959}
 raw={f'Deut {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.deuteronomy_source.read_text(),re.S) for c,v in [re.search(r'osisID="Deut\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==959
 l=json.loads((BATCH/'deuteronomy-verse-review.json').read_text());byref={v['reference'].replace('Deuteronomy ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 source_refs=[]
 for ref,v in byref.items():
  sr='Deut 28:69' if ref=='29:1' else ('Deut 29:'+str(int(ref.split(':')[1])-1) if ref.startswith('29:') else 'Deut '+ref);source_refs.append(sr)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len(source_refs)==len(set(source_refs))==266
 assert set(source_refs)=={ref for ref in raw if 27<=int(ref.split()[1].split(':')[0])<=34}
 assert refs['Deuteronomy']=={r for r in raw if int(r.split()[1].split(':')[0])<=34}
 annotated=[ref for ref in source_refs if '<note' in raw[ref]]
 assert set(ref for ref in source_refs if 'x-qere' in raw[ref])=={'Deut 28:27','Deut 28:30','Deut 29:22','Deut 32:13','Deut 33:2','Deut 33:9'}
 assert 'KJV:Deut.29.1' in raw['Deut 28:69']
 for v in range(2,30):assert f'KJV:Deut.29.{v}<' in raw[f'Deut 29:{v-1}']
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
 checks={'27:4': ['Ebal', 'plaster'], '27:5': ['iron'], '27:12': ['Simeon, Levi, Judah, Issachar, Joseph, and Benjamin'], '27:13': ['Reuben, Gad, Asher, Zebulun, Dan, and Naphtali'], '27:19': ['resident foreigner', 'fatherless', 'widow'], '27:20': ['father’s wife', 'father’s covering'], '28:2': ['overtake'], '28:7': ['one road', 'seven'], '28:15': ['overtake'], '28:20': ['forsaking me'], '28:22': ['sword', 'blight', 'mildew'], '28:23': ['bronze', 'iron'], '28:25': ['one road', 'seven'], '28:27': ['hemorrhoids'], '28:30': ['rape', 'house', 'vineyard'], '28:32': ['sons and daughters', 'hands'], '28:43': ['higher and higher', 'lower and lower'], '28:44': ['head', 'tail'], '28:48': ['hunger, thirst, nakedness', 'iron yoke'], '28:53': ['fruit of your womb', 'flesh', 'sons and daughters'], '28:57': ['afterbirth', 'between her legs', 'eat them secretly'], '28:62': ['stars'], '28:63': ['rejoiced', 'will rejoice', 'destroying'], '28:68': ['Egypt', 'ships', 'male and female slaves', 'no buyer'], '29:1': ['Moab', 'in addition', 'Horeb'], '29:4': ['has not given', 'heart', 'eyes', 'ears'], '29:5': ['forty', 'clothes', 'sandals'], '29:6': ['I am the LORD'], '29:8': ['half the tribe of Manasseh'], '29:11': ['children', 'wives', 'resident foreigner', 'wood', 'water'], '29:15': ['not here'], '29:19': ['watered', 'thirsty'], '29:23': ['Sodom, Gomorrah, Admah, and Zeboiim'], '29:29': ['hidden', 'revealed', 'children forever'], '30:6': ['circumcise your heart', 'descendants', 'all your soul'], '30:12': ['heavens', 'hear it and carry it out'], '30:13': ['sea', 'hear it and carry it out'], '30:14': ['mouth', 'heart', 'carry it out'], '30:19': ['heavens and the earth', 'Choose life'], '30:20': ['he is your life', 'Abraham, Isaac, and Jacob'], '31:2': ['hundred and twenty', 'go out and come in'], '31:7': ['go with'], '31:10': ['seven years', 'release', 'Booths'], '31:12': ['men, women, children', 'resident foreigner', 'hear, learn'], '31:19': ['both of you', 'Moses, teach', 'mouths'], '31:23': ['bring the Israelites'], '31:26': ['beside the ark', 'witness'], '32:5': ['not his children', 'blemish'], '32:8': ['children of Adam', 'children of Israel'], '32:10': ['pupil'], '32:13': ['honey from rock', 'oil from flinty'], '32:14': ['Bashan', 'blood of grapes'], '32:15': ['Jeshurun', 'you grew fat'], '32:18': ['fathered', 'gave you birth'], '32:19': ['sons and daughters'], '32:21': ['no god', 'no people'], '32:22': ['Sheol', 'foundations'], '32:25': ['young man and virgin', 'nursing infant', 'gray-haired'], '32:27': ['I feared'], '32:30': ['a thousand', 'ten thousand', 'sold', 'handed'], '32:36': ['confined or free'], '32:39': ['I, I am he', 'death', 'life', 'wound', 'heal'], '32:42': ['captives', 'long-haired'], '32:43': ['atonement', 'land', 'people'], '32:44': ['Hoshea son of Nun'], '32:47': ['it is your life'], '32:50': ['Aaron', 'Mount Hor'], '32:51': ['both of you', 'Meribath-kadesh', 'Zin'], '33:2': ['Sinai', 'Seir', 'Paran', 'myriads', 'fiery law'], '33:3': ['peoples', 'his holy ones', 'your hand'], '33:4': ['Moses commanded us'], '33:6': ['few'], '33:8': ['Thummim and Urim', 'Massah', 'Meribah'], '33:10': ['nostrils'], '33:11': ['Shatter the loins'], '33:12': ['between his shoulders'], '33:14': ['sun', 'moons'], '33:16': ['bush', 'set apart'], '33:17': ['wild ox', 'gores', 'Ephraim’s ten thousands', 'Manasseh’s thousands'], '33:18': ['Zebulun', 'Issachar'], '33:20': ['arm', 'scalp'], '33:22': ['Dan', 'Bashan'], '33:23': ['west and the south'], '33:24': ['foot in oil'], '33:25': ['iron and bronze'], '33:27': ['everlasting arms', 'Destroy'], '33:28': ['spring of Jacob'], '33:29': ['shield', 'sword', 'high places'], '34:1': ['Nebo', 'Pisgah', 'Gilead', 'Dan'], '34:2': ['Naphtali', 'Ephraim', 'Manasseh', 'Judah', 'western sea'], '34:3': ['Negev', 'Jericho', 'Zoar'], '34:6': ['He buried him', 'Beth-peor', 'no one knows'], '34:7': ['hundred and twenty', 'not grown dim', 'vigor'], '34:8': ['thirty days'], '34:9': ['spirit of wisdom', 'hands'], '34:10': ['whom the LORD knew face to face'], '34:12': ['mighty hand', 'great terror', 'all Israel']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['29:1']['source_reference']=='Deut 28:69' and byref['29:29']['source_reference']=='Deut 29:28'
 assert sum('Amen!' in byref[f'27:{v}']['after'] for v in range(15,27))==12
 assert all('Simeon' not in byref[f'33:{v}']['after'] for v in range(1,30))
 assert q['next_work'][0]['scope']=='Deuteronomy whole-book consistency review' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/deuteronomy/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/deuteronomy/Deuteronomy_{c:02}.md' for c in COUNTS}|{reviewdir+f'Deuteronomy_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,35))
  assert len(new['revision_batches'])==5 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  assert new['current_revision']['not_yet_revised_chapters']==[]
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Deuteronomy 27–34; 266 public verses / 266 source records','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Deuteronomy 27–34; 266 public verses / 266 source records','revision_audits':audits,'cumulative_coverage':{'chapters':192,'verses':5960},'source_record_count':959,'public_source_mapping':'Public 29:1 binds Hebrew 28:69; public 29:2–29 binds Hebrew 29:1–28. Other verses in chapters 27–34 align directly. All 959 Deuteronomy source records are bound exactly once across five ledgers. Earlier books retain their established mappings.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 266 selected Hebrew records were read before drafting and all 266 TSW comparator verses afterward. Selected NET translator notes on chapters 29, 32 and 33 were consulted during drafting. The authoring check covered twelve congregational responses, blessing/curse reversals, retained harm and divine first-person shifts, chapter 29 mapping, return/heart/life repetitions, seven-year reading, Joshua commissioning, poetry within verse paragraphs, pinned children of Israel, Hoshea, tribal names and numbers, omitted Simeon, obscure poetic terms, burial agency, and Moses’ age and vigor. Assertions cover selected risks and structure; this is not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':45,'chapters':192,'verses':5960,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
