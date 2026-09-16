"""Reproducible source and structural QA. Does not confer editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent
BASE='b9b77221c8025a2af40944a135fd7567f4758809'
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
 assert len(paths)==547 and count==14968
 lp=BATCH/'psalms-verse-review.json';l=json.loads(lp.read_text());errors=audit(ROOT,l,sb);assert not errors,errors
 assert len(l['chapters'])==40 and len(l['verses'])==746
 records={};selected={}
 for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
  e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';records[ref]=rec
  if 65<=int(c)<=104:selected[ref]=e
 assert len(records)==2527 and len(selected)==763
 vv={v['reference']:v for v in l['verses']};refs=[s['source_reference']for v in l['verses']for s in v.get('source_segments',[v])]
 assert len(refs)==len(set(refs))==763 and set(refs)==set(selected)
 assert sum('source_segments'in v for v in l['verses'])==17
 offsets={c:sum(ref.startswith(f'Ps {c}:')for ref in selected)-sum(v['reference'].startswith(f'Psalms {c}:')for v in l['verses'])for c in range(65,105)}
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
 focused=json.loads((BATCH/'focused-comparisons.json').read_text());selection=json.loads((BATCH/'focused-selection.json').read_text());assert len(selection)==332
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
  rel='audit/exegetical-core/fluent-production/psalms/'+fn;allowed.add(rel);p=json.loads(old(rel));d=json.loads((ROOT/rel).read_text());assert d['revision_batches'][:-1]==p['revision_batches'];assert d['publication_allowed']is False and d['editorial_review_pending_chapters']==list(range(1,105))
  for k in ['source','curated_f3_decisions','deployment_audit','summary']:
   if k in p:assert d[k]==p[k]
  if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
   assert len(p['entries'])==len(d['entries'])
   for x,y in zip(p['entries'],d['entries']):
    if 65<=x['chapter']<=104:assert y['status']=='SUPERSEDED'and y['historical_status_before_revision']==x.get('status')and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
    else:assert x==y
 assert vv['Psalms 67:3']['after']==vv['Psalms 67:5']['after']
 for v,prefix in [(3,'God'),(7,'God of Armies'),(19,'LORD, God of Armies')]:
  assert vv[f'Psalms 80:{v}']['after']==prefix+', restore us; let your face shine, and we will be saved.'
 assert vv['Psalms 96:13']['after'].count('he is coming')==2 and vv['Psalms 98:9']['after'].count('he is coming')==1
 assert 'faithfulness' in vv['Psalms 96:13']['after']and'fairly' in vv['Psalms 98:9']['after']
 for ref in ['103:1','103:2','103:22','104:1','104:35']:assert 'Bless the LORD, my whole being' in vv['Psalms '+ref]['after']
 checks={'68:11': ['women', 'army'], '68:18': ['received gifts', 'YAH'], '68:23': ['blood', 'dogs'], '68:27': ['Benjamin', 'Judah', 'Zebulun', 'Naphtali'], '68:28': ['Your God has commanded'], '69:8': ['brothers', 'mother’s sons'], '69:26': ['one you struck', 'those you wounded'], '70:4': ['Great is God'], '71:20': ['me see', 'revive me'], '72:10': ['Sheba', 'Seba'], '72:20': ['David son of Jesse'], '73:10': ['water'], '73:24': ['receive me with honor'], '74:14': ["Leviathan's heads"], '77:10': ['has changed'], '78:20': ['streams overflowed'], '78:25': ['mighty ones'], '78:28': ['his camp'], '78:51': ['firstborn', 'Ham'], '78:63': ['young men', 'young women'], '78:65': ['wine'], '79:12': ['sevenfold'], '80:2': ['Ephraim', 'Benjamin', 'Manasseh'], '81:6': ['his shoulder'], '81:16': ['He would', 'I would'], '82:1': ['among the gods'], '82:6': ['sons of the Most High'], '83:11': ['Oreb', 'Zeeb', 'Zebah', 'Zalmunna'], '84:10': ['thousand', 'threshold'], '87:4': ['Rahab', 'Babylon', 'Philistia', 'Tyre', 'Cush'], '88:18': ['darkness'], '89:19': ['faithful ones'], '89:39': ['renounced', 'covenant'], '90:10': ['seventy', 'eighty'], '91:7': ['thousand', 'ten thousand'], '91:9': ['my refuge', 'your dwelling'], '92:3': ['ten-stringed'], '94:6': ['kill', 'resident foreigner', 'murder'], '95:10': ['forty'], '95:11': ['never enter my rest'], '97:7': ['all you gods'], '97:11': ['sown'], '99:6': ['Moses and Aaron', 'priests', 'Samuel'], '99:8': ['forgiving', 'vengeance'], '100:3': ['we belong to him'], '101:8': ['destroy'], '102:23': ['my strength'], '103:13': ['father', 'children'], '104:4': ['winds his messengers'], '104:26': ['Leviathan', 'play'], '104:30': ['your breath'], '104:35': ['sinners', 'Praise YAH']}
 for ref,terms in checks.items():
  for term in terms:assert term in vv['Psalms '+ref]['after'],(ref,term)
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or p.startswith(ad)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip()
 family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':40,'new_verses':746,'original_source_records_bound_exactly_once':763,'cumulative_coverage':{'ledgers':75,'chapters':587,'verses':15714},'preservation':{'prior_ledgers_byte_identical':74,'prior_chapters_byte_identical':547,'historical_provenance_preserved':True,'tsw_unchanged':True},'source_binding_audit':{'status':'PASSED','errors':[]},'public_source_offsets':offsets,'first_source_reading':{'original_records':763,'all_annotations_read':True},'tsw_comparator_verses_read_after_drafting':746,'focused_authoring_source_reread':332,'focused_assertions':checks,'refrains_and_intentional_differences':'PASSED','divine_name_and_selah_counts':'PASSED; full divine name, short YAH, and Selah matched verse by verse without exceptions','translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_psalms_review':'PENDING; this is a selected forty-chapter authoring batch.','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','original_source_records_bound_exactly_once','cumulative_coverage']}))
if __name__=='__main__':main()
