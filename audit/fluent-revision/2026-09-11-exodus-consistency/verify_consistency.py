"""Whole-book structure and source-bound selected concordances; no fidelity claim."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).resolve().parent
BASE='4ba664785f37da521607ff831ce9b3affd8376ce'

def main():
 p=argparse.ArgumentParser();p.add_argument('--exodus-source',required=True,type=Path);a=p.parse_args()
 data=a.exodus_source.read_bytes()
 assert hashlib.sha256(data).hexdigest()=='5e53e6841562f2c7af6756984a643b05628b29c39dc690d914dce6c70c6c38cb'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()=='9f1174a401696a1625e88c0d87ed2359889fb79e'
 raw={f'Exod {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',data.decode(),re.S) for c,v in [re.search('osisID="Exod\\.(\\d+)\\.(\\d+)"',s).groups()]}
 assert len(raw)==1213
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text())
 ledgers=[json.loads((ROOT/s['ledger']).read_text()) for s in q['completed_draft_scopes']]
 ex=[l for l in ledgers if l['source'].get('osis_book_id')=='Exod']
 bysource={v['source_reference']:v for l in ex for v in l['verses']}
 assert len(bysource)==sum(len(l['verses']) for l in ex)==1213 and set(bysource)==set(raw)
 for ref,v in bysource.items():assert v['source_verse_sha256']==hashlib.sha256(raw[ref].encode()).hexdigest()
 # Prior full audit evidence remains applicable: no chapter, comparator or ledger is changed.
 evidence=ROOT/'audit/fluent-revision/2026-09-11-exodus-35-40/verification.json'
 previous=json.loads(evidence.read_text());assert previous['status']=='PASSED' and len(previous['revision_audits'])==20
 for l in ledgers:
  for c in l['chapters']:
   assert hashlib.sha256((ROOT/c['path']).read_bytes()).hexdigest()==c['after_sha256']
 allowed={'audit/fluent-revision/WORK_QUEUE.json'}
 for cmd in [['git','diff','--name-only',BASE],['git','ls-files','--others','--exclude-standard']]:
  paths=subprocess.check_output(cmd,cwd=ROOT,text=True).splitlines()
  assert all(x in allowed or x.startswith(str(BATCH.relative_to(ROOT))+'/') for x in paths),paths
 structural=[]
 for l in ex:
  for c in l['chapters']:
   t=(ROOT/c['path']).read_text(); main=t.split('---',2)[2].split('## Notes')[0]
   labels=re.findall(r'^v(\d\d):',main,re.M)
   assert labels==[f'{n:02}' for n in range(1,c['verse_count']+1)]
   assert main.count('“')==main.count('”')
   inside=False
   for line in main.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['chapter'],line)
   assert not inside
   for part in main.split('</p>')[:-1]:assert not part.rstrip().endswith((',',':','—',';'))
   assert all(x in t for x in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   structural.append({'chapter':c['chapter'],'verses':len(labels),'sha256':c['after_sha256'],'headings':re.findall('^## (.*)$',main,re.M)})
 assert len(structural)==40
 concordance=json.loads((BATCH/'concordance.json').read_text())
 focused=json.loads((BATCH/'focused-comparisons.json').read_text())
 wanted=set(concordance['lemmas']);expected=set();serve=set();annotations={}
 for ref,xml in raw.items():
  e=E.fromstring(xml)
  ids={i for w in e.iter('w') for i in re.findall(r'\d+',w.get('lemma',''))}
  if ids&wanted:expected.add(ref)
  if '5647' in ids:serve.add(ref)
 assert {r['source_reference'] for r in concordance['rows']}==expected
 assert {r['source_reference'] for r in focused['rows'] if r['domain']=='serve/enslave'}==serve
 for r in concordance['rows']+focused['rows']:
  ref=r['source_reference'];v=bysource[ref]
  assert r['reference']==v['reference'] and r['fluent']==v['after'] and r['source_verse_sha256']==v['source_verse_sha256']
  notes=re.findall('<note.*?</note>',raw[ref],re.S)
  if notes:annotations[ref]=notes
 assert len(concordance['rows'])==62 and len(focused['rows'])==81
 public={v['reference'].replace('Exodus ',''):v['after'] for v in bysource.values()}
 pairs=[('25:10','37:1',['two and a half','a cubit and a half']),('25:17','37:6',['two and a half','a cubit and a half']),('25:23','37:10',['two cubits long','a cubit and a half high']),('25:39','37:24',['talent','gold']),('26:2','36:9',['twenty-eight','four cubits']),('26:8','36:15',['thirty','four cubits']),('26:16','36:21',['ten cubits','a cubit and a half']),('27:1','38:1',['five cubits','three cubits']),('30:2','37:25',['a cubit long','a cubit wide','two cubits high'])]
 for a,b,terms in pairs:
  assert all(x in public[a] and x in public[b] for x in terms),(a,b)
 assert all('covenant' in r['fluent'] for r in concordance['rows'] if any('covenant' in m['domains'] for m in r['matches']))
 assert all('faithful love' in r['fluent'] for r in concordance['rows'] if any('faithful love' in m['domains'] for m in r['matches']))
 # Honor and the rare male-denoting form are legitimate contextual exceptions to the concordance labels.
 assert 'honor' in public['28:2'] and 'honor' in public['28:40'] and 'firstborn male' in public['34:19']
 diff=subprocess.run(['git','diff','--check'],cwd=ROOT,text=True,capture_output=True,check=True)
 result={'status':'PASSED','base_commit':BASE,'scope':'Exodus 1–40 structure plus source-bound selected thematic comparison','structural_chapters':structural,'source_records':1213,'concordance_verses':62,'focused_verses':81,'unique_comparison_verses':len({r['source_reference'] for r in concordance['rows']+focused['rows']}),'command_fulfillment_dimension_pairs':pairs,'source_annotations_preserved':annotations,'prior_full_audit_evidence':str(evidence.relative_to(ROOT)),'prior_evidence_sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),'prior_twenty_ledger_audits_and_family_audit_still_applicable':True,'all_chapter_and_ledger_bytes_unchanged':True,'git_diff_check':diff.stdout+diff.stderr,'independent_editorial_review':'REVIEW_PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','source_records','concordance_verses','focused_verses','unique_comparison_verses','all_chapter_and_ledger_bytes_unchanged']},indent=2))
if __name__=='__main__':main()
