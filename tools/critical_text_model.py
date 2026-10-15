#!/usr/bin/env python3
"""Fail-closed Markdown/reader model for the October 2026 correction candidate.

No network or publishing. Paragraph/heading boundaries never silently discard
unowned words. Resolve an orphan in source Markdown before generating output.
Only the supported, deliberately small source format is accepted.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import hashlib,html,json,re,xml.etree.ElementTree as ET

class ContentError(ValueError):
    """Source cannot be safely represented without an explicit editorial repair."""

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def plain(text: str) -> str:
    # Deliberately do not turn arbitrary HTML into executable reader markup.
    return re.sub(r'\s+', ' ', text.replace('**','').replace('*','')).strip()

def frontmatter(raw: str) -> tuple[dict[str,Any],str]:
    match=re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)',raw,re.S)
    if not match: raise ContentError('Missing or malformed initial front matter')
    meta={}
    for line in match.group(1).splitlines():
        if not line.strip():continue
        if ':' not in line:raise ContentError(f'Unsupported metadata line: {line!r}')
        key,value=line.split(':',1);key=key.strip();value=value.strip()
        if key in meta:raise ContentError(f'Duplicate metadata key: {key}')
        if value in ('true','false'):v=value=='true'
        elif re.fullmatch(r'\d+',value):v=int(value)
        else:v=value.strip('"\'')
        meta[key]=v
    for k in ('book','testament','chapter','translation'):
        if k not in meta:raise ContentError(f'Missing metadata: {k}')
    return meta,raw[match.end():]

def parse_targets(ref: str, book: str, chapter: int) -> list[dict[str,Any]]:
    targets=[]
    for group in ref.split(';'):
        group=group.strip();target_chapter=chapter
        if ':' in group:
            prefix,group=group.split(':',1)
            if not prefix.strip().isdigit():raise ContentError(f'Invalid chapter reference: {ref}')
            target_chapter=int(prefix.strip())
            if target_chapter < 1:raise ContentError(f'Invalid chapter reference: {ref}')
        for atom in group.split(','):
            m=re.fullmatch(r'\s*v?(\d+)([a-z]?)(?:\s*[–—-]\s*v?(\d+)([a-z]?))?\s*',atom)
            if not m:raise ContentError(f'Unparseable reference: {ref!r}')
            start=int(m[1]);end=int(m[3]) if m[3] else start
            if start<1 or end<start or end>250:raise ContentError(f'Unsafe verse range: {ref}')
            if m[2] or m[4]:raise ContentError(f'Subverse reference needs explicit support: {ref}')
            for verse in range(start,end+1):
                item={'book_slug':book,'chapter':target_chapter,'verse':verse}
                if item not in targets:targets.append(item)
    return targets

def apparatus_entries(raw: str, book: str, chapter: int) -> list[dict[str,Any]]:
    entries=[];current=None
    for line in raw.splitlines():
        if not line.strip():
            if current is not None:current['raw_lines'].append('')
            continue
        # Delimiter is colon FOLLOWED BY WHITESPACE, never the internal 23:13 colon.
        m=re.match(r'^\s*(v\d[^\n]*?):[ \t]+(.*)$',line)
        if m:
            ref=m[1].strip();targets=parse_targets(ref,book,chapter)
            current={'ref':ref,'targets':targets,'verses':sorted({t['verse'] for t in targets if t['chapter']==chapter}), 'raw_lines':[m[2]]}
            entries.append(current)
        elif current is not None:
            if re.match(r'^\s*v\d',line):raise ContentError(f'Malformed apparatus entry: {line}')
            current['raw_lines'].append(line)
        else:
            raise ContentError(f'Apparatus prose without an explicit reference: {line!r}')
    for e in entries:e['raw_text']='\n'.join(e.pop('raw_lines')).strip()
    return entries

def vocabulary_fields(raw: str) -> dict[str,str]:
    text=raw.strip();first,*following=text.splitlines()
    first=first.replace('**','').replace('*','').strip()
    # Remove redundant legacy reference labels in the term, retaining them in raw_text.
    first=re.sub(r'^\d+:\d+(?:[–-]\d+)?\s*[—–]\s*','',first)
    m=re.match(r'^(.*?)(?::\s+|\s+[—–]\s+)(.+)$',first)
    if m:term=m[1].strip();definition=m[2].strip()
    else:term=first.rstrip(':');definition=''
    if following:definition='\n'.join(([definition] if definition else [])+following).strip()
    transliteration=''
    m=re.fullmatch(r'(.*?)\s*\(([^()]*)\)',term)
    if m and re.search(r'[\u0370-\u03ff\u1f00-\u1fff\u0590-\u05ff]',m[1]):
        term=m[1].strip();transliteration=m[2].strip()
    if not term:raise ContentError(f'Empty vocabulary term: {raw!r}')
    return {'term':term,'transliteration':transliteration,'definition':plain(definition),'html':html.escape(plain(definition)), 'raw_text':raw}

def parse_chapter(path: Path) -> dict[str,Any]:
    raw=path.read_text(encoding='utf-8');meta,rest=frontmatter(raw)
    slug=path.parent.name;chapter=int(meta['chapter']);blocks=[];verses=[]
    sections=re.split(r'^##\s+(Notes|Vocabulary)\s*$',rest,flags=re.M)
    body=sections[0];ap={}
    for i in range(1,len(sections),2):
        if sections[i] in ap:raise ContentError('Repeated apparatus section')
        ap[sections[i]]=sections[i+1]
    paragraph=None;current=None;inside=False
    for number,line in enumerate(body.splitlines(),1):
        s=line.strip()
        if not s:continue
        if re.match(r'^(?:---|book:|chapter:|testament:|translation:|revision_id:)',s):
            raise ContentError(f'Embedded metadata at body line {number}')
        if re.fullmatch(r'<p(?:\s[^>]*)?>',s):
            if inside:raise ContentError(f'Nested paragraph at line {number}')
            inside=True;paragraph=None;current=None;continue
        if s=='</p>':
            if not inside:raise ContentError(f'Unmatched paragraph close at line {number}')
            inside=False;paragraph=None;current=None;continue
        if re.match(r'^#{1,6}\s+',s):
            if inside:raise ContentError(f'Heading inside paragraph at line {number}')
            blocks.append({'type':'heading','text':re.sub(r'^#{1,6}\s+','',s)})
            paragraph=None;current=None;continue
        m=re.match(r'^v(\d+)([a-z]?):\s*(.*)$',s)
        if m:
            if m[2]:raise ContentError('Subverse labels need an explicit merge contract')
            v=int(m[1]);label=f'v{m[1]}'
            if any(x['number']==v for x in verses):raise ContentError(f'Duplicate verse label {v}')
            current={'number':v,'label':label,'text':'','lines':[m[3]] if m[3] else []}
            if paragraph is None:
                paragraph={'type':'paragraph','verses':[]};blocks.append(paragraph)
            paragraph['verses'].append(current);verses.append(current)
        else:
            if current is None:raise ContentError(f'Unowned Scripture text at body line {number}: {s!r}')
            if '<' in s or '>' in s:raise ContentError(f'Unsupported body markup at line {number}')
            current['lines'].append(s)
    if inside:raise ContentError('Unclosed paragraph')
    for v in verses:
        if any('<' in line or '>' in line for line in v['lines']):raise ContentError('Unsupported verse markup')
        v['text']=re.sub(r'\s+', ' ', ' '.join(v['lines'])).strip()
        if not v['text']:raise ContentError(f'Empty verse {v["number"]}')
    if not verses:raise ContentError('No verses')
    if [x['number'] for x in verses]!=sorted(x['number'] for x in verses):raise ContentError('Nonmonotonic verse order')
    notes=[]
    for e in apparatus_entries(ap.get('Notes',''),slug,chapter):
        notes.append({**e,'text':plain(e['raw_text']),'html':html.escape(plain(e['raw_text']))})
    vocab=[]
    for e in apparatus_entries(ap.get('Vocabulary',''),slug,chapter):
        vocab.append({**e,**vocabulary_fields(e['raw_text'])})
    return {'meta':meta,'book_slug':slug,'chapter':chapter,'blocks':blocks,'verses':verses,'notes':notes,'vocabulary':vocab,'source_sha256':sha256(raw.encode())}

OSIS='{http://www.bibletechnologies.net/2003/OSIS/namespace}'
def oshb_single_qere(verse: ET.Element) -> dict[str,Any]:
    """Separate direct written tokens and single-position qere; reject complex cases.
    This helper is NOT a replacement for a complete Hebrew apparatus adapter.
    """
    written=[];read=[];variants=[];last_ketiv=None
    for child in verse:
        tag=child.tag.rsplit('}',1)[-1]
        if tag=='w':
            if last_ketiv is not None:raise ContentError('Unpaired ketiv before next word requires review')
            token={'surface':child.text or '', 'lemma':child.get('lemma'),'morph':child.get('morph'),'id':child.get('id')}
            written.append(token);read.append(token.copy())
            last_ketiv=len(read)-1 if child.get('type')=='x-ketiv' else None
        elif tag=='note':
            rdgs=child.findall(f'{OSIS}rdg[@type="x-qere"]')
            if rdgs:
                if last_ketiv is None or len(rdgs)!=1:raise ContentError('Complex qere alignment requires review')
                words=rdgs[0].findall(f'{OSIS}w')
                if len(words)!=1:raise ContentError('Multiword qere requires review')
                w=words[0];token={'surface':w.text or '', 'lemma':w.get('lemma'),'morph':w.get('morph'),'id':w.get('id')}
                variants.append({'position':last_ketiv,'ketiv':read[last_ketiv].copy(),'qere':token.copy()})
                read[last_ketiv]=token;last_ketiv=None
            elif child.get('type')=='variant':raise ContentError('Unsupported variant note requires review')
        elif tag=='seg':continue
        else:raise ContentError(f'Unsupported source element: {tag}')
    if last_ketiv is not None:raise ContentError('Unpaired ketiv requires review')
    return {'written_tokens':written,'reading_tokens':read,'alternatives':variants}

def greek_markup(text: str) -> dict[str,Any]:
    """Inventory markers without confusing apparatus-unit delimiters and doubt."""
    return {'has_apparatus_unit_markers':bool(re.search('[⸀⸁⸂⸃⸄⸅]',text)),
            'has_square_doubt_brackets':'[' in text or ']' in text,
            'has_double_brackets':'[[' in text or ']]' in text or '⟦' in text or '⟧' in text,
            'source_text':text}
