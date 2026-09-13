"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='ca252fdc5596a1a4ffd9a165c5406c4c414c01d2';COUNTS={7:26,8:20,9:29,10:22,11:32,12:32}
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
 assert len(audits)==42 and len(chapters)==170 and sum(a['verses'] for a in audits)==5381
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':1289,'Deuteronomy':380}
 raw={f'Deut {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.deuteronomy_source.read_text(),re.S) for c,v in [re.search(r'osisID="Deut\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==959
 l=json.loads((BATCH/'deuteronomy-verse-review.json').read_text());byref={v['reference'].replace('Deuteronomy ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 source_refs=[]
 for ref,v in byref.items():
  sr='Deut 13:1' if ref=='12:32' else 'Deut '+ref;source_refs.append(sr)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len(source_refs)==len(set(source_refs))==161
 assert set(source_refs)=={ref for ref in raw if 7<=int(ref.split()[1].split(':')[0])<=12 or ref=='Deut 13:1'}
 assert refs['Deuteronomy']=={r for r in raw if int(r.split()[1].split(':')[0])<=12 or r=='Deut 13:1'}
 annotated=[ref for ref in source_refs if '<note' in raw[ref]]
 assert annotated==['Deut 7:8','Deut 7:9','Deut 8:2','Deut 8:3','Deut 9:3','Deut 9:20','Deut 10:1','Deut 10:7','Deut 10:15','Deut 10:22','Deut 12:2','Deut 12:3','Deut 13:1']
 for ref in ['Deut 7:9','Deut 8:2']:assert 'x-ketiv' in raw[ref] and 'x-qere' in raw[ref]
 assert 'KJV:Deut.12.32' in raw['Deut 13:1']
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
 checks={'7:1': ['Hittites, Girgashites, Amorites, Canaanites, Perizzites, Hivites, and Jebusites', 'seven nations'], '7:2': ['devote them completely to destruction', 'no covenant', 'no mercy'], '7:3': ['daughter', 'son'], '7:4': ['following the LORD'], '7:5': ['standing stones', 'Asherah poles'], '7:8': ['redeemed', 'house of slavery', 'Pharaoh'], '7:9': ['thousand generations', 'his commands'], '7:10': ['to their face', 'destroying'], '7:13': ['fruit of your womb', 'fruit of your ground', 'grain, new wine, and oil', 'calves', 'flocks'], '7:14': ['man or woman', 'livestock'], '7:16': ['devour', 'pity', 'snare'], '7:20': ['hornets'], '7:22': ['little by little', 'wild animals'], '7:26': ['you too', 'devoted to destruction'], '8:2': ['forty years', 'humble', 'test', 'know', 'his commands'], '8:3': ['go hungry', 'manna', 'bread alone', "LORD's mouth"], '8:4': ['clothing', 'feet', 'forty years'], '8:5': ['man disciplines his son'], '8:8': ['wheat and barley', 'vines', 'fig trees', 'pomegranates', 'olive oil', 'honey'], '8:9': ['iron', 'copper'], '8:15': ['fiery snakes', 'scorpions', 'flint rock'], '8:17': ['My power', 'my own hand'], '8:18': ['power to gain wealth', 'covenant'], '8:20': ['Like the nations', 'so you will perish'], '9:1': ['fortified up to the heavens'], '9:3': ['consuming fire', 'quickly'], '9:4': ['my righteousness'], '9:5': ['uprightness', 'wickedness', 'Abraham, Isaac, and Jacob'], '9:6': ['stiff-necked'], '9:9': ['forty days and forty nights', 'no bread', 'no water'], '9:10': ['finger of God'], '9:12': ['Your people', 'you brought'], '9:14': ['Leave me alone', 'wipe out their name'], '9:15': ['two hands'], '9:18': ['forty days and forty nights', 'no bread', 'no water'], '9:20': ['Aaron', 'destroy'], '9:21': ['burned', 'crushed', 'grinding', 'dust', 'stream'], '9:22': ['Taberah', 'Massah', 'Kibroth-hattaavah'], '9:25': ['those forty days'], '9:26': ['your people', 'your inheritance'], '9:28': ['could not', 'hated'], '10:1': ['two stone tablets', 'wooden ark'], '10:3': ['acacia wood'], '10:4': ['Ten Words'], '10:6': ['Beeroth Bene-jaakan', 'Moserah', 'Aaron', 'Eleazar'], '10:7': ['Gudgodah', 'Jotbathah'], '10:8': ['Levi', 'carry', 'serve', 'bless'], '10:9': ['no share', 'LORD is his inheritance'], '10:10': ['forty days and forty nights'], '10:12': ['fear', 'walk', 'love', 'serve', 'all your heart', 'all your soul'], '10:16': ['Circumcise your hearts', 'stiffen your necks'], '10:17': ['God of gods', 'Lord of lords', 'no favoritism', 'no bribe'], '10:18': ['fatherless', 'widow', 'resident foreigner', 'food and clothing'], '10:19': ['love the resident foreigner', 'Egypt'], '10:22': ['seventy', 'stars'], '11:2': ['not to your children'], '11:4': ['horses and chariots', 'Sea of Reeds'], '11:6': ['Dathan and Abiram', 'Eliab', 'Reuben', 'earth opened its mouth', 'households', 'tents'], '11:10': ['with your foot'], '11:11': ['drinks water'], '11:12': ['eyes', 'beginning of the year'], '11:14': ['I will give', 'autumn rain', 'spring rain', 'grain, new wine, and oil'], '11:15': ['grass', 'livestock'], '11:17': ['shut up the heavens', 'no rain'], '11:18': ['heart and soul', 'hand', 'between your eyes'], '11:19': ['sit at home', 'walk along the road', 'lie down', 'get up'], '11:20': ['doorposts', 'gates'], '11:21': ['heavens are over the earth'], '11:24': ['sole of your foot', 'Lebanon', 'Euphrates', 'western sea'], '11:29': ['blessing on Mount Gerizim', 'curse on Mount Ebal'], '11:30': ['Jordan', 'road', 'sunset', 'Arabah', 'Gilgal', 'Moreh'], '12:2': ['mountains', 'hills', 'leafy tree'], '12:3': ['burn their Asherah poles', 'cut down the carved images'], '12:5': ['will choose', 'his name', 'dwelling'], '12:6': ['burnt offerings', 'sacrifices', 'tithes', 'contributions', 'vow offerings', 'freewill offerings', 'firstborn'], '12:12': ['sons and daughters', 'male and female slaves', 'Levite', 'no share'], '12:15': ['slaughter', 'towns', 'unclean and the clean', 'gazelle or deer'], '12:16': ['not eat the blood', 'ground like water'], '12:18': ['son and daughter', 'male and female slave', 'Levite'], '12:19': ['not to neglect'], '12:21': ['too far', 'as I commanded you'], '12:22': ['together'], '12:23': ['blood is the life', 'life with the flesh'], '12:24': ['ground like water'], '12:27': ['flesh and blood', 'altar', 'other sacrifices', 'eat their flesh'], '12:31': ['burned their sons and daughters'], '12:32': ['Do not add', 'take anything away']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['8:2']['after'].count('his commands')==1
 assert byref['12:32']['source_reference']=='Deut 13:1'
 assert q['next_work'][0]['scope']=='Deuteronomy 13–18' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/deuteronomy/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/deuteronomy/Deuteronomy_{c:02}.md' for c in COUNTS}|{reviewdir+f'Deuteronomy_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','DEUTERONOMY_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,13))
  assert len(new['revision_batches'])==2 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  assert new['current_revision']['not_yet_revised_chapters']==list(range(13,35))
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Deuteronomy 7–12; 161 public verses / 161 source records','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Deuteronomy 7–12; 161 public verses / 161 source records','revision_audits':audits,'cumulative_coverage':{'chapters':170,'verses':5381},'source_record_count':959,'public_source_mapping':'Public Deuteronomy 7–11 and 12:1–31 align directly; public 12:32 binds the full original Hebrew 13:1 record including its numbering note. Other books retain their earlier mappings, including the two-record Numbers 26:1 binding.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 161 selected Hebrew records were read before drafting, and all 161 TSW comparator verses after drafting. NET translators’ notes on chapters 7 and 11 were consulted before drafting for selected lexical and grammatical difficulties. The self-check covered seven people names, explicit ban and harm, spelling variants without duplicate words, fruit and resource lists, all forty-day and forty-year references, divine and human speech, tablets and intercession, the divergent journey notice without harmonization, love and provision for the resident foreigner, irrigation imagery and rain seasons, daily teaching repetition, mountain assignments, sacred versus ordinary meals, clean and unclean diners, blood disposal, explicit child burning, and the 12:32/13:1 mapping. This is authoring and structural QA, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':42,'chapters':170,'verses':5381,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
