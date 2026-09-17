#!/usr/bin/env python3
"""Verify completion of source-bound drafting; no independent editorial approval."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
A=Path(__file__).resolve().parent
PARENT='2b1ff481e1e390d6ddbcaf7ca03aa19bfcb62975'
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',PARENT+':'+p],cwd=R)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-directory',required=True,type=Path);ap.add_argument('--bind-focused-records',action='store_true');a=ap.parse_args()
 sys.path.insert(0,str(R/'tools'));from audit_fluent_revision import audit
 qpath='audit/fluent-revision/WORK_QUEUE.json';q=json.loads((R/qpath).read_text());oq=json.loads(old(qpath));cfg=json.loads((A/'config.json').read_text());lp=A/'revelation-verse-review.json';l=json.loads(lp.read_text());sb=(a.source_directory/cfg['source_filename']).read_bytes()
 assert len(oq['completed_draft_scopes'])==144 and len(q['completed_draft_scopes'])==145
 assert q['completed_draft_scopes'][:-1]==oq['completed_draft_scopes']
 assert q['completed_fifty_chapter_blocks']==oq['completed_fifty_chapter_blocks']
 assert q['next_work'][2:]==oq['next_work'][1:]
 assert sha(sb)==cfg['source']['sha256']==l['source']['sha256']
 assert hashlib.sha1(b'blob '+str(len(sb)).encode()+b'\0'+sb).hexdigest()==cfg['source']['git_blob_sha']
 errors=audit(R,l,sb);assert not errors,errors
 prior_paths=set();prior_verses=0
 for scope in oq['completed_draft_scopes']:
  p=scope['ledger'];assert (R/p).read_bytes()==old(p),p
  prior=json.loads((R/p).read_text())
  for c in prior['chapters']:
   p=c['path'];assert p not in prior_paths;prior_paths.add(p);prior_verses+=c['verse_count'];assert (R/p).read_bytes()==old(p),p
   assert sha((R/p).read_bytes())==c['after_sha256']
   assert sha((R/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
 assert (len(prior_paths),prior_verses)==(1167,30679)
 raw=dict(x.split('\t',1) for x in sb.decode().splitlines() if '\t' in x)
 refs=[s['source_reference'] for v in l['verses'] for s in v.get('source_segments',[v])]
 assert len(refs)==len(set(refs))==405 and set(refs)==set(raw)
 assert len(l['verses'])==404 and len(l['chapters'])==22
 merged=[v for v in l['verses'] if 'source_segments' in v];assert len(merged)==1 and merged[0]['reference']=='Revelation 13:1'
 assert [s['source_reference'] for s in merged[0]['source_segments']]==['Rev 12:18','Rev 13:1']
 assert merged[0]['source_mapping_reason']==cfg['source_merge_reasons']['13:1']
 original=(A/'source-first-authoring-input.tsv').read_text().splitlines();assert len(original)==405
 authored=(A/'authoring-input.tsv').read_text().splitlines();assert len(authored)==404 and all(len(x.split('|'))==3 for x in authored)
 reread=A/'authoring-reread.md';assert 'not human or independent scholarly review' in reread.read_text()
 focus=[{**v,'exact_source_records':[{'reference':s['source_reference'],'payload':raw[s['source_reference']]} for s in v.get('source_segments',[v])]} for v in l['verses'] if v['delta']=='F3']
 assert len(focus)==111
 record=dict(status='AUTHORING_REREAD_COMPLETED',review_type='Drafting-assistant bilingual self-reread; not human or independent scholarly review',authoring_record_sha256=sha(reread.read_bytes()),rows=focus)
 fp=A/'focused-comparisons.json'
 if a.bind_focused_records:dump(fp,record)
 else:assert json.loads(fp.read_text())==record
 allowed={qpath,'tools/build_fluent_mark_checkpoint.py','tools/package_fluent_checkpoint.py'}
 allowed.update(str(p.relative_to(R)) for p in A.rglob('*') if p.is_file())
 new_paths=set()
 for c in l['chapters']:
  p=c['path'];assert p not in prior_paths;new_paths.add(p);allowed.add(p)
  review='audit/exegetical-core/fluent-production/revelation/'+Path(p).name.replace('.md','_review.json');allowed.add(review)
  d=json.loads((R/review).read_text());assert d['chapter_binding']==c and d['status']=='REVIEW_PENDING' and not d['publication_allowed']
  before=old(p).decode();after=(R/p).read_text()
  assert all(line in after.split('---',2)[1].splitlines() for line in before.split('---',2)[1].splitlines() if line.strip())
  assert re.findall(r'^## .+$',before.split('## Notes')[0],re.M)==re.findall(r'^## .+$',after.split('## Notes')[0],re.M)
  assert re.findall(r'^v\d+:',before.split('## Notes')[0],re.M)==re.findall(r'^v\d+:',after.split('## Notes')[0],re.M)
 for fn in cfg['book_record_files']:
  p='audit/exegetical-core/fluent-production/revelation/'+fn;allowed.add(p);cur=json.loads((R/p).read_text());prev=json.loads(old(p))
  assert cur['source']==prev['source'] and cur['status']=='REVIEW_PENDING' and not cur['publication_allowed']
  assert cur['revision_batches'][:-1]==prev.get('revision_batches',[])
  for key in ['public_verse_slots','pinned_source_record_count','summary','curated_f3_decisions','deployment','deployment_audit']:
   if key in prev:assert cur[key]==prev[key],key
  if 'entries' in prev:
   assert len(cur['entries'])==len(prev['entries'])
   for x,y in zip(cur['entries'],prev['entries']):assert all(x[k]==v for k,v in y.items()) and x['status']=='SUPERSEDED'
 after={v['reference'].split()[1]:v['after'] for v in l['verses']}
 checks={
 'opening_variants':'freed us' in after['1:5'] and 'a kingdom' in after['1:6'],
 'specific_harm':'kill her children' in after['2:23'] and 'kidneys and hearts' in after['2:23'] and 'vomit' in after['3:16'],
 'lamb_reign':'they reign' in after['5:10'] and 'slaughtered' in after['5:6'],
 'tribal_names':all(x in ' '.join(after[f'7:{v}'] for v in range(5,9)) for x in ['Judah','Reuben','Gad','Asher','Naphtali','Manasseh','Simeon','Levi','Issachar','Zebulun','Joseph','Benjamin']),
 'tribal_numbers':sum(after[f'7:{v}'].count('12,000') for v in range(5,9))==12 and '144,000' in after['7:4'],
 'trumpet_variants':'eagle' in after['8:13'] and 'four' not in after['9:13'] and 'two hundred million' in after['9:16'],
 'witness_numbers':'1,260' in after['11:3'] and 'seven thousand' in after['11:13'] and 'who is coming' not in after['11:17'],
 'dragon_boundary':after['13:1'].startswith('He stood on the sand of the sea. I saw a beast'),
 'beast_variants':'is to be killed' in after['13:10'] and 'six hundred sixty-six' in after['13:18'],
 'specific_gender':'a son, a male child' in after['12:5'] and 'women' in after['14:4'] and 'virgins' in after['14:4'],
 'songs_and_speakers':'King of the ages' in after['15:3'] and 'holy one' in after['16:5'] and 'altar say' in after['16:7'],
 'babylon_variants':'have fallen' in after['18:3'] and 'human lives' in after['18:13'] and 'they will never find' in after['18:14'],
 'final_judgment':'we will give' in after['19:7'] and 'dipped in blood' in after['19:13'] and 'thrown alive' in after['19:20'] and 'beheaded' in after['20:4'],
 'new_city':'his peoples' in after['21:3'] and '12,000 stadia' in after['21:16'] and '144 cubits' in after['21:17'],
 'twelve_stones':all(x in after['21:19']+' '+after['21:20'] for x in ['jasper','sapphire','chalcedony','emerald','sardonyx','carnelian','chrysolite','beryl','topaz','chrysoprase','jacinth','amethyst']),
 'ending_variants':'wash their robes' in after['22:14'] and 'tree of life' in after['22:19'] and after['22:21']=='The grace of the Lord Jesus be with all.',
 }
 assert all(checks.values()),[k for k,v in checks.items() if not v]
 chapters=[c for s in q['completed_draft_scopes'] for c in json.loads((R/s['ledger']).read_text())['chapters']]
 assert len(chapters)==len({c['path'] for c in chapters})==1189 and sum(c['verse_count'] for c in chapters)==31083
 assert q['draft_status']=='DRAFT_COMPLETE' and q['draft_coverage']==dict(chapters=1189,verses=31083,ledgers=145)
 block=q['active_fifty_chapter_block'];assert (block['status'],block['chapters_target'],block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==('DRAFT_COMPLETED',32,32,0,602)
 changed=subprocess.check_output(['git','diff','--name-only',PARENT],cwd=R).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R).decode().splitlines()
 for p in changed:
  if p=='.fluent-revision-writer.lock':continue
  assert p in allowed,p
 assert not subprocess.check_output(['git','diff',PARENT,'--','books','companions'],cwd=R).strip()
 subprocess.run(['git','diff','--check',PARENT],cwd=R,check=True)
 family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=R).decode()
 result=dict(status='PASSED',qa_scope='structural',parent_commit=PARENT,new_chapters=22,new_verses=404,unique_original_source_records=405,cumulative_coverage=dict(ledgers=145,chapters=1189,verses=31083),prior_preservation=dict(ledgers_byte_identical=144,chapters_byte_identical=1167,verses=30679,tsw_and_companion_unchanged=True),source_binding_audits=[dict(ledger=str(lp.relative_to(R)),status='PASSED',public_verses=404,unique_source_records=405)],source_sensitive_checks=checks,focused_authoring_reread_count=111,translation_family=family,active_fifty_chapter_block=block,draft_status='DRAFT_COMPLETE',independent_editorial_review='REVIEW_PENDING',whole_book_reviews='PENDING; all prior queue entries retained and Revelation added',reader_testing='PENDING',companion_reconciliation='PENDING; no quotations or bindings changed',publication_allowed=False)
 dump(A/'verification.json',result)
 dump(A/'block-boundary-verification.json',dict(status='PASSED',draft_status='DRAFT_COMPLETE',final_block_chapters=32,final_block_public_verses=602,final_block_source_records=603,cumulative_coverage=result['cumulative_coverage'],evidence=['audit/fluent-revision/2026-09-17-jude-1-1/verification.json',str((A/'verification.json').relative_to(R))],publication_allowed=False,independent_editorial_review='REVIEW_PENDING'))
 print(json.dumps(dict(status='PASSED',new_chapters=22,new_verses=404,source_records=405,coverage=result['cumulative_coverage'],focused_rereads=111,draft_status='DRAFT_COMPLETE')))
if __name__=='__main__':main()
