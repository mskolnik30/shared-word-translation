"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='8980e86d3e2e0a31a3eea88057e9492975c999a8';COUNTS={16:34,17:16}
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
 assert len(audits)==26 and len(chapters)==112 and sum(a['verses'] for a in audits)==3360
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':506}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==50
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['16:21']
 assert '<catchWord>יד/ו</catchWord>' in raw['Lev 16:21'] and 'יָדָ֗י/ו' in raw['Lev 16:21'] and 'type="x-qere"' in raw['Lev 16:21']
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
 checks={'16:1': ["Aaron's two sons", 'died', 'drew near'], '16:2': ['your brother Aaron', 'whenever he wishes', 'behind the curtain', 'atonement cover', 'ark', 'will die', 'cloud'], '16:3': ['young bull', 'sin offering', 'ram', 'burnt offering'], '16:4': ['linen tunic', 'linen undergarments', 'linen sash', 'linen turban', 'bathe', 'before putting'], '16:5': ['two male goats', 'sin offering', 'one ram', 'burnt offering'], '16:6': ['himself', 'household'], '16:7': ['two goats', 'before the LORD', 'entrance'], '16:8': ['lots', 'for the LORD', 'for Azazel'], '16:9': ['for the LORD', 'sin offering'], '16:10': ['alive before the LORD', 'atonement over it', 'send it away', 'wilderness'], '16:11': ['own sin offering', 'himself and his household', 'slaughter'], '16:12': ['censer full', 'burning coals', 'two handfuls', 'finely ground', 'behind the curtain'], '16:13': ['cloud', 'above the testimony', 'will not die'], '16:14': ['finger', 'east side', 'seven times in front'], '16:15': ["people's sin offering", 'behind the curtain', "bull's blood", 'on the atonement cover', 'in front'], '16:16': ['inner sanctuary', "Israelites' impurities and rebellions", 'all their sins', 'tent of meeting', 'midst of their impurities'], '16:17': ['No one else', 'from the time', 'until he comes out', 'himself', 'household', 'whole assembly'], '16:18': ['go out', 'altar', "bull's blood", "goat's blood", 'horns all around'], '16:19': ['finger seven times', 'cleansing', 'making it holy'], '16:20': ['finished', 'inner sanctuary', 'tent of meeting', 'altar', 'live goat'], '16:21': ['both hands', 'live goat', "all the Israelites' wrongdoing", 'all their rebellions', 'all their sins', "goat's head", 'man appointed'], '16:22': ['carry all their wrongdoing', 'remote land', 'release'], '16:23': ['take off', 'linen garments', 'leave them there'], '16:24': ['bathe', 'holy place', 'put on his clothes', 'his burnt offering', "people's burnt offering", 'himself and for the people'], '16:25': ['fat', 'sin offering', 'altar'], '16:26': ['Azazel', 'wash his clothes', 'bathe his body', 'After that', 'enter the camp'], '16:27': ['bull and goat', 'outside the camp', 'hides, flesh, and dung', 'burned in the fire'], '16:28': ['wash their clothes', 'bathe their body', 'After that', 'enter the camp'], '16:29': ['tenth day of the seventh month', 'deny yourselves', 'do no work', 'native-born', 'foreigners living among you'], '16:30': ['atonement will be made', 'clean from all your sins before the LORD'], '16:31': ['sabbath of complete rest', 'deny yourselves', 'lasting statute'], '16:32': ['anointed and ordained', "father's place", 'linen garments', 'holy garments'], '16:33': ['inner sanctuary', 'tent of meeting', 'altar', 'priests', 'all the assembled people'], '16:34': ['lasting statute', 'once a year', 'all their sins', 'Aaron did', 'commanded Moses'], '17:1': ['Moses'], '17:2': ['Aaron, his sons, and all the Israelites'], '17:3': ['house of Israel', 'ox', 'sheep', 'goat', 'inside or outside the camp'], '17:4': ['entrance', 'offering', 'tabernacle', 'guilty of bloodshed', 'shed blood', 'cut off from their people'], '17:5': ['open country', 'priest', 'peace offerings'], '17:6': ['splash', 'blood', 'fat', 'pleasing aroma'], '17:7': ['no longer', 'goat demons', 'prostituting themselves', 'generations'], '17:8': ['house of Israel', 'foreigner living among them', 'burnt offering or a sacrifice'], '17:9': ['entrance', 'cut off'], '17:10': ['foreigner living among them', 'any blood', 'I will set my face', 'cut them off'], '17:11': ['life of the flesh', 'in the blood', 'I myself have given', 'altar', 'your lives', 'through the life it carries'], '17:12': ['None of you', 'no foreigner living among you'], '17:13': ['Israelite', 'foreigner living among them', 'hunts', 'wild animal or bird', 'may be eaten', 'pour out its blood', 'cover it with earth'], '17:14': ['life of every creature', 'blood', 'carries its life', 'cut off'], '17:15': ['native-born or a foreigner', 'died on its own', 'torn by wild animals', 'wash their clothes', 'bathe in water', 'unclean until evening', 'then they will be clean'], '17:16': ['do not wash', 'and do not bathe', 'bear their guilt']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert sum(v['after'].count('Azazel') for v in byref.values())==4
 assert byref['16:11']['after'].count('bull for his own sin offering')==2
 assert 'household' not in byref['16:24']['after']
 assert 'foreigner' not in byref['17:3']['after']
 assert 'all around' not in byref['17:6']['after']
 assert byref['17:14']['after'].count('life')==3
 assert all('forgiven' not in v['after'] for v in byref.values())
 assert all('cliff' not in v['after'] and 'Satan' not in v['after'] for v in byref.values())
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,18))
  assert len(new['revision_batches'])==6 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 16–17; 50 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 16–17; 50 verses','revision_audits':audits,'cumulative_coverage':{'chapters':112,'verses':3360},'source_record_count':859,'public_source_mapping':'Leviticus 16–17 aligns directly; all 50 records are unique and complete, including written hand and read hands forms at 16:21. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 50 pinned Hebrew records including written/read forms at 16:21 before drafting, then selected NET lexical and grammatical notes. All TSW comparators were read after drafting. The assembled text was reread. Focused checks cover sanctuary spaces, all four linen garments, animal counts and beneficiaries, lots and four occurrences of Azazel, incense and blood applications, both hands and complete confession, live release, cleansing of attendants, exact annual date and native/foreigner scope, priestly succession, broad slaughter wording, bloodguilt, goat-demon metaphor, repeated blood/life language, edible hunted game and carrion consequences. This is an authoring self-check, not independent scholarly review.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':26,'chapters':112,'verses':3360,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
