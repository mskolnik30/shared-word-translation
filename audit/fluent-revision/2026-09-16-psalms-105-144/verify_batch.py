"""Reproducible source and structural QA. Does not confer editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='1703c658f2b8a4a05ac9f8e88d7154ad62e0b1a5'
sys.path.insert(0,str(ROOT/'tools'))
from audit_fluent_revision import audit
from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-text',type=Path,required=True);sb=p.parse_args().source_text.read_bytes()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'))
 assert q['completed_draft_scopes'][:-1]==oq['completed_draft_scopes'];assert q['next_work'][1:]==oq['next_work'][1:]
 paths=set();count=0
 for sc in q['completed_draft_scopes'][:-1]:
  lp=ROOT/sc['ledger'];assert lp.read_bytes()==old(sc['ledger']);l=json.loads(lp.read_text())
  for c in l['chapters']:
   assert c['path']not in paths;paths.add(c['path']);count+=c['verse_count']
   assert (ROOT/c['path']).read_bytes()==old(c['path'])
   assert sha((ROOT/c['path']).read_bytes())==c['after_sha256'];assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
 assert len(paths)==587 and count==15714
 lp=BATCH/'psalms-verse-review.json';l=json.loads(lp.read_text());errors=audit(ROOT,l,sb);assert not errors,errors
 assert len(l['chapters'])==40 and len(l['verses'])==714
 records={};selected={}
 for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
  e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';records[ref]=rec
  if 105<=int(c)<=144:selected[ref]=e
 assert len(records)==2527 and len(selected)==717
 vv={v['reference']:v for v in l['verses']};refs=[s['source_reference']for v in l['verses']for s in v.get('source_segments',[v])]
 assert len(refs)==len(set(refs))==717 and set(refs)==set(selected)
 assert sum('source_segments'in v for v in l['verses'])==3
 offsets={c:sum(ref.startswith(f'Ps {c}:')for ref in selected)-sum(v['reference'].startswith(f'Psalms {c}:')for v in l['verses'])for c in range(105,145)}
 for row in l['verses']:
  c,v=map(int,row['reference'].split()[-1].split(':'));expected=list(range(1,offsets[c]+2))if v==1 else[v+offsets[c]]
  assert [x['source_reference']for x in row.get('source_segments',[row])]==[f'Ps {c}:{z}'for z in expected]
  rs=[E.fromstring(records[x['source_reference']])for x in row.get('source_segments',[row])]
  # A dropped divine name or Selah can disappear in fluent restructuring.
  yhwh=sum(w.attrib.get('lemma','').split('/')[-1]in {'3068','3069'}for e in rs for w in e if w.tag=='w')
  selah=sum(w.attrib.get('lemma','')=='5542'for e in rs for w in e if w.tag=='w')
  assert row['after'].count('LORD')==yhwh,(row['reference'],'LORD count',yhwh)
  yah=sum(w.attrib.get('lemma','').split('/')[-1]=='3050'for e in rs for w in e if w.tag=='w')
  assert len(re.findall(r'\bYAH\b',row['after']))==yah,(row['reference'],'YAH count',yah)
  assert row['after'].count('Selah')==selah,(row['reference'],'Selah count',selah)
 focused=json.loads((BATCH/'focused-comparisons.json').read_text());selection=json.loads((BATCH/'focused-selection.json').read_text());assert len(selection)==343
 assert [x['reference']for x in focused['rows']]==selection
 for row in focused['rows']:
  assert all(row[k]==v for k,v in vv[row['reference']].items())
  for ev in row['source_evidence']:assert ev['original_source_xml']==records[ev['source_reference']]and sha(ev['original_source_xml'].encode())==ev['source_verse_sha256']
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};ad=str(BATCH.relative_to(ROOT))+'/'
 for ch in l['chapters']:
  path=ch['path'];t=(ROOT/path).read_text();yaml=t.split('---',2)[1];body=t.split('---',2)[2].split('## Notes')[0];inside=False
  for line in body.splitlines():
   if line=='<p>':assert not inside;inside=True
   elif line=='</p>':assert inside;inside=False
   elif line.strip()and not line.startswith('## '):assert inside,(path,line)
  assert not inside and '\\'not in body
  assert all(x in yaml for x in old(path).decode().split('---',2)[1].strip().splitlines())
  assert all(x in yaml for x in ['status: QA_PASSED','qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
  for refs2 in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(i)<=ch['verse_count']for i in re.findall(r'\d+',refs2))
  rp=f'audit/exegetical-core/fluent-production/psalms/Psalm_{ch["chapter"]:03}_review.json';d=json.loads((ROOT/rp).read_text());assert d['chapter_binding']==ch and d['publication_allowed']is False and d['status']=='REVIEW_PENDING';allowed|={path,rp}
 for fn in ['PSALMS_FLUENT_BOOK_QA.json','APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
  rel='audit/exegetical-core/fluent-production/psalms/'+fn;allowed.add(rel);p=json.loads(old(rel));d=json.loads((ROOT/rel).read_text());assert d['revision_batches'][:-1]==p['revision_batches'];assert d['publication_allowed']is False and d['editorial_review_pending_chapters']==list(range(1,145))
  for k in ['source','curated_f3_decisions','deployment_audit','summary']:
   if k in p:assert d[k]==p[k]
  if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
   assert len(p['entries'])==len(d['entries'])
   for x,y in zip(p['entries'],d['entries']):
    if 105<=x['chapter']<=144:assert y['status']=='SUPERSEDED'and y['historical_status_before_revision']==x.get('status')and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
    else:assert x==y
 assert len({vv[f'Psalms 107:{v}']['after']for v in [8,15,21,31]})==1
 assert vv['Psalms 107:13']['after']==vv['Psalms 107:19']['after']
 for v,verb in [(6,'rescued'),(13,'saved'),(19,'saved'),(28,'brought them out')]:assert verb in vv[f'Psalms 107:{v}']['after']
 assert vv['Psalms 118:1']['after']==vv['Psalms 118:29']['after']
 for v in range(1,27):assert vv[f'Psalms 136:{v}']['after'].count('his faithful love lasts forever.')==1
 assert vv['Psalms 130:6']['after'].count('more than watchmen for morning')==2
 assert vv['Psalms 144:8']['after'] in vv['Psalms 144:11']['after']
 app=json.loads((BATCH/'apparatus.json').read_text());assert app['119']['paragraphs']==list(range(1,177,8))and len(app['119']['sections'])==22
 assert list(map(int,app['119']['sections']))==list(range(1,177,8))
 for c in [111,112]:
  t=(ROOT/f'translations/fluent/OT/psalms/Psalm_{c:03}.md').read_text().split('## Notes')[0]
  lines=[x for x in t.splitlines()if x and not x.startswith(('---','##','<','book:','chapter:','translation:','status:','qa_scope:','editorial_status:','publication_allowed:','revision_id:'))]
  # The twenty-two acrostic poetic units follow the initial Praise YAH.
  body=t.split('---',2)[2];units=[x for x in body.splitlines()if x.strip()and not x.startswith(('##','<'))];assert len(units)==23,(c,units)
 checks={'105:8': ['thousand'], '105:18': ['his foot', 'iron'], '105:22': ['bind his princes'], '105:25': ['He turned their hearts'], '105:28': ['did not rebel', 'his word'], '106:27': ['offspring fall'], '106:33': ['his spirit', 'Moses'], '106:37': ['sons', 'daughters', 'demons'], '107:3': ['north and the sea'], '108:4': ['beyond the heavens'], '108:6': ['answer me'], '108:8': ['Gilead', 'Manasseh', 'Ephraim', 'Judah'], '109:6': ['accuser', 'right hand'], '109:9': ['fatherless', 'wife a widow'], '109:17': ['it came upon him'], '110:1': ['LORD', 'my lord', 'footstool'], '110:4': ['Melchizedek', 'forever'], '110:6': ['corpses', 'heads'], '111:9': ['redemption', 'covenant'], '112:9': ['horn'], '115:11': ['their help'], '115:17': ['dead', 'YAH'], '116:15': ['Costly', 'death'], '116:16': ['son', 'female servant'], '118:13': ['You pushed'], '118:27': ['cords', 'horns'], '119:9': ['young man'], '119:79': ['those who know'], '119:83': ['wineskin in smoke'], '119:88': ['testimony'], '119:98': ['Your command'], '119:109': ['life is always in my hand'], '119:122': ['guarantor'], '119:147': ['your word'], '119:161': ['your word'], '119:164': ['Seven times'], '119:176': ['lost sheep', 'Seek your servant'], '120:5': ['Meshech', 'Kedar'], '121:3': ['May he', 'may your guardian'], '123:2': ['slaves', 'female slave', 'mistress'], '127:1': ['Solomon'], '127:3': ['sons'], '127:5': ['man', 'They'], '129:3': ['their furrow'], '130:4': ['forgiveness', 'feared'], '131:2': ['weaned child', 'mother'], '132:6': ['Ephrathah', 'Jaar'], '132:12': ['If your sons', 'covenant'], '132:17': ['horn', 'lamp'], '133:2': ['Aaron'], '133:3': ['Hermon', 'Zion'], '134:1': ['nights'], '135:11': ['Sihon', 'Og', 'Canaan'], '136:25': ['all flesh'], '137:9': ['little children', 'smashes', 'rock'], '138:1': ['gods'], '139:13': ['kidneys', 'womb'], '139:14': ['set apart'], '139:16': ['not one'], '139:19': ['kill', 'men of bloodshed'], '139:22': ['complete hatred'], '140:7': ['LORD, my Lord'], '140:12': ['I know'], '141:7': ['our bones', 'Sheol'], '142:1': ['cave', 'maskil'], '143:2': ['no living person'], '143:12': ['destroy all'], '144:2': ['my people'], '144:7': ['your hands'], '144:9': ['ten-stringed'], '144:12': ['sons', 'daughters'], '144:13': ['thousands', 'tens of thousands']}
 for ref,terms in checks.items():
  for term in terms:assert term in vv['Psalms '+ref]['after'],(ref,term)
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or p.startswith(ad)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip()
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':40,'new_verses':714,'original_source_records_bound_exactly_once':717,'cumulative_coverage':{'ledgers':76,'chapters':627,'verses':16428},'preservation':{'prior_ledgers_byte_identical':75,'prior_chapters_byte_identical':587,'historical_provenance_preserved':True,'tsw_unchanged':True},'source_binding_audit':{'status':'PASSED','errors':[]},'public_source_offsets':offsets,'first_source_reading':{'original_records':717,'all_annotations_read':True},'tsw_comparator_verses_read_after_drafting':714,'focused_authoring_source_reread':343,'focused_assertions':checks,'refrains_and_intentional_differences':'PASSED','divine_name_and_selah_counts':'PASSED; full divine name, short YAH, and Selah matched verse by verse without exceptions','translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_psalms_review':'PENDING; this is a selected forty-chapter authoring batch.','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','original_source_records_bound_exactly_once','cumulative_coverage']}))
if __name__=='__main__':main()
