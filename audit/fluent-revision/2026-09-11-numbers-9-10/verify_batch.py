"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='f557a6833b748ba1a83fc82badb3edbccf84d2b8';COUNTS={9:23,10:36}
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
 assert len(audits)==35 and len(chapters)==132 and sum(a['verses'] for a in audits)==4133
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':420}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Num '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Num '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==59
 annotated=[ref for ref in byref if '<note' in raw['Num '+ref]];assert annotated==['9:3','9:10','9:21','10:9','10:25','10:34','10:36']
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
 checks={'9:1': ['first month', 'second year', 'Egypt', 'Sinai'], '9:3': ['twilight', 'fourteenth', 'all its statutes', 'all its regulations'], '9:5': ['fourteenth day of the first month', 'Sinai', 'twilight'], '9:6': ['some men', 'unclean', 'dead person', 'could not', 'same day', 'Moses and Aaron'], '9:7': ['Why should we be kept', 'appointed time', 'rest of Israel'], '9:8': ['Wait', 'hear', 'concerning you'], '9:10': ['descendants', 'dead person', 'distant journey', 'may still'], '9:11': ['fourteenth day of the second month', 'twilight', 'unleavened bread', 'bitter herbs'], '9:12': ['none', 'morning', 'not break any', 'bones', 'every statute'], '9:13': ['clean and not away', 'fails', 'cut off', 'appointed time', 'bear their sin'], '9:14': ['resident foreigner', 'one rule', 'native-born'], '9:15': ['tent of the testimony', 'evening until morning', 'like fire'], '9:16': ['always', 'at night', 'appearance of fire'], '9:17': ['Whenever', 'Wherever', 'set out', 'make camp'], '9:19': ['many days', 'kept the LORD’s charge', 'did not'], '9:20': ['few days'], '9:21': ['evening to morning', 'By day or by night'], '9:22': ['two days', 'month', 'year', 'did not set out'], '9:23': ['kept the LORD’s charge', 'through Moses'], '10:2': ['two trumpets', 'hammered silver', 'call the community', 'camps to move'], '10:3': ['both trumpets', 'whole community', 'entrance'], '10:4': ['one', 'leaders', 'thousands'], '10:5': ['alarm signal', 'east'], '10:6': ['second alarm signal', 'south'], '10:7': ['do not sound the alarm signal'], '10:8': ['Aaron’s sons', 'priests', 'lasting statute', 'generations'], '10:9': ['war', 'your own land', 'oppresses', 'remembered', 'rescued'], '10:10': ['rejoicing', 'festivals', 'beginnings of your months', 'burnt offerings', 'peace-offering sacrifices', 'reminder'], '10:11': ['second year', 'twentieth day', 'second month', 'tabernacle of the testimony'], '10:12': ['Sinai', 'Paran', 'stages'], '10:17': ['Gershonites and Merarites', 'carrying'], '10:21': ['Kohathites', 'holy things', 'already be set up'], '10:25': ['rear guard for all the camps'], '10:29': ['Hobab son of Reuel', 'Midianite', 'Moses’ relative by marriage', 'I will give it to you', 'promised good'], '10:30': ['Hobab', 'will not', 'own land', 'own people'], '10:31': ['Please do not leave', 'camp in the wilderness', 'our eyes'], '10:32': ['If you come', 'whatever good'], '10:33': ['mountain of the LORD', 'three days', 'three-day journey', 'ark of the LORD’s covenant', 'ahead', 'resting place'], '10:34': ['cloud', 'by day'], '10:35': ['Rise, LORD', 'enemies scatter', 'hate you flee'], '10:36': ['Return, LORD', 'myriads of thousands']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 leaders={14:('Judah','Nahshon','Amminadab'),15:('Issachar','Nethanel','Zuar'),16:('Zebulun','Eliab','Helon'),18:('Reuben','Elizur','Shedeur'),19:('Simeon','Shelumiel','Zurishaddai'),20:('Gad','Eliasaph','Deuel'),22:('Ephraim','Elishama','Ammihud'),23:('Manasseh','Gamaliel','Pedahzur'),24:('Benjamin','Abidan','Gideoni'),25:('Dan','Ahiezer','Ammishaddai'),26:('Asher','Pagiel','Ochran'),27:('Naphtali','Ahira','Enan')}
 for verse,terms in leaders.items():
  assert all(t in byref[f'10:{verse}']['after'] for t in terms)
 for verse in [14,18,22,25]:assert 'banner' in byref[f'10:{verse}']['after'] and 'divisions' in byref[f'10:{verse}']['after']
 for verse in [18,20,23]:assert byref[f'9:{verse}']['after'].count('At the LORD’s command')+byref[f'9:{verse}']['after'].count('at the LORD’s command')==2
 assert byref['9:23']['after'].count('LORD')==4
 assert 'by day' not in byref['9:16']['after']
 assert sum(raw['Num '+ref].count('<note') for ref in annotated)==8
 assert '\u05c4' in raw['Num 9:10'] or chr(0x5c4) in raw['Num 9:10']
 assert 'Inverted nun' in raw['Num 10:34'] and 'Inverted nun' in raw['Num 10:36']
 t10=(ROOT/'translations/fluent/OT/numbers/Numbers_10.md').read_text().split('## Notes')[0]
 assert 'would say:\n“Rise, LORD!\nLet your enemies scatter;\nlet those who hate you flee before you!”' in t10
 assert 'would say:\n“Return, LORD,\nto Israel’s myriads of thousands!”' in t10
 assert byref['10:32']['delta']=='F0' and byref['10:32']['before']==byref['10:32']['after']
 n9=(ROOT/'translations/fluent/OT/numbers/Numbers_09.md').read_text().split('## Notes')[1]
 n10=(ROOT/'translations/fluent/OT/numbers/Numbers_10.md').read_text().split('## Notes')[1]
 assert 'day and a night' in n9 and 'literally “days,”' in n9
 assert 'father-in-law' in n10 and 'attached to Reuel' in n10 and 'does not record his answer' in n10
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==[1,2,3,4,5,6,7,8,9,10]
  assert len(new['revision_batches'])==5 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 9–10; 59 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 9–10; 59 verses','revision_audits':audits,'cumulative_coverage':{'chapters':132,'verses':4133},'source_record_count':1289,'public_source_mapping':'Numbers 9–10 aligns directly; all 59 original records are unique and complete, including eight annotations across seven verses, the extraordinary dot at 9:10 and inverted-nun annotations at 10:34 and 10:36. Earlier books and their public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read every one of the 59 pinned Hebrew verses before drafting. NET grammatical and lexical comparison followed; all 59 TSW verses were read after drafting. Self-checks preserve first/second-month Passover dates, both exceptions and the severe sanction, ritual versus moral impurity, shared resident/native rule, repeated divine command, cloud durations and alternatives, both/one trumpet and alarm/assembly distinctions, exact departure date, all twelve leaders and tribal order, the separate carrying groups, ambiguous Hobab kinship, the eyes image and unanswered invitation, both three-day references and the ark’s position, and both poetic invocations. Eight source annotations remain in the hashes. Existing clear wording at 10:32 is retained without an overlap quota. These are authoring self-checks, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':35,'chapters':132,'verses':4133,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
