"""Apply the specifically reviewed editorial corrections, preserving prior provenance."""
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
from difflib import SequenceMatcher
R=Path(__file__).resolve().parents[3]; A=Path(__file__).resolve().parent
BASE='dc09c88b7080e042e915474fe50e92f56adeee3c'
sys.path.insert(0,str(R/'tools'))
from audit_translation_overlap import verse_texts,words
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==BASE
changes={};deferred=[]
def change(path,fn,why):
 p=R/path;old=p.read_text();new=fn(old);assert old!=new,path
 if path not in changes:changes[path]=dict(path=path,before_sha256=sha(p.read_bytes()),reasons=[])
 changes[path]['reasons'].append(why);p.write_text(new)
def replace(path,old,new,why):
 def f(t):assert t.count(old)==1,(path,old);return t.replace(old,new)
 change(path,f,why)
def remove_note(path,prefix):
 def f(t):
  start=t.index('## Notes');pre=t[:start];tail=t[start:];m=re.search(r'^'+re.escape(prefix)+r'.*(?:\n(?!\n|v\d|##).*)*',tail,re.M);assert m
  deferred.append(dict(path=path,removed_note=m[0],reason='Application/commentary belongs in a separately reviewed Companion, not the translation apparatus. Not inserted into the Companion.'))
  return pre+tail[:m.start()]+tail[m.end():].lstrip('\n')
 change(path,f,'Remove application/commentary from selective translation notes; archive the wording for possible Companion review.')

for d in json.loads((A/'paragraph-decisions.json').read_text()):
 def f(t):
  pat=rf'(^v{d["join_after"]:02}:.*?)(\n</p>\s*\n<p>\n)(?=v{d["join_after"]+1:02}:)'
  out,n=re.subn(pat,r'\1\n',t,count=1,flags=re.M|re.S);assert n==1,(d,pat);return out
 change(d['path'],f,d['reason']+f' Join after verse {d["join_after"]}.')

for ch,breaks in {
 3:{7:None,10:None,12:None,14:None,15:None,18:None,21:'The Baptism of Jesus',23:'The Ancestry of Jesus'},
 6:{6:'Healing on the Sabbath',12:'The Twelve Apostles',17:'The Gathering on the Plain',20:'Blessings and Woes',24:None,27:'Love for Enemies',32:None,37:'Judging and Giving',39:'The Blind Guide and the Speck',43:'A Tree and Its Fruit',46:'Hearing and Doing'}
}.items():
 path=f'translations/fluent/NT/luke/Luke_{ch:02}.md'
 for verse,heading in breaks.items():
  marker=f'v{verse:02}:';gap='</p>\n\n'+(f'## {heading}\n\n' if heading else '')+'<p>\n'
  def f(t):
   body,apparatus=t.split('## Notes',1);assert body.count('\n'+marker)==1
   return body.replace('\n'+marker,'\n'+gap+marker)+'## Notes'+apparatus
  change(path,f,'Mark the narrative, speaker, or teaching transition before verse '+str(verse)+'; preserve Scripture wording and sentence relationships.')

replace('translations/fluent/NT/galatians/Galatians_02.md','## Set Right through the Faithfulness of Christ','## Justification and Life in Christ','Keep the editorial heading from privileging one interpretation of the disputed faith/faithfulness genitive.')
for path,prefixes in {
 'translations/fluent/NT/luke/Luke_06.md':['v29–30:'],
 'translations/fluent/NT/luke/Luke_21.md':['v01–04:'],
 'translations/fluent/NT/1corinthians/1Corinthians_06.md':['v07–8:'],
 'translations/fluent/NT/2corinthians/2Corinthians_01.md':['v08–10:'],
 'translations/fluent/NT/galatians/Galatians_02.md':['v04–5:','v11–14:']
}.items():
 for prefix in prefixes:remove_note(path,prefix)
replace('translations/fluent/NT/1corinthians/1Corinthians_07.md',"v15: When an unbelieving spouse leaves, the believer is ‘not enslaved’; the passage's call to peace should not be used to require coercive control.","v15: ‘Not enslaved’ translates a form of douloō, ‘enslave.’ Paul uses a different verb, deō, ‘bind,’ for the marriage bond in verse 39.",'Replace pastoral application with a concise lexical distinction supported by the Greek.')
replace('translations/fluent/NT/2corinthians/2Corinthians_04.md',"v17: Calling affliction ‘light’ is Paul's contrast with an immeasurable weight of glory; it should not be used to minimize another person's suffering.","v17: ‘Light’ and ‘weight’ form a contrast; ‘momentary’ and ‘eternal’ form a second contrast.",'Describe the source rhetoric without adding pastoral instructions.')
replace('translations/fluent/NT/2thessalonians/2Thessalonians_01.md','## Vocabulary',"v12: The Greek can be read ‘our God and Lord Jesus Christ’ or ‘our God and the Lord Jesus Christ.’\n\n## Vocabulary",'Name the consequential alternative construal of the shared article and coordinated titles.')
replace('translations/fluent/NT/revelation/Revelation_02.md','I will kill her children with death.','I will put her children to death.','Render the emphatic death expression in natural English without specifying plague or changing children to an explanatory label; retain the literal/plague possibility in the note.')
replace('translations/fluent/NT/revelation/Revelation_21.md','The one who overcomes will inherit these things, and I will be their God, and they will be my son.',"The one who overcomes will inherit these things. I will be that person's God, and that person will be my son.",'Make the singular generic recipient explicit while preserving the scriptural sonship formula and the promised inheritance.')

qpath=R/'audit/fluent-revision/WORK_QUEUE.json';q=json.loads(qpath.read_text());affected=[];versechanges=[]
for scope in q['completed_draft_scopes']:
 lp=R/scope['ledger'];l=json.loads(lp.read_text());hit=False
 for c in l['chapters']:
  if c['path'] not in changes:continue
  hit=True;record=changes[c['path']];before=subprocess.check_output(['git','show',BASE+':'+c['path']],cwd=R)
  assert sha(before)==record['before_sha256']==c['after_sha256']
  after=(R/c['path']).read_bytes();record['after_sha256']=sha(after);record['ledger']=scope['ledger'];c['after_sha256']=sha(after)
  priorvs=verse_texts(before.decode());aftervs=verse_texts(after.decode());assert list(priorvs)==list(aftervs)
  for v in l['verses']:
   if int(re.search(r'(\d+):\d+$',v['reference'])[1])!=c['chapter']:continue
   label=f'{int(v["reference"].split(":")[-1]):02}';assert v['after']==priorvs[label]
   if v['after']!=aftervs[label]:
    vc=dict(reference=v['reference'],path=c['path'],before=v['after'],after=aftervs[label],source_reference=v['source_reference'],source_verse_sha256=v['source_verse_sha256'],rationale=record['reasons'][-1]);versechanges.append(vc)
    v.setdefault('subsequent_editorial_changes',[]).append(dict(audit='2026-09-17-full-corpus-audit',previous_after=v['after'],rationale=vc['rationale'],base_commit=BASE))
    v['after']=aftervs[label];v['identical_words_to_tsw']=words(v['after'])==words(v['tsw_comparator']);v['word_similarity_to_tsw']=round(SequenceMatcher(None,words(v['after']),words(v['tsw_comparator']),autojunk=False).ratio(),6)
  crp=R/'audit/exegetical-core/fluent-production'/Path(c['path']).parts[-2]/(Path(c['path']).stem+'_review.json')
  cr=json.loads(crp.read_text());cr['chapter_binding']=copy.deepcopy(c)
  cv={v['reference']:v for v in l['verses']}
  for field in ['key_decisions','verse_decisions']:
   if field in cr:
    changedrefs={v['reference'] for v in versechanges}
    cr[field]=[copy.deepcopy(cv[v['reference']]) if v.get('reference') in changedrefs else v for v in cr[field]]
  cr.setdefault('subsequent_editorial_audits',[]).append(dict(audit='audit/fluent-revision/2026-09-17-full-corpus-audit/corrections.json',base_commit=BASE,previous_chapter_sha256=record['before_sha256'],editorial_status='REVIEW_PENDING'))
  dump(crp,cr)
 if hit:
  affected.append(scope['ledger']);l.setdefault('subsequent_editorial_audits',[]).append(dict(audit='audit/fluent-revision/2026-09-17-full-corpus-audit/corrections.json',base_commit=BASE,editorial_status='REVIEW_PENDING'));dump(lp,l)

dump(A/'corrections.json',dict(base_commit=BASE,status='AUTHORING_CORRECTIONS_APPLIED',publication_allowed=False,chapters=list(changes.values()),verse_changes=versechanges,affected_ledgers=affected))
dump(A/'deferred-companion-material.json',deferred)
q.setdefault('completed_corpus_audits',[]).append(dict(scope='All 66 books: structural/source binding and overlap screens, targeted bilingual review',report='audit/fluent-revision/2026-09-17-full-corpus-audit/Fluent-Translation-Audit.md',status='AUDIT_COMPLETE_WITH_OPEN_FINDINGS',independent_editorial_review='REVIEW_PENDING',publication_allowed=False))
q['next_work'].insert(0,dict(scope='Resolve full-corpus audit findings',action='Read the full-corpus report and remaining-actions.json. Finish apparatus, paragraph/heading, key-term, and continuous-reading review without a word-change quota; rebind any changed text.'))
dump(qpath,q)
print(json.dumps(dict(changed_chapters=len(changes),changed_scripture_verses=len(versechanges),affected_ledgers=len(affected),archived_commentary_notes=len(deferred))))
