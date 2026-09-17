#!/usr/bin/env python3
"""Package the completed audit without counting its corrections as new drafting."""
import argparse,hashlib,json,re,shutil,subprocess,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();P=a.parent.resolve();O=a.output.resolve()
 assert not O.exists();assert not git('status','--porcelain');O.mkdir(parents=True)
 pm=json.loads((P/'manifest.json').read_text())
 for name,meta in pm['files'].items():
  b=(P/name).read_bytes();assert len(b)==meta['bytes'] and sha(b)==meta['sha256'],name
 state=json.loads((P/'CONTINUATION.json').read_text());base=state['base_commit'];parent=state['head_commit'];head=git('rev-parse','HEAD');branch=git('branch','--show-current')
 assert parent=='dc09c88b7080e042e915474fe50e92f56adeee3c' and git('rev-parse','HEAD^')==parent
 ver=json.loads((A/'verification.json').read_text());assert ver['status']=='PASSED' and ver['base_commit']==parent
 files=git('diff','--name-only',base,head).splitlines()
 for name in files:
  src=R/name;assert src.is_file();dest=O/'repository'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 shutil.copytree(P/'sources',O/'sources');shutil.copytree(P/'provenance',O/'provenance')
 pp=O/'provenance/parent-version-97';pp.mkdir()
 for name in ['manifest.json','CONTINUATION.json','README.md','CONTINUATION_TASK.txt']:shutil.copy2(P/name,pp/name)
 subprocess.run(['git','bundle','create',str(O/'Fluent-Revision.bundle'),base+'..'+branch],cwd=R,check=True)
 bv=subprocess.run(['git','bundle','verify',str(O/'Fluent-Revision.bundle')],cwd=R,capture_output=True,text=True);assert bv.returncode==0
 hist=git('log','--reverse','--format=%H %s',base+'..HEAD').splitlines();assert hist[:-1]==json.loads((P/'history.json').read_text())['commits_oldest_first']
 dump(O/'history.json',dict(base_commit=base,head_commit=head,commits_oldest_first=hist,bundle_verification=bv.stdout+bv.stderr))
 with (O/'Fluent-combined.patch').open('wb') as f:subprocess.run(['git','diff','--binary',base,head],cwd=R,stdout=f,check=True)
 q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());changes=json.loads((A/'corrections.json').read_text());paths={c['path'] for c in changes['chapters']}
 chapters=[c for s in q['completed_draft_scopes'] for c in json.loads((R/s['ledger']).read_text())['chapters']]
 assert len(chapters)==len({c['path'] for c in chapters})==1189 and sum(c['verse_count'] for c in chapters)==31083
 order='genesis exodus leviticus numbers deuteronomy joshua judges ruth 1samuel 2samuel 1kings 2kings 1chronicles 2chronicles ezra nehemiah esther job psalms proverbs ecclesiastes songofsongs isaiah jeremiah lamentations ezekiel daniel hosea joel amos obadiah jonah micah nahum habakkuk zephaniah haggai zechariah malachi matthew mark luke john acts romans 1corinthians 2corinthians galatians ephesians philippians colossians 1thessalonians 2thessalonians 1timothy 2timothy titus philemon hebrews james 1peter 2peter 1john 2john 3john jude revelation'.split()
 chapters.sort(key=lambda c:(order.index(Path(c['path']).parent.name),c['chapter']))
 header='Editorial draft. Independent editorial review and reader testing pending. Publication not allowed.\n'
 allreader=['# Fluent: cumulative revised reader\n\n1,189 chapters · 31,083 public verse records\n\n'+header];corrected=['# Fluent: chapters corrected during the full-corpus audit\n\n31 chapter files; two Scripture verses refined.\n\n'+header];active=['# Fluent: final drafting block\n\n32 chapters; drafting complete. Current audit corrections incorporated.\n\n'+header]
 ranges=json.loads((R/'audit/fluent-revision/2026-09-17-revelation-1-22/config.json').read_text())['active_block_ranges'];active_count=0
 for ch in chapters:
  b=(R/ch['path']).read_bytes();assert sha(b)==ch['after_sha256'];t=b.decode();name=re.search(r'^book: (.+)$',t,re.M)[1];body=t.split('---',2)[2].strip();lines=[]
  for line in body.splitlines():
   if line in ['<p>','</p>']:lines.append('');continue
   line='#'+line if line.startswith('## ') else re.sub(r'^v(\d+):',r'**\1**',line)
   lines.append(line+'  ' if line.strip() and not line.startswith('#') else line)
  rendered='\n## '+name+' '+str(ch['chapter'])+'\n\n'+'\n'.join(lines)+'\n';allreader.append(rendered)
  if ch['path'] in paths:corrected.append(rendered)
  if any(Path(ch['path']).parent.name==x['slug'] and x['start']<=ch['chapter']<=x['end'] for x in ranges):active.append(rendered);active_count+=1
 assert active_count==32
 for fn,lines in [('Fluent-Reader.md',allreader),('Fluent-Audit-Corrected-Chapters.md',corrected),('Fluent-Active-Block.md',active)]: (O/fn).write_text('\n'.join(lines))
 shutil.copy2(A/'Fluent-Translation-Audit.md',O/'Fluent-Translation-Audit.md')
 state.update(head_commit=head,branch=branch,parent_checkpoint_head=parent,parent_checkpoint_library_version=97,local_checkout=str(R),next_work=q['next_work'],completed=q['completed_draft_scopes'],latest_batch='Full-corpus audit completed with open editorial findings. 31 chapters corrected; two Scripture verses refined. No new chapters drafted. Fluent is substantially distinct from TSW; full editorial compliance is not yet certified.',latest_verification='repository/'+str(A.relative_to(R))+'/verification.json',latest_audit='repository/'+str(A.relative_to(R))+'/Fluent-Translation-Audit.md',editorial_status='REVIEW_PENDING',publication_allowed=False)
 dump(O/'CONTINUATION.json',state)
 instructions=(P/'CONTINUATION_TASK.txt').read_text()
 instructions=re.sub(r'Current head: .*?; parent: .*?;',f'Current head: {head}; parent: {parent};',instructions)
 instructions=re.sub(r'This checkpoint follows version \d+', 'This checkpoint follows version 97',instructions)
 instructions='LATEST WORK: Full-corpus audit, not another drafting batch. Read Fluent-Translation-Audit.md and repository/audit/fluent-revision/2026-09-17-full-corpus-audit/remaining-actions.json first. The draft automation is paused; do not restart it as an audit continuation. Draft counts remain 1189 chapters and 31083 public verse records. All editorial/independent-review gates remain open.\n\n'+instructions
 (O/'CONTINUATION_TASK.txt').write_text(instructions)
 (O/'README.md').write_text(f'''# Fluent audit checkpoint

Draft coverage remains 1,189 chapters and 31,083 public verse records in 145 ledgers. This checkpoint adds a full-corpus audit and corrections to 31 chapters, including two Scripture verses. It does not add new drafting coverage or grant editorial approval.

Read Fluent-Translation-Audit.md for the qualified judgment, corrections and remaining work. Fluent is substantially distinct from TSW, but full editorial compliance, independent review, reader testing and Companion reconciliation remain pending. Publication is not allowed. TSW and Companion are unchanged.

Head: {head}. Parent: {parent}. Required repository base: {base}. Branch: {branch}. This bundle preserves {len(hist)} revision commits. Prior checkpoint evidence is retained under provenance/parent-version-97.

Verify manifest.json, restore the repository base plus Fluent-Revision.bundle, and run `python3 audit/fluent-revision/2026-09-17-full-corpus-audit/verify_audit.py --sources /path/to/checkpoint/sources`. Historical checkpoint verifiers belong to their historical commits. Read CONTINUATION.json and CONTINUATION_TASK.txt before further work. Always replace the same canonical checkpoint with the current version guard. No remote GitHub write or public deployment was performed.
''')
 m=dict(base_commit=base,head_commit=head,branch=branch,chapters=1189,verses=31083,repository_file_count=len(files),files={})
 for p in sorted(O.rglob('*')):
  if p.is_file() and not p.name.endswith('.lock'):
   b=p.read_bytes();m['files'][str(p.relative_to(O))]=dict(bytes=len(b),sha256=sha(b))
 dump(O/'manifest.json',m);out=O.parent/'Fluent-Revision-Checkpoint.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name in sorted([*m['files'],'manifest.json']):z.write(O/name,name)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None and len(z.namelist())==len(m['files'])+1
  for name,meta in m['files'].items():
   b=z.read(name);assert len(b)==meta['bytes'] and sha(b)==meta['sha256']
 assert not git('status','--porcelain')
 print(json.dumps(dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out.read_bytes()),head=head,commits=len(hist),manifest_entries=len(m['files']),expected_current_version=97)))
if __name__=='__main__':main()
