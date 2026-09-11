"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='2e7038c947b7956652b04ffa82cddd46ff140731';COUNTS={5:31,6:27}
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
 assert len(audits)==33 and len(chapters)==128 and sum(a['verses'] for a in audits)==3959
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':246}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Num '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Num '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==58
 annotated=[ref for ref in byref if '<note' in raw['Num '+ref]];assert annotated==[]
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
 checks={'5:2': ['skin condition', 'bodily discharge', 'unclean by a dead person'], '5:3': ['male and female', 'Send them outside', 'I dwell'], '5:6': ['man or woman', 'breaking faith', 'guilt'], '5:7': ['confess', 'full restitution', 'one-fifth', 'person they wronged'], '5:8': ['family redeemer', 'LORD for the priest', 'in addition to the ram', 'guilty person'], '5:10': ['their own', 'belongs to the priest'], '5:13': ['sexual intercourse', 'without her husband knowing', 'no witness', 'without her being caught'], '5:14': ['when she has defiled herself', 'when she has not defiled herself'], '5:15': ['husband is to bring his wife', 'tenth of an ephah', 'barley flour', 'must not pour oil', 'frankincense', 'jealousy', 'remembrance'], '5:17': ['holy water', 'clay vessel', 'dust', 'tabernacle floor'], '5:18': ['loosen her hair', 'in her hands', 'He is to hold', 'bitter water'], '5:19': ['under oath', 'no other man', 'under your husband’s authority', 'unharmed'], '5:20': ['other than your husband', 'sexual intercourse'], '5:21': ['curse and an oath', 'thigh waste away', 'belly swell'], '5:22': ['belly swell', 'thigh waste away', 'Amen, amen'], '5:23': ['scroll', 'wash them off into'], '5:24': ['make the woman drink', 'bitter effects'], '5:25': ['woman’s hands', 'wave', 'altar'], '5:26': ['handful', 'memorial portion', 'burn', 'After that', 'make the woman drink'], '5:27': ['if she has defiled herself', 'belly will swell', 'thigh will waste away', 'curse among her people'], '5:28': ['has not defiled herself', 'clean', 'unharmed', 'able to conceive'], '5:30': ['spirit of jealousy', 'entire instruction'], '5:31': ['husband will be free from guilt', 'woman will bear her guilt'], '6:2': ['man or woman', 'special vow', 'Nazirite', 'set themselves apart'], '6:3': ['wine and other strong drink', 'vinegar made from either', 'soaking grapes', 'fresh or dried grapes'], '6:4': ['nothing', 'grapevine', 'seeds to the skins'], '6:5': ['no razor', 'holy', 'grow freely'], '6:6': ['not go near a dead person'], '6:7': ['father, mother, brother or sister', 'consecration to God', 'on their head'], '6:9': ['suddenly', 'unexpectedly', 'seventh day'], '6:10': ['eighth day', 'two turtledoves or two young pigeons', 'entrance of the tent'], '6:11': ['sin offering', 'burnt offering', 'atonement', 'sin in connection with the dead person', 'That same day'], '6:12': ['again', 'year-old male lamb', 'guilt offering', 'earlier days will not count'], '6:13': ['person is to be brought', 'entrance'], '6:14': ['one year-old male lamb without defect as a burnt offering', 'one year-old female lamb without defect as a sin offering', 'one ram without defect as a peace offering'], '6:15': ['fine flour', 'loaves mixed with oil', 'wafers spread with oil', 'grain offerings and drink offerings'], '6:16': ['sin offering and burnt offering'], '6:17': ['ram', 'peace-offering sacrifice', 'basket of unleavened bread', 'grain offering and drink offering'], '6:18': ['hair', 'fire beneath', 'peace-offering sacrifice'], '6:19': ['boiled shoulder', 'one unleavened loaf', 'one unleavened wafer', 'Nazirite’s hands'], '6:20': ['wave offering', 'belong to the priest', 'breast', 'contributed thigh', 'After this', 'may drink wine'], '6:21': ['anything else they can afford', 'do what they vowed'], '6:23': ['Aaron and his sons', 'bless the Israelites'], '6:24': ['LORD bless you and keep you'], '6:25': ['LORD make his face shine', 'gracious'], '6:26': ['LORD lift his face', 'peace'], '6:27': ['place my name on the Israelites', 'I myself will bless them']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['5:14']['after'].count('spirit of jealousy')==2
 assert byref['5:21']['after'].count('LORD')==2
 assert byref['5:20']['after'].endswith('—’')
 assert byref['5:21']['after'].index('thigh')<byref['5:21']['after'].index('belly')
 assert byref['5:22']['after'].index('belly')<byref['5:22']['after'].index('thigh')
 assert all('miscarriage' not in v['after'] and 'pregnant' not in v['after'] for v in byref.values())
 assert sum(byref[f'6:{v}']['after'].count('LORD') for v in [24,25,26])==3
 assert byref['6:14']['after'].count('without defect')==3
 assert byref['6:9']['after'].count('shave')==2
 for ref in ['6:25','6:26']:assert '\n' in byref[ref]['after'] or 'and ' in byref[ref]['after']
 t=(ROOT/'translations/fluent/OT/numbers/Numbers_06.md').read_text().split('## Notes')[0]
 assert 'v25:' in t and '\nand be gracious to you;' in t and '\nand give you peace.' in t
 notes=(ROOT/'translations/fluent/OT/numbers/Numbers_05.md').read_text().split('## Notes')[1]
 assert 'precise bodily outcome is uncertain' in notes and 'not explicitly state' in notes
 assert 'required number of separate drinks' in notes and 'may instead refer to the priest' in notes
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==[1,2,3,4,5,6]
  assert len(new['revision_batches'])==3 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 5–6; 58 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 5–6; 58 verses','revision_audits':audits,'cumulative_coverage':{'chapters':128,'verses':3959},'source_record_count':1289,'public_source_mapping':'Numbers 5–6 aligns directly; all 58 original records are unique and complete. No source note elements occur in this scope. Earlier books and their public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 58 pinned Hebrew verses before drafting. NET comparison and selected translators’ notes followed; all 58 TSW comparators were read after drafting. Checks address ritual versus moral categories, restitution and the added fifth, both jealousy conditions, husband/priest/woman agency, the bodily images and uncertainty, interrupted speech, repeated drinking, female and male Nazirites, seven/eight-day sequence, animal sex and offering assignments, loss of earlier days, priestly portions, and the blessing’s three invocations and face images. These are authoring self-checks, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':33,'chapters':128,'verses':3959,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
