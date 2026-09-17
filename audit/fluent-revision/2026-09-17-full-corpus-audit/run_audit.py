#!/usr/bin/env python3
"""Reproducible corpus screens. These do not certify translation accuracy."""
import argparse, hashlib, json, re, sys, subprocess
from pathlib import Path
from collections import Counter, defaultdict
from difflib import SequenceMatcher

R = Path(__file__).resolve().parents[3]
A = Path(__file__).resolve().parent
sys.path.insert(0, str(R/'tools'))
from audit_translation_overlap import audit as overlap_audit, verse_texts, words
from audit_translation_family import audit as family_audit, main_text
from audit_fluent_revision import audit as binding_audit

def dump(name, data):
    (A/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def main():
    global A
    ap=argparse.ArgumentParser(); ap.add_argument('--sources',type=Path,required=True); ap.add_argument('--output',type=Path); args=ap.parse_args()
    if args.output:
        A=args.output.resolve();A.mkdir(parents=True,exist_ok=True)
    q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text())
    source_files={hashlib.sha256(p.read_bytes()).hexdigest():p for p in args.sources.iterdir() if p.suffix in ('.xml','.txt')}
    ledgers=[]; bindings=[]; alignments=[]; chapter_rows=[]; rows=[]; flags=[]; paragraphs=[]; exact_runs=[]
    for scope in q['completed_draft_scopes']:
        l=json.loads((R/scope['ledger']).read_text()); ledgers.append(l)
        sp=source_files.get(l['source']['sha256'])
        errors=binding_audit(R,l,sp.read_bytes()) if sp else ['source file unavailable']
        bindings.append(dict(ledger=scope['ledger'],source_file=sp.name if sp else None,chapters=len(l['chapters']),verses=len(l['verses']),errors=errors))
        for c in l['chapters']:
            if any('alignment' in k or 'omission' in k or 'omitted' in k for k in c):
                details={k:v for k,v in c.items() if ('tsw_' in k or 'source_' in k or 'parent_' in k) and k not in ('tsw_comparator_path','tsw_comparator_sha256')}
                if any(details.values()):alignments.append(dict(path=c['path'],details=details))
            path=R/c['path']; text=path.read_text(); tsw=(R/c['tsw_comparator_path']).read_text(); vs=verse_texts(text); tv=verse_texts(tsw)
            body=main_text(text).split('---',2)[-1]
            notes=text.split('## Notes',1)[1].split('## Vocabulary',1)[0]
            vocab=text.split('## Vocabulary',1)[1]
            slug=path.parent.name; book=re.search(r'^book: (.*)',text,re.M)[1]
            cr=dict(path=c['path'],book=book,slug=slug,chapter=c['chapter'],verses=len(vs),words=sum(len(words(v)) for v in vs.values()),note_entries=len(re.findall(r'^v\d',notes,re.M)),vocabulary_entries=len(re.findall(r'^v\d',vocab,re.M)),poetic_continuation_lines=sum(bool(x.strip()) and not re.match(r'^(#|<|v\d)',x) for x in body.splitlines()))
            chapter_rows.append(cr)
            if re.search(r'^##(?:Notes|Vocabulary)',text,re.M):flags.append(dict(kind='nonstandard_heading',path=c['path']))
            for section,contents in [('Notes',notes),('Vocabulary',vocab)]:
                for entry in re.split(r'\n(?=v\d)',contents.strip()):
                    if re.search(r'\b(pinned|ledger|audit|source record|public label|source-number|draft retains|not silently|not harmoniz|not softened|not normalized|not sanitized)\b',entry,re.I):
                        flags.append(dict(kind='apparatus_process_language',path=c['path'],section=section,text=entry.strip()))
                    if re.search(r'\b(preserves?|retains?|avoids?|resists?|without (?:adding|resolving|reducing)|not (?:reduced|resolved|harmonized))\b',entry,re.I):
                        flags.append(dict(kind='apparatus_defense_candidate',path=c['path'],section=section,text=entry.strip()))
            for label,value in vs.items():
                w=words(value); tw=words(tv[label]) if label in tv else None
                row=dict(reference=f'{book} {c["chapter"]}:{int(label)}',path=c['path'],slug=slug,chapter=c['chapter'],verse=int(label),word_count=len(w),tsw_word_count=len(tw) if tw is not None else None,identical=w==tw,similarity=round(SequenceMatcher(None,tw,w,autojunk=False).ratio(),6) if tw is not None else None)
                rows.append(row)
                if len(w)>=100:flags.append(dict(kind='long_verse_candidate',reference=row['reference'],text=value,words=len(w)))
                if re.search(r'\b(thou|thee|thy|thine|ye|hath|doth|whosoever|wherefore|thereunto)\b',value,re.I):flags.append(dict(kind='archaic_word_candidate',reference=row['reference'],text=value))
            for p in re.findall(r'<p>(.*?)</p>',body,re.S):
                clean=re.sub(r'^v\d+:\s*','',p,flags=re.M).strip(); count=len(words(clean))
                paragraphs.append(dict(path=c['path'],first_verse=(re.search(r'^v(\d+):',p,re.M) or [None,None])[1],words=count))
            lines=body.splitlines()
            for i,line in enumerate(lines):
                if line=='</p>':
                    prior=next((x for x in reversed(lines[:i]) if x.strip()),'')
                    if prior.rstrip().endswith((',', ';', '—')):
                        flags.append(dict(kind='paragraph_continuity_candidate',path=c['path'],preceding_line=prior))
            run=[]
            for label,value in vs.items():
                if label in tv and words(value)==words(tv[label]):run.append((int(label),len(words(value))))
                else:
                    if len(run)>=3:exact_runs.append(dict(book=book,chapter=c['chapter'],start=run[0][0],end=run[-1][0],verses=len(run),words=sum(x[1] for x in run),path=c['path']))
                    run=[]
            if len(run)>=3:exact_runs.append(dict(book=book,chapter=c['chapter'],start=run[0][0],end=run[-1][0],verses=len(run),words=sum(x[1] for x in run),path=c['path']))
    overlap=overlap_audit(R);dump('overlap.json',overlap)
    family,errors=family_audit(R);dump('family.json',dict(report=family,errors=errors))
    dump('source-bindings.json',bindings);dump('verse-metrics.json',rows);dump('chapter-metrics.json',chapter_rows);dump('screening-candidates.json',flags);dump('alignment-caveats.json',alignments);dump('identical-runs.json',sorted(exact_runs,key=lambda x:x['words'],reverse=True))
    summary=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),chapters=len(chapter_rows),verses=len(rows),books=len(set(x['slug'] for x in rows)),ledgers=len(ledgers),sources=len(set(l['source']['sha256'] for l in ledgers)),binding_errors=sum(len(x['errors']) for x in bindings),family_errors=errors,overlap=overlap['totals']['ALL'],flag_counts=dict(Counter(f['kind'] for f in flags)),identical_runs=len(exact_runs),identical_at_least_25_words=sum(r['identical'] and r['word_count']>=25 for r in rows),identical_at_least_20_words=sum(r['identical'] and r['word_count']>=20 for r in rows),longest_paragraphs=sorted(paragraphs,key=lambda x:x['words'],reverse=True)[:20],notes=sum(x['note_entries'] for x in chapter_rows),vocabulary=sum(x['vocabulary_entries'] for x in chapter_rows),chapters_with_process_language=len(set(f['path'] for f in flags if f['kind']=='apparatus_process_language')),status='SCREEN_COMPLETE',editorial_approval='REVIEW_PENDING',publication_allowed=False)
    dump('summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
