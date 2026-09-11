"""Check exact source bindings and structure; independent editorial review is pending."""
from pathlib import Path
from difflib import SequenceMatcher
import argparse,hashlib,json,re,subprocess,sys,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='13ca74b86a42a8948f1c3841bf42f6b70def443d';COUNTS={21:24,22:33}
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
 assert len(audits)==28 and len(chapters)==117 and sum(a['verses'] for a in audits)==3511
 assert {k:len(v) for k,v in refs.items()}=={'James':108,'Genesis':1533,'Exodus':1213,'Leviticus':657}
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',args.leviticus_source.read_text(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 assert len(raw)==859
 l=json.loads((BATCH/'leviticus-verse-review.json').read_text());byref={v['reference'].replace('Leviticus ',''):v for v in l['verses']}
 assert set(byref)=={f'{c}:{v}' for c,n in COUNTS.items() for v in range(1,n+1)}
 for ref,v in byref.items():assert v['source_reference']=='Lev '+ref and v['source_verse_sha256']==hashlib.sha256(raw['Lev '+ref].encode()).hexdigest()
 assert len({v['source_reference'] for v in byref.values()})==57
 annotated=[ref for ref in byref if '<note' in raw['Lev '+ref]];assert annotated==['21:5']
 assert '<catchWord>יקרחה</catchWord>' in raw['Lev 21:5'] and 'יִקְרְח֤וּ' in raw['Lev 21:5'] and 'type="x-qere"' in raw['Lev 21:5']
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
 checks={'21:1': ["Aaron's sons", 'A priest', 'dead person'], '21:2': ['mother', 'father', 'son', 'daughter', 'brother'], '21:3': ['virgin sister', 'close to him', 'has not married', 'may make himself unclean'], '21:4': ['husband', 'profane himself'], '21:5': ['bald patches', 'edges of their beards', 'gashes'], '21:6': ['holy to their God', 'profane', 'offerings by fire', 'food of their God', 'They must be holy'], '21:7': ['prostitute', 'defiled', 'divorced by her husband', 'A priest is holy'], '21:8': ['Treat the priest as holy', 'food of your God', 'makes you holy'], '21:9': ["priest's daughter", 'prostitution', 'profane', 'father', 'burned with fire'], '21:10': ['high priest', 'above his fellow priests', 'oil poured on his head', 'ordained', 'hair hang loose', 'tear his garments'], '21:11': ['any dead body', 'even for his father or mother'], '21:12': ['not leave the sanctuary', 'profane the sanctuary', 'consecration', "God's anointing oil"], '21:13': ['marries', 'virgin'], '21:14': ['widow', 'divorced woman', 'defiled woman', 'prostitute', 'virgin from his own people'], '21:15': ['offspring', 'makes him holy'], '21:17': ['generations', 'no man', 'descendants', 'physical blemish', 'food of his God'], '21:18': ['blind', 'difficulty walking', 'disfigured face', 'overlong limb'], '21:19': ['broken foot or hand'], '21:20': ['curved back', 'stunted growth', 'eye blemish', 'itching sores', 'skin eruption', 'crushed testicle'], '21:21': ['Aaron the priest', 'offerings by fire', 'He has a blemish', 'food of his God'], '21:22': ['may eat', 'most holy offerings', 'holy offerings'], '21:23': ['curtain', 'altar', 'holy places', 'makes them holy'], '21:24': ['Aaron, his sons, and all the Israelites'], '22:2': ['Aaron and his sons', 'keep away', 'offerings the Israelites consecrate to me', 'holy name'], '22:3': ['generations', 'descendants', 'while he is unclean', 'cut off from my presence'], '22:4': ['defiling skin disease', 'discharge', 'until he is clean', 'contact with the dead', 'emission of semen'], '22:5': ['swarming creature', 'person', 'whatever that person'], '22:6': ['until evening', 'unless he bathes his body in water'], '22:7': ['sun sets', 'will be clean', 'Then he may eat', 'his food'], '22:8': ['died on its own', 'torn by wild animals'], '22:9': ['priests', 'bear sin and die', 'holy food', 'makes them holy'], '22:10': ['outside the priestly household', 'lodger', 'hired worker'], '22:11': ['buys as a slave', 'his own money', 'born in his household', 'may also eat'], '22:12': ["priest's daughter", 'marries a man outside the priestly household', 'contributions'], '22:13': ['widowed or divorced', 'no offspring', "returns to her father's house", 'as in her youth', 'may eat', 'outside the priestly household'], '22:14': ['by mistake', 'repay', 'priest', 'one-fifth'], '22:15': ['priests', 'Israelites contribute', 'LORD'], '22:16': ['cause the people', 'guilt and its penalty', 'when they eat their holy offerings', 'makes them holy'], '22:18': ['Aaron, his sons, and all the Israelites', 'house of Israel', 'foreigner residing in Israel', 'burnt offering', 'vow', 'freewill'], '22:19': ['male without blemish', 'cattle, sheep, or goats', 'accepted on your behalf'], '22:20': ['blemish', 'not be accepted'], '22:21': ['peace sacrifice', 'herd or flock', 'vow', 'freewill', 'without blemish', 'no blemish at all'], '22:22': ['blind', 'broken bone', 'mutilated part', 'growth', 'itching sores', 'skin eruption', 'altar', 'offering by fire'], '22:23': ['cattle, sheep, or goats', 'overlong or stunted limb', 'freewill', 'not be accepted in fulfillment of a vow'], '22:24': ['testicles', 'bruised, crushed, torn away, or cut off', 'not do this in your land'], '22:25': ['any such animals', 'foreigner', 'food of your God', 'damaged', 'blemish', 'not be accepted'], '22:27': ['calf, lamb, or kid', 'mother', 'seven days', 'eighth day onward', 'may be accepted'], '22:28': ['cattle, sheep, or goats', 'animal and its young', 'same day'], '22:29': ['thanksgiving', 'accepted on your behalf'], '22:30': ['same day', 'not leave any of it until morning'], '22:31': ['Keep my commandments', 'carry them out'], '22:32': ['holy name', 'held holy among the Israelites', 'makes you holy'], '22:33': ['brought you out of Egypt', 'to be your God', 'I am the LORD']}
 for ref,ts in checks.items():
  for term in ts:assert term.casefold() in byref[ref]['after'].casefold(),(ref,term)
 assert byref['21:21']['after'].count('come forward')==2
 assert byref['21:21']['after'].count('blemish')==2
 assert byref['22:21']['after'].count('blemish')==2
 assert 'male' not in byref['22:21']['after']
 assert 'from their people' not in byref['22:3']['after']
 assert 'through the curtain' not in byref['21:23']['after']
 assert 'foreigner' not in byref['22:10']['after'] and 'foreigner' not in byref['22:12']['after']
 assert 'must' not in byref['22:27']['after'].split('From the eighth')[1]
 assert all(t not in ' '.join(v['after'].lower() for v in byref.values()) for t in ['hansen', 'leprosy', 'worthless', 'inferior', 'cursed'])
 reviewdir='audit/exegetical-core/fluent-production/leviticus/'
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{f'translations/fluent/OT/leviticus/Leviticus_{c:02}.md' for c in COUNTS}|{reviewdir+f'Leviticus_{c:02}_review.json' for c in COUNTS}|{reviewdir+x for x in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines()
 assert all(s in allowed or s.startswith(str(BATCH.relative_to(ROOT))+'/') for s in changed),changed
 for n in ['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','LEVITICUS_FLUENT_BOOK_QA.json']:
  old=json.loads(run('git','show',BASE+':'+reviewdir+n));new=json.loads((ROOT/reviewdir/n).read_text())
  assert new['publication_allowed'] is False and new['editorial_review_pending_chapters']==list(range(1,23))
  assert len(new['revision_batches'])==8 and new['revision_batches'][:-1]==old['revision_batches']
  if 'entries' in old:
   assert len(old['entries'])==len(new['entries'])
   for a,b in zip(old['entries'],new['entries']):
    if a['chapter'] not in COUNTS:assert a==b
 overlap={'scope':'Leviticus 21–22; 57 verses','method':'Case-folded word tokens and SequenceMatcher; near-identical is nonidentical >=0.90. Triage only; not fidelity or originality evidence.','stages':{}}
 for stage in ['before','after']:
  rows=[]
  for v in l['verses']:
   a,b=words(v[stage]),words(v['tsw_comparator']);rows.append({'reference':v['reference'],'identical':a==b,'similarity':round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)})
  overlap['stages'][stage]={'identical_verses':sum(x['identical'] for x in rows),'near_identical_verses':sum(not x['identical'] and x['similarity']>=.90 for x in rows),'mean_similarity':round(sum(x['similarity'] for x in rows)/len(rows),6),'verses':rows}
 put('overlap-before-after.json',overlap)
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 put('verification.json',{'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Leviticus 21–22; 57 verses','revision_audits':audits,'cumulative_coverage':{'chapters':117,'verses':3511},'source_record_count':859,'public_source_mapping':'Leviticus 21–22 aligns directly; all 57 records are unique and complete, including the original written/read forms at 21:5. Prior Genesis and Exodus public/source differences remain bound unchanged.','source_annotations_hashed_in_full':annotated,'focused_assertions':checks,'TSW_prior_revisions_Companion_and_unaffected_approvals_preserved':True,'translation_family_audit':family,'git_diff_check':diff,'editorial_self_check':'The authoring model read all 57 pinned Hebrew verses and the written/read annotation at 21:5 before drafting. Selected NET lexical and grammatical notes were consulted after Hebrew reading and before drafting. All 57 TSW comparators were read after the independent draft. The assembled English was reread against the source reading; the bodily-condition list and two sanctuary prohibitions were clarified. Focused checks cover ordinary/high-priest differences, all named relatives, marriage categories and fire penalty, food-of-God and holiness repetition, all listed bodily conditions with lexical uncertainty, retained eating entitlement, curtain/altar access, uncleanness and sunset, purchase and household status, daughters and return conditions, one-fifth restitution, ambiguous priestly responsibility, resident/outsider distinctions, animal sex and conditions, vow/freewill exception, four genital injuries, foreign sourcing, seven/eight-day and same-day limits, and the final exodus identity. This is an authoring self-check, not independent scholarly review.','independent_editorial_review':'REVIEW_PENDING','publication_allowed':False})
 print(json.dumps({'status':'PASSED','ledgers':28,'chapters':117,'verses':3511,'overlap':{k:{a:b for a,b in v.items() if a!='verses'} for k,v in overlap['stages'].items()}},indent=2))
if __name__=='__main__':main()
