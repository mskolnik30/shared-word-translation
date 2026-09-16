"""Reproducible structural/source checks; no independent editorial approval."""
from pathlib import Path
import argparse,collections,hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];BATCH=Path(__file__).resolve().parent;BASE='10f26b8d4f7f1388c7b9ac557aab217a21d92ca5'
sys.path.insert(0,str(ROOT/'tools'));from audit_fluent_revision import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
def run(*cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout
C=[('jeremiah','Jeremiah','Jeremiah',2,41,52,353,111),('lamentations','Lamentations','Lamentations',2,1,5,154,66)]
def qa_name(b):return ('SONG_OF_SONGS'if b=='songofsongs'else b.upper())+'_FLUENT_BOOK_QA.json'

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory.resolve();q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'));assert q['completed_draft_scopes'][:-2]==oq['completed_draft_scopes'];assert q['next_work'][1:len(oq['next_work'])]==oq['next_work'][1:]
 priorpaths=set();total=0
 for sc in oq['completed_draft_scopes']:
  p=ROOT/sc['ledger'];assert p.read_bytes()==old(sc['ledger']);l=json.loads(p.read_text())
  for ch in l['chapters']:
   assert ch['path']not in priorpaths;priorpaths.add(ch['path']);total+=ch['verse_count'];assert(ROOT/ch['path']).read_bytes()==old(ch['path']);assert sha((ROOT/ch['path']).read_bytes())==ch['after_sha256'];assert sha((ROOT/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert len(oq['completed_draft_scopes'])==86 and len(priorpaths)==790 and total==20065
 allowed={'audit/fluent-revision/WORK_QUEUE.json'};prefixes=[str(BATCH.relative_to(ROOT))+'/'];allvv={};allbooks={};sourcecounts={}
 for b,name,pre,width,lo,hi,N,F in C:
  rel=f'audit/fluent-revision/2026-09-16-{b}-{lo}-{hi}';a=ROOT/rel;prefixes.append(rel+'/');l=json.loads((a/f'{b}-verse-review.json').read_text());sb=(sd/f'{b}-pinned-hebrew.xml').read_bytes();errors=audit(ROOT,l,sb);assert not errors,errors
  assert len(l['chapters'])==hi-lo+1 and len(l['verses'])==N
  raw={};selected={}
  for rec in re.findall(r'<verse\b[^>]*>.*?</verse>',sb.decode(),re.S):
   e=E.fromstring(rec);o,c,v=e.attrib['osisID'].split('.');ref=f'{o} {c}:{v}';raw[ref]=rec
   if lo<=int(c)<=hi:selected[ref]=e
  assert len(raw)==l['source']['book_verse_count']and len(selected)==N-(1 if b=='isaiah'else 0)
  refs=[v['source_reference']for v in l['verses']];assert len(refs)==N and set(refs)==set(selected);assert len(set(refs))==len(selected);sourcecounts[b]=len(selected)
  vv={v['reference']:v for v in l['verses']};allvv.update(vv);allbooks[b]=l
  for row in l['verses']:
   e=selected[row['source_reference']];assert sha(raw[row['source_reference']].encode())==row['source_verse_sha256'];assert row['rationale'].strip()
   ws=[w for w in e if w.tag=='w'];part=row.get('source_partition');ws=ws[part['word_start']-1:part['word_end']]if part else ws;lemmas=[w.attrib.get('lemma','').split('/')[-1]for w in ws]
   assert sum(x in ['3068','3069']for x in lemmas)==len(re.findall(r'\b(?:LORD|GOD)\b',row['after'])),row['reference']
   assert lemmas.count('3050')==len(re.findall(r'\bYAH\b',row['after'])),row['reference']
  focus=json.loads((a/'focused-comparisons.json').read_text());sel=json.loads((a/'focused-selection.json').read_text());assert len(sel)==F and [x['reference']for x in focus['rows']]==sel
  for row in focus['rows']:
   assert all(row[k]==v for k,v in vv[row['reference']].items());assert row['original_source_xml']==raw[row['source_reference']]
  for ch in l['chapters']:
   path=ch['path'];assert path not in priorpaths;t=(ROOT/path).read_text();yaml=t.split('---',2)[1];body=t.split('---',2)[2].split('## Notes')[0];inside=False
   for line in body.splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip()and not line.startswith('## '):assert inside,(path,line)
   assert not inside and '\\'not in body
   assert all(x in yaml for x in old(path).decode().split('---',2)[1].strip().splitlines());assert all(x in yaml for x in ['status: QA_PASSED','qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false'])
   for ref in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(x)<=ch['verse_count']for x in re.findall(r'\d+',ref)),(path,ref)
   rp=f'audit/exegetical-core/fluent-production/{b}/{pre}_{ch["chapter"]:0{width}}_review.json';d=json.loads((ROOT/rp).read_text());assert d['chapter_binding']==ch and d['publication_allowed']is False and d['status']=='REVIEW_PENDING';allowed|={path,rp}
  for fn in [qa_name(b),'APPROVE_QA.json','BOOK_VERSE_REVIEW_LEDGER.json']:
   rp=f'audit/exegetical-core/fluent-production/{b}/{fn}';allowed.add(rp);d=json.loads((ROOT/rp).read_text());p=json.loads(old(rp));assert d['revision_batches'][:-1]==p.get('revision_batches',[]);assert d['publication_allowed']is False
   for k in ['source','curated_f3_decisions','deployment_audit','summary']:
    if k in p:assert d[k]==p[k]
   if fn=='BOOK_VERSE_REVIEW_LEDGER.json':
    assert len(d['entries'])==len(p['entries'])
    for x,y in zip(p['entries'],d['entries']):
     if lo<=x['chapter']<=hi:assert y['status']=='SUPERSEDED'and all(y[k]==v for k,v in x.items()if k not in ['status','superseded_by'])
     else:assert x==y
 # Focused mechanical guards support, but do not replace, the recorded source/English reread.
 checks={'Jeremiah 41:1': ['seventh', 'ten', 'Elishama'], 'Jeremiah 41:5': ['eighty', 'Shechem', 'Shiloh', 'Samaria', 'frankincense'], 'Jeremiah 41:8': ['ten', 'wheat', 'barley', 'oil', 'honey'], 'Jeremiah 41:15': ['eight'], 'Jeremiah 42:1': ['Jezaniah'], 'Jeremiah 42:7': ['Ten days'], 'Jeremiah 42:10': ['relented', 'build', 'plant'], 'Jeremiah 43:2': ['Azariah'], 'Jeremiah 43:6': ['daughters', 'Jeremiah', 'Baruch'], 'Jeremiah 44:19': ['husbands'], 'Jeremiah 44:26': ['Lord **GOD**'], 'Jeremiah 44:30': ['Hophra', 'Zedekiah', 'Nebuchadnezzar'], 'Jeremiah 45:1': ['fourth', 'Jehoiakim'], 'Jeremiah 45:5': ['life as plunder'], 'Jeremiah 46:2': ['Neco', 'Carchemish', 'fourth'], 'Jeremiah 46:9': ['Cush', 'Put', 'Ludim'], 'Jeremiah 47:3': ['fathers', 'children'], 'Jeremiah 48:10': ['sword', 'blood'], 'Jeremiah 48:19': ['man', 'woman'], 'Jeremiah 48:32': ['sea of Jazer'], 'Jeremiah 48:47': ['restore'], 'Jeremiah 49:6': ['restore'], 'Jeremiah 49:11': ['orphans', 'widows'], 'Jeremiah 49:39': ['restore'], 'Jeremiah 50:37': ['women'], 'Jeremiah 51:3': ['young men', 'destruction'], 'Jeremiah 51:27': ['Ararat', 'Minni', 'Ashkenaz'], 'Jeremiah 51:30': ['women'], 'Jeremiah 51:34': ['me', 'monster'], 'Jeremiah 51:64': ['grow weary', 'Here end'], 'Jeremiah 52:1': ['twenty-one', 'eleven', 'Hamutal'], 'Jeremiah 52:12': ['tenth', 'fifth', 'nineteenth'], 'Jeremiah 52:20': ['two', 'twelve', 'stands'], 'Jeremiah 52:21': ['eighteen', 'twelve', 'four', 'hollow'], 'Jeremiah 52:22': ['five'], 'Jeremiah 52:23': ['ninety-six', 'hundred'], 'Jeremiah 52:25': ['seven', 'sixty'], 'Jeremiah 52:28': ['3,023', 'seventh'], 'Jeremiah 52:29': ['832', 'eighteenth'], 'Jeremiah 52:30': ['745', '4,600', 'twenty-third'], 'Jeremiah 52:31': ['thirty-seventh', 'twenty-fifth', 'twelfth'], 'Lamentations 1:16': ['my eye, my eye'], 'Lamentations 2:11': ['liver'], 'Lamentations 2:20': ['eat', 'children'], 'Lamentations 3:1': ['man'], 'Lamentations 3:13': ['quiver', 'kidneys'], 'Lamentations 3:22': ['we have not come to an end'], 'Lamentations 3:42': ['not forgiven'], 'Lamentations 3:65': ['covering', 'curse'], 'Lamentations 4:10': ['compassionate', 'cooked', 'children'], 'Lamentations 4:20': ['anointed'], 'Lamentations 5:11': ['raped', 'virgins'], 'Lamentations 5:22': ['unless', 'rejected', 'angry']}
 for ref,terms in checks.items():
  for term in terms:assert term.lower()in allvv[ref]['after'].lower(),(ref,term)
 assert all(row['source_reference']==row['reference'].replace('Jeremiah','Jer').replace('Lamentations','Lam')for l in allbooks.values()for row in l['verses'])
 assert len(q['completed_draft_scopes'])==88
 cumulative=[ch for sc in q['completed_draft_scopes']for ch in json.loads((ROOT/sc['ledger']).read_text())['chapters']]
 assert len(cumulative)==807 and sum(ch['verse_count']for ch in cumulative)==20572
 block=q['active_fifty_chapter_block'];assert block['status']=='DRAFT_COMPLETED'and block['completed_chapters']==50 and block['remaining_chapters']==0 and block['completed_verses']==1311
 # Verify the alphabetic form described in Lamentations notes against the pinned source.
 alpha=list('אבגדהוזחטיכלמנסעפצקרשת');pefirst=alpha.copy();pefirst[15:17]=list('פע')
 for ch in range(1,5):
  es=[E.fromstring(x)for x in re.findall(r'<verse\b[^>]*>.*?</verse>',(sd/'lamentations-pinned-hebrew.xml').read_text(),re.S)if E.fromstring(x).attrib['osisID'].startswith(f'Lam.{ch}.')]
  initials=[re.sub('[^א-ת]','',''.join(list(e)[0].itertext()))[0]for e in es]
  expected=alpha if ch==1 else pefirst
  if ch==3:expected=[a for a in expected for _ in range(3)]
  assert initials==expected,(ch,initials)
 assert 3023+832+745==4600
 cipher=dict(zip(alpha,alpha[::-1]));assert ''.join(cipher[a]for a in 'ששכ')=='בבל';assert ''.join(cipher[a]for a in 'לבקמי')=='כשדימ'
 changed=run('git','diff','--name-only',BASE).splitlines()+run('git','ls-files','--others','--exclude-standard').splitlines();assert all(p in allowed or any(p.startswith(x)for x in prefixes)for p in changed),changed
 assert not run('git','diff',BASE,'--','books').strip();family=run(sys.executable,'tools/audit_translation_family.py');diff=run('git','diff','--check')
 result={'status':'PASSED','base_commit':BASE,'new_chapters':17,'new_verses':507,'unique_original_source_records':sourcecounts,'cumulative_coverage':{'ledgers':88,'chapters':807,'verses':20572},'prior_preservation':{'ledgers_byte_identical':86,'chapters_byte_identical':790,'verses':20065,'tsw_unchanged':True,'historical_provenance_preserved':True},'source_binding_audit':'PASSED for affected Jeremiah and Lamentations ledgers','divine_names':'PASSED verse by verse, including LORD/GOD and YAH separately','focused_assertions':checks,'versification':'All 507 selected public labels match the original Hebrew records. Lamentations alphabetic patterns verified from source.','repeated_refrains':'Divine-name repetitions checked verse by verse; recurring promise and judgment phrases reread.','focused_authoring_reread':177,'translation_family':family,'git_diff_check':diff,'independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','whole_book_consistency_reviews':'All prior pending reviews preserved.','active_fifty_chapter_block':block,'publication_allowed':False}
 (BATCH/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
