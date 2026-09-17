#!/usr/bin/env python3
"""Structural/source verification for John 18–21 and Acts 1–6."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from audit_fluent_revision import audit
PARENT='027d78b5e44b2c3983b66df0d4de64f9dac8c0fd'
SCOPES=[
 ('audit/fluent-revision/2026-09-16-john-18-21','john','john-pinned-greek.txt',138),
 ('audit/fluent-revision/2026-09-16-acts-1-6','acts','acts-pinned-greek.txt',193),
]
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def old(p):return subprocess.check_output(['git','show',PARENT+':'+p],cwd=ROOT)
def records(b):
 d={}
 for line in b.decode().splitlines():
  if '\t' in line:
   k,v=line.split('\t',1);assert k not in d;d[k]=v
 return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-directory',type=Path,required=True);ap.add_argument('--bind-focused-records',action='store_true');a=ap.parse_args()
 q=json.loads((ROOT/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'))
 assert len(oq['completed_draft_scopes'])==116 and q['completed_draft_scopes'][:-2]==oq['completed_draft_scopes'] and q['next_work'][4:]==oq['next_work'][1:]
 assert [x['scope'] for x in q['next_work'][1:4]]==['Whole-book Mark consistency review','Whole-book Luke consistency review','Whole-book John consistency review']
 prior=set();prior_v=0
 for sc in oq['completed_draft_scopes']:
  p=sc['ledger'];assert (ROOT/p).read_bytes()==old(p),p;l=json.loads((ROOT/p).read_text())
  for c in l['chapters']:
   assert c['path'] not in prior;prior.add(c['path']);prior_v+=c['verse_count']
   assert (ROOT/c['path']).read_bytes()==old(c['path']) and sha((ROOT/c['path']).read_bytes())==c['after_sha256']
   assert sha((ROOT/c['tsw_comparator_path']).read_bytes())==c['tsw_comparator_sha256']
 assert (len(prior),prior_v)==(1019,26882)
 ledgers=[];focus_total=0
 for rel,slug,fn,n in SCOPES:
  A=ROOT/rel;cfg=json.loads((A/'config.json').read_text());sb=(a.source_directory/fn).read_bytes()
  assert sha(sb)==cfg['source']['sha256']
  assert hashlib.sha1(b'blob '+str(len(sb)).encode()+b'\0'+sb).hexdigest()==cfg['source']['git_blob_sha']
  L=json.loads((A/f'{slug}-verse-review.json').read_text());errs=audit(ROOT,L,sb);assert not errs,errs
  assert L['summary']['verses_drafted']==n and L['status']=='REVIEW_PENDING' and L['qa_scope']=='structural' and L['publication_allowed'] is False
  src=records(sb);focus=[{**v,'exact_source_record':src[v['source_reference']]} for v in L['verses']];assert len(focus)==n
  record={'status':'AUTHORING_REREAD_COMPLETED','review_type':'Drafting assistant self-reread, not human or independent scholarly review','authoring_record_sha256':sha((A/'authoring-reread.md').read_bytes()),'rows':focus}
  if a.bind_focused_records:dump(A/'focused-comparisons.json',record);dump(A/'focused-selection.json',focus)
  else:assert json.loads((A/'focused-comparisons.json').read_text())==record and json.loads((A/'focused-selection.json').read_text())==focus
  ledgers.append(L);focus_total+=n
 john,acts=ledgers;j={v['reference'].split(' ',1)[1]:v['after'] for v in john['verses']};v={x['reference'].split(' ',1)[1]:x['after'] for x in acts['verses']}
 js=records((a.source_directory/'john-pinned-greek.txt').read_bytes());ss=records((a.source_directory/'acts-pinned-greek.txt').read_bytes())
 checks={
  'john_malchus':all(x in j['18:10'] for x in ['right ear','Malchus']),
  'john_gatekeeper_gender':'servant girl' in j['18:17'],
  'john_officer_violence':'slapped him' in j['18:22'] and 'hit me' in j['18:23'],
  'john_passover_purity':all(x in j['18:28'] for x in ['ceremonially unclean','Passover meal']),
  'john_kingdom_source':'does not come from this world' in j['18:36'],
  'john_barabbas':'violent rebel' in j['18:40'],
  'john_flogging':'flogged' in j['19:1'] and 'slapped' in j['19:3'],
  'john_no_charge':all('no basis for a charge' in j[x] for x in ['19:4','19:6']),
  'john_passover_noon':'preparation for Passover' in j['19:14'] and 'noon' in j['19:14'],
  'john_three_languages':all(x in j['19:20'] for x in ['Hebrew','Latin','Greek']),
  'john_four_soldiers':'four parts' in j['19:23'] and 'each soldier' in j['19:23'],
  'john_women_named':all(x in j['19:25'] for x in ['his mother','Mary the wife of Clopas','Mary Magdalene']),
  'john_completed':j['19:30'].startswith('After receiving') and 'It is completed' in j['19:30'],
  'john_leg_breaking':'broke the legs' in j['19:32'] and 'did not break' in j['19:33'],
  'john_spear_blood_water':all(x in j['19:34'] for x in ['spear','blood','water']),
  'john_hundred_pounds':'hundred Roman pounds' in j['19:39'],
  'john_mary_witness':'I have seen the Lord' in j['20:18'],
  'john_locked_fear':'doors' in j['20:19'] and 'locked' in j['20:19'] and 'Judean leaders' in j['20:19'],
  'john_breath_spirit':'breathed on them' in j['20:22'] and 'Holy Spirit' in j['20:22'],
  'john_thomas_wounds':all(x in j['20:25'] for x in ['nail marks','finger','side']),
  'john_thomas_confession':j['20:28']=='Thomas answered him, “My Lord and my God!”',
  'john_purpose':'Jesus is the Messiah, the Son of God' in j['20:31'],
  'john_153':'153 large fish' in j['21:11'] and 'net was not torn' in j['21:11'],
  'john_threefold':all('Simon son of John' in j[x] for x in ['21:15','21:16','21:17']) and 'third time' in j['21:17'],
  'john_peter_death':'kind of death' in j['21:19'] and 'glorify God' in j['21:19'],
  'john_rumor_corrected':'did not tell Peter that he would not die' in j['21:23'],
  'acts_forty_days':'forty days' in v['1:3'],
  'acts_geography':all(x in v['1:8'] for x in ['Jerusalem','Judea','Samaria','ends of the earth']),
  'acts_women_mary_brothers':all(x in v['1:14'] for x in ['women','Mary the mother of Jesus','brothers']),
  'acts_120':'about 120 people' in v['1:15'],
  'acts_judas_harm':all(x in v['1:18'] for x in ['headfirst','burst open','insides spilled out']),
  'acts_candidate_span':all(x in v['1:22'] for x in ['John’s baptism','taken up','witness','resurrection']),
  'acts_matthias':'Matthias' in v['1:26'] and 'eleven apostles' in v['1:26'],
  'acts_languages':all(x in v['2:4'] for x in ['Holy Spirit','other languages']),
  'acts_nations':all(x in ' '.join(v[f'2:{n}'] for n in range(9,12)) for x in ['Parthians','Medes','Elamites','Rome','Cretans','Arabs']),
  'acts_gendered_prophecy':all(x in ' '.join([v['2:17'],v['2:18']]) for x in ['sons','daughters','young men','elders','male slaves','female slaves']),
  'acts_cross_agency':all(x in v['2:23'] for x in ['determined plan','foreknowledge','you killed him','lawless people']),
  'acts_three_thousand':'about three thousand people' in v['2:41'],
  'acts_four_practices':all(x in v['2:42'] for x in ['teaching','fellowship','breaking of bread','prayers']),
  'acts_need_sharing':'according to each person’s need' in v['2:45'],
  'acts_congenital_condition':'from his mother’s womb' in v['3:2'],
  'acts_feet_ankles':all(x in v['3:7'] for x in ['feet','ankles']),
  'acts_murderer':'murderer' in v['3:14'] and 'Author of life' in v['3:15'],
  'acts_restoration':'everything is restored' in v['3:21'],
  'acts_five_thousand_men':'about five thousand' in v['4:4'] and 'men' in v['4:4'],
  'acts_cornerstone':'cornerstone' in v['4:11'],
  'acts_no_other_name':'no other name under heaven' in v['4:12'],
  'acts_creation_prayer':all(x in v['4:24'] for x in ['heaven','earth','sea']),
  'acts_agents_named':all(x in v['4:27'] for x in ['Herod','Pontius Pilate','Gentiles','Israel']),
  'acts_no_needy':'not a needy person' in v['4:34'] and 'according to need' in v['4:35'],
  'acts_ananias_sapphira':all(x in v['5:1'] for x in ['Ananias','wife Sapphira']),
  'acts_property_control':'remain yours' in v['5:4'] and 'under your authority' in v['5:4'],
  'acts_deaths':v['5:5'].endswith('heard about it.') and 'died' in v['5:5'] and 'died' in v['5:10'],
  'acts_men_women':'both men and women' in v['5:14'],
  'acts_shadow_reported':'shadow might fall' in v['5:15'],
  'acts_no_violence_stoning':'without violence' in v['5:26'] and 'stone them' in v['5:26'],
  'acts_tree':'hanging him on a tree' in v['5:30'],
  'acts_beaten':'beaten' in v['5:40'] and 'dishonor' in v['5:41'],
  'acts_widows_language_groups':all(x in v['6:1'] for x in ['Greek-speaking Jewish believers','Hebrew-speaking believers','widows','daily distribution']),
  'acts_seven_men':all(x in v['6:3'] for x in ['seven men','Spirit','wisdom']),
  'acts_seven_names':all(x in v['6:5'] for x in ['Stephen','Philip','Prochorus','Nicanor','Timon','Parmenas','Nicolaus']),
  'acts_false_witnesses':'false witnesses' in v['6:13'],
  'acts_angel_face':'face was like the face of an angel' in v['6:15'],
  'variant_payloads_retained':'⸀' in js['John 20:31'] and '⸂' in ss['Acts 1:5']
 }
 assert all(checks.values()),[k for k,x in checks.items() if not x]
 affected=[]
 for p,fn in [('audit/fluent-revision/2026-09-16-john-1-17/john-verse-review.json','john-pinned-greek.txt')]:
  e=audit(ROOT,json.loads((ROOT/p).read_text()),(a.source_directory/fn).read_bytes());assert not e,e;affected.append(p)
 for L in ledgers:
  for c in L['chapters']:
   assert c['path'] not in prior;t=(ROOT/c['path']).read_text();main=t.split('## Notes')[0]
   assert all(x in t for x in ['qa_scope: structural','editorial_status: REVIEW_PENDING','publication_allowed: false','## Notes','## Vocabulary'])
   assert len(re.findall(r'^v\d\d:',main,re.M))==c['verse_count']
   prior_text=old(c['path']).decode().split('## Notes')[0]
   assert abs(main.count('“')-main.count('”'))<=abs(prior_text.count('“')-prior_text.count('”'))
   inside=False
   for line in main.split('---',2)[2].splitlines():
    if line=='<p>':assert not inside;inside=True
    elif line=='</p>':assert inside;inside=False
    elif line.strip() and not line.startswith('## '):assert inside,(c['path'],line)
   assert not inside
 for slug,names,chs,ledger_rel in [
  ('john',['JOHN_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json'],list(range(18,22)),SCOPES[0][0]+'/john-verse-review.json'),
  ('acts',['ACTS_FLUENT_BOOK_QA.json','BOOK_VERSE_REVIEW_LEDGER.json'],list(range(1,7)),SCOPES[1][0]+'/acts-verse-review.json')]:
  for name in names:
   p=f'audit/exegetical-core/fluent-production/{slug}/{name}';d=json.loads((ROOT/p).read_text());od=json.loads(old(p))
   assert d['source']==od['source'] and d['revision_batches'][:-1]==od.get('revision_batches',[]) and d['revision_batches'][-1]['chapters']==chs and d['revision_batches'][-1]['verse_ledger']==ledger_rel and not d['publication_allowed']
   if 'entries' in od:
    assert len(d['entries'])==len(od['entries'])
    for e,oe in zip(d['entries'],od['entries']):
     if e['chapter'] in chs:assert e['status']=='SUPERSEDED' and e['superseded_by_verse_ledger']==ledger_rel and all(e[k]==x for k,x in oe.items())
     else:assert e==oe
    assert d['summary']==od['summary']
 subprocess.run(['git','diff','--check',PARENT],cwd=ROOT,check=True)
 assert not subprocess.check_output(['git','diff',PARENT,'--','books','companions'],cwd=ROOT).strip()
 family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=ROOT).decode()
 chapters=[]
 for sc in q['completed_draft_scopes']:chapters+=json.loads((ROOT/sc['ledger']).read_text())['chapters']
 assert len(q['completed_draft_scopes'])==118 and len({c['path'] for c in chapters})==len(chapters)==1029 and sum(c['verse_count'] for c in chapters)==27213
 block=q['active_fifty_chapter_block'];assert (block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==(22,28,859)
 allowed={'audit/fluent-revision/WORK_QUEUE.json','tools/package_fluent_checkpoint.py'}
 for rel,slug,_,_ in SCOPES:
  allowed.update(subprocess.check_output(['find',rel,'-type','f'],cwd=ROOT).decode().splitlines());L=json.loads((ROOT/rel/f'{slug}-verse-review.json').read_text())
  for c in L['chapters']:
   allowed.add(c['path']);allowed.add(f'audit/exegetical-core/fluent-production/{slug}/'+Path(c['path']).name.replace('.md','_review.json'))
  cfg=json.loads((ROOT/rel/'config.json').read_text());allowed.update(f'audit/exegetical-core/fluent-production/{slug}/{n}' for n in cfg['book_record_files'])
 changed=subprocess.check_output(['git','diff','--name-only',PARENT],cwd=ROOT).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT).decode().splitlines()
 unexpected=[p for p in changed if p not in allowed and p!='.fluent-revision-writer.lock'];assert not unexpected,unexpected
 result={'status':'PASSED','qa_scope':'structural','parent_commit':PARENT,'batch_scope':'John 18–21; Acts 1–6','new_chapters':10,'new_verses':331,'cumulative_coverage':{'ledgers':118,'chapters':1029,'verses':27213},'prior_preservation':{'ledgers_byte_identical':116,'chapters_byte_identical':1019,'tsw_and_companion_unchanged':True},'source_binding_audit':'PASSED; exact verse payload hashes, whole-file SHA-256, and Git blob identities verified','additional_affected_source_audits':affected,'source_sensitive_checks':checks,'focused_authoring_reread_count':focus_total,'translation_family':family,'block_progress':block,'whole_book_john':'DRAFT_COVERAGE_COMPLETE; consistency and independent review pending','independent_editorial_review':'REVIEW_PENDING','reader_testing':'PENDING','companion_reconciliation':'PENDING; no quotations or bindings changed','publication_allowed':False}
 dump(ROOT/SCOPES[1][0]/'verification.json',result);print(json.dumps({k:result[k] for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
