"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='25019230ceb7baf9d68aac312da5c86f9a893e85';COUNTS={19:21,20:20,21:23,22:30,23:25,24:22,25:19,26:19}
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
 assert len(audits)==44 and len(chapters)==184 and sum(a['verses'] for a in audits)==5694
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':1289,'Deuteronomy':693}
 raw={f'Deut {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.deuteronomy_source.read_text(),re.S) for c,v in [re.search(r'osisID="Deut\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==959
 l=json.loads((BATCH/'deuteronomy-verse-review.json').read_text());byref={v['reference'].replace('Deuteronomy ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 source_refs=[]
 for ref,v in byref.items():
  sr='Deut 23:1' if ref=='22:30' else ('Deut 23:'+str(int(ref.split(':')[1])+1) if ref.startswith('23:') else 'Deut '+ref);source_refs.append(sr)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len(source_refs)==len(set(source_refs))==179
 assert set(source_refs)=={ref for ref in raw if 19<=int(ref.split()[1].split(':')[0])<=26}
 assert refs['Deuteronomy']=={r for r in raw if int(r.split()[1].split(':')[0])<=26}
 annotated=[ref for ref in source_refs if '<note' in raw[ref]]
 assert set(ref for ref in source_refs if 'x-qere' in raw[ref])=={'Deut 21:7'}|{f'Deut 22:{v}' for v in [15,16,20,21,23,24,25,26,27,28,29]}
 assert 'KJV:Deut.22.30' in raw['Deut 23:1']
 for v in range(1,26):assert f'KJV:Deut.23.{v}<' in raw[f'Deut 23:{v+1}']
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
 checks={'19:2': ['three towns'], '19:3': ['roads', 'three regions'], '19:4': ['unintentionally', 'hated'], '19:5': ['iron head', 'handle', 'kills'], '19:6': ['avenger of blood', 'journey is long', 'does not deserve death'], '19:9': ['three more', 'these three'], '19:11': ['hates', 'lies in wait', 'kills'], '19:12': ['elders', 'avenger', 'death'], '19:15': ['two or three witnesses'], '19:19': ['plotted', 'purge'], '19:21': ['life for life, eye for eye, tooth for tooth, hand for hand, foot for foot'], '20:1': ['horses', 'chariots', 'larger'], '20:5': ['house', 'dedicated', 'die'], '20:6': ['vineyard', 'fruit', 'die'], '20:7': ['betrothed', 'married', 'die'], '20:8': ['hearts melt'], '20:11': ['forced labor'], '20:13': ['all its males', 'sword'], '20:14': ['women, children, livestock', 'plunder'], '20:16': ['nothing that breathes'], '20:17': ['Hittites, Amorites, Canaanites, Perizzites, Hivites, and Jebusites'], '20:19': ['trees', 'axe', 'human being'], '20:20': ['do not produce food', 'siegeworks'], '21:3': ['heifer', 'never been worked', 'yoke'], '21:4': ['flowing stream', 'worked or sown', 'break its neck'], '21:7': ['hands', 'eyes'], '21:8': ['atonement', 'redeemed', 'bloodguilt'], '21:11': ['beautiful', 'captives', 'desire'], '21:13': ['father and mother', 'full month', 'sex'], '21:14': ['free', 'not sell', 'slave', 'humiliated'], '21:17': ['double share', 'strength'], '21:19': ['father and mother', 'seize'], '21:21': ['all the men', 'stone him to death'], '21:23': ['overnight', 'same day', "God's curse"], '22:1': ['do not look the other way', 'bring it back'], '22:4': ['Help the owner'], '22:5': ["man's gear", "woman's garment"], '22:6': ['chicks or eggs', 'mother'], '22:7': ['let the mother go'], '22:8': ['parapet', 'bloodguilt'], '22:9': ['two kinds', 'forfeited'], '22:11': ['wool and linen'], '22:12': ['four corners'], '22:17': ['cloth'], '22:19': ['hundred shekels', 'father', 'never divorce'], '22:24': ['did not cry out', 'stone them to death'], '22:25': ['overpowers', 'rapes', 'only the man'], '22:26': ['Do nothing', 'no offense', 'murdering'], '22:28': ['not betrothed', 'seizes'], '22:29': ['fifty shekels', 'father', 'violated', 'never divorce'], '22:30': ["father's wife", "father's garment"], '23:1': ['testicles', 'penis', 'assembly'], '23:2': ['forbidden union', 'tenth generation'], '23:3': ['Ammonite', 'Moabite', 'never'], '23:4': ['Balaam son of Beor', 'Pethor', 'Aram-naharaim', 'bread and water'], '23:5': ['curse', 'blessing', 'loved'], '23:7': ['Edomite', 'brother', 'Egyptian', 'resident foreigner'], '23:8': ['third generation'], '23:11': ['evening', 'sunset'], '23:13': ['digging tool', 'excrement'], '23:14': ['He must not see', 'turn away'], '23:15': ['Do not hand a slave back'], '23:16': ['chooses', 'Do not mistreat'], '23:17': ['daughter', 'son'], '23:18': ['price of a dog'], '23:19': ['silver, food'], '23:20': ['foreigner', 'fellow Israelite'], '23:22': ['refrain', 'not be guilty'], '23:24': ['satisfied', 'none in your basket'], '23:25': ['by hand', 'sickle'], '24:1': ['certificate of divorce', 'hand', 'house'], '24:3': ['second husband dies'], '24:4': ['first husband', 'may not', 'defiled'], '24:5': ['one year', 'joy'], '24:6': ['upper stone', "someone's life"], '24:7': ['kidnapping', 'slave', 'selling', 'must die'], '24:9': ['Miriam'], '24:11': ['Stand outside'], '24:13': ['sunset', 'cloak', 'righteousness'], '24:14': ['hired worker', 'resident foreigner'], '24:15': ['same day', 'before sunset', 'cry'], '24:16': ['Parents', 'children', 'own sin'], '24:17': ['resident foreigner', 'fatherless', "widow's garment"], '24:19': ['sheaf', 'resident foreigner, the fatherless, and the widow'], '24:20': ['olive', 'resident foreigner, the fatherless, and the widow'], '24:21': ['grapes', 'resident foreigner, the fatherless, and the widow'], '25:3': ['Forty', 'no more', 'degraded'], '25:4': ['muzzle', 'ox', 'threshing'], '25:5': ['brothers live together', 'without a son', "brother-in-law's duty"], '25:6': ['firstborn', 'name'], '25:9': ['sandal', 'spit in his face', "brother's house"], '25:11': ['rescue her husband', 'genitals'], '25:12': ['cut off her hand'], '25:15': ['full and honest weight', 'full and honest measure'], '25:18': ['stragglers', 'tired and weary', 'did not fear God'], '25:19': ['wipe out the memory', 'Do not forget'], '26:3': ['the LORD your God', 'our ancestors'], '26:5': ['My father', 'wandering Aramean', 'few people', 'mighty and numerous'], '26:6': ['us', 'hard labor'], '26:7': ['heard our voice', 'affliction, our toil, and our oppression'], '26:8': ['mighty hand', 'outstretched arm', 'terror, signs, and wonders'], '26:10': ['I bring', 'bow down'], '26:12': ['third year', 'Levite, the resident foreigner, the fatherless, and the widow'], '26:14': ['mourning', 'unclean', 'dead'], '26:15': ['milk and honey'], '26:16': ['all your heart', 'all your soul'], '26:18': ['treasured people', 'keep all his commands'], '26:19': ['praise, renown, and honor', 'holy']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['22:30']['source_reference']=='Deut 23:1' and byref['23:25']['source_reference']=='Deut 23:26'
 assert q['next_work'][0]['scope']=='Deuteronomy 27–34' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/deuteronomy/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/deuteronomy/Deuteronomy_{c:02}.md' for c in COUNTS}|{reviewdir+f'Deuteronomy_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,27))
  assert len(new['revision_batches'])==4 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  assert new['current_revision']['not_yet_revised_chapters']==list(range(27,35))
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Deuteronomy 19–26; 179 public verses / 179 source records','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Deuteronomy 19–26; 179 public verses / 179 source records','revision_audits':audits,'cumulative_coverage':{'chapters':184,'verses':5694},'source_record_count':959,'public_source_mapping':'Public 22:30 binds Hebrew 23:1; public 23:1–25 binds Hebrew 23:2–26. Other verses in chapters 19–26 align directly. Deuteronomy source records through chapter 26 are bound exactly once across four ledgers. Earlier books retain their established mappings.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 179 selected Hebrew records were read before drafting and all 179 TSW comparator verses afterward. NET translators’ notes on chapters 21, 22, 23 and 26 were consulted for selected difficult terms. The authoring check covered refuge eligibility, intentional killing, witness thresholds, siege distinctions and named peoples, captive women, inheritance, explicit penalties, sexual case distinctions without invented consent, assembly exclusions, escaped slaves, pledges and wages, individual liability, repeated gleaning recipients, forty blows, brother-in-law duty, Amalek, and the singular/plural voices of the firstfruits declaration. Automated assertions check selected risks and structure; this is not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':44,'chapters':184,'verses':5694,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
