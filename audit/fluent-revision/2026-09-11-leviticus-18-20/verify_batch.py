"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='fbe6cb003ee8a9f0298ff74743f9afdfec4a7ff6';COUNTS={18:30,19:37,20:27}
sys.path.insert(0,str(ROOT/'tools'))
from audit_translation_overlap import words

def run(*args):
 r=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);assert r.returncode==0,r.stdout+r.stderr
 return r.stdout.strip()
def put(name,d):(BATCH/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser()
 for book in ['genesis','exodus','leviticus','james']:p.add_argument('--'+book+'-source',type=Path,required=True)
 args=p.parse_args();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];chapters=set();refs={}
 for s in q['completed_draft_scopes']:
  book=s['scope'].split()[0];l=json.loads((ROOT/s['ledger']).read_text())
  audits.append({'ledger':s['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',s['ledger'],'--source-text',str(getattr(args,book.lower()+'_source').resolve())))})
  for c in l['chapters']:assert c['path'] not in chapters;chapters.add(c['path'])
  rs=refs.setdefault(book,set())
  for v in l['verses']:assert v['source_reference'] not in rs;rs.add(v['source_reference'])
 assert len(audits)==27 and len(chapters)==115 and sum(a['verses'] for a in audits)==3454
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':600}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==94
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['18:17','19:1','20:2']
 for ref in annotated:
  assert 'BHS has been faithful to the Leningrad Codex' in raw['Lev '+ref]
 assert all('KJV:' not in raw['Lev '+ref] and 'type="x-qere"' not in raw['Lev '+ref] for ref in byref)
 for c,n in COUNTS.items():
  t=(ROOT/f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md').read_text();m=t.split('---',2)[2].split('## Notes')[0]
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
 checks={'18:3': ['Egypt', 'where you lived', 'Canaan', 'where I am bringing you'], '18:5': ['Whoever', 'will live by them'], '18:7': ["father's nakedness", "mother's nakedness", 'She is your mother'], '18:8': ["father's wife", "father's nakedness"], '18:9': ["father's daughter", "mother's daughter", 'born within the household or outside it', 'either'], '18:10': ["son's daughter", "daughter's daughter", 'your own nakedness'], '18:11': ["father's wife", 'born to your father', 'your sister'], '18:12': ["father's sister", "father's close relative"], '18:13': ["mother's sister", "mother's close relative"], '18:14': ["father's brother's nakedness", 'his wife', 'your aunt'], '18:15': ['daughter-in-law', "son's wife"], '18:16': ["brother's wife", "brother's nakedness"], '18:17': ['both a woman and her daughter', "her son's daughter", "her daughter's daughter", "woman's close relatives", 'depravity'], '18:18': ['While your wife is alive', 'her sister', 'rival wife'], '18:19': ['menstrual uncleanness'], '18:20': ["neighbor's wife", 'unclean'], '18:21': ['offspring', 'Molech', 'profane'], '18:22': ['male as with a woman', 'abomination'], '18:23': ['any animal', 'A woman', 'for it to mate with her', 'perversion'], '18:25': ['land became unclean', 'punished it', 'wrongdoing', 'vomited out its inhabitants'], '18:26': ['native-born', 'foreigner living among you'], '18:28': ['vomit you out', 'vomited out the nation'], '18:29': ['Anyone', 'any', 'cut off'], '19:2': ['whole Israelite community', 'Be holy', 'am holy'], '19:3': ['mother and your father', 'sabbaths'], '19:4': ['idols', 'cast metal'], '19:5': ['peace sacrifice', 'accepted on your behalf'], '19:6': ['day you offer it or the next day', 'third day', 'burned with fire'], '19:7': ['third day', 'defiled thing', 'not be accepted'], '19:8': ['bear their guilt', 'cut off'], '19:9': ['edges', 'leave behind'], '19:10': ['vineyard bare', 'fallen grapes', 'poor', 'foreigner'], '19:13': ['exploit', 'rob', 'hired worker', 'overnight until morning'], '19:14': ['deaf', 'blind', 'stumble', 'Fear your God'], '19:15': ['favor the poor', 'defer to the powerful', 'justice'], '19:16': ['slandering', "neighbor's blood"], '19:17': ['fellow Israelite', 'in your heart', 'rebuke', 'bear sin'], '19:18': ['revenge', 'grudge', 'Love your neighbor as yourself'], '19:19': ['different kinds of livestock', 'mixed kinds of seed', 'mixed materials'], '19:20': ['enslaved woman who', 'promised to another man', 'neither been redeemed nor granted freedom', 'inquiry', 'must not be put to death', 'she has not been freed'], '19:21': ['The man', 'ram', 'guilt offering', 'entrance', 'tent of meeting'], '19:22': ['priest', 'atonement for him', 'He will be forgiven'], '19:23': ['uncircumcised', 'three years', 'must not be eaten'], '19:24': ['fourth year', 'all its fruit', 'holy', 'praise'], '19:25': ['fifth year', 'eat its fruit', 'yield may increase'], '19:26': ['blood', 'divination', 'omens'], '19:28': ['cut your flesh for the dead', 'tattoo marks'], '19:29': ['your daughter', 'making her a prostitute', 'land', 'depravity'], '19:30': ['sabbaths', 'sanctuary'], '19:31': ['mediums or spiritists', 'seek them out'], '19:32': ['Rise', 'gray hair', 'elderly', 'fear your God'], '19:34': ['foreigner living among you', 'native-born', 'Love them as yourself', 'foreigners in Egypt'], '19:35': ['length, weight, or volume'], '19:36': ['scales', 'weights', 'ephah', 'hin', 'brought you out of Egypt'], '20:2': ['Israelite or foreigner living in Israel', 'offspring', 'put to death', 'people of the land', 'stone'], '20:3': ['I myself', 'set my face', 'cut them off', 'sanctuary', 'holy name'], '20:4': ['close their eyes', 'fail to put that person to death'], '20:5': ['their family', 'all who follow them', 'prostituting themselves'], '20:6': ['mediums and spiritists', 'prostituting themselves', 'set my face', 'cut them off'], '20:7': ['Consecrate yourselves', 'be holy'], '20:8': ['makes you holy'], '20:9': ['curses their father or mother', 'put to death', 'blood is on themselves'], '20:10': ["another man's wife", "neighbor's wife", 'adulterer and the adulteress', 'put to death'], '20:11': ["father's wife", "father's nakedness", 'Both of them must be put to death'], '20:12': ['daughter-in-law', 'Both of them', 'perversion'], '20:13': ['male as with a woman', 'both have committed an abomination', 'put to death'], '20:14': ['both a woman and her mother', 'He and the women', 'burned with fire', 'depravity'], '20:15': ['man', 'put to death', 'kill the animal'], '20:16': ['woman', 'for it to mate with her', 'kill both the woman and the animal', 'put to death'], '20:17': ["father's daughter", "mother's daughter", 'sees her nakedness while she sees his', 'disgrace', 'before the eyes', 'bear his guilt'], '20:18': ['during her period', 'her fountain', 'fountain of her blood', 'Both will be cut off'], '20:19': ["mother's sister or your father's sister", 'close relative', 'their guilt'], '20:20': ["uncle's wife", "uncle's nakedness", 'bear their sin', 'die childless'], '20:21': ["brother's wife", 'uncleanness', 'will be childless'], '20:22': ['all my statutes and all my ordinances', 'vomit you out'], '20:23': ['the nation', 'all these things', 'loathed them'], '20:24': ['take possession', 'your possession', 'flowing with milk and honey', 'set you apart'], '20:25': ['clean animals from unclean', 'unclean birds from clean', 'moves along the ground', 'set apart for you as unclean'], '20:26': ['Be holy to me', 'set you apart', 'to be mine'], '20:27': ['man or woman', 'spirit of the dead or a familiar spirit', 'put to death', 'stoned', 'blood is on themselves']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['18:15']['after'].count('sexual relations')==2
 assert byref['19:22']['after'].count('sin he committed')==2
 assert byref['19:23']['after'].count('uncircumcised')==2
 assert byref['19:36']['after'].count('honest')==4
 assert byref['20:10']['after'].count('adultery')==2
 assert byref['20:18']['after'].count('fountain')==2
 assert sum('their blood is on themselves' in v['after'].lower() for v in byref.values())==6
 for ref in ['18:21','20:2','20:3','20:4','20:5']:assert 'fire' not in byref[ref]['after']
 for ref in ['18:22','20:13']:assert all(t not in byref[ref]['after'].lower() for t in ['homosexual','boy','temple','rape','consensual'])
 assert 'die childless' not in byref['20:21']['after']
 assert 'consent' not in byref['19:20']['after']
 assert byref['19:25']['delta']=='F0' and byref['19:25']['before']==byref['19:25']['after']
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,21))
  assert len(new['revision_batches'])==7 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 18–20; 94 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 18–20; 94 verses','revision_audits':audits,'cumulative_coverage':{'chapters':115,'verses':3454},'source_record_count':859,'public_source_mapping':'Leviticus 18–20 aligns directly; all 94 records are unique and complete, including original annotation notes at 18:17, 19:1 and 20:2. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 94 pinned Hebrew records and their annotations before drafting. Selected NET lexical and grammatical notes and NRSVUE 19:20 were consulted before drafting; all 94 TSW comparators were read afterward. A scholarly discussion of the mlk offering interpretation was checked during apparatus review. The assembled English was reread, and ambiguous pronoun attachment in 19:20 was corrected. Focused checks cover kinship alternatives, native/foreigner scope, ritual dates, gleanings, wages, disability, equal justice, neighbor/foreigner love, slavery and unspecific consent, inquiry alternatives, male offering liability, uncircumcised fruit, honest units, cultic imagery, explicit harms and penalties, repeated adultery, nakedness and fountain language, blood responsibility and die/be childless distinctions. This is an authoring self-check, not independent scholarly review.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':27,'chapters':115,'verses':3454,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
