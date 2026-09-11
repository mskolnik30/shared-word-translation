"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='a7dec96ed90a90e6bc6d1de03c80cfb5429bc3ab';COUNTS={26:46,27:34}
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
 assert len(audits)==30 and len(chapters)==122 and sum(a['verses'] for a in audits)==3713
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':859}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==80
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['26:7','26:8','26:28']
 assert sum(raw['Lev '+ref].count('<note') for ref in byref)==3
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
 checks={'26:1': ['idols', 'carved image', 'sacred pillar', 'figured stone', 'bow down on it'], '26:2': ['Sabbaths', 'sanctuary', 'reverence'], '26:3': ['walk', 'statutes', 'commandments', 'doing them'], '26:4': ['rain in its season', 'crops', 'fruit'], '26:5': ['threshing', 'grape harvest', 'sowing time', 'fill of bread', 'securely'], '26:6': ['peace', 'lie down', 'no one to frighten', 'harmful animals', 'no sword'], '26:7': ['pursue', 'fall before you by the sword'], '26:8': ['Five of you', 'a hundred', 'ten thousand', 'by the sword'], '26:9': ['turn toward', 'fruitful', 'increase your numbers', 'covenant'], '26:10': ['old, stored grain', 'make room for the new'], '26:11': ['my dwelling', 'not abhor'], '26:12': ['walk among you', 'your God', 'my people'], '26:13': ['Egypt', 'their slaves', 'bars of your yoke', 'walk upright'], '26:15': ['reject', 'abhor', 'all my commandments', 'breaking my covenant'], '26:16': ['terror', 'wasting disease and fever', 'eyes', 'life', 'enemies will eat'], '26:17': ['face against', 'defeated', 'hate you will rule', 'no one pursues'], '26:18': ['still will not listen', 'sevenfold', 'sins'], '26:19': ['pride', 'strength', 'sky like iron', 'land like bronze'], '26:20': ['strength for nothing', 'no crops', 'no fruit'], '26:21': ['walk in hostility', 'refuse to listen', 'sevenfold blows'], '26:22': ['wild animals', 'children', 'livestock', 'reduce your numbers', 'roads deserted'], '26:23': ['accept my correction', 'walking in hostility'], '26:24': ['walk in hostility', 'I myself', 'sevenfold'], '26:25': ['sword', 'avenge the covenant', 'cities', 'pestilence', 'enemy'], '26:26': ['staff of bread', 'ten women', 'one oven', 'by weight', 'not be satisfied'], '26:28': ['furious hostility', 'I myself', 'sevenfold'], '26:29': ['flesh of your sons', 'flesh of your daughters'], '26:30': ['high places', 'incense altars', 'your corpses', 'corpses of your idols', 'abhor'], '26:31': ['cities into ruins', 'sanctuaries desolate', 'not smell your pleasing aromas'], '26:32': ['I myself', 'land desolate', 'enemies', 'appalled'], '26:33': ['scatter you among the nations', 'sword in pursuit', 'land', 'cities'], '26:34': ['land will enjoy its Sabbaths', 'enemies’ land', 'land will rest'], '26:35': ['rest it did not have', 'when you lived on it'], '26:36': ['survive', 'hearts with dread', 'windblown leaf', 'sword', 'no one pursues'], '26:37': ['stumble over one another', 'no one pursues', 'no strength to stand'], '26:38': ['perish among the nations', 'land will devour'], '26:39': ['survive', 'their guilt', 'ancestors’ guilt'], '26:40': ['confess their guilt', 'ancestors’ guilt', 'unfaithfulness', 'hostility'], '26:41': ['hostility', 'enemies’ land', 'perhaps', 'uncircumcised heart', 'penalty for their guilt'], '26:42': ['Jacob', 'Isaac', 'Abraham', 'remember the land'], '26:43': ['land', 'Sabbaths', 'penalty', 'precisely because', 'rejected', 'abhorred'], '26:44': ['not reject or abhor', 'so completely', 'destroy', 'break my covenant', 'their God'], '26:45': ['For their sake', 'covenant', 'ancestors', 'Egypt', 'sight of the nations'], '26:46': ['statutes, ordinances and instructions', 'between himself and the Israelites', 'Mount Sinai', 'Moses'], '27:2': ['special vow', 'assessed value of a person'], '27:3': ['male', 'twenty to sixty', 'fifty shekels of silver', 'sanctuary shekel'], '27:4': ['female', 'thirty shekels'], '27:5': ['five to twenty', 'male at twenty', 'female at ten'], '27:6': ['one month to five years', 'male at five', 'female at three'], '27:7': ['sixty years old and upward', 'male at fifteen', 'female at ten'], '27:8': ['too poor', 'person being valued', 'priest', 'one who made the vow can afford'], '27:9': ['animal of a kind', 'may be offered', 'becomes holy'], '27:10': ['good for bad or bad for good', 'both the original and its substitute'], '27:11': ['unclean animal', 'may not be offered', 'before the priest'], '27:12': ['whether good or bad', 'priest sets will stand'], '27:13': ['redeems the animal', 'one-fifth', 'assessed value'], '27:14': ['house as holy', 'good or bad', 'priest sets will stand'], '27:15': ['house', 'one-fifth', 'silver', 'belong to him again'], '27:16': ['family’s field', 'seed needed to sow', 'fifty shekels of silver', 'homer of barley seed'], '27:17': ['Jubilee year', 'full assessed value'], '27:18': ['after the Jubilee', 'years left', 'reduce'], '27:19': ['field', 'one-fifth', 'silver', 'belong to him again'], '27:20': ['does not redeem', 'sold to someone else', 'no longer be redeemed'], '27:21': ['released at the Jubilee', 'devoted beyond recall', 'priest’s holding'], '27:22': ['field he bought', 'not part of his family holding'], '27:23': ['years until the Jubilee', 'pay that amount that very day'], '27:24': ['Jubilee year', 'person he bought it from', 'family holding'], '27:25': ['sanctuary shekel', 'twenty gerahs'], '27:26': ['No one may consecrate', 'firstborn', 'cattle, sheep or goats', 'belongs to the LORD'], '27:27': ['unclean animal', 'ransom', 'plus one-fifth', 'not redeemed', 'sold at the assessed value'], '27:28': ['person', 'animal', 'family’s field', 'neither be sold nor redeemed', 'most holy'], '27:29': ['No person', 'ban', 'ransomed', 'put to death'], '27:30': ['tithe', 'grain', 'fruit', 'holy'], '27:31': ['redeems any', 'one-fifth'], '27:32': ['cattle, sheep and goats', 'every tenth animal', 'under the rod'], '27:33': ['good animals from bad', 'substitute', 'may not be redeemed'], '27:34': ['commandments', 'Moses', 'Israelites', 'Mount Sinai']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['26:29']['after'].count('eat')==2
 assert byref['26:42']['after'].count('remember')==3 and byref['26:42']['after'].count('covenant')==3
 assert [x for x in ['Jacob','Isaac','Abraham']]==re.findall('Jacob|Isaac|Abraham',byref['26:42']['after'])
 assert [ref for ref,v in byref.items() if 'sevenfold' in v['after']]==['26:18','26:21','26:24','26:28']
 assert [ref for ref,v in byref.items() if 'one-fifth' in v['after']]==['27:13','27:15','27:19','27:27','27:31']
 assert 'Jubilee day' not in byref['27:23']['after']
 assert all(x not in byref['27:29']['after'] for x in ['war','prisoner','volunteer'])
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') or s.startswith('audit/fluent-revision/2026-09-11-leviticus-consistency/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,28))
  assert len(new['revision_batches'])==10 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 26–27; 80 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 26–27; 80 verses','revision_audits':audits,'cumulative_coverage':{'chapters':122,'verses':3713},'source_record_count':859,'public_source_mapping':'Leviticus 26–27 aligns directly; all 80 records are unique and complete, including all three annotations at 26:7, 26:8 and 26:28. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 80 pinned Hebrew verses and three annotations before drafting, then consulted selected NET translators’ notes. All 80 TSW comparators were read after drafting. Source and English were compared for conditional progression, four sevenfold stages, covenant and land-rest links, repeated eating and remembering, exact assessment amounts and age bands, property and redemption outcomes, the extra fifth, and human death under the ban. Consequential uncertainties have notes. These are authoring self-checks, not independent scholarly review or reader testing.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':30,'chapters':122,'verses':3713,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
