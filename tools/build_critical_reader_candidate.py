#!/usr/bin/env python3
"""Build review-only JSON from the exact correction candidate; never publish.

Requires the complete Fluent corpus, but only the seven explicitly listed TSW
chapters. A partial TSW manifest is never installed as a whole-Bible manifest.
Uses a new output directory, validates all input before writing, and never
rewrites source Markdown or historical review records.
"""
from __future__ import annotations
from pathlib import Path
import argparse,collections,json,shutil,tempfile
from critical_text_model import ContentError,parse_chapter,sha256

AUDIT=Path('audit/corrections/2026-10-15')
VERSION='2026.10.15-correction-candidate'

def write_json(path:Path,value:object)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def build(repo:Path,destination:Path)->dict:
    repo=repo.resolve();destination=destination.absolute()
    if destination.exists():raise ContentError('Output must be a new directory; existing data are never overwritten')
    contract=json.loads((repo/AUDIT/'CORPUS_CONTRACT.json').read_text(encoding='utf-8'))
    records=contract['chapters'];parsed=[];by_reference={}
    for record in records:
        p=repo/record['path']
        if not p.is_file() or p.is_symlink():raise ContentError(f'Missing or unsafe source: {record["path"]}')
        if sha256(p.read_bytes())!=record['candidate_sha256']:raise ContentError(f'Unreviewed bytes: {record["path"]}')
        c=parse_chapter(p)
        if [v['number'] for v in c['verses']]!=record['verse_labels']:raise ContentError(f'Unexpected verse labels: {p}')
        translation='fluent' if record['path'].startswith('translations/fluent/') else 'tsw'
        if str(c['meta']['translation']).lower()!=translation:raise ContentError(f'Translation mismatch: {p}')
        k=(translation,c['book_slug'],c['chapter'])
        if k in by_reference:raise ContentError(f'Duplicate chapter identity: {k}')
        by_reference[k]={v['number'] for v in c['verses']};parsed.append((translation,record,c))
    if sum(t=='fluent' for t,_,_ in parsed)!=1189:raise ContentError('Not the complete Fluent candidate')
    if sum(t=='tsw' for t,_,_ in parsed)!=7:raise ContentError('Unexpected targeted TSW scope')
    # References must resolve inside the complete Fluent corpus; local TSW ones
    # resolve inside the selected chapter. External TSW targets cannot be certified.
    for t,rec,c in parsed:
        for entry in c['notes']+c['vocabulary']:
            for target in entry['targets']:
                key=(t,target['book_slug'],target['chapter'])
                if key not in by_reference:
                    if t=='fluent':raise ContentError(f'Unknown cross-chapter target: {target}')
                    continue
                if target['verse'] not in by_reference[key]:
                    # Notes may intentionally document an omitted verse label.
                    # Preserve that reference, flag it explicitly, never remap it.
                    entry.setdefault('target_cautions',[]).append({'target':target,'status':'NO_MAIN_TEXT_VERSE_AT_THIS_LABEL'})
    destination.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.critical-reader-',dir=destination.parent))
    counts=collections.defaultdict(collections.Counter);search=collections.defaultdict(list);bookinfo=collections.defaultdict(dict);digests=[]
    try:
        for t,record,c in parsed:
            meta=c['meta']
            payload={'translation':t.upper(),'translation_id':t,'version':VERSION,'book':meta['book'],'book_slug':c['book_slug'],'testament':meta['testament'],'chapter':c['chapter'],'blocks':c['blocks'],'verses':c['verses'],'notes':c['notes'],'vocabulary':c['vocabulary'],'publication_allowed':False,'editorial_status':'CORRECTION_CANDIDATE_REVIEW_PENDING','provenance':{'base_commit':contract['base_commit'],'markdown_path':record['path'],'markdown_sha256':c['source_sha256'],'revision_id':meta.get('revision_id'),'scope':'complete_fluent_draft' if t=='fluent' else 'selected_TSW_chapter_only','independent_human_approval':False}}
            rel=Path('fluent' if t=='fluent' else 'tsw-selected')/'chapters'/c['book_slug']/f'{c["chapter"]:03d}.json'
            write_json(temp/rel,payload);digests.append({'path':str(rel),'sha256':sha256((temp/rel).read_bytes()),'markdown_sha256':c['source_sha256']})
            counts[t].update({'chapters':1,'verses':len(c['verses']),'notes':len(c['notes']),'vocabulary':len(c['vocabulary'])})
            for v in c['verses']:search[t,c['book_slug']].append({'c':c['chapter'],'v':v['number'],'t':v['text']})
            b=bookinfo[t].setdefault(c['book_slug'],{'name':meta['book'],'slug':c['book_slug'],'testament':meta['testament'],'included_chapters':[]})
            b['included_chapters'].append(c['chapter'])
        for (t,slug),rows in search.items():
            rel=Path('fluent' if t=='fluent' else 'tsw-selected')/'search'/f'{slug}.json'
            write_json(temp/rel,sorted(rows,key=lambda v:(v['c'],v['v'])))
            digests.append({'path':str(rel),'sha256':sha256((temp/rel).read_bytes())})
        for t in ('fluent','tsw'):
            order={b['slug']:i for i,b in enumerate(contract['canonical_books'])}
            books=sorted(bookinfo[t].values(),key=lambda v:order[v['slug']])
            for book in books:
                book['included_chapters'].sort()
                if t=='fluent':book['chapters']=len(book['included_chapters'])
            manifest={'translation':t.upper(),'version':VERSION,'publication_allowed':False,'status':'REVIEW_CANDIDATE_NOT_DEPLOYED','full_translation_coverage':t=='fluent','book_order':'Canonical order retained from the examined reader manifest.','books':books,'counts':dict(counts[t]),'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','attribution':'The Shared Word Project / Matthew J. Skolnik; English draft and correction candidate.','scope_notice':'All 1189 Fluent draft chapters; independent editorial approval remains pending.' if t=='fluent' else 'SEVEN SELECTED TSW CHAPTERS ONLY. Not a full TSW release; do not overwrite a full TSW manifest with this inventory.'}
            write_json(temp/('fluent/manifest.json' if t=='fluent' else 'tsw-selected/PARTIAL_SCOPE_ONLY.json'),manifest)
        summary={'version':VERSION,'publication_allowed':False,'counts':{t:dict(v) for t,v in counts.items()},'input_contract_sha256':sha256((repo/AUDIT/'CORPUS_CONTRACT.json').read_bytes()),'files':digests,'checks':['Exact source SHA-256 matches correction contract','No duplicate or empty verse records','No unowned Scripture continuation discarded','Verse labels preserved against declared source-file contract','Cross-chapter targets kept separate from local verse list','Raw apparatus text retained beside normalized fields'],'limitations':['Not a full current TSW checkout','No live-site verification','No independent human language approval','No existing production reader code or source adapter was replaced']}
        write_json(temp/'BUILD_MANIFEST.json',summary)
        (temp/'DO_NOT_DEPLOY.txt').write_text('REVIEW CANDIDATE ONLY\nNo publication approval is granted.\nFluent: full 1189-chapter draft export.\nTSW: seven selected chapters only, NOT a replacement full-Bible dataset.\nNo installer in this package uploads these files or changes a website.\n',encoding='utf-8')
        temp.rename(destination)
    except BaseException:
        shutil.rmtree(temp,ignore_errors=True);raise
    return {'output':str(destination),'counts':summary['counts'],'publication_allowed':False}

def main()->None:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    try:print(json.dumps(build(args.repo,args.out),indent=2))
    except (ContentError,OSError,ValueError) as e:p.exit(1,f'BUILD BLOCKED: {e}\n')
if __name__=='__main__':main()
