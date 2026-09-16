#!/usr/bin/env python3
"""Structural and preservation checks, separate from authoring judgment."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'tools'))
from audit_fluent_revision import audit
R=Path(__file__).resolve().parents[3]
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('scope_directory',type=Path);ap.add_argument('--source-directory',required=True,type=Path);ap.add_argument('--bind-focused-records',action='store_true');a=ap.parse_args()
 A=a.scope_directory.resolve();rel=str(A.relative_to(R));cfg=json.loads((A/'config.json').read_text());parent=cfg['parent_commit']
 def old(p):return subprocess.check_output(['git','show',parent+':'+p],cwd=R)
 q=json.loads((R/'audit/fluent-revision/WORK_QUEUE.json').read_text());oq=json.loads(old('audit/fluent-revision/WORK_QUEUE.json'))
 assert q['completed_draft_scopes'][:-1]==oq['completed_draft_scopes'] and q['next_work'][1:]==oq['next_work'][1:]
 prior=set();prior_verses=0
 for sc in oq['completed_draft_scopes']:
  assert (R/sc['ledger']).read_bytes()==old(sc['ledger']),sc['ledger'];l=json.loads((R/sc['ledger']).read_text())
  for ch in l['chapters']:
   assert ch['path'] not in prior;prior.add(ch['path']);prior_verses+=ch['verse_count']
   assert (R/ch['path']).read_bytes()==old(ch['path']) and sha((R/ch['path']).read_bytes())==ch['after_sha256']
   assert sha((R/ch['tsw_comparator_path']).read_bytes())==ch['tsw_comparator_sha256']
 assert (len(prior),prior_verses)==(986,25401)
 L=json.loads((A/'luke-verse-review.json').read_text());sb=(a.source_directory/cfg['source_filename']).read_bytes();errors=audit(R,L,sb);assert not errors,errors
 affected=[]
 for p in ['audit/fluent-revision/2026-09-16-luke-5-8/luke-verse-review.json','audit/fluent-revision/2026-09-16-luke-1-4/luke-verse-review.json']:
  errs=audit(R,json.loads((R/p).read_text()),sb);assert not errs,errs;affected.append(p)
 src={line.split('\t',1)[0]:line.split('\t',1)[1] for line in sb.decode().splitlines() if '\t' in line};rows={v['reference']:v for v in L['verses']}
 focus=[{**v,'exact_source_record':src[v['source_reference']]} for v in L['verses']];assert len(focus)==158
 record=dict(status='AUTHORING_REREAD_COMPLETED',review_type='Drafting assistant self-reread, not human or independent scholarly review',authoring_record_sha256=sha((A/'authoring-reread.md').read_bytes()),rows=focus)
 if a.bind_focused_records:dump(A/'focused-comparisons.json',record);dump(A/'focused-selection.json',focus)
 else:assert json.loads((A/'focused-comparisons.json').read_text())==record and json.loads((A/'focused-selection.json').read_text())==focus
 v={k.split()[1]:x['after'] for k,x in rows.items()}
 checks={
  'mission_restrictions':all(x in v['9:3'] for x in ['staff','bag','bread','money','two tunics']),
  'herod_beheaded':'I beheaded John' in v['9:9'],
  'bethsaida':'Bethsaida' in v['9:10'],
  'feeding_numbers':all(x in v['9:13'] for x in ['five loaves','two fish']) and 'five thousand men' in v['9:14'] and 'fifty' in v['9:14'] and 'twelve baskets' in v['9:17'],
  'messiah':'God’s Messiah' in v['9:20'],
  'passion_groups':all(x in v['9:22'] for x in ['elders','chief priests','scribes','killed','third day']),
  'daily_cross':'cross every day' in v['9:23'],
  'self_forfeit':'lose or forfeit themselves' in v['9:25'],
  'eight_days':'About eight days' in v['9:28'],
  'exodos_jerusalem':'departure' in v['9:31'] and 'Jerusalem' in v['9:31'] and 'ἔξοδον' in src['Luke 9:31'],
  'chosen_one':'Chosen One' in v['9:35'] and 'ἐκλελεγμένος' in src['Luke 9:35'],
  'only_son_harm':'only child' in v['9:38'] and all(x in v['9:39'] for x in ['screams','convulses','foams','crushing']),
  'human_hands':'handed over into human hands' in v['9:44'],
  'outsider_boundary':'does not follow with us' in v['9:49'] and 'not against you is for you' in v['9:50'],
  'jerusalem_face':'set his face' in v['9:51'] and 'Jerusalem' in v['9:51'],
  'samaritan_reason':'Samaritan village' in v['9:52'] and 'heading toward Jerusalem' in v['9:53'],
  'fire_rebuked':'fire from heaven' in v['9:54'] and 'consume them' in v['9:54'] and v['9:55']=='But Jesus turned and rebuked them.' and 'another village' in v['9:56'],
  'seventy_two':all('seventy-two' in v[x] for x in ['10:1','10:17']) and 'ἑβδομήκοντα' in src['Luke 10:1'],
  'lambs_wolves':'lambs among wolves' in v['10:3'],
  'person_peace':'person of peace' in v['10:6'] and 'peace will rest' in v['10:6'],
  'kingdom_both':all('kingdom of God has come near' in v[x] for x in ['10:9','10:11']),
  'place_names':all(x in ' '.join(v[f'10:{n}'] for n in range(13,16)) for x in ['Chorazin','Bethsaida','Tyre','Sidon','Capernaum','Hades']),
  'satan_lightning':'Satan fall from heaven like lightning' in v['10:18'],
  'danger_authority':all(x in v['10:19'] for x in ['authority','snakes','scorpions','enemy']),
  'names_heaven':'names are written in heaven' in v['10:20'],
  'holy_spirit':'rejoiced in the Holy Spirit' in v['10:21'],
  'four_love_terms':all(x in v['10:27'] for x in ['heart','soul','strength','mind','neighbor']),
  'assault_explicit':all(x in v['10:30'] for x in ['stripped','beat','half dead']),
  'samaritan_care':all(x in ' '.join(v[f'10:{n}'] for n in range(33,36)) for x in ['Samaritan','compassion','oil','wine','animal','inn','two denarii','repay']),
  'became_neighbor':'became a neighbor' in v['10:36'] and 'showed him mercy' in v['10:37'],
  'martha_mary':all(x in ' '.join(v[f'10:{n}'] for n in range(38,43)) for x in ['Martha','Mary','serve alone','worried','good portion']),
  'few_or_one':'few things are needed—or only one' in v['10:42'],
  'short_prayer':all(x in ' '.join(v[f'11:{n}'] for n in range(2,5)) for x in ['Father','name','kingdom','daily bread','sins','indebted','testing']) and 'evil one' not in v['11:4'],
  'three_loaves':'midnight' in v['11:5'] and 'three loaves' in v['11:5'],
  'anaideia':'shameless persistence' in v['11:8'] and 'ἀναίδειαν' in src['Luke 11:8'],
  'holy_spirit_gift':'Father from heaven' in v['11:13'] and 'Holy Spirit' in v['11:13'],
  'mute_man':'man who had been mute spoke' in v['11:14'],
  'beelzebul':'Beelzebul' in v['11:15'] and 'ruler of demons' in v['11:15'],
  'finger_god':'finger of God' in v['11:20'],
  'seven_worse':'seven other spirits' in v['11:26'] and 'worse than the first' in v['11:26'],
  'maternal_body':all(x in v['11:27'] for x in ['womb','breasts','nursed']),
  'hear_keep':'hear the word of God and keep it' in v['11:28'],
  'jonah_no_three_days':'Jonah became a sign' in v['11:30'] and 'three days' not in v['11:30'],
  'queen_nineveh':all(x in v['11:31'] for x in ['queen of the South','Solomon']) and all(x in v['11:32'] for x in ['Nineveh','repented','Jonah']),
  'eye_light':'healthy' in v['11:34'] and 'darkness' in v['11:35'],
  'ceremonial_wash':'wash ceremonially' in v['11:38'],
  'inside_alms':'give what is inside as alms' in v['11:41'],
  'mint_rue_justice_love':all(x in v['11:42'] for x in ['mint','rue','justice','love of God']),
  'unmarked_graves':'unmarked graves' in v['11:44'],
  'burdens_finger':all(x in v['11:46'] for x in ['burdens hard to carry','one of your fingers']),
  'abel_zechariah':all(x in v['11:51'] for x in ['Abel','Zechariah','altar','sanctuary']),
  'key_knowledge':'key of knowledge' in v['11:52'],
  'verbal_trap':'catch him in something he might say' in v['11:54']}
 assert all(checks.values()),[k for k,x in checks.items() if not x]
 allowed={'audit/fluent-revision/WORK_QUEUE.json','tools/build_fluent_mark_checkpoint.py','tools/verify_fluent_mark_checkpoint.py','tools/package_fluent_checkpoint.py'}
 for ch in L['chapters']:
  allowed.add(ch['path']);assert ch['path'] not in prior;p=f'audit/exegetical-core/fluent-production/luke/Luke_{ch["chapter"]:02}_review.json';allowed.add(p)
  d=json.loads((R/p).read_text());assert d['chapter_binding']==ch and not d['publication_allowed'];t=(R/ch['path']).read_text();main=t.split('## Notes')[0];assert main.count('“')==main.count('”')
  inside=False
  for line in t.split('---',2)[2].split('## Notes')[0].splitlines():
   if line=='<p>':assert not inside;inside=True
   elif line=='</p>':assert inside;inside=False
   elif line.strip() and not line.startswith('## '):assert inside,(ch['path'],line)
  assert not inside
  for nr in re.findall(r'^v([\d,–\- ]+):',t.split('## Notes')[1],re.M):assert all(1<=int(n)<=ch['verse_count'] for n in re.findall(r'\d+',nr))
 for fn in cfg['book_record_files']:
  p='audit/exegetical-core/fluent-production/luke/'+fn;allowed.add(p);d=json.loads((R/p).read_text());od=json.loads(old(p))
  assert d['revision_batches'][:-1]==od.get('revision_batches',[]) and d['source']==od['source'] and d['editorial_review_pending_chapters']==list(range(1,12)) and not d['publication_allowed']
  if 'entries' in od:
   assert len(d['entries'])==len(od['entries'])
   for e,oe in zip(d['entries'],od['entries']):
    if e['chapter'] in cfg['chapters']:assert e['status']=='SUPERSEDED' and e['superseded_by_verse_ledger']==rel+'/luke-verse-review.json' and all(e[k]==x for k,x in oe.items())
    else:assert e==oe
   assert d['summary']==od['summary']
 changed=subprocess.check_output(['git','diff','--name-only',parent],cwd=R).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R).decode().splitlines()
 assert all(p in allowed or p.startswith(rel+'/') for p in changed),[p for p in changed if p not in allowed and not p.startswith(rel+'/')]
 assert not subprocess.check_output(['git','diff',parent,'--','books','companions'],cwd=R).strip();subprocess.run(['git','diff','--check',parent],cwd=R,check=True)
 family=subprocess.check_output([sys.executable,'tools/audit_translation_family.py'],cwd=R).decode();chapters=[c for sc in q['completed_draft_scopes'] for c in json.loads((R/sc['ledger']).read_text())['chapters']]
 assert len({c['path'] for c in chapters})==len(chapters)==989 and sum(c['verse_count'] for c in chapters)==25559 and len(q['completed_draft_scopes'])==114
 block=q['active_fifty_chapter_block'];assert (block['status'],block['completed_chapters'],block['remaining_chapters'],block['completed_verses'])==('IN_PROGRESS',32,18,1497)
 result=dict(status='PASSED',qa_scope='structural',parent_commit=parent,new_chapters=3,new_verses=158,cumulative_coverage=dict(ledgers=114,chapters=989,verses=25559),prior_preservation=dict(ledgers_byte_identical=113,chapters_byte_identical=986,tsw_and_companion_unchanged=True),source_binding_audit='PASSED; all exact payloads, whole-file SHA-256 and Git blob identity',additional_affected_ledgers_passed=affected,source_sensitive_checks=checks,focused_authoring_reread_count=len(focus),translation_family=family,block_progress=block,independent_editorial_review='REVIEW_PENDING',reader_testing='PENDING',companion_reconciliation='PENDING; no quotations or bindings changed',publication_allowed=False)
 dump(A/'verification.json',result);print(json.dumps({k:result[k] for k in ['status','new_chapters','new_verses','cumulative_coverage']}))
if __name__=='__main__':main()
