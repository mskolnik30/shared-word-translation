"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='329682fd0c9232ce0a8283577b98c496ba1306ce';COUNTS={7:89,8:26}
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
 assert len(audits)==34 and len(chapters)==130 and sum(a['verses'] for a in audits)==4074
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':361}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Num '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Num '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==115
 annotated=[ref for ref in byref if '<note' in raw['Num '+ref]];assert annotated==['7:4','7:32','7:40','7:55','7:59','7:68']
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
 checks={'7:3': ['six covered carts', 'twelve oxen', 'one cart for every two leaders', 'one ox from each'], '7:7': ['two carts', 'four oxen', 'Gershonites'], '7:8': ['four carts', 'eight oxen', 'Merarites', 'Ithamar', 'Aaron'], '7:9': ['none', 'Kohathites', 'holy things', 'shoulders'], '7:84': ['twelve silver dishes', 'twelve silver basins', 'twelve gold ladles'], '7:85': ['130', '70', '2,400', 'sanctuary'], '7:86': ['twelve', '10', '120', 'incense'], '7:87': ['twelve bulls', 'twelve rams', 'twelve male lambs a year old', 'grain offering', 'twelve male goats', 'sin offering'], '7:88': ['twenty-four bulls', 'sixty rams', 'sixty male goats', 'sixty male lambs a year old', 'after it was anointed'], '7:89': ['voice', 'atonement cover', 'ark of the testimony', 'two cherubim'], '8:2': ['seven lamps', 'in front'], '8:4': ['hammered gold', 'base', 'flowers', 'pattern'], '8:7': ['sprinkle', 'purification water', 'shave their whole bodies', 'wash their clothes'], '8:8': ['They are to take', 'You are to take a second', 'fine flour mixed with oil', 'sin offering'], '8:9': ['whole Israelite community'], '8:10': ['Israelites are to lay their hands on the Levites'], '8:11': ['Aaron', 'wave offering', 'from the Israelites', 'LORD’s work'], '8:12': ['Levites are to lay their hands', 'bulls’ heads', 'sin offering', 'burnt offering', 'atonement'], '8:13': ['Aaron and his sons', 'wave offering'], '8:15': ['After this', 'purify', 'wave offering'], '8:16': ['wholly', 'in place of', 'firstborn son', 'opens the womb'], '8:17': ['human and animal', 'struck down every firstborn', 'Egypt', 'holy'], '8:19': ['gift', 'Aaron and his sons', 'atonement', 'plague', 'sanctuary'], '8:21': ['purified themselves', 'washed their clothes', 'Aaron made atonement'], '8:24': ['twenty-five', 'man', 'company'], '8:25': ['fifty', 'withdraw', 'no longer'], '8:26': ['assist', 'keeping its charge', 'must not perform the work']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 donors=[('first','Nahshon','Amminadab','Judah'),('second','Nethanel','Zuar','Issachar'),('third','Eliab','Helon','Zebulun'),('fourth','Elizur','Shedeur','Reuben'),('fifth','Shelumiel','Zurishaddai','Simeon'),('sixth','Eliasaph','Deuel','Gad'),('seventh','Elishama','Ammihud','Ephraim'),('eighth','Gamaliel','Pedahzur','Manasseh'),('ninth','Abidan','Gideoni','Benjamin'),('tenth','Ahiezer','Ammishaddai','Dan'),('eleventh','Pagiel','Ochran','Asher'),('twelfth','Ahira','Enan','Naphtali')]
 for i,(day,name,father,tribe) in enumerate(donors):
  v=12+6*i;at=lambda offset:byref[f'7:{v+offset}']['after']
  assert all(x in at(0) for x in [day,name,father,tribe])
  assert all(x in at(1) for x in ['one silver dish','130','one silver basin','70','sanctuary shekel','Both were filled','fine flour mixed with oil','grain offering'])
  assert all(x in at(2) for x in ['one gold ladle','10','incense'])
  assert all(x in at(3) for x in ['burnt offering','one young bull','one ram','one year-old male lamb'])
  assert all(x in at(4) for x in ['sin offering','one male goat'])
  assert all(x in at(5) for x in ['two bulls','five rams','five male goats','five male lambs a year old',name,father])
  assert at(3).endswith(';') and at(4).endswith(';') and at(5).endswith('.')
 assert 12*(130+70)==2400 and 12*10==120 and 12*2==24 and 12*5==60
 assert byref['7:11']['after'].casefold().count('one leader each day')==2
 assert byref['8:19']['after'].count('Israelites')==5
 assert byref['8:4']['after'].count('hammered')==2
 for ref in ['8:11','8:13','8:15','8:21']:assert 'wave offering' in byref[ref]['after']
 n7=(ROOT/'translations/fluent/OT/numbers/Numbers_07.md').read_text().split('## Notes')[1]
 n8=(ROOT/'translations/fluent/OT/numbers/Numbers_08.md').read_text().split('## Notes')[1]
 assert 'Reuel' in n7 and 'Moses speaking to the LORD' in n7
 assert 'twenty-five' in n8 and 'thirty in chapter 4' in n8 and 'neither explanation is stated explicitly' in n8
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==[1,2,3,4,5,6,7,8]
  assert len(new['revision_batches'])==4 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 7–8; 115 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 7–8; 115 verses','revision_audits':audits,'cumulative_coverage':{'chapters':130,'verses':4074},'source_record_count':1289,'public_source_mapping':'Numbers 7–8 aligns directly; all 115 original records are unique and complete, including all six source annotations at 7:4, 7:32, 7:40, 7:55, 7:59 and 7:68. Earlier books and their public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read every one of the 115 pinned Hebrew verses, including all twelve offering lists, before drafting. NET lexical and grammatical comparison followed the Hebrew reading; all 115 TSW verses were read after drafting. Self-checks preserve each day, donor and quantity; both filled silver vessels; all animal categories, ages and sex; silver/gold and animal totals; the Deuel/Reuel difference; voice and atonement-cover location; lamp direction and unnamed maker; distinct ritual actors; human wave-offering terminology without an invented physical mechanism; firstborn substitution, divine agency in Egypt and plague prevention; twenty-five versus thirty, fifty-year withdrawal and continued assistance. Programmatic reuse transcribes the source’s repeated lists, with no English comparator substitution engine. These are authoring self-checks, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':34,'chapters':130,'verses':4074,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
