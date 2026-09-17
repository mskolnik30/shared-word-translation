import json,re,hashlib,sys,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[3]; A=Path(__file__).resolve().parent
S=Path(sys.argv[1]);q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());ix={}
key=lambda s:re.sub(r'\s','',s).replace('Psalms','Psalm')
for item in q['completed_draft_scopes']:
 l=json.loads((R/item['ledger']).read_text())
 for v in l['verses']:
  c=next(c for c in l['chapters'] if c['chapter']==int(re.search(r'(\d+):\d+$',v['reference'])[1]))
  ix[key(v['reference'])]={**v,'source':l['source'],'path':c['path'],'ledger':item['ledger']}
sp={hashlib.sha256(p.read_bytes()).hexdigest():p for p in S.iterdir() if p.suffix in ['.xml','.txt']};raw={}
for h,p in sp.items():
 if p.suffix=='.xml':
  d={}
  for record in re.findall(r'<verse\b[^>]*>.*?</verse>',p.read_text(),re.S):
   e=ET.fromstring(record);b,c,v=e.attrib['osisID'].split('.');d[f'{b} {c}:{v}']=record
 else:d=dict(x.split('\t',1) for x in p.read_text().splitlines() if '\t' in x)
 raw[h]=d
refs=[r['reference'] for r in json.loads((A/'verse-metrics.json').read_text()) if r['identical'] and r['word_count']>=25]
select={'Genesis':{1:[1,2,3,4,5]},'Exodus':{3:[14]},'Leviticus':{19:[18]},'Numbers':{6:[24,25,26]},'Deuteronomy':{6:[4]},'Ruth':{1:[16]},'Job':{19:[25,26,27]},'Psalms':{23:list(range(1,7))},'Proverbs':{8:[22]},'Ecclesiastes':{3:list(range(1,9))},'Isaiah':{7:[14],9:[6],42:[14],53:[4,5,6],66:[13]},'Jeremiah':{7:[5,6,7]},'Daniel':{7:[13]},'Micah':{6:[8]},'John':{1:[1,18],3:[16]},'Romans':{3:[22]},'Galatians':{2:[16,20],3:[28]},'Philippians':{2:list(range(6,12))},'1 Timothy':{2:[12]},'Revelation':{2:[23],7:[5,6,7,8],13:[8],21:[7],22:[14]},'Joshua':{12:list(range(10,24))}}
for b,cs in select.items():
 for c,vs in cs.items():refs.extend(f'{b} {c}:{v}' for v in vs)
rows=[]
for ref in dict.fromkeys(refs):
 v=ix[key(ref)];records=[{'reference':s['source_reference'],'payload':raw[v['source']['sha256']][s['source_reference']],'sha256':s['source_verse_sha256']} for s in v.get('source_segments',[v])]
 for s in records:
  assert hashlib.sha256(s['payload'].encode()).hexdigest()==s['sha256']
  if s['payload'].startswith('<'):s['reading_text']=' '.join(''.join(e.itertext()) for e in ET.fromstring(s['payload']) if e.tag.split('}')[-1]=='w')
  else:s['reading_text']=s['payload']
 rows.append({**v,'public_reference':ref,'exact_source_records':records})
(A/'targeted-source-evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('Extracted',len(rows),'source comparisons; extraction is not review.')
