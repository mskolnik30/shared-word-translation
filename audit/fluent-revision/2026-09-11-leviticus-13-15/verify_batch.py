"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='77d88c1de8474692b597753a6720ee9af23b9ca9';COUNTS={13:59,14:57,15:33}
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
 assert len(audits)==25 and len(chapters)==110 and sum(a['verses'] for a in audits)==3310
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':456}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==149
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['14:48']
 assert 'vowels in L differently from BHS' in raw['Lev 14:48']
 assert all(w in raw['Lev 13:31'] for w in ['שֵׂעָ֥ר','שָׁחֹ֖ר','אֵ֣ין'])
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
 checks={'13:1': ['Moses and Aaron'], '13:2': ['someone', 'swelling', 'scab', 'bright spot', 'Aaron', 'sons'], '13:3': ['hair', 'white', 'and', 'deeper', 'declare the person unclean'], '13:4': ['does not look deeper', 'hair has not turned white', 'seven days'], '13:5': ['unchanged', 'has not spread', 'another seven days'], '13:6': ['second seven-day', 'faded', 'has not spread', 'declare the person clean', 'wash their clothes'], '13:10': ['white swelling', 'hair', 'raw flesh'], '13:11': ['longstanding', 'must not confine', 'already unclean'], '13:12': ['head to foot', 'priest can see'], '13:13': ['whole body', 'completely white', 'they are clean'], '13:15': ['raw flesh is unclean'], '13:18': ['boil', 'healed'], '13:19': ['white swelling', 'reddish-white'], '13:20': ['lower', 'hair has turned white'], '13:21': ['no white hair', 'not lower', 'faded', 'seven days'], '13:23': ['does not spread', 'scar', 'clean'], '13:24': ['fire', 'reddish-white or white'], '13:25': ['deeper', 'burn'], '13:28': ['not spread', 'faded', 'swelling', 'scar'], '13:29': ['man or a woman', 'scalp', 'beard'], '13:30': ['thin yellow hair'], '13:31': ['no black hair', 'seven days'], '13:32': ['no yellow hair', 'not look deeper'], '13:33': ['leave the scaly area unshaved', 'another seven days'], '13:34': ['not spread', 'not look deeper', 'wash their clothes'], '13:36': ['need not look for yellow hair'], '13:37': ['black hair has grown', 'healed', 'clean'], '13:39': ['dull white', 'pale rash', 'clean'], '13:40': ['back of his head', 'clean'], '13:41': ['front of his head', 'clean'], '13:44': ['certainly declare', 'head'], '13:45': ['torn clothes', 'hair loose', 'upper lip', 'Unclean! Unclean!'], '13:46': ['as long as', 'live alone', 'outside the camp'], '13:48': ['warp', 'weft', 'linen', 'wool', 'leather'], '13:49': ['greenish or reddish'], '13:51': ['seventh day', 'destructive'], '13:52': ['burn', 'wool or linen', 'leather'], '13:54': ['washed', 'another seven days'], '13:55': ['not changed', 'even if', 'not spread', 'burn', 'back or front'], '13:56': ['faded', 'tear that part out'], '13:57': ['again', 'burn'], '13:58': ['disappears', 'second time', 'clean'], '14:3': ['outside the camp', 'healed'], '14:4': ['two live, clean birds', 'cedar wood', 'scarlet yarn', 'hyssop'], '14:5': ['order', 'slaughtered', 'fresh water', 'earthenware'], '14:6': ['including the live bird'], '14:7': ['seven times', 'release', 'live bird'], '14:8': ['all their hair', 'enter the camp', 'outside their tent', 'seven days'], '14:9': ['seventh day', 'beard', 'eyebrows'], '14:10': ['eighth day', 'two male lambs without defect', 'one year-old female lamb without defect', 'three-tenths', 'ephah', 'one log'], '14:11': ['man being cleansed'], '14:12': ['guilt offering', 'log', 'wave offering'], '14:13': ['belongs to the priest', 'most holy'], '14:14': ['right earlobe', 'right thumb', 'right big toe'], '14:15': ['left palm'], '14:16': ['right finger', 'left palm', 'seven times'], '14:17': ['right earlobe', 'right thumb', 'right big toe', 'over the blood'], '14:18': ['rest of the oil', 'head', 'atonement'], '14:19': ['impurity', 'burnt offering must be slaughtered'], '14:21': ['poor', 'one male lamb', 'one-tenth', 'ephah', 'log'], '14:22': ['two turtledoves or two young pigeons', 'sin offering', 'burnt offering'], '14:23': ['eighth day'], '14:24': ['wave offering', 'log'], '14:25': ['right earlobe', 'right thumb', 'right big toe'], '14:26': ['left palm'], '14:27': ['right finger', 'left palm', 'seven times'], '14:28': ['right earlobe', 'right thumb', 'right big toe', 'where the blood'], '14:29': ['rest of the oil', 'head'], '14:30': ['can afford'], '14:31': ['can afford', 'one as a sin offering', 'other as a burnt offering', 'grain offering'], '14:33': ['Moses and Aaron'], '14:34': ['Canaan', 'I put', 'possess'], '14:35': ['looks like'], '14:36': ['Before', 'emptied', 'none of its contents'], '14:37': ['greenish or reddish', 'lower'], '14:38': ['leave the house', 'entrance', 'seven days'], '14:40': ['stones', 'unclean place outside the city'], '14:41': ['all around', 'unclean place outside the city'], '14:42': ['Other stones', 'fresh plaster'], '14:43': ['removed', 'scraped', 'replastered'], '14:45': ['torn down', 'stones', 'timbers', 'all its plaster', 'unclean place outside the city'], '14:46': ['enters', 'until evening'], '14:47': ['lies down', 'eats'], '14:48': ['not spread', 'healed'], '14:51': ['cedar wood', 'hyssop', 'scarlet yarn', 'live bird', 'blood', 'fresh water', 'seven times'], '14:52': ['blood', 'fresh water', 'live bird', 'cedar wood', 'hyssop', 'scarlet yarn'], '14:53': ['release', 'outside the city', 'atonement for the house'], '14:57': ['to teach', 'unclean', 'clean'], '15:2': ['any man', 'genitals'], '15:3': ['flow', 'blocked'], '15:4': ['bed', 'lies', 'sits'], '15:8': ['spits', 'that person'], '15:9': ['Anything', 'rides on'], '15:10': ['touches', 'carries'], '15:11': ['his hands', 'person he touches'], '15:12': ['earthenware', 'broken', 'wooden', 'rinsed'], '15:13': ['free of his discharge', 'seven days', 'fresh water'], '15:14': ['eighth day', 'two turtledoves or two young pigeons'], '15:15': ['sin offering', 'burnt offering', 'discharge'], '15:16': ['semen', 'whole body', 'until evening'], '15:17': ['clothing or leather', 'washed', 'until evening'], '15:18': ['intercourse', 'emits semen', 'both must bathe', 'both remain unclean'], '15:19': ['seven days', 'touches her', 'until evening'], '15:23': ['something is on her bed', 'touches it'], '15:24': ['intercourse', 'seven days', 'Every bed'], '15:25': ['many days outside', 'continues beyond'], '15:26': ['bed', 'sits', 'discharge lasts'], '15:28': ['free of her discharge', 'seven days'], '15:29': ['eighth day', 'two turtledoves or two young pigeons'], '15:30': ['sin offering', 'burnt offering', 'discharge'], '15:31': ['Israelites', 'die', 'defiling my tabernacle', 'among them'], '15:33': ['male or female', 'intercourse']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 for v in [5,6,7,8,10,11,21,22,27]:
  t=byref[f'15:{v}']['after'];assert all(x in t for x in ['wash their clothes','bathe in water','unclean until evening'])
 assert 'wash' not in byref['15:10']['after'].split('.')[0]
 assert 'bathe' not in byref['15:28']['after']
 assert byref['14:47']['after'].count('wash their clothes')==2
 assert 'Aaron' not in byref['14:1']['after']
 assert all('forgiven' not in v['after'] for v in byref.values())
 assert all('leprosy' not in v['after'] and 'contagious' not in v['after'] for v in byref.values())
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,16))
  assert len(new['revision_batches'])==5 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 13–15; 149 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 13–15; 149 verses','revision_audits':audits,'cumulative_coverage':{'chapters':110,'verses':3310},'source_record_count':859,'public_source_mapping':'Leviticus 13–15 aligns directly; all 149 records are unique and complete, including the vowel annotation at 14:48. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 149 pinned Hebrew records, including the vowel annotation at 14:48. Selected NET lexical and grammatical notes were consulted after reading each Hebrew chapter, before and during drafting. All TSW comparators were read after drafting. The complete assembled text was reread. Focused checks cover observation criteria and black/yellow hair; staged confinement and cleansing; garment washing, removal and burning; male/female lamb counts and poverty provisions; blood/oil side, order and counts; house emptying, disposal and divine agency; discharge versus semen and menstruation; touch versus carrying; seven/eight-day intervals; text and pronoun ambiguities. This is an authoring self-check, not independent scholarly review.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':25,'chapters':110,'verses':3310,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
