"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='ce1b25c8c533b82bc1c2cd55edfff348bfe2589a';COUNTS={3:51,4:49}
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
 assert len(audits)==32 and len(chapters)==126 and sum(a['verses'] for a in audits)==3901
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':188}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Num '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Num '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==100
 annotated=[ref for ref in byref if '<note' in raw['Num '+ref]];assert annotated==['3:30','3:39']
 assert sum(raw['Num '+ref].count('<note') for ref in byref)==2
 assert '\u05c4' in raw['Num 3:39'] and 'Aaron' in byref['3:39']['after']
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
 checks={'3:1': ['Aaron and Moses', 'Mount Sinai'], '3:2': ['Nadab, the firstborn', 'Abihu', 'Eleazar', 'Ithamar'], '3:3': ['anointed', 'ordained', 'priests'], '3:4': ['died', 'unauthorized fire', 'no sons', 'presence of their father Aaron'], '3:7': ['duties owed to him', 'whole community', 'work of the tabernacle'], '3:9': ['Aaron and his sons', 'given entirely', 'from among the Israelites'], '3:10': ['priesthood', 'unauthorized', 'put to death'], '3:12': ['I myself', 'in place of', 'opens the womb', 'belong to me'], '3:13': ['struck down', 'every firstborn', 'Egypt', 'human and animal'], '3:15': ['ancestral household and clan', 'every male one month'], '3:17': ['Gershon, Kohath and Merari'], '3:18': ['Libni and Shimei'], '3:19': ['Amram, Izhar, Hebron and Uzziel'], '3:20': ['Mahli and Mushi'], '3:21': ['Libnite and Shimeite'], '3:23': ['behind', 'west'], '3:24': ['Eliasaph son of Lael'], '3:25': ['tabernacle and tent', 'covering', 'entrance screen'], '3:26': ['courtyard hangings', 'tabernacle and altar', 'ropes', 'all the work'], '3:27': ['Amramite, Izharite, Hebronite and Uzzielite'], '3:29': ['south'], '3:30': ['Elizaphan son of Uzziel'], '3:31': ['ark', 'table', 'lampstand', 'altars', 'utensils', 'screen'], '3:32': ['Eleazar son of Aaron', 'chief over the Levite leaders'], '3:33': ['Mahlite and Mushite'], '3:35': ['Zuriel son of Abihail', 'north'], '3:36': ['frames, crossbars, pillars, bases', 'equipment'], '3:37': ['pillars', 'bases, pegs and ropes'], '3:38': ['Moses, Aaron and Aaron’s sons', 'east', 'sunrise', 'on behalf of the Israelites', 'put to death'], '3:39': ['Moses and Aaron', 'one month old and upward'], '3:40': ['firstborn male', 'one month old', 'names'], '3:41': ['Levites’ livestock', 'firstborn of the Israelites’ livestock'], '3:45': ['Levites’ livestock', 'belong to me'], '3:47': ['five shekels for each person', 'sanctuary shekel', 'twenty gerahs'], '3:48': ['silver to Aaron and his sons'], '3:49': ['beyond the number redeemed'], '3:51': ['Aaron and his sons', 'LORD’s direction', 'LORD had commanded Moses'], '4:4': ['most holy things'], '4:5': ['Aaron and his sons', 'dividing curtain', 'ark of the testimony'], '4:6': ['taḥash skin', 'entirely of blue', 'carrying poles'], '4:7': ['table of the Presence', 'dishes, ladles, bowls and pitchers', 'regular bread', 'remain'], '4:8': ['scarlet', 'taḥash skin', 'carrying poles'], '4:9': ['lampstand', 'lamps, tongs, firepans', 'oil containers'], '4:10': ['taḥash skin', 'carrying bar'], '4:11': ['gold altar', 'blue', 'taḥash skin', 'carrying poles'], '4:12': ['all the utensils', 'blue', 'taḥash skin', 'carrying bar'], '4:13': ['remove the ashes', 'purple'], '4:14': ['firepans, forks, shovels and basins', 'taḥash skin', 'carrying poles'], '4:15': ['Once Aaron and his sons have finished covering', 'Kohathites may come to carry', 'must not touch', 'or they will die'], '4:16': ['lighting oil, fragrant incense, regular grain offering and anointing oil', 'whole tabernacle'], '4:18': ['Do not let', 'cut off', 'Levites'], '4:19': ['live and not die', 'Aaron and his sons', 'each man his task and his load'], '4:20': ['Kohathites', 'look', 'even for a moment', 'or they will die'], '4:25': ['tabernacle curtains', 'its covering', 'taḥash covering above', 'entrance'], '4:26': ['courtyard hangings', 'ropes', 'all the work'], '4:27': ['directed by Aaron and his sons', 'assign them responsibility'], '4:28': ['Ithamar son of Aaron'], '4:31': ['frames, crossbars, pillars and bases'], '4:32': ['bases, pegs, ropes', 'Assign by name the items'], '4:33': ['Ithamar son of Aaron'], '4:37': ['command given through Moses'], '4:41': ['LORD’s command'], '4:45': ['command given through Moses'], '4:47': ['do the work and carry the loads'], '4:49': ['each man', 'assigned task and load', 'registration followed']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 census={'3:22':7500,'3:28':8600,'3:34':6200,'3:39':22000,'3:43':22273,'3:46':273,'3:50':1365,'4:36':2750,'4:40':2630,'4:44':3200,'4:48':8580}
 for ref,n in census.items():assert re.findall(r'\d[\d,]*',byref[ref]['after'])==[f'{n:,}'],ref
 assert sum(census[x] for x in ['3:22','3:28','3:34'])==22300!=census['3:39']
 assert census['3:43']-census['3:39']==census['3:46'] and census['3:46']*5==census['3:50']
 assert sum(census[x] for x in ['4:36','4:40','4:44'])==census['4:48']
 for v in [3,23,30,35,39,43,47]:assert 'thirty years old up to fifty' in byref[f'4:{v}']['after']
 for v in [15,22,28,34,39,40,43]:assert 'one month old' in byref[f'3:{v}']['after']
 assert byref['4:6']['after'].index('taḥash')<byref['4:6']['after'].index('blue')
 assert byref['4:8']['after'].index('scarlet')<byref['4:8']['after'].index('taḥash')
 assert all('put to death' not in byref[x]['after'] for x in ['4:15','4:20'])
 assert 'through Moses' not in byref['4:41']['after']
 notes=(ROOT/'translations/fluent/OT/numbers/Numbers_03.md').read_text().split('## Notes')[1]
 assert '22,300' in notes and '22,000' in notes and 'scribal dots' in notes
 notes=(ROOT/'translations/fluent/OT/numbers/Numbers_04.md').read_text().split('## Notes')[1]
 assert 'while the holy things are being covered' in notes and 'compressed and difficult' in notes
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==[1,2,3,4]
  assert len(new['revision_batches'])==2 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 3–4; 100 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 3–4; 100 verses','revision_audits':audits,'cumulative_coverage':{'chapters':126,'verses':3901},'source_record_count':1289,'public_source_mapping':'Numbers 3–4 aligns directly; all 100 records are unique and complete, including the source annotations at 3:30 and 3:39 and extraordinary dots in 3:39. Earlier books and their public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'census_counts':census,'chapter_3_discrepancy_preserved':True,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 100 pinned Hebrew verses and both source annotations before drafting. NET comparison and selected translators’ notes followed the Hebrew reading; all 100 TSW comparators were read after drafting. Self-checks cover lineage and leaders, all listed counts, the retained 22300 versus 22000 discrepancy, the 273-person redemption and 1365-shekel payment, age bands, inventory categories and colors, covering before carrying, priest/Levite responsibilities, death warnings, and the compressed final clause. Earlier revised Exodus sanctuary terminology was checked. These are authoring self-checks, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':32,'chapters':126,'verses':3901,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
