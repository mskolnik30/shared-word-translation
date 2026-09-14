"""Cumulative source bindings, structural checks, and preservation; not editorial approval."""
from pathlib import Path
import argparse,json,subprocess,sys,re,hashlib,xml.etree.ElementTree as E,datetime
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='f35c4160019aa32e5b0c0f4af167df1759cde7d0'
sha=lambda b:hashlib.sha256(b).hexdigest()
def run(*a):
 p=subprocess.run(a,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());audits=[];paths=set()
 names={'Gen':'genesis','Exod':'exodus','Lev':'leviticus','Num':'numbers','Deut':'deuteronomy','Josh':'joshua','Judg':'judges','Ruth':'ruth','1Sam':'1samuel','2Sam':'2samuel'}
 for sc in q['completed_draft_scopes']:
  l=json.loads((ROOT/sc['ledger']).read_text());bk=names.get(l['source'].get('osis_book_id'),'james');s=sd/(bk+'-pinned-'+('greek.txt' if bk=='james' else 'hebrew.xml'))
  audits.append({'ledger':sc['ledger'],**json.loads(run(sys.executable,'tools/audit_fluent_revision.py',sc['ledger'],'--source-text',str(s)))})
  for c in l['chapters']:assert c['path'] not in paths;paths.add(c['path'])
 assert len(audits)==55 and len(paths)==277 and sum(x['verses'] for x in audits)==8266
 structural=[];allowed={'audit/fluent-revision/WORK_QUEUE.json'};allv={};focused_counts={};all_1sam_sources=[]
 for sc in q['completed_draft_scopes']:
  l=json.loads((ROOT/sc['ledger']).read_text())
  if l['source'].get('osis_book_id')=='1Sam':
   for v in l['verses']:all_1sam_sources.extend(s['source_reference']for s in v.get('source_segments',[v]))
 assert len(all_1sam_sources)==len(set(all_1sam_sources))==811
 for bk,pre,name,start,end in [('1samuel','1Samuel','1 Samuel',17,31),('2samuel','2Samuel','2 Samuel',1,5)]:
  ad=ROOT/f'audit/fluent-revision/2026-09-14-{bk}-{start}-{end}';l=json.loads((ad/f'{bk}-verse-review.json').read_text());allv.update({v['reference']:v for v in l['verses']});rd=f'audit/exegetical-core/fluent-production/{bk}/'
  for c in l['chapters']:
   t=(ROOT/c['path']).read_text();m=t.split('---',2)[2].split('## Notes')[0];inside=False
   for line in m.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['path'],line)
   assert not inside
   assert all(s in t.split('---',2)[1] for s in ['status: QA_PASSED','qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   original=run('git','show',BASE+':'+c['path']).split('---',2)[1]
   assert all(line in t.split('---',2)[1]for line in original.strip().splitlines())
   rp=rd+f'{pre}_{c["chapter"]:02}_review.json';rv=json.loads((ROOT/rp).read_text());assert rv['chapter_binding']==c and rv['publication_allowed'] is False and rv['status']=='REVIEW_PENDING';allowed|={c['path'],rp}
   structural.append({'path':c['path'],'verses':c['verse_count'],'sha256':c['after_sha256'],'paragraphs':m.count('<p>'),'poetry_and_verse_lines_inside_paragraphs':True})
  for fn in [f'{bk[0]}_SAMUEL_FLUENT_BOOK_QA.json','APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
   rel=rd+fn;allowed.add(rel);prev=json.loads(run('git','show',BASE+':'+rel));now=json.loads((ROOT/rel).read_text());assert now['publication_allowed'] is False
   assert now['current_revision']['editorial_status']=='REVIEW_PENDING'
   assert now['revision_batches'][:-1]==prev.get('revision_batches',[])
   for k in ['human_textual_review','source_lock','resolved_f3']:
    if k in prev:assert now[k]==prev[k],(rel,k)
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(prev['entries'])==len(now['entries'])
    for a,b in zip(prev['entries'],now['entries']):
     if not start<=a['chapter']<=end:assert a==b
     else:
      assert all(b[k]==v for k,v in a.items() if k not in ('status','superseded_by'))
      assert b['historical_status_before_revision']==a.get('status') and b['status']=='SUPERSEDED'
  selected=json.loads((ad/'focused-selection.json').read_text());raw={}
  for s in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/(bk+'-pinned-hebrew.xml')).read_text(),re.S):
   e=E.fromstring(s);ob,c,v=e.attrib['osisID'].split('.');raw[f'{ob} {int(c)}:{int(v)}']=(s,e)
  focused=[]
  for key in selected:
   v=allv[key];segments=[]
   for segment in v.get('source_segments',[v]):
    sr=segment['source_reference'];s,e=raw[sr];assert sha(s.encode())==segment['source_verse_sha256'];segments.append({'source_reference':sr,'source_verse_sha256':segment['source_verse_sha256'],'hebrew':' '.join(''.join(x.itertext())for x in e if x.tag=='w'),'annotations':[E.tostring(x,encoding='unicode')for x in e if x.tag=='note']})
   focused.append({'reference':key,'source_segments':segments,'after':v['after'],'rationale':v['rationale']})
  focused_counts[bk]={'public_verses':len(focused),'source_records':sum(len(v['source_segments'])for v in focused)}
  (ad/'focused-comparisons.json').write_text(json.dumps({'qualification':'Selected authoring reread after the complete first Hebrew reading and source-led drafting; not independent editorial review.','rows':focused},ensure_ascii=False,indent=2)+'\n')
 checks={'1 Samuel 17:4':['six cubits','span'],'1 Samuel 17:5':['five thousand shekels'],'1 Samuel 17:7':['six hundred shekels'],'1 Samuel 17:12':['eight sons'],'1 Samuel 17:16':['forty days','morning and evening'],'1 Samuel 17:18':['ten','cheese','thousand'],'1 Samuel 17:50':['killed'],'1 Samuel 17:51':['killed','head'],'1 Samuel 18:10':['harmful spirit from God','prophesied'],'1 Samuel 18:25':['hundred','foreskins'],'1 Samuel 18:27':['two hundred','foreskins'],'1 Samuel 19:9':['harmful spirit from the LORD'],'1 Samuel 19:24':['naked'],'1 Samuel 20:16':['David’s enemies'],'1 Samuel 20:25':['Jonathan stood up'],'1 Samuel 20:30':['mother’s nakedness'],'1 Samuel 20:41':['three times','kissed','wept'],'1 Samuel 20:42':['David got up and left','Jonathan went'],'1 Samuel 21:5':['vessels'],'1 Samuel 22:18':['eighty-five'],'1 Samuel 22:19':['men and women','nursing infants','sword'],'1 Samuel 22:22':['deaths'],'1 Samuel 23:16':['strengthened his hand in God'],'1 Samuel 23:29':['En-gedi'],'1 Samuel 24:3':['relieve himself'],'1 Samuel 25:1':['Paran'],'1 Samuel 25:18':['two hundred loaves','two skins of wine','five prepared sheep','five seahs','hundred raisin','two hundred fig'],'1 Samuel 25:22':['David’s enemies','urinates against a wall'],'1 Samuel 25:29':['bundle of the living','sling'],'1 Samuel 25:34':['urinates against a wall'],'1 Samuel 26:12':['No one saw','no one knew','no one woke'],'1 Samuel 26:19':['scent','serve other gods'],'1 Samuel 27:7':['year and four months'],'1 Samuel 27:8':['Gizrites'],'1 Samuel 27:9':['neither man nor woman alive'],'1 Samuel 27:11':['report'],'1 Samuel 28:6':['dreams','Urim','prophets'],'1 Samuel 28:12':['saw Samuel'],'1 Samuel 28:13':['divine being'],'1 Samuel 28:19':['Tomorrow','with me'],'1 Samuel 29:3':['days or these years'],'1 Samuel 30:10':['four hundred','Two hundred','exhausted'],'1 Samuel 30:13':['slave','abandoned'],'1 Samuel 30:15':['not kill me','my master'],'1 Samuel 30:29':['Racal'],'1 Samuel 30:30':['Bor-ashan'],'1 Samuel 31:2':['Jonathan','Abinadab','Malchi-shua'],'1 Samuel 31:5':['Saul was dead'],'1 Samuel 31:12':['burned'],'1 Samuel 31:13':['bones','seven days'],'2 Samuel 1:10':['I stood over him and killed him'],'2 Samuel 1:22':['blood','fat'],'2 Samuel 1:26':['my brother Jonathan','beyond the love of women'],'2 Samuel 2:10':['forty years','two years'],'2 Samuel 2:11':['seven years and six months'],'2 Samuel 2:23':['butt','back'],'2 Samuel 2:30':['Nineteen','besides Asahel'],'2 Samuel 2:31':['three hundred sixty','killed'],'2 Samuel 3:3':['Chileab','Maacah','Talmai'],'2 Samuel 3:14':['hundred Philistine foreskins'],'2 Samuel 3:15':['her husband','Paltiel'],'2 Samuel 3:16':['weeping'],'2 Samuel 3:29':['spindle'],'2 Samuel 4:4':['five years','Mephibosheth'],'2 Samuel 4:12':['hands and feet','hung'],'2 Samuel 5:4':['thirty years','forty years'],'2 Samuel 5:5':['seven years and six months','thirty-three years'],'2 Samuel 5:8':['water shaft','lame and the blind','house'],'2 Samuel 5:21':['carried them away'],'2 Samuel 5:25':['Geba','Gezer']}
 for ref,terms in checks.items():
  for term in terms:assert term.casefold() in allv[ref]['after'].casefold(),(ref,term,allv[ref]['after'])
 song='Saul has struck down his thousands, and David his tens of thousands'
 for ref in ['1 Samuel 18:7','1 Samuel 21:11','1 Samuel 29:5']:assert song in allv[ref]['after']
 for ref in ['2 Samuel 1:19','2 Samuel 1:25','2 Samuel 1:27']:assert 'How the mighty have fallen' in allv[ref]['after']
 assert [x['source_reference']for x in allv['1 Samuel 20:42']['source_segments']]==['1Sam 20:42','1Sam 21:1']
 assert allv['1 Samuel 21:1']['source_reference']=='1Sam 21:2' and allv['1 Samuel 21:15']['source_reference']=='1Sam 21:16'
 assert allv['1 Samuel 23:29']['source_reference']=='1Sam 24:1' and allv['1 Samuel 24:22']['source_reference']=='1Sam 24:23'
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();ads=['audit/fluent-revision/2026-09-14-1samuel-17-31/','audit/fluent-revision/2026-09-14-2samuel-1-5/'];assert all(n in allowed or any(n.startswith(a)for a in ads)for n in changed),changed
 for sc in q['completed_draft_scopes'][:-2]:assert (ROOT/sc['ledger']).read_bytes()==subprocess.check_output(['git','show',BASE+':'+sc['ledger']],cwd=ROOT)
 assert q['next_work'][0]['scope']=='Whole-book 1 Samuel consistency review'
 result={'status':'PASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':BASE,'scope':'1 Samuel 17–31 and 2 Samuel 1–5','revision_audits':audits,'cumulative_coverage':{'chapters':277,'verses':8266},'structural_chapters':structural,'first_source_reading':{'public_verses':539,'original_records':540},'focused_source_reread':focused_counts,'focused_assertions':checks,'repeated_songs_checked':True,'all_1samuel_source_records_bound_once':811,'public_source_versification_checked':True,'translation_family_audit':run(sys.executable,'tools/audit_translation_family.py'),'git_diff_check':run('git','diff','--check'),'historical_provenance_and_unrelated_work_preserved':True,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASSED','ledgers':55,'chapters':20,'new_verses':539,'cumulative_verses':8266,'focused_reread':focused_counts}))
if __name__=='__main__':main()
