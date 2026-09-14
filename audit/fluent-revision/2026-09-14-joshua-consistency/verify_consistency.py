"""Whole-book structure and selected source comparisons, not independent editorial approval."""
from pathlib import Path
import argparse,json,re,hashlib,subprocess,sys,datetime,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='cc09484292131e85dd89e5835f700ee01e363cc2'
sys.path.insert(0,str(ROOT/'tools'));from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout.strip()
def main():
 p=argparse.ArgumentParser()
 for b in ['genesis','exodus','leviticus','numbers','deuteronomy','joshua','james']:p.add_argument('--'+b+'-source',type=Path,required=True)
 a=p.parse_args();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];deut=[];allpaths=set()
 for scope in q['completed_draft_scopes']:
  lp=scope['ledger'];l=json.loads((ROOT/lp).read_text());book=scope['scope'].split()[0]
  audits.append({'ledger':lp,**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',lp,'--source-text',str(getattr(a,book.lower()+'_source').resolve())))})
  for c in l['chapters']:assert c['path'] not in allpaths;allpaths.add(c['path'])
  if book=='Joshua':deut.append((lp,l))
 assert len(audits)==48 and len(allpaths)==216 and sum(x['verses'] for x in audits)==6618
 data=a.joshua_source.read_bytes();assert sha(data)=='d32a65fc6dc7207625c05ddcd133a0833a0c48e3d2343ba6fff4e01be9d5beaf'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()=='817453d2312e7cf359f6324e5456c5ba59c5bfa2'
 raw={f'Josh {c}:{v}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',data.decode(),re.S) for c,v in [re.search(r'osisID="Josh\.(\d+)\.(\d+)"',s).groups()]}
 public={v['reference']:v for lp,l in deut for v in l['verses']};refs=[v['source_reference'] for v in public.values()];assert len(deut)==3 and len(public)==len(refs)==len(set(refs))==len(raw)==658 and set(refs)==set(raw)
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
   cr=json.loads((ROOT/f'audit/exegetical-core/fluent-production/joshua/Joshua_{c["chapter"]:02}_review.json').read_text());assert cr['chapter_binding']==c and cr['publication_allowed'] is False
   structural.append({'chapter':c['chapter'],'verses':c['verse_count'],'sha256':sha(b),'headings':re.findall(r'^## (.*)$',m,re.M)})
 assert sorted(c['chapter'] for c in structural)==list(range(1,25))
 mapping={}
 fo=json.loads((BATCH/'focused-comparisons.json').read_text());changes=json.loads((BATCH/'changes.json').read_text());selected=fo['rows']
 assert len(selected)==len({x['reference'] for x in selected})==200
 for row in selected:
  v=public[row['reference']];assert row['fluent']==v['after'] and row['source_verse_sha256']==v['source_verse_sha256']==sha(raw[v['source_reference']].encode())
  e=E.fromstring(raw[v['source_reference']]);assert row['hebrew']==' '.join(''.join(w.itertext()) for w in e if w.tag=='w');assert row['annotations']==[E.tostring(w,encoding='unicode') for w in e if w.tag=='note']
 text=lambda ref:public['Joshua '+ref]['after']
 checks={'1:6': ['inheritance', 'swore'], '1:10': ['officers'], '3:2': ['officers'], '8:33': ['officers', 'Resident foreigners'], '11:23': ['land rested from war'], '14:15': ['land rested from war'], '13:1': ['still remains'], '13:14': ['offerings made by fire'], '13:33': ['LORD, the God of Israel, is their inheritance'], '18:7': ['priestly service'], '23:2': ['officers'], '24:1': ['officers'], '23:8': ['Cling'], '23:12': ['cling'], '21:45': ['Not one word failed'], '23:14': ['not one word has failed'], '6:21': ['men and women, young and old'], '7:24': ['sons and daughters'], '7:25': ['stoned him', 'burned them'], '17:3': ['Mahlah, Noah, Hoglah, Milcah, and Tirzah'], '19:22': ['Shahazimah'], '19:34': ['Judah'], '20:9': ['resident foreigners'], '22:31': ['from the LORD’s hand'], '24:19': ['cannot serve', 'will not forgive']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in text(ref).casefold(),(ref,term)
 changedrefs={x['reference'] for x in changes};assert changedrefs=={'Joshua 1:6','Joshua 23:2','Joshua 24:1'}
 for x in changes:
  b=subprocess.check_output(['git','show',BASE+':'+x['chapter_path']],cwd=ROOT);assert sha(b)==x['before_chapter_sha256'];assert verse_texts(b.decode())[x['reference'].split(':')[1].zfill(2)]==x['before'];assert public[x['reference']]['after']==x['after'];assert sha((ROOT/x['chapter_path']).read_bytes())==x['after_chapter_sha256']
 for lp,l in deut:
  old=json.loads(run('git','show',BASE+':'+lp));ov={v['reference']:v for v in old['verses']};assert l['base_commit']==old['base_commit'] and l['source']==old['source']
  for v in l['verses']:
   if v['reference'] not in changedrefs:assert v==ov[v['reference']]
   else:
    for k in ['before','source_reference','source_verse_sha256','tsw_comparator','delta']:assert v[k]==ov[v['reference']][k]
  for c in l['chapters']:
   if c['chapter'] not in [1,23,24]:assert c==next(x for x in old['chapters'] if x['chapter']==c['chapter'])
 rd='audit/exegetical-core/fluent-production/joshua/';names=['APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json','JOSHUA_FLUENT_BOOK_QA.json']
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}|{x['chapter_path'] for x in changes}|{x['verse_ledger'] for x in changes}|{rd+f'Joshua_{c:02}_review.json' for c in [1,23,24]}|{rd+n for n in names}
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or p.startswith(str(BATCH.relative_to(ROOT))+'/') for p in changed),changed
 for n in names:
  old=json.loads(run('git','show',BASE+':'+rd+n));new=json.loads((ROOT/rd/n).read_text());assert all(new[k]==v for k,v in old.items());assert new['publication_allowed'] is False
 assert q['next_work'][0]['scope']=='Judges 1–5'
 result={'status':'PASSED','base_commit':BASE,'scope':'All 24 chapters structurally scanned, all 658 English verses and apparatus read; 200 selected source/English comparisons reread','revision_audits':audits,'cumulative_coverage':{'chapters':216,'verses':6618},'joshua_source_records':658,'all_source_records_bound_once':True,'structural_chapters':structural,'focused_rows':200,'focused_assertions':checks,'corrected_references':sorted(changedrefs),'prior_provenance_and_unaffected_work_preserved':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':48,'chapters_scanned':24,'selected_verses':200,'refined_verses':len(changes)},indent=2))
if __name__=='__main__':main()
