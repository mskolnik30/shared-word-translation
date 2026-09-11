"""Whole-book structure and selected source-bound comparisons; not scholarly approval."""
from pathlib import Path
import argparse,hashlib,json,re,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--leviticus-source',type=Path,required=True);a=p.parse_args();data=a.leviticus_source.read_bytes()
 assert hashlib.sha256(data).hexdigest()=='75a4a96e7b64f2145bede15ae37ac8a0b301f110d5d6b2daf9d8048adebbd2e6'
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()=='6025e0713ccfc79de0c90cb92ed0e8c0062d2614'
 raw={f'Lev {int(c)}:{int(v)}':s for s in re.findall(r'<verse\b[^>]*>.*?</verse>',data.decode(),re.S) for c,v in [re.search(r'osisID="Lev\.(\d+)\.(\d+)"',s).groups()]}
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());ledgers=[json.loads((ROOT/s['ledger']).read_text()) for s in q['completed_draft_scopes'] if s['scope'].startswith('Leviticus')]
 assert len(ledgers)==10
 bysource={v['source_reference']:v for l in ledgers for v in l['verses']};public={v['reference'].replace('Leviticus ',''):v for v in bysource.values()}
 assert len(bysource)==sum(len(l['verses']) for l in ledgers)==len(raw)==859 and set(bysource)==set(raw)
 for ref,v in bysource.items():assert hashlib.sha256(raw[ref].encode()).hexdigest()==v['source_verse_sha256']
 assert [public[f'6:{i}']['source_reference'] for i in range(1,8)]==[f'Lev 5:{i}' for i in range(20,27)]
 assert [public[f'6:{i}']['source_reference'] for i in range(8,31)]==[f'Lev 6:{i}' for i in range(1,24)]
 structural=[]
 for l in ledgers:
  for c in l['chapters']:
   b=(ROOT/c['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==c['after_sha256'];t=b.decode();m=t.split('---',2)[2].split('## Notes')[0]
   assert re.findall(r'^v(\d\d):',m,re.M)==[f'{i:02}' for i in range(1,c['verse_count']+1)]
   assert m.count('“')==m.count('”')
   inside=False
   for line in m.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['chapter'],line)
   assert not inside
   for part in m.split('</p>')[:-1]:assert not part.rstrip().endswith((',',':',';','—'))
   assert all(s in t for s in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   structural.append({'chapter':c['chapter'],'verse_count':c['verse_count'],'sha256':c['after_sha256']})
 assert {c['chapter'] for c in structural}==set(range(1,28)) and len(structural)==27
 co=json.loads((BATCH/'concordance.json').read_text());fo=json.loads((BATCH/'focused-comparisons.json').read_text());wanted=set(co['lemmas']);expected=set()
 for ref,s in raw.items():
  ids={i for w in E.fromstring(s).findall('w') for i in re.findall(r'\d+',w.get('lemma',''))}
  if ids&wanted:expected.add(ref)
 assert {x['source_reference'] for x in co['rows']}==expected and len(co['rows'])==56
 assert len(fo['rows'])==77
 for row in co['rows']+fo['rows']:
  v=bysource[row['source_reference']]
  assert row['reference']==v['reference'] and row['fluent']==v['after'] and row['source_verse_sha256']==v['source_verse_sha256']
 for row in co['rows']:
  for match in row['matches']:
   if match['domain'] in ['covenant','Sabbath','redeem','Jubilee']:assert match['domain'].casefold() in row['fluent'].casefold()
   if match['domain']=='devoted/ban':assert any(s in row['fluent'] for s in ['devoted beyond recall','such a ban'])
 text=lambda r:public[r]['after'].casefold()
 assert all(s in text('10:10') for s in ['holy','common','unclean','clean'])
 assert all(s in text('21:22') for s in ['may eat','most holy','holy offerings'])
 assert 'outside the priestly household' in text('22:10') and 'buys as a slave' in text('22:11')
 assert all('leaven' in text(r) for r in ['2:11','23:17'])
 assert 'none of it may be left until morning' in text('7:15') and 'next day' in text('7:16') and 'same day' in text('22:30')
 assert 'each loaf' in text('24:5') and 'each loaf' not in text('23:17')
 assert all('deny yourselves' in text(r) for r in ['16:29','16:31','23:27','23:32'])
 assert 'cut off' in text('23:29') and 'i will destroy' in text('23:30')
 assert 'my slaves' in text('25:42') and 'my slaves' in text('25:55') and 'their slaves' in text('26:13')
 assert 'slaves permanently' in text('25:46') and 'he and his children' in text('25:54')
 assert 'not be released' in text('25:30') and 'will be released' in text('25:31')
 assert 'always have the right to redeem' in text('25:32') and 'must not be sold' in text('25:34')
 assert 'priest’s holding' in text('27:21') and 'person he bought it from' in text('27:24')
 assert 'put to death' in text('27:29') and 'assessed value of a person' in text('27:2')
 epath=ROOT/'audit/fluent-revision/2026-09-11-leviticus-26-27/verification.json';ev=json.loads(epath.read_text());assert ev['status']=='PASSED' and len(ev['revision_audits'])==30
 result={'status':'PASSED','scope':'Leviticus 1–27: complete structural scan and selected thematic authoring self-check','source_records':859,'structural_chapters':structural,'concordance_verses':56,'focused_comparison_rows':77,'unique_selected_verses':len({x['source_reference'] for x in co['rows']+fo['rows']}),'all_source_records_bound_once':True,'public_chapter_6_shift_verified':True,'prior_chapter_texts_and_bindings_unchanged':True,'current_draft_audit_evidence':str(epath.relative_to(ROOT)),'current_draft_evidence_sha256':hashlib.sha256(epath.read_bytes()).hexdigest(),'style_review_pending':['Sabbath/sabbath capitalization varies between earlier and later batches; this scan verifies retained terminology without normalizing typography.'],'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','source_records','concordance_verses','focused_comparison_rows','unique_selected_verses']},indent=2))
if __name__=='__main__':main()
