"""Whole-book structure and selected source comparisons, not independent editorial approval."""
from pathlib import Path
import argparse,json,re,hashlib,subprocess,sys,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='3504ff60de9df091d43250021588219d735a45a7'
sys.path.insert(0,str(ROOT/'tools'));from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
def main():
 p=argparse.ArgumentParser()
 for b in ['genesis','exodus','leviticus','numbers','deuteronomy','joshua','judges','james']:p.add_argument('--'+b+'-source',type=Path,required=True)
 a=p.parse_args();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];deut=[];allpaths=set()
 for scope in q['completed_draft_scopes']:
  lp=scope['ledger'];l=json.loads((ROOT/lp).read_text());book=scope['scope'].split()[0]
  audits.append({'ledger':lp,**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',lp,'--source-text',str(getattr(a,book.lower()+'_source').resolve())))})
  for c in l['chapters']:assert c['path'] not in allpaths;allpaths.add(c['path'])
  if book=='Judges':deut.append((lp,l))
 assert len(audits)==51 and len(allpaths)==237 and sum(x['verses'] for x in audits)==7236
 data=a.judges_source.read_bytes();assert sha(data)=='1429da54e4c60bf805adea3ce2b96a57140d9d44a77bfb47050bae2ac954e1a3'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()=='8732f355c2d6718aa2d0a8821c451ad0450eacb4'
 raw={f'Judg {c}:{v}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',data.decode(),re.S) for c,v in [re.search(r'osisID="Judg\.(\d+)\.(\d+)"',s).groups()]}
 public={v['reference']:v for lp,l in deut for v in l['verses']};refs=[v['source_reference'] for v in public.values()];assert len(deut)==3 and len(public)==len(refs)==len(set(refs))==len(raw)==618 and set(refs)==set(raw)
 structural=[]
 for lp,l in deut:
  for c in l['chapters']:
   b=(ROOT/c['path']).read_bytes();t=b.decode();m=t.split('---',2)[2].split('## Notes')[0]
   assert sha(b)==c['after_sha256'] and re.findall(r'^v(\d\d):',m,re.M)==[f'{v:02}' for v in range(1,c['verse_count']+1)]
   assert m.count('“')==m.count('”'),c['chapter']
   inside=False
   for line in m.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['chapter'],line)
   assert not inside
   for para in m.split('</p>')[:-1]:assert not para.rstrip().endswith((',',':',';','—'))
   assert all(x in t for x in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   cr=json.loads((ROOT/f'audit/exegetical-core/fluent-production/judges/Judges_{c["chapter"]:02}_review.json').read_text());assert cr['chapter_binding']==c and cr['publication_allowed'] is False
   structural.append({'chapter':c['chapter'],'verses':c['verse_count'],'sha256':sha(b),'headings':re.findall(r'^## (.*)$',m,re.M)})
 assert sorted(c['chapter'] for c in structural)==list(range(1,22))
 mapping={}
 fo=json.loads((BATCH/'focused-comparisons.json').read_text());changes=json.loads((BATCH/'changes.json').read_text());selected=fo['rows']
 assert len(selected)==len({x['reference'] for x in selected})==265
 for row in selected:
  v=public[row['reference']];assert row['fluent']==v['after'] and row['source_verse_sha256']==v['source_verse_sha256']==sha(raw[v['source_reference']].encode())
  e=E.fromstring(raw[v['source_reference']]);assert row['hebrew']==' '.join(''.join(w.itertext()) for w in e if w.tag=='w');assert row['annotations']==[E.tostring(w,encoding='unicode') for w in e if w.tag=='note']
 text=lambda ref:public['Judges '+ref]['after']
 checks={'1:1': ['Who should go up first'], '1:13': ['Othniel son of Kenaz'], '1:19': ['could not drive out', 'iron chariots'], '1:28': ['forced labor'], '2:9': ['Timnath-heres'], '2:11': ['evil in the LORD’s eyes'], '2:16': ['judges', 'rescued', 'hand'], '3:7': ['Asheroth'], '3:10': ['Spirit', 'judged'], '3:11': ['forty years'], '3:15': ['left-handed'], '3:30': ['eighty years'], '4:3': ['nine hundred', 'twenty years'], '4:4': ['prophetess', 'judging'], '4:9': ['woman’s hand'], '5:18': ['even to death'], '5:28': ['clatter'], '5:30': ['a womb, two wombs'], '5:31': ['forty years'], '6:13': ['grasp'], '6:14': ['grasp'], '6:25': ['second bull', 'seven years'], '6:34': ['clothed himself with Gideon'], '7:3': ['Gilead', 'Twenty-two thousand', 'ten thousand'], '7:6': ['Three hundred', 'hands'], '7:18': ['For the LORD and for Gideon'], '7:20': ['A sword for the LORD and for Gideon'], '8:14': ['seventy-seven'], '8:16': ['taught', 'thorns'], '8:17': ['killed'], '8:23': ['LORD will rule'], '8:26': ['one thousand seven hundred'], '8:27': ['snare'], '8:28': ['forty years'], '8:35': ['loyal kindness'], '9:5': ['seventy sons', 'Jotham', 'survived'], '9:18': ['slave woman'], '9:23': ['God sent an evil spirit'], '9:34': ['four companies'], '9:43': ['three companies'], '9:44': ['companies with him', 'other two'], '9:49': ['thousand men and women'], '10:4': ['thirty sons', 'thirty donkeys', 'thirty towns'], '10:12': ['Maon'], '11:24': ['Chemosh'], '11:26': ['three hundred years'], '11:29': ['Mizpeh'], '11:31': ['and I will offer', 'burnt offering'], '11:34': ['only child'], '11:39': ['he did to her what he had vowed'], '11:40': ['four days'], '12:6': ['Shibboleth', 'Sibboleth', 'Forty-two thousand'], '12:14': ['forty sons', 'thirty grandsons', 'seventy donkeys'], '13:5': ['begin to rescue'], '13:7': ['until the day he dies'], '14:3': ['right in my eyes'], '14:15': ['seventh day'], '15:6': ['burned her and her father to death'], '15:19': ['hollow at Lehi'], '16:17': ['all that was in his heart'], '16:18': ['all that was in his heart', 'all that is in his heart'], '16:21': ['gouged out his eyes'], '16:27': ['On the roof', 'about three thousand'], '16:28': ['one of my two eyes'], '17:4': ['two hundred'], '17:7': ['clan of Judah', 'Levite'], '18:30': ['Manasseh'], '19:8': ['“Please strengthen yourself. Stay', 'decline.” The two men ate'], '19:25': ['her husband seized', 'raped', 'abused'], '19:27': ['Her master', 'hands on the threshold'], '19:28': ['no answer'], '20:5': ['meant to kill me'], '20:10': ['Geba'], '20:15': ['twenty-six thousand', 'seven hundred'], '20:18': ['Who should go up first'], '20:28': ['Phinehas son of Eleazar, son of Aaron', 'tomorrow'], '20:35': ['twenty-five thousand one hundred'], '20:46': ['twenty-five thousand'], '20:47': ['Six hundred', 'four months'], '21:10': ['women and children'], '21:12': ['four hundred'], '21:21': ['seize a wife'], '21:23': ['carried off']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in text(ref).casefold(),(ref,term)
 assert text('17:6')==text('21:25')
 assert 'cast image' not in text('18:20')
 assert 'dead' not in text('19:28')
 e=E.fromstring(raw['Judg 19:8']);assert any(w.get('morph')=='HC/Vtv2mp' for w in e if w.tag=='w')
 changedrefs={x['reference'] for x in changes};assert changedrefs=={'Judges 5:18','Judges 5:28','Judges 16:18','Judges 19:8','Judges 19:25'}
 for x in changes:
  b=subprocess.check_output(['git','show',BASE+':'+x['chapter_path']],cwd=ROOT);assert sha(b)==x['before_chapter_sha256'];assert verse_texts(b.decode())[x['reference'].split(':')[1].zfill(2)]==x['before'];assert public[x['reference']]['after']==x['after'];assert sha((ROOT/x['chapter_path']).read_bytes())==x['after_chapter_sha256']
 for lp,l in deut:
  old=json.loads(run('git','show',BASE+':'+lp));ov={v['reference']:v for v in old['verses']};assert l['base_commit']==old['base_commit'] and l['source']==old['source']
  for v in l['verses']:
   if v['reference'] not in changedrefs:assert v==ov[v['reference']]
   else:
    for k in ['before','source_reference','source_verse_sha256','tsw_comparator','delta']:assert v[k]==ov[v['reference']][k]
  for c in l['chapters']:
   if c['chapter'] not in [5,16,19]:assert c==next(x for x in old['chapters'] if x['chapter']==c['chapter'])
 rd='audit/exegetical-core/fluent-production/judges/';names=['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','JUDGES_FLUENT_BOOK_QA.json']
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{x['chapter_path'] for x in changes}|{x['verse_ledger'] for x in changes}|{rd+f'Judges_{c:02}_review.json' for c in [5,16,19]}|{rd+n for n in names}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or p.startswith(str(BATCH.relative_to(ROOT))+'/') for p in changed),changed
 for n in names:
  old=json.loads(run('git','show',BASE+':'+rd+n));new=json.loads((ROOT/rd/n).read_text());assert all(new[k]==v for k,v in old.items());assert new['publication_allowed'] is False
 assert q['next_work'][0]['scope']=='Ruth 1–4'
 result={'status':'PASSED','base_commit':BASE,'scope':'All 21 chapters structurally scanned, all 618 English verses and apparatus read; 265 selected source/English comparisons reread','revision_audits':audits,'cumulative_coverage':{'chapters':237,'verses':7236},'judges_source_records':618,'all_source_records_bound_once':True,'structural_chapters':structural,'focused_rows':265,'focused_assertions':checks,'corrected_references':sorted(changedrefs),'prior_provenance_and_unaffected_work_preserved':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':51,'chapters_scanned':21,'selected_verses':265,'refined_verses':len(changes)},indent=2))
if __name__=='__main__':main()
