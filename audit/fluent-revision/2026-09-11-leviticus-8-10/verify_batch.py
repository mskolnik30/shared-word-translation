"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='89b69d19dab98aeb4ff3383bd1f2765bccd0841a';COUNTS={8:36,9:24,10:20}
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
 assert len(audits)==23 and len(chapters)==105 and sum(a['verses'] for a in audits)==3106
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':252}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==80
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['9:22']
 assert 'type="x-qere"' in raw['Lev 9:22'] and '<catchWord>יד/ו</catchWord>' in raw['Lev 9:22'] and 'יָדָ֛י/ו' in raw['Lev 9:22']
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
 checks={'8:2':['Aaron and his sons','garments','anointing oil','bull','two rams','unleavened bread'],'8:7':['tunic','sash','robe','ephod','woven waistband'],'8:8':['breastpiece','Urim and Thummim'],'8:9':['turban','gold plate','holy crown'],'8:11':['seven times','basin and its stand'],'8:12':['poured','Aaron’s head'],'8:15':['finger','horns','purifying','base','atonement'],'8:16':['all the fat','lobe of the liver','both kidneys'],'8:17':['skin, flesh, and dung','outside the camp'],'8:22':['second ram','ordination'],'8:23':['right earlobe','right thumb','big toe of his right foot'],'8:24':['right earlobes','right thumbs','big toes of their right feet','splashed'],'8:26':['one unleavened cake','one cake made with oil','one wafer','right thigh'],'8:27':['Aaron’s hands','sons’ hands','were waved'],'8:28':['from their hands','on top of the burnt offering'],'8:29':['breast','Moses’ share'],'8:30':['anointing oil','blood from the altar','Aaron and his garments','sons and their garments'],'8:31':['Boil','entrance','Eat it there','as I commanded'],'8:32':['meat and bread'],'8:33':['seven days','ordination'],'8:35':['day and night','seven days','do not die','I was commanded'],'9:1':['eighth day','Aaron','sons','elders'],'9:2':['bull calf','ram','both without defect'],'9:3':['male goat','calf and a lamb','both a year old'],'9:4':['ox and a ram','grain offering mixed with oil','today'],'9:7':['yourself and the people','people’s offering','atonement for them'],'9:9':['sons brought','finger','horns','base'],'9:12':['sons handed','splashed','all sides'],'9:15':['people’s offering','goat','first one'],'9:17':['handful','in addition to the morning'],'9:20':['they placed','Aaron burned'],'9:21':['breasts and right thigh','as Moses had commanded'],'9:22':['hands','blessed','sin offering','burnt offering','peace offerings'],'9:23':['Moses and Aaron','came out','all the people'],'9:24':['consumed','shouted','fell facedown'],'10:1':['Nadab and Abihu','each','firepan','incense','not commanded'],'10:2':['consumed them','they died'],'10:3':['show myself holy','honored','Aaron was silent'],'10:4':['Mishael and Elzaphan','Aaron’s uncle Uzziel','relatives'],'10:5':['in their tunics'],'10:6':['Eleazar and Ithamar','hair hang loose','tear your clothes','wrath','whole community','may mourn'],'10:8':['LORD spoke to Aaron'],'10:9':['wine or other intoxicating drink','when you enter','do not die'],'10:10':['holy and the common','unclean and the clean'],'10:11':['teach','all the statutes','through Moses'],'10:12':['surviving sons','without leaven','beside the altar','most holy'],'10:14':['clean place','sons and daughters'],'10:15':['lasting share','you and your sons'],'10:16':['searched carefully','burned','angry','surviving sons'],'10:17':['bear the community’s guilt','atonement'],'10:18':['not brought inside','should certainly have eaten'],'10:19':['Today they','happened to me','would that have pleased'],'10:20':['Moses heard','satisfied']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 for v in [9,13,17,21,29]:assert 'just as the LORD had commanded Moses' in byref[f'8:{v}']['after']
 assert byref['8:33']['after'].count('seven days')==2
 assert byref['8:30']['after'].count('Aaron and his garments')==2 and byref['8:30']['after'].count('sons and their garments')==2
 assert byref['9:24']['after'].startswith('Fire came out from before the LORD and consumed') and byref['10:2']['after'].startswith('Fire came out from before the LORD and consumed')
 assert 'Moses' not in byref['10:8']['after'] and 'daughters' not in byref['10:12']['after']
 assert not any('drunk' in byref[f'10:{v}']['after'] for v in range(1,21))
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,11))
  assert len(new['revision_batches'])==3 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 8–10; 80 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 8–10; 80 verses','revision_audits':audits,'cumulative_coverage':{'chapters':105,'verses':3106},'source_record_count':859,'public_source_mapping':'Leviticus 8–10 aligns directly; all 80 records are unique and complete, including the written/read forms at 9:22. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 80 selected pinned Hebrew records including the written/read note at 9:22, drafted independently, then read all TSW comparators and selected NET translator notes. It reread the complete assembled chapters and checked garments, ritual actors, right-side body applications, animal quantities, seven/eighth-day sequence, repeated commands, divine fire, death and mourning, holy/clean categories, daughters’ portions and Aaron’s response. This is an authoring self-check, not independent scholarly review.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':23,'chapters':105,'verses':3106,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
