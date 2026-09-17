#!/usr/bin/env python3
"""Package editorial checkpoint 101, preserving unchanged draft coverage."""
import argparse,hashlib,json,re,shutil,subprocess,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
PARENT='f59146de202775e61a608552e8564bddd46c4599';VERSION=100
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();P=a.parent.resolve();O=a.output.resolve()
 assert not O.exists() and not git('status','--porcelain')
 pm=json.loads((P/'manifest.json').read_text())
 for name,meta in pm['files'].items():
  b=(P/name).read_bytes();assert len(b)==meta['bytes'] and sha(b)==meta['sha256'],name
 state=json.loads((P/'CONTINUATION.json').read_text());base=state['base_commit'];parent=state['head_commit'];head=git('rev-parse','HEAD');branch=git('branch','--show-current');assert parent==PARENT and git('rev-parse','HEAD^')==parent
 ver=json.loads((A/'verification.json').read_text());assert ver['status']=='PASSED' and ver['base_commit']==parent and not ver['publication_allowed']
 O.mkdir(parents=True);files=git('diff','--name-only',base,head).splitlines()
 for name in files:
  src=R/name;assert src.is_file();dest=O/'repository'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 shutil.copytree(P/'sources',O/'sources');shutil.copytree(P/'provenance',O/'provenance');pp=O/f'provenance/parent-version-{VERSION}';pp.mkdir()
 for name in ['manifest.json','CONTINUATION.json','README.md','CONTINUATION_TASK.txt']:shutil.copy2(P/name,pp/name)
 subprocess.run(['git','bundle','create',str(O/'Fluent-Revision.bundle'),base+'..'+branch],cwd=R,check=True)
 bv=subprocess.run(['git','bundle','verify',str(O/'Fluent-Revision.bundle')],cwd=R,capture_output=True,text=True);assert bv.returncode==0
 hist=git('log','--reverse','--format=%H %s',base+'..HEAD').splitlines();assert hist[:-1]==json.loads((P/'history.json').read_text())['commits_oldest_first'];dump(O/'history.json',dict(base_commit=base,head_commit=head,commits_oldest_first=hist,bundle_verification=bv.stdout+bv.stderr))
 with (O/'Fluent-combined.patch').open('wb') as f:subprocess.run(['git','diff','--binary',base,head],cwd=R,stdout=f,check=True)
 q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());chapters=[c for s in q['completed_draft_scopes'] for c in json.loads((R/s['ledger']).read_text())['chapters']]
 assert len(chapters)==len({c['path'] for c in chapters})==1189 and sum(c['verse_count'] for c in chapters)==31083
 order='genesis exodus leviticus numbers deuteronomy joshua judges ruth 1samuel 2samuel 1kings 2kings 1chronicles 2chronicles ezra nehemiah esther job psalms proverbs ecclesiastes songofsongs isaiah jeremiah lamentations ezekiel daniel hosea joel amos obadiah jonah micah nahum habakkuk zephaniah haggai zechariah malachi matthew mark luke john acts romans 1corinthians 2corinthians galatians ephesians philippians colossians 1thessalonians 2thessalonians 1timothy 2timothy titus philemon hebrews james 1peter 2peter 1john 2john 3john jude revelation'.split();chapters.sort(key=lambda c:(order.index(Path(c['path']).parent.name),c['chapter']))
 header='Editorial draft. Independent editorial review and reader testing pending. Publication not allowed.\n'
 allreader=['# Fluent: cumulative revised reader\n\n1,189 chapters · 31,083 public verse records\n\n'+header];genesis=['# Fluent: Genesis 1–50\n\nSource self-review now covers Genesis 1–50; open issues, whole-book reading and independent review remain pending.\n\n'+header];gcount=0
 for ch in chapters:
  b=(R/ch['path']).read_bytes();assert sha(b)==ch['after_sha256'];t=b.decode();name=re.search(r'^book: (.+)$',t,re.M)[1];body=t.split('---',2)[2].strip();lines=[]
  for line in body.splitlines():
   if line in ['<p>','</p>']:lines.append('');continue
   line='#'+line if line.startswith('## ') else re.sub(r'^v(\d+):',r'**\1**',line)
   lines.append(line+'  ' if line.strip() and not line.startswith('#') else line)
  rendered='\n## '+name+' '+str(ch['chapter'])+'\n\n'+'\n'.join(lines)+'\n';allreader.append(rendered)
  if Path(ch['path']).parent.name=='genesis':genesis.append(rendered);gcount+=1
 assert gcount==50
 (O/'Fluent-Reader.md').write_text('\n'.join(allreader));(O/'Fluent-Genesis-Reader.md').write_text('\n'.join(genesis))
 for name in ['FLUENT_EDITORIAL_STANDARD.md','FLUENT_READER_GUIDANCE.md','EDITORIAL_PROGRESS.json']:shutil.copy2(R/name,O/name)
 shutil.copy2(A/'Genesis-Source-Review.md',O/'Genesis-Source-Review.md');shutil.copy2(P/'Genesis-Editorial-Review.md',O/'Genesis-Editorial-Review.md');shutil.copy2(P/'Fluent-Translation-Audit.md',O/'Fluent-Translation-Audit.md')
 # The prior audit remains a dated historical report, not a recalculated apparatus screen.
 state.update(head_commit=head,branch=branch,parent_checkpoint_head=parent,parent_checkpoint_library_version=VERSION,local_checkout=str(R),next_work=q['next_work'],completed=q['completed_draft_scopes'],latest_batch='Genesis 11–50 fresh source self-review: 40 chapters and 1266 verses compared; nine Scripture corrections and two note edits in seven chapters. Cumulative Genesis source self-review covers 50 chapters and 1533 verses. Complete remaining continuous reading, specialist questions and editorial criteria before closing the block.',latest_verification='repository/'+str(A.relative_to(R))+'/verification.json',latest_audit='repository/'+str(A.relative_to(R))+'/Genesis-Source-Review.md',editorial_progress='repository/EDITORIAL_PROGRESS.json',editorial_status='REVIEW_PENDING',publication_allowed=False)
 dump(O/'CONTINUATION.json',state)
 instructions=(P/'CONTINUATION_TASK.txt').read_text();instructions=re.sub(r'Current head: .*?; parent: .*?;',f'Current head: {head}; parent: {parent};',instructions);instructions=re.sub(r'This checkpoint follows version \d+',f'This checkpoint follows version {VERSION}',instructions)
 instructions=f'''LATEST WORK: Genesis 11–50 source comparison, 40 chapters and 1266 verses; nine Scripture corrections and two note edits in seven chapters. Combined with the earlier 1–10 pass, all 50 Genesis chapters and 1533 public verse records have fresh source self-review. The previously targeted 15 verses are included, not additional. Read Genesis-Source-Review.md and EDITORIAL_PROGRESS.json. Complete continuous whole-book reading, G01–G20 questions and remaining editorial criteria; source self-review does not close the block or confer independent approval. Routine continuation needs no approval. The drafting automation remains paused; do not retry denied remote GitHub writes. Draft counts remain 1189 chapters and 31083 public verse records. TSW and Companion are unchanged. Independent review and final approval remain pending.

Current head: {head}; parent: {parent}; this checkpoint follows version {VERSION}.

HISTORICAL CONTINUATION INSTRUCTIONS BELOW; current progress above and current JSON take precedence.

'''+instructions
 (O/'CONTINUATION_TASK.txt').write_text(instructions)
 (O/'README.md').write_text(f'''# Fluent source-review checkpoint

This batch compared Genesis 11–50: 40 chapters and 1,266 verses. Nine Scripture verses and two notes were corrected in seven chapter files. Combined with the earlier pass, all 50 Genesis chapters and 1,533 public verses have fresh source self-review. This is not independent philological certification or final editorial approval.

Read Genesis-Source-Review.md and EDITORIAL_PROGRESS.json for exact completed work, G01–G20 issues, and next actions. Complete continuous whole-book reading and remaining semantic, lexical, formatting and editorial questions before closing the Genesis block. Routine batch continuation already has authorization.

Fluent-Genesis-Reader.md and Fluent-Reader.md contain current wording. The preserved Genesis-Editorial-Review.md and Fluent-Translation-Audit.md are historical reports, not recalculated statistics. Prior source-review reports and their exact evidence remain in the repository history and cumulative repository files.

Draft coverage remains 1,189 chapters and 31,083 public verse records in 145 ledgers. Independent language review, reader testing, Companion reconciliation and final editorial approval remain pending. Publication is not allowed. TSW and Companion are unchanged.

Head: {head}. Parent: {parent}. Required repository base: {base}. Branch: {branch}. This bundle preserves {len(hist)} revision commits. Parent evidence is under provenance/parent-version-{VERSION}.

Verify manifest.json, restore the repository base plus Fluent-Revision.bundle, and run `python3 audit/fluent-revision/2026-09-17-genesis-source-11-50/verify_review.py --sources /path/to/checkpoint/sources`. Historical verifiers belong to their historical commits. Read CONTINUATION.json and CONTINUATION_TASK.txt. Replace the same canonical checkpoint with the current version guard. No remote GitHub write or public deployment was performed.
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
 assert not git('status','--porcelain');print(json.dumps(dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out.read_bytes()),head=head,commits=len(hist),manifest_entries=len(m['files']),expected_current_version=VERSION)))
if __name__=='__main__':main()
