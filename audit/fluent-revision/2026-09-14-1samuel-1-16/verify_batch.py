"""Cumulative source bindings, format and preservation; not editorial approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='ef956502c0b537887d9fb14f6e4ec742853c71ae'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*a):
 p=subprocess.run(a,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];paths=set()
 names={'Gen':'genesis','Exod':'exodus','Lev':'leviticus','Num':'numbers','Deut':'deuteronomy','Josh':'joshua','Judg':'judges','Ruth':'ruth','1Sam':'1samuel'}
 for sc in q['completed_draft_scopes']:
  l=json.loads((ROOT/sc['ledger']).read_text());bk=names.get(l['source'].get('osis_book_id'),'james');s=sd/(bk+'-pinned-'+('greek.txt' if bk=='james' else 'hebrew.xml'))
  audits.append({'ledger':sc['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',sc['ledger'],'--source-text',str(s)))})
  for c in l['chapters']:assert c['path'] not in paths;paths.add(c['path'])
 assert len(audits)==53 and len(paths)==257 and sum(x['verses'] for x in audits)==7727
 structural=[];allowed={'audit/fluent-revision/WORK_QUEUE.json'};allv={};focused_counts={}
 for bk,pre,name,end in [('ruth','Ruth','Ruth',4),('1samuel','1Samuel','1 Samuel',16)]:
  ad=ROOT/f'audit/fluent-revision/2026-09-14-{bk}-1-{end}';l=json.loads((ad/f'{bk}-verse-review.json').read_text());allv.update({v['reference']:v for v in l['verses']});rd=f'audit/exegetical-core/fluent-production/{bk}/'
  for c in l['chapters']:
   t=(ROOT/c['path']).read_text();m=t.split('---',2)[2].split('## Notes')[0];inside=False
   for line in m.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['path'],line)
   assert not inside
   assert all(s in t.split('---',2)[1] for s in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   rp=rd+f'{pre}_{c["chapter"]:02}_review.json';rv=json.loads((ROOT/rp).read_text());assert rv['chapter_binding']==c and rv['publication_allowed'] is False and rv['status']=='REVIEW_PENDING';allowed|={c['path'],rp}
   structural.append({'path':c['path'],'verses':c['verse_count'],'sha256':c['after_sha256'],'paragraphs':m.count('<p>'),'poetry_and_verse_lines_inside_paragraphs':True})
  for fn in (['RUTH_FLUENT_BOOK_QA.json'] if bk=='ruth' else ['1_SAMUEL_FLUENT_BOOK_QA.json','APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']):
   rel=rd+fn;allowed.add(rel);prev=json.loads(run('git','show',BASE+':'+rel));now=json.loads((ROOT/rel).read_text());assert now['publication_allowed'] is False
   assert now['current_revision']['editorial_status']=='REVIEW_PENDING'
   for k in ['human_textual_review','source_lock','resolved_f3']: 
    if k in prev:assert now[k]==prev[k],(rel,k)
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(prev['entries'])==len(now['entries'])
    for a,b in zip(prev['entries'],now['entries']):
     assert all(b[k]==v for k,v in a.items() if k!='status')
     if a['chapter']>16:assert a==b
     else:assert b['status']=='SUPERSEDED'
  selected=json.loads((ad/'focused-selection.json').read_text());raw={}
  for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/(bk+'-pinned-hebrew.xml')).read_text(),re.S):
   e=E.fromstring(s);ob,c,v=e.attrib['osisID'].split('.');raw[f'{name} {int(c)}:{int(v)}']=(s,e)
  focused=[]
  for key in selected:
   s,e=raw[key];v=allv[key];assert sha(s.encode())==v['source_verse_sha256'];focused.append({'reference':key,'source_verse_sha256':v['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext()) for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode') for x in e if x.tag=='note'],'after':v['after']})
  focused_counts[bk]=len(focused);(ad/'focused-comparisons.json').write_text(json.dumps({'qualification':'Authoring self-check after complete first Hebrew reading and source-led drafting; not independent editorial review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 checks={'Ruth 1:14':['Orpah','Ruth','held tightly'],'Ruth 1:16':['your people','your God'],'Ruth 2:12':['wings'],'Ruth 3:9':['wing','redeemer'],'Ruth 3:15':['six','he went'],'Ruth 4:20':['Salmah'],'Ruth 4:21':['Salmon'],'1 Samuel 1:24':['three bulls'],'1 Samuel 2:3':['by him','deeds'],'1 Samuel 2:6':['kills','Sheol','raises'],'1 Samuel 2:9':['For no one prevails by strength.'],'1 Samuel 2:21':['three sons','two daughters'],'1 Samuel 2:22':['slept with','women'],'1 Samuel 3:13':['themselves'],'1 Samuel 4:10':['thirty thousand'],'1 Samuel 4:15':['ninety-eight'],'1 Samuel 6:19':['fifty thousand and seventy'],'1 Samuel 7:2':['twenty years'],'1 Samuel 8:11':['take'],'1 Samuel 8:13':['take'],'1 Samuel 8:14':['take'],'1 Samuel 8:15':['tenth'],'1 Samuel 8:17':['slaves'],'1 Samuel 9:8':['quarter-shekel'],'1 Samuel 10:3':['three young goats','three loaves','skin of wine'],'1 Samuel 10:8':['seven days'],'1 Samuel 11:2':['right eyes'],'1 Samuel 11:8':['three hundred thousand','thirty thousand'],'1 Samuel 12:11':['Bedan','Samuel'],'1 Samuel 13:1':['…','two years'],'1 Samuel 13:5':['thirty thousand chariots','six thousand'],'1 Samuel 13:21':['pim'],'1 Samuel 14:18':['ark'],'1 Samuel 14:41':['true answer'],'1 Samuel 14:49':['Ishvi','Merab','Michal'],'1 Samuel 14:50':['Abner','uncle Ner'],'1 Samuel 15:3':['men and women','nursing infants','camels and donkeys'],'1 Samuel 15:11':['regret'],'1 Samuel 15:24':['their voice'],'1 Samuel 15:29':['change his mind'],'1 Samuel 15:33':['cut Agag in pieces'],'1 Samuel 15:35':['regretted'],'1 Samuel 16:7':['heart'],'1 Samuel 16:14':['harmful spirit from the LORD'],'1 Samuel 16:23':['lyre','breathe freely']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in allv[ref]['after'].casefold(),(ref,term,allv[ref]['after'])
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();ads=['audit/fluent-revision/2026-09-14-ruth-1-4/','audit/fluent-revision/2026-09-14-1samuel-1-16/'];assert all(n in allowed or any(n.startswith(a) for a in ads) for n in changed),changed
 for sc in q['completed_draft_scopes'][:-2]:assert (ROOT/sc['ledger']).read_bytes()==subprocess.check_output(['git','show',BASE+':'+sc['ledger']],cwd=ROOT)
 assert q['next_work'][0]['scope']=='1 Samuel 17–31'
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'Ruth 1–4 and 1 Samuel 1–16','revision_audits':audits,'cumulative_coverage':{'chapters':257,'verses':7727},'structural_chapters':structural,'first_source_reading_verses':491,'focused_source_reread_verses':focused_counts,'focused_assertions':checks,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':53,'chapters':20,'new_verses':491,'cumulative_verses':7727}))
if __name__=='__main__':main()
