#!/usr/bin/env python3
"""Package a verified clean revision with cumulative Git history and pinned sources.

No upload is performed here. The canonical replacement must separately use its
exact expected Library version guard. Resolve the current file on every run.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=R).decode().strip()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent-checkpoint',type=Path,required=True)
    ap.add_argument('--scope-directory',type=Path,required=True)
    ap.add_argument('--output-directory',type=Path,required=True)
    a=ap.parse_args(); P=a.parent_checkpoint.resolve(); A=a.scope_directory.resolve(); O=a.output_directory.resolve()
    assert not O.exists(),'Use a fresh packaging directory to exclude stale files.'
    O.mkdir(parents=True)
    pm=json.loads((P/'manifest.json').read_text())
    for f,v in pm['files'].items():
        b=(P/f).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256'],f
    state=json.loads((P/'CONTINUATION.json').read_text()); cfg=json.loads((A/'config.json').read_text())
    base=state['base_commit']; parent=state['head_commit'];head=git('rev-parse','HEAD');branch=git('branch','--show-current')
    assert parent==cfg['parent_commit'] and git('rev-parse','HEAD^')==parent
    assert not git('status','--porcelain'),'Commit verified work before packaging.'
    hist=git('log','--reverse','--format=%H %s',base+'..HEAD').splitlines()
    assert hist[:-1]==json.loads((P/'history.json').read_text())['commits_oldest_first']
    files=git('diff','--name-only',base,head).splitlines()
    for f in files:
        src=R/f;assert src.is_file(),f
        dest=O/'repository'/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    shutil.copytree(P/'sources',O/'sources')
    if (P/'provenance').exists():shutil.copytree(P/'provenance',O/'provenance')
    prov=O/'provenance'/('parent-version-'+str(cfg['parent_library_version']))
    prov.mkdir(parents=True,exist_ok=True)
    for name in ['manifest.json','CONTINUATION.json','README.md','CONTINUATION_TASK.txt']:
        if (P/name).exists():shutil.copy2(P/name,prov/name)
    bundle=O/'Fluent-Revision.bundle'
    subprocess.run(['git','bundle','create',str(bundle),base+'..'+branch],cwd=R,check=True)
    v=subprocess.run(['git','bundle','verify',str(bundle)],cwd=R,capture_output=True,text=True)
    assert v.returncode==0,v.stderr
    dump(O/'history.json',dict(base_commit=base,head_commit=head,commits_oldest_first=hist,bundle_verification=v.stdout+v.stderr))
    with (O/'Fluent-combined.patch').open('wb') as f:subprocess.run(['git','diff','--binary',base,head],cwd=R,stdout=f,check=True)
    q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text())
    ledgers=[json.loads((R/x['ledger']).read_text()) for x in q['completed_draft_scopes']]
    chapters=[c for l in ledgers for c in l['chapters']]
    assert len({c['path'] for c in chapters})==len(chapters)
    counts=dict(chapters=len(chapters),verses=sum(c['verse_count'] for c in chapters))
    verification=json.loads((A/'verification.json').read_text())
    assert verification['status']=='PASSED' and all(verification['cumulative_coverage'][k]==v for k,v in counts.items())
    block=q['active_fifty_chapter_block']; n=len(cfg['chapters']); nv=cfg['expected_verses']; rel=str(A.relative_to(R))
    state.update(head_commit=head,branch=branch,completed=q['completed_draft_scopes'],counts=counts,
      next_work=q['next_work'],local_checkout=str(R),parent_checkpoint_head=parent,
      parent_checkpoint_library_version=cfg['parent_library_version'],
      latest_batch=f'Intermediate checkpoint: {cfg["scope"]}, {n} chapters and {nv} verses newly drafted. Active block: {block["completed_chapters"]}/50 chapters, {block["remaining_chapters"]} remaining. Not a completed fifty-chapter block.',
      latest_verification='repository/'+rel+'/verification.json',batch_preference=q['batch_preference'],
      sources=[l['source'] for l in ledgers],active_fifty_chapter_block=block)
    dump(O/'CONTINUATION.json',state)
    order='genesis exodus leviticus numbers deuteronomy joshua judges ruth 1samuel 2samuel 1kings 2kings 1chronicles 2chronicles ezra nehemiah esther job psalms proverbs ecclesiastes songofsongs isaiah jeremiah lamentations ezekiel daniel hosea joel amos obadiah jonah micah nahum habakkuk zephaniah haggai zechariah malachi matthew mark luke john acts romans 1corinthians 2corinthians galatians ephesians philippians colossians 1thessalonians 2thessalonians 1timothy 2timothy titus philemon hebrews james 1peter 2peter 1john 2john 3john jude revelation'.split()
    chapters.sort(key=lambda c:(order.index(c['path'].split('/')[-2]),c['chapter']))
    reader=[f'# Fluent: cumulative revised reader\n\nEditorial draft · {counts["chapters"]} chapters · {counts["verses"]:,} verses\n\nIndependent editorial review and reader testing pending. Publication not allowed.\n']
    scope_reader=[f'# Fluent: {cfg["scope"]}\n\nIntermediate editorial draft · {n} chapters · {nv} verses\n\nThe active fifty-chapter block remains incomplete. Publication not allowed.\n']
    active_reader=[f'# Fluent: active fifty-chapter block\n\nIN_PROGRESS · {block["completed_chapters"]}/50 chapters · {block["completed_verses"]} verses\n\nDraft-covered: {block["completed_scope"]}. Remaining: {block["remaining_scope"]}.\n\nIndependent review pending. Publication not allowed.\n']
    scope_paths={c['path'] for c in json.loads((A/'mark-verse-review.json').read_text())['chapters']};active_count=0
    for ch in chapters:
        t=(R/ch['path']).read_text();name=re.search(r'^book: (.+)$',t,re.M)[1];body=t.split('---',2)[2].strip();lines=[]
        for line in body.splitlines():
            if line in ['<p>','</p>']:lines.append('');continue
            line='#'+line if line.startswith('## ') else re.sub(r'^v(\d+):',r'**\1**',line)
            lines.append(line+'  ' if line.strip() and not line.startswith('#') else line)
        rendered='\n## '+name+' '+str(ch['chapter'])+'\n\n'+'\n'.join(lines)+'\n'
        reader.append(rendered)
        if ch['path'] in scope_paths:scope_reader.append(rendered)
        slug=ch['path'].split('/')[-2]
        if (slug=='matthew' and ch['chapter']>=24) or slug in ['mark','luke'] or (slug=='john' and ch['chapter']<=5):
            active_reader.append(rendered);active_count+=1
    assert active_count==block['completed_chapters']
    (O/'Fluent-Reader.md').write_text('\n'.join(reader))
    (O/('Fluent-'+cfg['slug'].title()+'-'+str(min(cfg['chapters']))+'-'+str(max(cfg['chapters']))+'.md')).write_text('\n'.join(scope_reader))
    (O/'Fluent-Active-Block.md').write_text('\n'.join(active_reader))
    shutil.copy2(A/'overlap-before-after.json',O/'Current-scope-overlap-summary.json')
    instructions=f'''Continue Matt Skolnik’s Fluent revision without routine approval pauses.
Canonical file: libfile_2ad42bca9020819190f859e702030d9a, /Bible Translation Project/Fluent-Revision-Checkpoint.zip.
Resolve the current canonical version every run through the Library skill. Verify manifest.json and read CONTINUATION.json; stale search results and prompt snapshots do not override it. This checkpoint follows version {cfg['parent_library_version']}; the successful upload response supplies its new version. Never remove the expected-current-version guard or overwrite a newer writer. Defer if another writer is active.
Current head: {head}; parent: {parent}; required base: {base}; branch: {branch}.
Draft coverage: {counts['chapters']} chapters, {counts['verses']} verses, {len(ledgers)} ledgers. Existing files across all 1189 chapters do not count as current revision coverage.
Active block: {block['scope']}. Completed {block['completed_chapters']} chapters / {block['completed_verses']} verses: {block['completed_scope']}. Remaining {block['remaining_chapters']}: {block['remaining_scope']}. Finish this block before starting another. This is explicitly an incomplete block.
Read repository instructions, FLUENT_TRANSLATION_PHILOSOPHY.md, WORK_QUEUE.json, and latest ledgers. Read every verified pinned original-language verse before authoring. TSW and prior English are comparators, not templates. Preserve meaning, voice, difficult images, consequential uncertainty, gender when specific, real harm, repetition, and clear relationships. Use selective Notes/Vocabulary, not sermons. No word-change quota.
Keep verse-level rationale, before/after, exact source hash/reference, TSW comparator, and provisional F0–F3. Preserve frontmatter, v01 labels, headings, paragraphs, and source omissions. Hash exact source payloads including whitespace, variant markers, and written/read annotations. Verify complete source SHA-256 and Git blob identity. Gospel source: Faithlife/SBLGNT commit c4d241a9c1c479a55b989ba35a4976c1d0b8052c. All four full Gospel source files are included; Luke/John bindings are in sources/additional-source-bindings.json. Actual variant-marked main-text words must not be mistaken for omissions. Mark 3:14 lacks the apostles clause; 6:30 includes apostles. Mark 7:4 includes couches, 7:16 is absent, adultery is in 7:22, and 7:35 lacks immediately. Do not use previous notes as source evidence. Treat Mark's bracketed endings separately from main-text uncertainty.
Keep REVIEW_PENDING, qa_scope structural, publication_allowed false. Old approvals and Companion bindings do not transfer. Preserve all prior ledgers, historical provenance, chapters outside active scope, TSW and Companion; queue quotation/binding reconciliation. Retain whole-book reviews. Run affected source audits, translation-family audit, git diff --check, names/numbers/speakers/variants checks, and a documented bilingual authoring reread. Never claim human or independent review.
Verify the local checkout against this archive. If absent, clone the authorized GitHub repository and fetch this cumulative bundle; preserve Git parent objects, not just a patch. The bundle contains every revision commit since the required base. Current build, verification and packaging scripts are in repository/tools and do not require transient scripts. Read their scope restrictions before adapting them. Older verify_batch scripts bind their historical checkpoints and should be run at those commits.
Update exact counts and queue; commit locally; rebuild cumulative bundle, changed files, pinned sources, readers, history, continuation and SHA-256 manifest. Replace the SAME canonical file with the retained current version guard using the Library upload helper. Reconcile conflicts; never bypass the guard. Save expensive unfinished work explicitly as incomplete.
GitHub writes remain blocked by prior missing terminal authentication / integration 403; do not retry rejected writes or bypass permissions. No GitHub write is needed. Do not publish, edit Companion, send third-party messages, create automations, or delegate to subagents. Current continuation automation is 6aa3382c01bc81918eac4c8503c34f5e. Leave it active while draft work remains; at 1189 revised chapters report pending independent and whole-book review, then pause it. For actual access/runtime blockers preserve work and state the exact blocker; transient errors are not reasons to disable.
Report only verified progress and the saved file link. No routine approval request.
'''
    (O/'CONTINUATION_TASK.txt').write_text(instructions)
    (O/'README.md').write_text(f'''# Fluent revision checkpoint

{counts['chapters']} revised chapters; {counts['verses']:,} verses; {len(ledgers)} verse ledgers.

New draft work: {cfg['scope']}, {n} chapters and {nv} verses. The active fifty-chapter block is IN_PROGRESS: {block['completed_chapters']} draft-covered and {block['remaining_chapters']} remaining. Next: {cfg['next_scope']}. This is an intermediate checkpoint, not a completed block.

All {nv} Greek payloads were read before authoring. Each verse has its own rationale, before/after English, exact source binding, TSW comparator and provisional F0–F3 decision. {verification['focused_authoring_reread_count']} focused bilingual self-rereads are documented. Structural checks passed; no human or independent scholarly review is claimed. Publication is not allowed. Companion quotation/binding reconciliation and all queued whole-book reviews remain pending.

All {verification['prior_preservation']['ledgers_byte_identical']} prior ledgers and {verification['prior_preservation']['chapters_byte_identical']} previously revised chapters are byte-identical to the parent. TSW, Companion and unrelated work are unchanged. Exact source files, including additional Gospel bindings, are preserved. The prior checkpoint manifest and continuation are retained under provenance. The bundle preserves {len(hist)} revision commits since base {base}. Current head: {head}; parent: {parent}; branch: {branch}.

## Recovery

Resolve the latest canonical Library file before any write. Reuse a matching checkout or clone a repository containing the required base, then fetch Fluent-Revision.bundle and check out its branch. Verify manifest.json before trusting payloads. The repository directory contains every changed file; the patch is supplementary, not a substitute for Git history.

Run `python3 {rel}/verify_checkpoint.py {rel} --source-directory /path/to/checkpoint/sources` at this head. Historical audit scripts with fixed counts belong to their historical commits. Read CONTINUATION.json and CONTINUATION_TASK.txt for the authoritative partial-block queue and operational constraints. No rejected GitHub write was retried; no public deployment occurred.
''')
    m=dict(base_commit=base,head_commit=head,branch=branch,**counts,repository_file_count=len(files),files={})
    for p in sorted(O.rglob('*')):
        if p == O/'Fluent-Revision.bundle.lock':
            continue  # Git's transient bundle lock is never a checkpoint payload.
        if p.is_file():b=p.read_bytes();m['files'][str(p.relative_to(O))]=dict(bytes=len(b),sha256=sha(b))
    dump(O/'manifest.json',m)
    out=O.parent/'Fluent-Revision-Checkpoint.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        # Archive the exact manifest set, excluding late transient files.
        for f in sorted([*m['files'], 'manifest.json']):
            z.write(O/f, f)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None and len(z.namelist())==len(m['files'])+1
        for f,meta in m['files'].items():
            b=z.read(f);assert len(b)==meta['bytes'] and sha(b)==meta['sha256'],f
    assert not git('status','--porcelain')
    print(json.dumps(dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out.read_bytes()),head=head,commits=len(hist),manifest_entries=len(m['files']),counts=counts,expected_current_version=cfg['parent_library_version'])))
if __name__=='__main__':main()
