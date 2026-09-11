"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='81ae342a7dc0e0da8e5b62f1aa8da495c57ea173';COUNTS={4:35,5:19,6:30,7:38}
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
 assert len(audits)==22 and len(chapters)==102 and sum(a['verses'] for a in audits)==3026
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':172}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 def mapped(ref):
  c,v=map(int,ref.split(':'));return f'Lev 5:{v+19}' if c==6 and v<=7 else f'Lev 6:{v-7}' if c==6 else 'Lev '+ref
 for ref,v in byref.items():assert v['source_reference']==mapped(ref) and v['source_verse_sha256']==hashlib.sha256(raw[mapped(ref)].encode()).hexdigest()
 assert len({mapped(ref) for ref in byref})==122
 annotated=[ref for ref in byref if '<note' in raw[mapped(ref)]];assert annotated==['4:2','5:2','5:7']+[f'6:{v}' for v in range(1,31)]
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
 checks={'4:3':['anointed priest','guilt on the people','young bull without defect'],'4:6':['finger','seven times','curtain'],'4:7':['horns','altar of fragrant incense','all the rest','base','altar of burnt offering'],'4:9':['both kidneys','lobe of the liver'],'4:11':['skin','flesh','head and legs','entrails and dung'],'4:12':['whole bull','outside the camp','clean place'],'4:15':['elders','their hands','bull is to be slaughtered'],'4:17':['seven times'],'4:23':['male goat without defect'],'4:28':['female goat without defect'],'4:31':['person bringing','priest','pleasing aroma'],'4:32':['sheep','female without defect'],'5:1':['under oath','seen or learned','does not speak','bear their guilt'],'5:6':['reparation','sin offering'],'5:7':['two turtledoves','two young pigeons','one for a sin offering','one for a burnt offering'],'5:8':['first','back of the neck','without severing'],'5:9':['sprinkle','side','drain','base'],'5:11':['a tenth of an ephah','must not put oil or frankincense'],'5:15':['unintentionally','holy things','ram without defect','silver shekels','sanctuary standard'],'5:16':['restitution','add a fifth','priest'],'5:17':['without knowing','bear their guilt'],'6:2':['against the LORD','neighbor','deposit','entrusted','robbery','defrauding'],'6:5':['full value','add a fifth','owner'],'6:10':['linen garment','linen undergarments','beside the altar'],'6:11':['other clothes','outside the camp','clean place'],'6:15':['handful','all its frankincense'],'6:18':['Every male','becomes holy'],'6:20':['he is anointed','a tenth','half in the morning','half in the evening'],'6:22':['anointed to succeed','his sons','burned entirely'],'6:23':['Every grain offering','by a priest','must not be eaten'],'6:28':['earthenware','broken','bronze','scoured','rinsed with water'],'6:30':['no sin offering','blood','sanctuary','may be eaten','burned with fire'],'7:2':['slaughtered','priest','splash','all sides'],'7:4':['both kidneys','lobe of the liver'],'7:8':['skin','belongs to that priest'],'7:9':['oven','pan','griddle'],'7:10':['oil','dry','equally','all Aaron’s sons'],'7:13':['leavened bread'],'7:14':['one of each kind','priest who splashes'],'7:15':['on the day','None','until morning'],'7:16':['vow offering','freewill offering','next day'],'7:17':['third day','burned with fire'],'7:18':['not be accepted or credited','defiled thing','bear their guilt'],'7:21':['human uncleanness','unclean animal','unclean detestable thing'],'7:23':['cattle, sheep, or goats'],'7:24':['dies on its own','torn by wild animals','other work','never eat'],'7:26':['Wherever you live','any blood','birds or livestock'],'7:30':['own hands','fat together with the breast','wave offering'],'7:32':['right thigh','contribution'],'7:33':['blood and fat','right thigh'],'7:34':['I have taken','Aaron the priest and his sons'],'7:37':['burnt offering','grain offering','sin offering','guilt offering','ordination offerings','peace offering'],'7:38':['Moses','Mount Sinai','wilderness of Sinai']}
 for ref,ts in checks.items():
  for term in ts:assert term in byref[ref]['after'],(ref,term)
 assert byref['4:12']['after'].count('where the ashes are poured out')==2
 assert all('forgiven' in byref[x]['after'] for x in ['4:20','4:26','4:31','4:35','5:10','5:13','5:16','5:18','6:7'])
 assert not any('forgiven' in byref[f'4:{v}']['after'] for v in range(1,13))
 assert all('must not go out' in byref[x]['after'] for x in ['6:12','6:13'])
 assert all('cut off from their people' in byref[x]['after'] for x in ['7:20','7:21','7:25','7:27'])
 assert all('seven' not in byref[f'4:{v}']['after'] for v in [25,30,34])
 assert 'leavened bread' in byref['7:13']['after'] and 'not' not in byref['7:13']['after']
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,8))
  assert len(new['revision_batches'])==2 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 4–7; 122 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 4–7; 122 verses','revision_audits':audits,'cumulative_coverage':{'chapters':102,'verses':3026},'source_record_count':859,'public_source_mapping':'Leviticus 4–5 and 7 align directly; public 6:1–7 maps to Hebrew 5:20–26 and public 6:8–30 to Hebrew 6:1–23. All 122 records are unique and complete. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 122 selected pinned Hebrew records, including complete numbering and BHS annotations, drafted independently, then read all TSW verse comparators and selected NET translator notes. It reread the assembled chapters and checked offering identities, animal sex, blood locations and actions, amounts, food portions, repeated sanctions, verse mapping and consequential ambiguities. This is an authoring self-check, not independent scholarly review.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':22,'chapters':102,'verses':3026,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
