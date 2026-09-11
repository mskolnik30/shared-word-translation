"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='a320dd05347e33f14e9512ac9064f4dc3dee6e4e';COUNTS={23:44,24:23,25:55}
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
 assert len(audits)==29 and len(chapters)==120 and sum(a['verses'] for a in audits)==3633
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':779}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==122
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['23:13','25:20','25:30','25:46']
 assert sum(raw['Lev '+ref].count('<note') for ref in byref)==5
 assert '<catchWord>לא</catchWord>' in raw['Lev 25:30'] and 'ל֣/וֹ' in raw['Lev 25:30'] and 'type="x-qere"' in raw['Lev 25:30']
 assert all('KJV:' not in raw['Lev '+ref] for ref in byref)
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
 checks={'23:2': ['appointed times', 'sacred assemblies', 'my appointed times'], '23:3': ['six days', 'seventh day', 'complete rest', 'no work at all', 'wherever you live'], '23:5': ['first month', 'fourteenth', 'twilight', 'Passover'], '23:6': ['fifteenth', 'Unleavened Bread', 'seven days'], '23:7': ['first day', 'ordinary work'], '23:8': ['seven days', 'offerings by fire', 'seventh day', 'ordinary work'], '23:10': ['land I am giving you', 'sheaf', 'first of your harvest'], '23:11': ['wave', 'accepted on your behalf', 'day after the Sabbath'], '23:12': ['year-old male lamb', 'without blemish', 'burnt offering'], '23:13': ['two-tenths of an ephah', 'fine flour mixed with oil', 'pleasing aroma', 'quarter of a hin of wine'], '23:14': ['bread, roasted grain or fresh grain', 'until that very day', 'your God’s offering'], '23:15': ['day after the Sabbath', 'seven Sabbaths', 'seven full weeks'], '23:16': ['fifty days', 'day after the seventh Sabbath', 'new grain'], '23:17': ['two loaves', 'two-tenths of an ephah', 'with leaven', 'firstfruits'], '23:18': ['seven year-old male lambs without blemish', 'one young bull', 'two rams', 'grain offering and drink offerings'], '23:19': ['one male goat', 'sin offering', 'two year-old male lambs', 'peace sacrifice'], '23:20': ['wave them', 'firstfruits bread', 'two lambs', 'belong to the priest'], '23:21': ['that very day', 'ordinary work', 'your generations'], '23:22': ['edges of your field', 'harvesters leave behind', 'poor', 'foreigner living among you'], '23:24': ['first day of the seventh month', 'rest', 'remembrance', 'blasts of sound'], '23:25': ['ordinary work', 'offering by fire'], '23:27': ['tenth day', 'seventh month', 'Day of Atonement', 'deny yourselves'], '23:28': ['no work at all', 'atonement is made for you'], '23:29': ['does not deny themselves', 'cut off from their people'], '23:30': ['any work', 'I will destroy', 'from among their people'], '23:32': ['complete rest', 'deny yourselves', 'evening of the ninth', 'until the next evening'], '23:34': ['fifteenth day', 'seventh month', 'Booths', 'seven days'], '23:36': ['seven days', 'eighth day', 'solemn gathering', 'ordinary work'], '23:37': ['burnt offerings, grain offerings, sacrifices and drink offerings', 'each on its proper day'], '23:38': ['Sabbaths', 'gifts', 'vow offerings', 'freewill offerings'], '23:39': ['fifteenth day', 'seventh month', 'land’s produce', 'first day', 'eighth'], '23:40': ['fruit', 'palm fronds', 'leafy trees', 'willows', 'Rejoice', 'seven days'], '23:42': ['booths for seven days', 'native-born in Israel'], '23:43': ['your generations will know', 'live in booths', 'brought them out of Egypt'], '24:2': ['pure oil from beaten olives', 'regularly'], '24:3': ['Aaron', 'evening until morning', 'outside the curtain of the testimony', 'tent of meeting'], '24:4': ['pure lampstand', 'regularly'], '24:5': ['twelve loaves', 'two-tenths of an ephah for each loaf'], '24:6': ['two arrangements', 'six in each', 'pure table'], '24:7': ['pure frankincense', 'each arrangement', 'bread’s memorial portion'], '24:8': ['Sabbath after Sabbath', 'from the Israelites', 'everlasting covenant'], '24:9': ['Aaron and his sons', 'eat it in a holy place', 'most holy', 'lasting share'], '24:10': ['mother was an Israelite', 'father was an Egyptian', 'Israelite man', 'fighting'], '24:11': ['Name', 'cursed', 'Shelomith', 'Dibri', 'Dan'], '24:12': ['custody', 'LORD’s own word', 'decision clear'], '24:14': ['outside the camp', 'Everyone who heard', 'hands on his head', 'whole assembly', 'stone'], '24:15': ['his God', 'guilt of his sin'], '24:16': ['put to death', 'whole assembly', 'stone', 'Foreigner and native-born'], '24:17': ['strikes a human being dead', 'put to death'], '24:18': ['animal dead', 'replace it', 'life for life'], '24:19': ['bodily injury', 'must be done to him'], '24:20': ['Fracture for fracture, eye for eye, tooth for tooth', 'inflicted on him'], '24:21': ['animal dead', 'replace it', 'human being dead', 'put to death'], '24:22': ['one rule', 'foreigner and native-born'], '24:23': ['outside the camp', 'stoned him', 'LORD had commanded Moses'], '25:1': ['Mount Sinai'], '25:2': ['land I am giving you', 'land is to keep a Sabbath'], '25:4': ['seventh year', 'land', 'complete rest', 'not sow', 'prune'], '25:5': ['grows on its own', 'untended vines', 'year of rest'], '25:6': ['male and female slaves', 'hired worker', 'residents'], '25:7': ['livestock', 'wild animals', 'All its produce'], '25:8': ['seven times seven', 'forty-nine years'], '25:9': ['tenth day of the seventh month', 'horn', 'Day of Atonement', 'throughout your land'], '25:10': ['fiftieth year', 'everyone living in it', 'family holding', 'to your family'], '25:11': ['fiftieth year', 'not sow', 'grows on its own', 'untended vines'], '25:12': ['holy', 'Eat what the fields produce'], '25:15': ['years since the Jubilee', 'harvest years left'], '25:16': ['More years', 'higher price', 'fewer years', 'lower price', 'number of harvests'], '25:20': ['What will we eat in the seventh year', 'do not sow or gather'], '25:21': ['sixth year', 'three years'], '25:22': ['eighth year', 'old crop', 'ninth year', 'crop comes in'], '25:23': ['not be sold permanently', 'land is mine', 'foreigners and residents living with me'], '25:25': ['brother becomes poor', 'part of his family holding', 'nearest redeemer'], '25:26': ['no redeemer', 'enough to redeem it himself'], '25:27': ['years since the sale', 'refund the balance', 'return to his family holding'], '25:28': ['cannot afford the refund', 'remain with the buyer', 'Jubilee', 'released'], '25:29': ['walled city', 'full year', 'right to redeem'], '25:30': ['not redeemed', 'full year', 'walled city', 'permanent property', 'his generations', 'not be released'], '25:31': ['no surrounding wall', 'open fields', 'redeemed', 'released'], '25:32': ['Levites', 'always have the right to redeem'], '25:33': ['redeems a house from the Levites', 'released at the Jubilee', 'holding among the Israelites'], '25:34': ['pastureland', 'must not be sold', 'permanent holding'], '25:35': ['brother becomes poor', 'support him', 'foreigner or resident', 'live with you'], '25:36': ['no interest or increase', 'Fear your God', 'brother live with you'], '25:37': ['money at interest', 'food for a profit'], '25:38': ['Egypt', 'land of Canaan', 'to be your God'], '25:39': ['is sold to you', 'not make him do a slave’s labor'], '25:40': ['hired worker or resident', 'until the Jubilee year'], '25:41': ['he and his children', 'return to his family', 'ancestors’ holding'], '25:42': ['my slaves', 'Egypt', 'not be sold as slaves'], '25:44': ['male and female slaves', 'nations around you', 'buy'], '25:45': ['buy people', 'children of residents', 'families born in your land', 'your property'], '25:46': ['your sons', 'inherited property', 'slaves permanently', 'brothers, the Israelites', 'harshly'], '25:47': ['foreigner or resident', 'wealthy', 'brother becomes poor', 'sold', 'member of the foreigner’s family'], '25:48': ['right to be redeemed', 'One of his brothers'], '25:49': ['uncle', 'uncle’s son', 'close relative', 'redeem himself'], '25:50': ['his buyer', 'year he was sold', 'Jubilee year', 'sale price', 'hired worker'], '25:51': ['many years remain', 'purchase price', 'in proportion'], '25:52': ['few years remain', 'Jubilee', 'with his buyer', 'in proportion'], '25:53': ['hired year by year', 'harshly before your eyes'], '25:54': ['not redeemed', 'he and his children', 'released in the Jubilee year'], '25:55': ['slaves belonging to me', 'my slaves', 'Egypt', 'I am the LORD your God']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['23:38']['after'].count('in addition to')==4
 assert byref['25:3']['after'].lower().count('six years')==2
 assert byref['25:44']['after'].count('male and female slaves')==2
 assert all(s not in byref['23:24']['after'].lower() for s in ['trumpet','shofar'])
 assert all(s not in byref['23:40']['after'].lower() for s in ['citron','myrtle','build'])
 assert 'foreigner' not in byref['23:42']['after'].lower()
 assert 'each loaf' not in byref['23:17']['after']
 assert 'not redeem' not in byref['25:33']['after']
 assert 'excessive' not in byref['25:36']['after']
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,26))
  assert len(new['revision_batches'])==9 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 23–25; 122 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 23–25; 122 verses','revision_audits':audits,'cumulative_coverage':{'chapters':120,'verses':3633},'source_record_count':859,'public_source_mapping':'Leviticus 23–25 aligns directly; all 122 records are unique and complete, including all five annotations in four verses and the original written/read forms at 25:30. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 122 pinned Hebrew verses and all five annotations before drafting. Selected NET translators’ notes were consulted after Hebrew reading and before drafting. All 122 TSW comparators were read after the independent draft. The English was checked against the source reading, with male lambs made explicit, speaker punctuation repaired, the impoverished brother’s support clarified, and resident children retained. Focused checks cover calendar dates, work distinctions, all offerings and quantities, leaven, Sabbath counting, unspecified signal instrument, cutoff versus divine destruction, booth materials and native-born scope, sanctuary location and bread quantities, named family and tribe, actual execution and injury formulas, Jubilee count and differing release conditions, land ownership, redemption arithmetic, walled-city read form, difficult Levitical redemption syntax, resident status ambiguity, slavery and inheritance, kinship roles, and repeated exodus identity. These are authoring self-checks, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':29,'chapters':120,'verses':3633,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
