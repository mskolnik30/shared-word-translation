"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='bc57156b1df19cd189e0196340afc6ba2c1f81a6';COUNTS={11:47,12:8}
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
 assert len(audits)==24 and len(chapters)==107 and sum(a['verses'] for a in audits)==3161
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':307}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==55
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['11:21','11:42']
 assert 'type="x-qere"' in raw['Lev 11:21'] and '<catchWord>לא</catchWord>' in raw['Lev 11:21'] and 'ל֤/וֹ' in raw['Lev 11:21']
 assert 'Large letter(s)' in raw['Lev 11:42']
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
 checks={'11:1':['Moses and Aaron'],'11:3':['completely split in two and chews the cud'],'11:4':['camel','chews the cud','does not have divided hooves'],'11:5':['rock hyrax','chews the cud'],'11:6':['hare','chews the cud'],'11:7':['pig','completely split in two','does not chew the cud'],'11:8':['eat their meat','touch their carcasses'],'11:9':['fins and scales','seas or the streams'],'11:10':['does not have both fins and scales','detestable'],'11:12':['does not have both fins and scales'],'11:13':['eagle','bearded vulture','black vulture'],'11:14':['kite','every kind of falcon'],'11:15':['every kind of raven'],'11:16':['ostrich','nighthawk','gull','every kind of hawk'],'11:17':['little owl','cormorant','great owl'],'11:18':['barn owl','pelican','carrion vulture'],'11:19':['stork','every kind of heron','hoopoe','bat'],'11:20':['on all fours'],'11:21':['may eat','jointed legs above their feet','leaping'],'11:22':['locust','bald locust','cricket','grasshopper'],'11:23':['other','four legs'],'11:25':['any part','wash their clothes','until evening'],'11:26':['not fully split and','does not chew'],'11:27':['paws','carcasses','until evening'],'11:29':['weasel','mouse','every kind of large lizard'],'11:30':['gecko','monitor lizard','common lizard','skink','chameleon'],'11:31':['when they are dead'],'11:32':['wooden utensil','clothing','leather','sackcloth','put in water','until evening','then it will be clean'],'11:33':['earthenware','everything inside','break the vessel'],'11:34':['food in it','contact with water','drink in such a vessel'],'11:35':['any part','oven or cooking stove','broken down'],'11:36':['spring or cistern','remains clean','touches the carcass'],'11:37':['seed intended for sowing','remains clean'],'11:38':['water has been put on the seed','unclean'],'11:39':['permitted to eat dies','until evening'],'11:40':['eats','carries','wash their clothes'],'11:42':['belly','all fours','many legs'],'11:43':['detestable','unclean'],'11:44':['Consecrate yourselves','be holy, because I am holy','swarming creature'],'11:45':['brought you up','land of Egypt','to be your God','Be holy, because I am holy'],'11:47':['unclean from the clean','may be eaten','must not be eaten'],'12:2':['woman','boy','seven days','menstrual period'],'12:3':['eighth day','foreskin','circumcised'],'12:4':['thirty-three days','bleeding','not touch anything holy','enter the sanctuary'],'12:5':['girl','two weeks','sixty-six days'],'12:6':['son or daughter','year-old lamb','burnt offering','young pigeon or turtledove','sin offering','priest'],'12:7':['atonement','clean from her flow of blood'],'12:8':['cannot afford','two turtledoves or two young pigeons','one for a burnt offering','one for a sin offering','she will be clean']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['11:40']['after'].count('wash their clothes and remain unclean until evening')==2
 assert byref['11:11']['after'].count('detestable')==2
 assert all('forgiven' not in byref[f'12:{v}']['after'] for v in range(1,9))
 assert 'Aaron' not in byref['12:1']['after']
 # The four birth periods remain distinct; the reader note totals are arithmetic only.
 assert 7+33==40 and 14+66==80
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,13))
  assert len(new['revision_batches'])==4 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 11–12; 55 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 11–12; 55 verses','revision_audits':audits,'cumulative_coverage':{'chapters':107,'verses':3161},'source_record_count':859,'public_source_mapping':'Leviticus 11–12 aligns directly; all 55 records are unique and complete, including written/read forms at 11:21 and large-letter annotation at 11:42. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 55 selected pinned Hebrew records including annotations at 11:21 and 11:42. Selected NET lexical notes informed provisional animal identifications before chapter-11 drafting; further grammatical notes and chapter-12 notes were consulted afterward. All TSW comparators were read after drafting. The complete assembled text was reread, checking animal-list coverage, both food criteria, carcass actions, material/water exceptions, repeated holiness language, childbirth periods, circumcision, offering alternatives and clean rather than forgiven conclusions. This is an authoring self-check, not independent scholarly review.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':24,'chapters':107,'verses':3161,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
