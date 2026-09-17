#!/usr/bin/env python3
"""Mechanically bind already-authored verse decisions; never generates translation wording.

Run with a scope directory and a verified checkpoint source directory. The scope
contains human-readable authoring-input.tsv and config.json. This script is
retained in the Git bundle so recovery does not depend on transient scripts.
"""
import argparse
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
from audit_fluent_revision import audit
from audit_translation_overlap import verse_texts, words

R = Path(__file__).resolve().parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()

def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope_directory', type=Path)
    ap.add_argument('--source-directory', required=True, type=Path)
    args = ap.parse_args()
    A = args.scope_directory.resolve()
    rel = str(A.relative_to(R))
    cfg = json.loads((A/'config.json').read_text())
    parent, book, slug = cfg['parent_commit'], cfg['book'], cfg['slug']
    def old(path):
        return subprocess.check_output(['git', 'show', parent+':'+path], cwd=R)
    source = dict(cfg['source']) if 'source' in cfg else json.loads(old(cfg['source_template_ledger']))['source']
    source['scope_chapters'] = cfg['chapters']
    sb = (args.source_directory/cfg['source_filename']).read_bytes()
    assert sha(sb) == source['sha256']
    assert hashlib.sha1(b'blob '+str(len(sb)).encode()+b'\0'+sb).hexdigest() == source['git_blob_sha']
    raw = {}
    for line in sb.decode().splitlines():
        m = re.fullmatch(r'\S+ (\d+):(\d+)\t(.*)', line)
        if m:
            raw[int(m[1]), int(m[2])] = m[3]
    source_to_public = {}
    public_to_source = {}
    partition_for_public = {}
    for (chapter, verse) in raw:
        if chapter not in cfg['chapters']:
            continue
        declared = cfg.get('source_public_mapping', {}).get(str(chapter), {}).get(str(verse))
        entries = declared if declared is not None else [{'public': verse}]
        source_to_public[chapter, verse] = [entry['public'] for entry in entries]
        for entry in entries:
            public = entry['public']
            assert (chapter, public) not in public_to_source
            public_to_source[chapter, public] = verse
            if 'token_start' in entry:
                partition_for_public[chapter, public] = dict(
                    token_start=entry['token_start'], token_end=entry['token_end'],
                    reason=entry['reason'])
    D = {}
    for line in (A/'authoring-input.tsv').read_text().splitlines():
        ref, text, why = line.split('|')
        key = tuple(map(int, ref.split(':')))
        assert key not in D and why.strip()
        D[key] = (text.replace('\\n', '\n'), why)
    assert set(D) == set(public_to_source)
    assert len(D) == cfg['expected_verses']
    rid = 'fluent-'+A.name.removeprefix('2026-09-16-')+'-biblical-fluency-2026-09-16'
    L = dict(schema_version=3, revision_id=rid, base_commit=parent,
             scope=cfg['scope'], status='REVIEW_PENDING', publication_allowed=False,
             source=source, automated_qa='PENDING', qa_scope='structural',
             method='Every pinned Greek verse read before authoring. All verses drafted before reading prior Fluent. TSW is a post-authoring comparator, not a wording template. Each authored verse has its own rationale. F0–F3 choices are provisional; no independent review or change quota.',
             chapters=[], verses=[])
    for c in cfg['chapters']:
        path = f'translations/fluent/NT/{slug}/{book}_{c:02}.md'
        before = old(path)
        text = before.decode()
        body = text.split('---', 2)[2].split('## Notes')[0]
        # Keep existing useful headings and paragraph boundaries, replacing only
        # complete verse units with the explicit authored payload.
        pattern = r'^v(\d+):.*?(?=^v\d+:|^</p>)'
        seen = []
        def sub(m):
            v = int(m[1])
            if (c, v) not in D:
                assert v in cfg.get('source_omissions', {}).get(str(c), []), (c, v)
                return ''
            seen.append(v)
            return f'v{v:02}: '+D[c, v][0]+'\n'
        body = re.sub(pattern, sub, body, flags=re.M|re.S)
        for prior, revised in cfg.get('heading_overrides', {}).items():
            body = body.replace('## '+prior+'\n', '## '+revised+'\n')
        assert seen == sorted(v for cc, v in D if cc == c)
        fm = text.split('---', 2)[1].strip()
        assert 'editorial_status:' not in fm
        out = ('---\n'+fm+'\nqa_scope: structural\neditorial_status: REVIEW_PENDING\n'
               'publication_allowed: false\nrevision_id: '+rid+'\n---\n'+body.rstrip()+'\n\n')
        app = cfg['apparatus'][str(c)]
        out += '## Notes\n\n'+'\n\n'.join('v'+v+': '+t for v,t in app['notes'])+'\n\n'
        out += '## Vocabulary\n\n'+'\n\n'.join('v'+v+': **'+term+'**: '+t for v,term,t in app['vocabulary'])+'\n'
        out = out.rstrip() + '\n'
        (R/path).write_text(out)
        cp = f'books/NT/{slug}/{book}_{c:02}.md'
        cb = (R/cp).read_bytes()
        ch = dict(chapter=c, verse_count=len(seen), path=path,
                  before_sha256=sha(before), after_sha256=sha(out.encode()),
                  tsw_comparator_path=cp, tsw_comparator_sha256=sha(cb))
        alignment = cfg.get('tsw_alignment', {}).get(str(c))
        if alignment:
            ch.update(tsw_public_labels=alignment['public_labels'],
                      tsw_unmatched_source_labels=alignment['unmatched_source_labels'],
                      tsw_additional_public_labels=alignment['additional_public_labels'],
                      tsw_alignment_reason=alignment['reason'])
        omitted = cfg.get('source_omissions', {}).get(str(c), [])
        if omitted:
            ch['source_omitted_public_labels'] = omitted
            ch['source_omission_reason'] = 'Absent from pinned SBLGNT; revised public labels follow the pinned source records.'
            bv0 = verse_texts(before.decode())
            parent_omitted = [v for v in omitted if f'{v:02}' not in bv0]
            ch['parent_omitted_public_labels'] = parent_omitted
            if parent_omitted:
                ch['parent_omission_reason'] = 'These public labels were already absent from the exact parent Fluent.'
            tv0 = verse_texts(cb.decode())
            comp_omitted = [v for v in omitted if f'{v:02}' not in tv0]
            if comp_omitted:
                ch['tsw_omitted_public_labels'] = comp_omitted
                ch['tsw_omission_reason'] = 'TSW also lacks these public labels; comparator bytes unchanged.'
        L['chapters'].append(ch)
        av,bv,tv = map(verse_texts, [out, text, cb.decode()])
        for v in seen:
            k = f'{v:02}'; ref = f'{c}:{v}'
            unmatched = set(alignment['unmatched_source_labels']) if alignment else set()
            assert k in tv or v in unmatched
            comparator = tv.get(k, '')
            source_v = public_to_source[c, v]
            source_ref = f'{c}:{source_v}'
            decision = dict(reference=book+' '+ref,
                delta='F3' if ref in cfg['f3'] else 'F0' if av[k]==bv[k] else 'F2',
                rationale=D[c,v][1], source_reference=source['osis_book_id']+' '+source_ref,
                source_verse_sha256=sha(raw[c,source_v].encode()), before=bv[k], after=av[k],
                tsw_comparator=comparator, identical_words_to_tsw=words(av[k])==words(comparator),
                word_similarity_to_tsw=round(difflib.SequenceMatcher(None,words(av[k]),words(comparator),autojunk=False).ratio(),6),
                editorial_status='REVIEW_PENDING')
            if (c, v) in partition_for_public:
                decision['source_partition'] = partition_for_public[c, v]
            merged = cfg.get('source_merges', {}).get(ref)
            if merged:
                # Preserve separately hashed records when a public verse spans
                # a source chapter boundary (Revelation 12:18 / public 13:1).
                assert source_ref in merged and len(merged) >= 2
                decision['source_segments'] = [dict(
                    source_reference=source['osis_book_id']+' '+r,
                    source_verse_sha256=sha(raw[tuple(map(int, r.split(':')))].encode()))
                    for r in merged]
                decision['source_mapping_reason'] = cfg['source_merge_reasons'][ref]
            if v in unmatched:
                decision['tsw_comparator_status'] = 'UNAVAILABLE_PUBLIC_LABEL'
                decision['tsw_comparator_reason'] = alignment['reason']
            L['verses'].append(decision)
    errors = audit(R, L, sb)
    assert not errors, errors
    L['automated_qa'] = 'PASSED'
    L['summary'] = dict(verses_drafted=len(D), verses_with_changed_text=sum(v['before']!=v['after'] for v in L['verses']), delta_counts=dict(Counter(v['delta'] for v in L['verses'])))
    ledger = rel+'/'+slug+'-verse-review.json'
    dump(R/ledger,L)
    for ch in L['chapters']:
        rp = f'audit/exegetical-core/fluent-production/{slug}/{book}_{ch["chapter"]:02}_review.json'
        dump(R/rp,dict(book=book,chapter=ch['chapter'],translation='FLUENT',status='REVIEW_PENDING',publication_allowed=False,qa_scope='structural',automated_qa='PASSED',revision_id=rid,supersedes=dict(commit=parent,path=rp),source=source,chapter_binding=ch,verse_ledger=ledger,key_decisions=[v for v in L['verses'] if v['reference'].startswith(f'{book} {ch["chapter"]}:') and v['delta']=='F3']))
    for fn in cfg.get('book_record_files', [slug.upper()+'_FLUENT_BOOK_QA.json',slug.upper()+'_SOURCE_BINDINGS.json']):
        rp = f'audit/exegetical-core/fluent-production/{slug}/'+fn
        d = json.loads(old(rp))
        rev = dict(id=rid,chapters=cfg['chapters'],verse_count=len(D),verse_ledger=ledger,automated_qa='PASSED',editorial_status='REVIEW_PENDING',qa_scope='structural',prior_record=dict(commit=parent,path=rp),note='Previous wording approvals and Companion bindings do not transfer.')
        d.update(status='REVIEW_PENDING', publication_allowed=False,
                 editorial_review_pending_chapters=sorted(set(d.get('editorial_review_pending_chapters',[])+cfg['chapters'])), current_revision=rev)
        d.setdefault('revision_batches',[]).append(rev)
        if fn in cfg.get('supersede_entry_records', []):
            for entry in d['entries']:
                if entry['chapter'] in cfg['chapters']:
                    entry.update(status='SUPERSEDED', superseded_by_verse_ledger=ledger,
                                 superseded_reason='Historical English hash and classification; see new source-bound revision.')
            d['historical_summary_note'] = 'Original classifications and English hashes remain historical; affected entries are explicitly superseded.'
        if 'publication_status' in d: d['publication_status']='REVIEW_PENDING'
        dump(R/rp,d)
    rows=[]
    for v in L['verses']:
        bw,aw,tw=map(words,[v['before'],v['after'],v['tsw_comparator']])
        rows.append(dict(reference=v['reference'],before_identical=bw==tw,after_identical=aw==tw,before_similarity=round(difflib.SequenceMatcher(None,bw,tw,autojunk=False).ratio(),6),after_similarity=v['word_similarity_to_tsw']))
    summary={s:dict(identical=sum(x[s+'_identical'] for x in rows),near_identical_nonidentical=sum(not x[s+'_identical'] and x[s+'_similarity']>=.9 for x in rows),mean_word_similarity=round(sum(x[s+'_similarity'] for x in rows)/len(rows),6)) for s in ['before','after']}
    dump(A/'overlap-before-after.json',dict(scope=cfg['scope'],verses=len(D),summary=summary,rows=rows,qualification='Triage only. No minimum change quota; not evidence of scholarly approval.'))
    # Use the already-updated working queue so several independently authored
    # book scopes can accumulate safely in one checkpoint commit. The exact
    # parent queue is still verified by the batch verifier before packaging.
    q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text())
    assert not any(x['ledger']==ledger for x in q['completed_draft_scopes'])
    q['completed_draft_scopes'].append(dict(scope=cfg['scope'],verses=len(D),ledger=ledger))
    block=q['active_fifty_chapter_block']
    block.update(completed_chapters=block['completed_chapters']+len(cfg['chapters']),completed_scope=cfg['completed_block_scope'],completed_verses=block['completed_verses']+len(D),remaining_scope=cfg['next_scope'],remaining_chapters=block['remaining_chapters']-len(cfg['chapters']))
    assert block['completed_chapters']+block['remaining_chapters']==block['chapters_target']
    q['next_work'][0]=dict(scope=cfg['next_scope'],action=f'Continue the remaining {block["remaining_chapters"]} chapters of the active fifty-chapter block without routine approval. Read verified pinned Greek before authoring.')
    dump(R/'audit/fluent-revision/WORK_QUEUE.json',q)
    print(json.dumps(dict(scope=cfg['scope'],summary=L['summary'],block=block)))

if __name__=='__main__': main()
