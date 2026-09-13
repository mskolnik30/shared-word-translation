"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='0fbd151ceeb009dfa4eb47d626d7d3914f10f5bd';COUNTS={11:35,12:16}
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
 assert len(audits)==36 and len(chapters)==134 and sum(a['verses'] for a in audits)==4184
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':471}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Num '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Num '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==51
 annotated=[ref for ref in byref if '<note' in raw['Num '+ref]];assert annotated==['12:3','12:9']
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
 checks={'11:1': ['LORD’s ears', 'anger blazed', 'fire burned', 'outskirts'], '11:2': ['cried out to Moses', 'Moses prayed', 'fire died down'], '11:3': ['Taberah', 'burned'], '11:4': ['rabble', 'Israelites', 'again'], '11:5': ['fish', 'for nothing', 'cucumbers', 'melons', 'leeks', 'onions', 'garlic'], '11:6': ['dried up', 'manna'], '11:7': ['coriander seed', 'bdellium'], '11:8': ['handmills', 'mortars', 'pots', 'cakes', 'oil'], '11:9': ['at night', 'manna fell on it'], '11:10': ['family by family', 'entrance', 'distressed'], '11:11': ['servant', 'favor', 'burden'], '11:12': ['conceive', 'give birth', 'chest', 'foster father', 'nursing child', 'swore'], '11:15': ['please kill me now', 'favor', 'my own misery'], '11:16': ['seventy men', 'elders and officers', 'tent of meeting'], '11:17': ['come down', 'some of the spirit', 'carry', 'alone'], '11:18': ['Consecrate', 'tomorrow', 'Egypt'], '11:19': ['one day', 'two days', 'five days', 'ten days', 'twenty days'], '11:20': ['whole month', 'nostrils', 'loathsome', 'rejected', 'among you'], '11:21': ['six hundred thousand', 'on foot', 'whole month'], '11:22': ['flocks and herds', 'all the fish'], '11:23': ['hand too short', 'whether', 'or not'], '11:24': ['seventy men', 'around the tent'], '11:25': ['spoke to Moses', 'seventy elders', 'did not do so again'], '11:26': ['Eldad', 'Medad', 'registered', 'had not gone out', 'in the camp'], '11:28': ['Joshua son of Nun', 'youth', 'stop them'], '11:29': ['jealous', 'all the LORD’s people', 'prophets'], '11:31': ['wind', 'sea', 'day’s journey', 'two cubits above the ground'], '11:32': ['all that day', 'all night', 'all the next day', 'least', 'ten homers', 'spread'], '11:33': ['between their teeth', 'before it was chewed', 'LORD struck', 'plague'], '11:34': ['Kibroth-hattaavah', 'buried'], '11:35': ['Hazeroth'], '12:1': ['Miriam and Aaron', 'Cushite woman'], '12:2': ['through Moses', 'through us', 'LORD heard'], '12:3': ['humble', 'anyone else'], '12:4': ['Suddenly', 'three'], '12:5': ['pillar of cloud', 'Aaron and Miriam', 'two'], '12:6': ['prophet', 'vision', 'dream'], '12:7': ['servant Moses', 'trusted', 'house'], '12:8': ['mouth to mouth', 'not in riddles', 'form of the LORD', 'afraid'], '12:9': ['against them', 'left'], '12:10': ['Miriam', 'white as snow', 'defiling skin condition'], '12:11': ['against us', 'foolishly', 'sinned'], '12:12': ['stillborn', 'half eaten away', 'mother’s womb'], '12:13': ['God, please', 'heal her, please'], '12:14': ['father', 'spat in her face', 'seven days', 'brought back'], '12:15': ['seven days', 'did not set out', 'brought back'], '12:16': ['Hazeroth', 'Paran']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['12:1']['after'].count('Cushite woman')==2
 assert byref['12:14']['after'].count('seven days')==2
 assert byref['11:22']['after'].count('would that be enough?')==2
 assert byref['11:29']['after'].count('If only')==2
 assert byref['12:13']['after'].count('please')==2
 assert 'x-qere' in raw['Num 12:3'] and 'ענו' in raw['Num 12:3'] and 'עָנָ֣יו' in raw['Num 12:3']
 t12=(ROOT/'translations/fluent/OT/numbers/Numbers_12.md').read_text()
 assert 'words:\nIf there is a prophet' in t12 and 'mouth to mouth,\nplainly, not in riddles.' in t12
 n11=(ROOT/'translations/fluent/OT/numbers/Numbers_11.md').read_text().split('## Notes')[1]
 assert 'did not cease' in n11 and 'registered' in n11 and 'height above the ground or the depth' in n11
 assert 'half eaten away' in t12 and 'moment of her healing' in t12
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,13))
  assert len(new['revision_batches'])==6 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 11–12; 51 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 11–12; 51 verses','revision_audits':audits,'cumulative_coverage':{'chapters':134,'verses':4184},'source_record_count':1289,'public_source_mapping':'Numbers 11–12 aligns directly; all 51 original records are unique and complete, including the written/read annotation at 12:3 and the form annotation at 12:9. Earlier books and their public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 51 pinned Hebrew verses were read before drafting. NET lexical and grammatical comparison followed; all TSW comparators were read after drafting. Authoring self-checks preserve fire and plague, the food list, Moses’ direct death plea and parental images, seventy elders versus the unspecified registration of Eldad and Medad, did-not-repeat prophecy with alternate interpretation noted, six hundred thousand and all day counts, spirit/wind linkage, quail extent/elevation and minimum ten homers, repeated Cushite designation, both siblings’ challenge, written/read humble form, poetic vision/dream contrast and mouth-to-mouth speech, Miriam’s snowlike skin condition and stillbirth comparison, both pleas in the prayer, and seven-day exclusion and return. No human scholarly review or reader testing is claimed.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':36,'chapters':134,'verses':4184,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
