#!/usr/bin/env python3
"""Read-only comparison of selected live chapter APIs with the correction candidate.

A matching API response is NOT publication approval or browser-interaction QA.
No credentials, POST requests, website writes, or automatic retries are used.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.parse
import urllib.request
from typing import Any
from critical_text_model import parse_chapter, ContentError, sha256
from critical_spacing_overlay import resolve_correction_snapshot

SITES = {
    'churchcommons': 'https://churchcommons.org/wp-json/tsw/v1/chapter/',
    'mvp': 'https://mvpresby.org/api/gateway/bible/chapter/',
}
MAX_BYTES = 2 * 1024 * 1024

def text(value: Any) -> str:
    if not isinstance(value, str):
        raise ContentError('Expected a text field')
    return ' '.join(value.split())

def verse_signature(value: Any) -> tuple:
    if not isinstance(value, dict) or type(value.get('number')) is not int or value['number'] < 1:
        raise ContentError('Invalid verse record')
    if not isinstance(value.get('label'), str) or not isinstance(value.get('lines'), list):
        raise ContentError('Missing verse label or lines')
    import re
    if not re.fullmatch(r'v0*'+str(value['number']), value['label']):
        raise ContentError('Verse label and number disagree')
    lines=tuple(text(s) for s in value['lines'] if isinstance(s,str) and s.strip())
    if len(lines)!=sum(bool(s.strip()) for s in value['lines'] if isinstance(s,str)) or any(not isinstance(s,str) for s in value['lines']):
        raise ContentError('Invalid verse lines')
    body=text(value.get('text'))
    if not body or body != text(' '.join(lines)):
        raise ContentError('Verse text does not agree with its lines')
    return value['number'],body,lines

def chapter_signature(data: Any, identity: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(data, dict):raise ContentError('Chapter response must be an object')
    ids=[data[k].lower() for k in ('translation','translation_id') if isinstance(data.get(k),str)]
    if not ids or any(x!=identity['translation'] for x in ids):raise ContentError('Wrong translation identity')
    for key in ('book','book_slug','chapter'):
        if data.get(key)!=identity[key]:raise ContentError('Wrong '+key+' identity')
    if type(data['chapter']) is not int:raise ContentError('Chapter must be an integer')
    for k in ('verses','blocks','notes','vocabulary'):
        if not isinstance(data.get(k),list):raise ContentError('Missing '+k+' array')
    verses=[verse_signature(v) for v in data['verses']]
    nums=[v[0] for v in verses]
    if not nums or nums!=sorted(set(nums)):raise ContentError('Empty, duplicated, or nonordered verses')
    blocks=[];in_blocks=[]
    for b in data['blocks']:
        if not isinstance(b,dict):raise ContentError('Invalid block')
        if b.get('type')=='heading':blocks.append(('heading',text(b.get('text'))))
        elif b.get('type')=='paragraph' and isinstance(b.get('verses'),list):
            vv=[verse_signature(v) for v in b['verses']]
            if not vv:raise ContentError('Empty paragraph')
            blocks.append(('paragraph',tuple(vv)));in_blocks.extend(vv)
        else:raise ContentError('Unsupported or missing block type')
    if in_blocks!=verses:raise ContentError('Block verses disagree with flat verses')
    notes=[]
    for n in data['notes']:
        if not isinstance(n,dict) or not isinstance(n.get('verses'),list):raise ContentError('Invalid note')
        if any(type(v) is not int or v<1 for v in n['verses']):raise ContentError('Invalid note verse reference')
        notes.append((text(n.get('ref')),tuple(n['verses']),text(n.get('text'))))
    vocab=[]
    for v in data['vocabulary']:
        if not isinstance(v,dict) or not isinstance(v.get('verses'),list):raise ContentError('Invalid vocabulary')
        if any(type(n) is not int or n<1 for n in v['verses']):raise ContentError('Invalid vocabulary reference')
        vocab.append((text(v.get('ref')),tuple(v['verses']),text(v.get('term')),
                      text(v.get('transliteration','')),text(v.get('definition'))))
    return {'verses':verses,'blocks':blocks,'notes':notes,'vocabulary':vocab}

def expected_chapter(repo: Path, relative: str) -> tuple[dict,dict]:
    p=repo/relative;m=parse_chapter(p)
    identity={'translation':m['meta']['translation'].lower(),'book':m['meta']['book'],
              'book_slug':m['book_slug'],'chapter':m['chapter']}
    data={**identity,'translation_id':identity['translation'],**{k:m[k] for k in ('verses','blocks','notes','vocabulary')}}
    return identity,chapter_signature(data,identity)

def compare_response(data: Any, identity: dict, expected: dict) -> dict:
    try:actual=chapter_signature(data,identity)
    except (ContentError,TypeError,KeyError,ValueError) as exc:
        return {'status':'UNVERIFIABLE_RESPONSE','message':str(exc),'content_match':False}
    differences=[k for k in expected if actual[k]!=expected[k]]
    return {'status':'DIFFERS_FROM_CANDIDATE' if differences else 'TARGET_CONTENT_MATCH',
            'different_components':differences,'content_match':not differences,
            'reported_version':data.get('version'),
            'counts':{'verses':len(actual['verses']),'notes':len(actual['notes']),'vocabulary':len(actual['vocabulary'])}}

def retrieve(url: str) -> Any:
    req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'SharedWord-ReadOnly-Correction-Check/1.0'})
    with urllib.request.urlopen(req,timeout=20) as response:
        if urllib.parse.urlparse(response.geturl()).hostname!=urllib.parse.urlparse(url).hostname:
            raise ContentError('Unexpected redirect host')
        if response.status!=200:raise ContentError('Unexpected HTTP status')
        raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ContentError('Response exceeds safe size')
        return json.loads(raw.decode('utf-8'))

def run(repo: Path, sites: list[str]) -> dict:
    # Verify the full pinned correction model before treating it as the comparison target.
    contract,ledger,_=resolve_correction_snapshot(repo)
    for record in contract['chapters']:
        if sha256((repo/record['path']).read_bytes())!=record['candidate_sha256']:
            raise ContentError('Changed source: '+record['path'])
    targets=[e['path'] for e in ledger['files']]
    extra='translations/fluent/OT/numbers/Numbers_22.md'
    if extra not in targets:targets.append(extra)
    prepared=[]
    for relative in targets:
        identity,expected=expected_chapter(repo,relative)
        for site in sites:
            url=SITES[site]+identity['book_slug']+'/'+str(identity['chapter'])+'?'+urllib.parse.urlencode({'translation':identity['translation']})
            prepared.append((site,relative,url,identity,expected))
    def check(item):
        site,relative,url,identity,expected=item
        try:result=compare_response(retrieve(url),identity,expected)
        except Exception as exc:result={'status':'UNVERIFIABLE_RESPONSE','message':str(exc),'content_match':False}
        return {'site':site,'source_path':relative,'url':url,'identity':identity,**result}
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(check,prepared))
    return {'checked_at_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Selected chapter API payloads only; not a whole-Bible accuracy audit or browser-interaction test.',
            'read_only':True,'publication_allowed':False,'website_changed':False,
            'all_targets_match':bool(results) and all(r['content_match'] for r in results),
            'results':results}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path('.'))
    parser.add_argument('--site',choices=['churchcommons','mvp','both'],default='both')
    parser.add_argument('--out',type=Path,required=True,help='New report path, outside the repository recommended')
    args=parser.parse_args()
    if args.out.exists():raise SystemExit('Refusing to overwrite an existing report')
    report=run(args.repo.resolve(),list(SITES) if args.site=='both' else [args.site])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'report':str(args.out),'checked_targets':len(report['results']),
                      'all_targets_match':report['all_targets_match'],'publication_allowed':False},indent=2))
    return 0 if report['all_targets_match'] else 1
if __name__=='__main__':raise SystemExit(main())
