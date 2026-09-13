"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='4be4e56371ea7046ba235e5ca03b911ba33b9c82';COUNTS={31:54,32:42,33:56,34:29,35:34,36:13}
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
  for v in l['verses']:
   for segment in v.get('source_segments',[v]):
    ref=segment['source_reference'];assert ref not in rs;rs.add(ref)
 assert len(audits)==40 and len(chapters)==158 and sum(a['verses'] for a in audits)==5001
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859,'Numbers':1289}
 raw={f'Num {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.numbers_source.read_text(),re.S) for c,v in [re.search(r'osisID="Num\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==1289
 l=json.loads((BATCH/'numbers-verse-review.json').read_text());byref={v['reference'].replace('Numbers ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 source_refs=[]
 for ref,v in byref.items():
  sr='Num '+ref;source_refs.append(sr)
  assert v['source_reference']==sr and v['source_verse_sha256']==hashlib.sha256(raw[sr].encode()).hexdigest()
 assert len(source_refs)==len(set(source_refs))==228
 assert set(source_refs)=={ref for ref in raw if 31<=int(ref.split()[1].split(':')[0])<=36}
 assert refs['Numbers']==set(raw), 'Complete Numbers source coverage, including previous numbering differences'
 annotated=[ref for ref in source_refs if '<note' in raw[ref]]
 assert annotated==['Num 32:7','Num 32:30','Num 34:4']
 for ref in ['Num 32:7','Num 34:4']:assert 'x-ketiv' in raw[ref] and 'x-qere' in raw[ref]
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
 checks={'31:2': ['vengeance', 'Israelites', 'gathered to your people'], '31:3': ['LORD’s vengeance'], '31:4': ['a thousand from each tribe', 'a thousand from every tribe'], '31:5': ['twelve thousand'], '31:6': ['Phinehas', 'Eleazar', 'holy articles', 'trumpets'], '31:7': ['every male'], '31:8': ['Evi, Rekem, Zur, Hur and Reba', 'five kings', 'Balaam son of Beor', 'sword'], '31:9': ['captured', 'women and little children'], '31:10': ['burned', 'towns', 'encampments'], '31:15': ['all the females'], '31:16': ['Balaam’s advice', 'Peor', 'plague'], '31:17': ['kill every boy', 'kill every woman', 'slept with a man'], '31:18': ['keep alive for yourselves', 'girls', 'not slept'], '31:19': ['seven days', 'third and seventh', 'captives'], '31:20': ['garment', 'leather', 'goats’ hair', 'wooden'], '31:22': ['Gold, silver, bronze, iron, tin and lead'], '31:23': ['also', 'water for removing impurity', 'cannot withstand fire'], '31:24': ['seventh day', 'After that'], '31:27': ['equally'], '31:28': ['one out of every five hundred', 'people'], '31:29': ['Eleazar'], '31:30': ['one out of every fifty', 'people', 'Levites'], '31:40': ['thirty-two people'], '31:47': ['one out of every fifty', 'Levites'], '31:49': ['not one of us is missing'], '31:50': ['anklets, bracelets, signet rings, earrings and necklaces', 'atonement for our lives'], '31:52': ['sixteen thousand seven hundred and fifty shekels'], '31:54': ['tent of meeting', 'memorial'], '32:1': ['Reubenites and Gadites', 'Jazer and Gilead'], '32:3': ['Ataroth, Dibon, Jazer, Nimrah, Heshbon, Elealeh, Sebam, Nebo and Beon'], '32:6': ['brothers', 'war', 'stay'], '32:8': ['Kadesh-barnea'], '32:9': ['Valley of Eshcol', 'discouraged'], '32:11': ['twenty years', 'Abraham, Isaac and Jacob'], '32:12': ['Caleb', 'Jephunneh', 'Kenizzite', 'Joshua', 'Nun'], '32:13': ['forty years'], '32:14': ['brood of sinful men'], '32:15': ['destroy this whole people'], '32:17': ['fortified towns'], '32:18': ['every Israelite'], '32:19': ['west', 'east'], '32:20': ['before the LORD'], '32:21': ['before the LORD', 'he has driven his enemies'], '32:22': ['free of your obligation', 'LORD and to Israel', 'before the LORD'], '32:23': ['your sin will find you out'], '32:24': ['do what you have said'], '32:26': ['little children', 'wives'], '32:28': ['Eleazar', 'Joshua', 'ancestral houses', 'tribes'], '32:29': ['If', 'Gilead'], '32:30': ['if they do not', 'among you in Canaan'], '32:33': ['half the tribe of Manasseh son of Joseph', 'Sihon', 'Amorites', 'Og', 'Bashan'], '32:34': ['Dibon, Ataroth and Aroer'], '32:35': ['Atroth-shophan, Jazer and Jogbehah'], '32:36': ['Beth-nimrah and Beth-haran'], '32:37': ['Heshbon, Elealeh and Kiriathaim'], '32:38': ['Nebo and Baal-meon', 'names were changed', 'Sibmah'], '32:39': ['descendants of Machir', 'Amorites'], '32:40': ['Machir’s family'], '32:41': ['Jair', 'Havvoth-jair'], '32:42': ['Nobah', 'Kenath', 'after himself'], '33:2': ['Moses recorded', 'LORD’s command'], '33:3': ['fifteenth', 'first month', 'day after Passover', 'raised hand'], '33:4': ['burying', 'firstborn', 'judgments against their gods'], '33:8': ['Hahiroth', 'middle of the sea', 'three days', 'Etham'], '33:9': ['twelve springs', 'seventy palm trees'], '33:14': ['no water'], '33:36': ['wilderness of Zin', 'Kadesh'], '33:37': ['Mount Hor', 'Edom'], '33:38': ['first day', 'fifth month', 'fortieth year'], '33:39': ['one hundred and twenty-three'], '33:40': ['Arad', 'Negev'], '33:49': ['Beth-jeshimoth', 'Abel-shittim'], '33:52': ['drive out all', 'figured stones', 'cast images', 'high places'], '33:54': ['by lot', 'larger', 'smaller', 'ancestral tribes'], '33:55': ['barbs in your eyes', 'thorns in your sides'], '33:56': ['to them', 'to you'], '34:3': ['Zin', 'Edom', 'eastern end', 'Salt Sea'], '34:4': ['south of the Ascent of Akrabbim', 'Zin', 'south of Kadesh-barnea', 'Hazar-addar', 'Azmon'], '34:5': ['Wadi of Egypt'], '34:6': ['Great Sea', 'western boundary'], '34:7': ['northern boundary', 'Mount Hor'], '34:8': ['Lebo-hamath', 'Zedad'], '34:9': ['Ziphron', 'Hazar-enan'], '34:10': ['Hazar-enan', 'Shepham'], '34:11': ['Riblah', 'east of Ain', 'ridge east', 'Sea of Chinnereth'], '34:12': ['Jordan', 'Salt Sea'], '34:13': ['nine tribes and the half-tribe'], '34:14': ['Reuben', 'Gad', 'half the tribe of Manasseh'], '34:15': ['two tribes and the half-tribe', 'east', 'sunrise'], '34:17': ['Eleazar', 'Joshua son of Nun'], '34:18': ['one leader from each tribe'], '35:2': ['Levites', 'inheritance', 'pastureland'], '35:4': ['a thousand cubits', 'outward', 'all around'], '35:5': ['two thousand cubits on the east', 'two thousand on the south', 'two thousand on the west', 'two thousand on the north', 'town in the middle'], '35:6': ['six', 'forty-two'], '35:7': ['forty-eight'], '35:8': ['more', 'fewer', 'in proportion'], '35:11': ['unintentionally'], '35:12': ['avenger', 'before standing trial', 'community'], '35:14': ['three towns on this side', 'three in the land of Canaan'], '35:15': ['foreigner and settler', 'unintentionally'], '35:16': ['iron', 'murderer must be put to death'], '35:17': ['stone', 'capable of killing', 'murderer must be put to death'], '35:18': ['wooden', 'capable of killing', 'murderer must be put to death'], '35:19': ['avenger of blood himself', 'kill him'], '35:20': ['hatred', 'deliberately'], '35:21': ['hostility', 'murderer'], '35:22': ['without hostility', 'without intending harm'], '35:23': ['without seeing', 'not an enemy', 'did not seek'], '35:24': ['community must judge'], '35:25': ['rescue', 'return', 'until the death of the high priest', 'holy oil'], '35:26': ['outside the boundary'], '35:27': ['no bloodguilt'], '35:28': ['After the high priest’s death', 'return'], '35:30': ['testimony of witnesses', 'single witness cannot'], '35:31': ['Do not accept a ransom', 'murderer'], '35:32': ['do not accept a ransom', 'before the priest dies'], '35:33': ['blood pollutes the land', 'No atonement', 'except by the blood'], '35:34': ['where I dwell', 'dwell among the Israelites'], '36:1': ['Gilead', 'Machir', 'Manasseh', 'Joseph'], '36:2': ['Zelophehad', 'daughters', 'by lot'], '36:3': ['taken away', 'added'], '36:4': ['Jubilee', 'will belong'], '36:5': ['Joseph’s descendants is right'], '36:6': ['whomever they think best', 'but only', 'father’s tribe'], '36:8': ['Every daughter who inherits', 'father’s tribe'], '36:9': ['No inheritance may pass'], '36:11': ['Mahlah, Tirzah, Hoglah, Milcah and Noah', 'sons of their father’s brothers'], '36:12': ['Manasseh son of Joseph', 'inheritance remained'], '36:13': ['commands and rulings', 'through Moses', 'Moab', 'Jordan', 'Jericho']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 quantities={32:(675000,'six hundred and seventy-five thousand'),33:(72000,'seventy-two thousand'),34:(61000,'sixty-one thousand'),35:(32000,'thirty-two thousand'),36:(337500,'three hundred and thirty-seven thousand five hundred'),37:(675,'six hundred and seventy-five'),38:(36000,'thirty-six thousand'),39:(30500,'thirty thousand five hundred'),40:(16000,'sixteen thousand'),43:(337500,'three hundred and thirty-seven thousand five hundred'),44:(36000,'thirty-six thousand'),45:(30500,'thirty thousand five hundred'),46:(16000,'sixteen thousand')}
 for v,(n,t) in quantities.items():assert t in byref[f'31:{v}']['after']
 divisions=[]
 for total,half,tribute in [(675000,337500,675),(72000,36000,72),(61000,30500,61),(32000,16000,32)]:
  assert total==half*2 and half//500==tribute and half%500==0
  divisions.append({'total':total,'each_half':half,'soldier_levy':tribute,'community_levy_implied_not_inserted':half//50})
 for v,t in {38:'seventy-two',39:'sixty-one',40:'thirty-two people'}.items():assert t in byref[f'31:{v}']['after']
 assert 6+42==48 and 3+3==6
 route={5:('Rameses','Succoth'),6:('Succoth','Etham'),7:('Etham','Pi-hahiroth','Baal-zephon','Migdol'),8:('Hahiroth','Etham','Marah'),9:('Marah','Elim'),10:('Elim','Sea of Reeds'),11:('Sea of Reeds','Sin'),12:('Sin','Dophkah'),13:('Dophkah','Alush'),14:('Alush','Rephidim'),15:('Rephidim','Sinai'),16:('Sinai','Kibroth-hattaavah'),17:('Kibroth-hattaavah','Hazeroth'),18:('Hazeroth','Rithmah'),19:('Rithmah','Rimmon-perez'),20:('Rimmon-perez','Libnah'),21:('Libnah','Rissah'),22:('Rissah','Kehelathah'),23:('Kehelathah','Mount Shepher'),24:('Mount Shepher','Haradah'),25:('Haradah','Makheloth'),26:('Makheloth','Tahath'),27:('Tahath','Terah'),28:('Terah','Mithkah'),29:('Mithkah','Hashmonah'),30:('Hashmonah','Moseroth'),31:('Moseroth','Bene-jaakan'),32:('Bene-jaakan','Hor-haggidgad'),33:('Hor-haggidgad','Jotbathah'),34:('Jotbathah','Abronah'),35:('Abronah','Ezion-geber'),36:('Ezion-geber','Zin','Kadesh'),37:('Kadesh','Mount Hor','Edom'),41:('Mount Hor','Zalmonah'),42:('Zalmonah','Punon'),43:('Punon','Oboth'),44:('Oboth','Iye-abarim','Moab'),45:('Iyim','Dibon-gad'),46:('Dibon-gad','Almon-diblathaim'),47:('Almon-diblathaim','Abarim','Nebo'),48:('Abarim','Moab','Jordan','Jericho')}
 for v,names in route.items():
  t=byref[f'33:{v}']['after'];positions=[t.index(n) for n in names];assert positions==sorted(positions),(v,names)
 leaders={19:('Judah','Caleb','Jephunneh'),20:('Simeon','Shemuel','Ammihud'),21:('Benjamin','Elidad','Chislon'),22:('Dan','Bukki','Jogli'),23:('Joseph','Manasseh','Hanniel','Ephod'),24:('Ephraim','Kemuel','Shiphtan'),25:('Zebulun','Elizaphan','Parnach'),26:('Issachar','Paltiel','Azzan'),27:('Asher','Ahihud','Shelomi'),28:('Naphtali','Pedahel','Ammihud')}
 for v,names in leaders.items():
  for n in names:assert n in byref[f'34:{v}']['after']
 assert q['next_work'][0]['scope']=='Numbers whole-book consistency review' and 'larger batches' in q['batch_preference']
 reviewdir='audit/exegetical-core/fluent-production/numbers/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/numbers/Numbers_{c:02}.md' for c in COUNTS}|{reviewdir+f'Numbers_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','NUMBERS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,37))
  assert len(new['revision_batches'])==10 and new['revision_batches'][:-1]==old.get('revision_batches',[])
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Numbers 31–36; 228 public verses / 228 source records','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Numbers 31–36; 228 public verses / 228 source records','revision_audits':audits,'cumulative_coverage':{'chapters':158,'verses':5001},'source_record_count':1289,'public_source_mapping':'Public Numbers 31–36 align directly with all 228 Hebrew records. Complete cumulative Numbers coverage is 1288 public verses bound to all 1289 source records; earlier offsets and the two-record public 26:1 binding remain preserved.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'captured_totals':quantities,'division_arithmetic':divisions,'journey_name_order':route,'allotment_leader_names':leaders,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'All 228 selected pinned Hebrew records were read before drafting; all 228 TSW comparator verses were read afterward. Supplemental NET translators’ notes were consulted on selected difficulties in Numbers 31 and 35. Source-focused self-check covered explicit killing and captivity, all division quantities and levy arithmetic, purification conditions, the eastern tribes’ pledge and alternative allotment, complete journey name order, dates and age, distinct Sin/Zin and Mount Hor settings, boundary and leader names, both pasture measurements without invented harmonization, intentional versus unintentional killing, communal judgment and refuge, bloodguilt and ransom, and the daughters’ choice and restricted inheritance marriages. The whole-book Numbers consistency review is next; this batch completes drafting only. This is authoring and structural QA, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':40,'chapters':158,'verses':5001,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
