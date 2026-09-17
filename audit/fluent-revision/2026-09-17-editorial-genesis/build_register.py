import hashlib,json,re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
issues=[
('G01','Genesis 1–50','F01','Complete a fresh, passage-by-passage source review of all 1,533 verses. Prior drafting and the earlier consistency pass are evidence, not a substitute for this new editorial pass.'),
('G02','Genesis 1–50','F02/F04/F08','Read the whole book continuously, including chapter transitions; review speaker tracking, paragraphs, headings, repetitions and the poetry in chapters 27 and 49.'),
('G03','Genesis 15:6; 16:13–14; 20:13,16; 24:55,63; 25:18,23','F03','Resolve or explicitly preserve the consequential grammatical and lexical alternatives already flagged by the notes. Confirm the notes against source and appropriate specialist evidence.'),
('G04','Genesis 31:24,29','F01/F03','The main text uses make any pronouncement for Hebrew speak from good to bad. Targeted inspection confirms the literal components but not the narrower formal-speech interpretation. Decide the idiom from contextual and lexical evidence and rebind any changed Scripture.'),
('G05','Genesis 35:7','F03/F06','A plural verb accompanies Elohim. The note now states this fact without asserting that the surrounding narrative settles it. Review the singular rendering and treatment of the alternative.'),
('G06','Genesis 38:21–22','F03/F07','The main text says shrine prostitute while the apparatus acknowledges uncertainty about the institutional connection of qedeshah. Evaluate whether the main wording is too specific.'),
('G07','Genesis 44:22','F03','The English identifies the father where the Hebrew pronoun can refer to father or son. Decide whether the existing note adequately preserves the ambiguity or the main text should retain a pronoun.'),
('G08','Genesis 49','F01/F03/F04','Review the complete poem, its difficult syntax and lexical alternatives, and the handling of Shiloh, Joseph imagery, divine titles and parallelism. No fresh complete source comparison of this poem occurred in this pass.'),
('G09','Genesis 1–50 vocabulary and notes','F05/F07','All entries received an editorial-scope decision, but lexical accuracy, transliteration, duplication between notes and vocabulary, and the usefulness of each surviving entry require source and reader checks. Routine entries such as dream, forget, or walk about should be tested for actual reader value.'),
('G10','Genesis 1–50','F06/F08','Apply the final corpus conventions for divine-name bolding, quotation marks, transliteration and rendered poetry. Verse-label padding is standardized here; the other style decisions are not thereby closed.'),
('G11','Genesis 1–50','F11/F12','Qualified independent language review, representative reader testing, Companion reconciliation and Matt’s final editorial signoff remain pending.')]
dump(A/'open-issues.json',dict(status='OPEN',items=[dict(id=i,scope=s,criterion=c,action=a,status='OPEN') for i,s,c,a in issues]))
q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());books={}
for scope in q['completed_draft_scopes']:
 l=json.loads((R/scope['ledger']).read_text())
 for ch in l['chapters']:
  slug=Path(ch['path']).parent.name
  books.setdefault(slug,[]).append(ch['chapter'])
register=dict(updated='2026-09-17',base_checkpoint_version=98,standard='FLUENT_EDITORIAL_STANDARD.md',reader_guidance='FLUENT_READER_GUIDANCE.md',routine_batch_approval_required=False,batch_size_chapters=50,draft_coverage=q['draft_coverage'],publication_allowed=False,independent_editorial_review='REVIEW_PENDING',criteria_status={},books=[])
for i in range(1,13):register['criteria_status'][f'F{i:02}']='IN_PROGRESS' if i in [7,10] else 'PENDING'
register['criteria_status']['F10']='STRUCTURAL_CHECKS_PASSED_AT_PRIOR_CHECKPOINT; CURRENT_RECHECK_REQUIRED'
for slug,chs in books.items():
 register['books'].append(dict(book=slug,chapters=len(set(chs)),fresh_source_review='IN_PROGRESS_TARGETED_ONLY' if slug=='genesis' else 'NOT_STARTED',continuous_reading='NOT_STARTED',apparatus_scope_review='SELF_REVIEW_COMPLETE_WITH_OPEN_ISSUES' if slug=='genesis' else 'NOT_STARTED',terminology_and_house_style='PENDING',independent_language_review='PENDING',reader_testing='PENDING',companion_reconciliation='PENDING',final_signoff='PENDING'))
register['active_block']=dict(scope='Genesis 1–50',status='IN_PROGRESS',completed_pass='Apparatus editorial scope and clarity',reviewed_notes=337,reviewed_vocabulary_entries=240,targeted_source_records=10,targeted_genesis_verse_records=9,total_genesis_verse_records=1533,full_bilingual_review_complete=False,report=str(A.relative_to(R))+'/Genesis-Editorial-Review.md',issues=str(A.relative_to(R))+'/open-issues.json')
register['next_action']='Complete Genesis fresh full source review and continuous reading before marking this 50-chapter block complete; then advance in 50-chapter units without routine approval.'
dump(R/'EDITORIAL_PROGRESS.json',register)
inputs=json.loads((A/'input-chapters.json').read_text());dump(A/'input-bindings.json',dict(base_commit='4d1c207f3645412e01c725431cb4bfc11e2ed655',chapters=[dict(path=c['path'],sha256=sha(c['text'].encode())) for c in inputs],criteria_snapshot='audit/fluent-revision/2026-09-17-full-corpus-audit/criteria-bindings.json'))
