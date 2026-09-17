"""One-time, explicitly selected Genesis apparatus edits at checkpoint 98."""
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]; A=Path(__file__).resolve().parent
BASE='4d1c207f3645412e01c725431cb4bfc11e2ed655'
sys.path.insert(0,str(R/'tools'))
from audit_translation_overlap import verse_texts
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==BASE
# Keys identify complete existing notes. None removes that note and archives it.
# These edits condense existing assertions; they are not a new bilingual verification.
E={
1:{'01–02':'The opening can also be understood as “When God began to create …” leading into the following scene. “The deep” names the waters already present; the wording does not explain their origin.', '06–08':'“Dome” renders raqia, also translated “expanse” or “vault.” It separates waters above from waters below.'},
2:{'02–04':'The Masoretic Text says God completed the work on the seventh day. “Rested” also means ceased. Verse 4 begins an account formula repeated throughout Genesis. Its second sentence introduces the garden narrative with “earth and heaven,” reversing the order of the opening phrase.', '04–07':'“The LORD” represents the divine name YHWH. Adam, “human,” sounds like adamah, “ground.” The human becomes a living being; the wording does not describe a separate soul being placed inside a body.', '10–14':'The locations of Pishon and Gihon are uncertain. Tigris and Euphrates render Hiddekel and Perath. Bdellium and onyx are traditional identifications of the materials in v12; their precise identification is uncertain.', '21–24':'“Side” renders tsela, which may mean a side or a rib here. Verse 23 plays on ish, “man,” and ishah, “woman.” These differ from adam, “human.” Verse 24 uses man and his wife and the image “one flesh.”'},
3:{'01–06':'The serpent is introduced as an animal; this passage does not name it Satan. “Shrewd” sounds like the word for “naked” in 2:25. In v03 the woman includes touching in her report of the prohibition, a detail absent from 2:17. Her husband is explicitly “with her” in v06.', '15':'“Offspring” translates zera, also the word for seed. The Hebrew refers back to the woman’s offspring with a masculine singular pronoun; the noun can have a collective sense, represented here by “their.” The same verb is used for the blows to head and heel.'},
4:{'01':'“Had sexual relations” renders the Hebrew idiom “knew.” Cain’s name is linked with Eve’s verb qaniti, “I have acquired/produced.” The compact, disputed phrase involving the LORD is rendered here “with the LORD’s help.”', '08':'The Masoretic Text says Cain spoke to Abel but does not give the words he spoke.'},
5:{'01–05':'Adam can name a person or humanity. The image and likeness language recalls 1:26–27. The ages follow the Masoretic Text.'},
6:{'01–04':'The passage does not identify the “sons of God” or explain the Nephilim. It describes the daughters as beautiful and says the sons of God took any they chose.', '03':'The verb rendered “remain” is uncertain and has also been understood as contend or judge. The 120 years may refer to a limit on human life or a period before the coming judgment.', '05–13':'The Hebrew root for corruption is also used for destruction, linking the earth’s condition with the announced action. “All flesh” includes more than human beings in this account.', '18–22':None},
7:{'02–03':'The Hebrew repeats “seven, seven” alongside pairing language, understood here as seven pairs; the counting has also been understood differently. “Clean” and “not clean” are ritual categories. Verse 3 speaks of birds without the word clean.', '09–12':None, '20–24':'The compact fifteen-cubit phrase is understood here as placing the waters above the mountains. The 150 days differs from the forty days of rain.'},
8:{'07–12':None, '20–22':'“Even though” in v21 interprets the connective ki; “because” is another possible reading. The promise in v22 is arranged in four pairs.'},
9:{'09–17':'“Bow” is the ordinary Hebrew word for a bow, including a weapon; its appearance in the clouds is a rainbow.', '25–27':'The curse names Canaan, not Ham. “Lowest of slaves” renders the emphatic “slave of slaves.” The pronoun is plural, “their,” in vv26–27. In v27 the subject of “may he live” may be God or Japheth.'},
10:{'01–07':'This genealogy presents peoples and territories through family lines. Mizraim is the Hebrew name associated with Egypt, used here as an ancestral name. Dodanim in v04 follows the Masoretic Text.', '13–19':'The parenthesis about the Philistines follows Casluhim in the Hebrew.', '21–25':'Verse 21 can identify either Shem or Japheth as the older brother; Shem is understood as older here. “Peleg” echoes the verb for dividing, but the verse does not explain what kind of division occurred.'},
11:{'01–03':'“One language” is literally one lip. “From the east” can also be rendered eastward. The building materials are fired brick and bitumen.', '10–26':'The ages follow the Masoretic Text, including Eber’s 430 years after Peleg’s birth. The age followed by three sons in v26 does not establish simultaneous births or necessarily their birth order.'},
13:{'03–07':None, '08–11':'“Family” renders brothers in its broader kinship sense: Abram is Lot’s uncle. The eastward phrase in v11 can also be read as movement from the east. Verse 9 uses left and right, not compass directions.', '14–18':None},
14:{'01–09':'Goiim can also mean nations.', '13–16':None, '18–20':'“Maker” renders qoneh, which can also mean possessor. The Hebrew does not name the subject of the final giving clause; Abram is understood here as giving the tenth to Melchizedek.'},
15:{'05–06':'The Hebrew leaves the subject of “counted” and the recipient unnamed. The LORD is understood here as counting Abram’s trust as righteousness; the reversed assignment has also been proposed.', '09–12':'The three mammals are described with a term conventionally read as three years old.', '17–21':'Making a covenant is literally cutting a covenant, beside the account of divided animals. The smoking firepot and torch pass between the pieces; Abram is not said to do so.'},
16:{'07–10':'Malakh means messenger and is traditionally translated angel in this setting. The messenger speaks with divine first-person language. The root behind “submit” in v09 is also used for Sarai’s harsh treatment in v06.'},
17:{'10–14':'“Cut off” does not specify the punishment’s mechanism here.', '23–27':None},
18:{'01–10':'The account moves among the LORD, three men, plural address, and a singular speaker. “My Lord” in v03 follows the Hebrew pointing; a respectful address to a visitor is another reading.', '06–08':None, '10–15':'The time expression is understood as this time next year. The word behind “too extraordinary” can suggest something wonderful or beyond ordinary possibility. Sarah’s laughter follows Abraham’s in 17:17.', '22–33':'The Masoretic Text has Abraham standing before the LORD in v22.'},
19:{'01–11':'The men’s demand to “know” the visitors uses a sexual idiom in a coercive scene.', '12–18':'The sons-in-law may be men already married to Lot’s daughters or prospective husbands, as understood here. The address in v18 is pointed as singular “my Lord,” although Lot addresses the messengers.', '30–38':'The older daughter’s claim that no man is available is her speech, not a narrator’s statement that every other man has died. Moab and Ben-ammi introduce the peoples associated with these names.'},
20:{'11–13':'In v13 Elohim is accompanied by a plural verb, although rendered here with the customary singular “God.” Abraham’s explanation of Sarah’s kinship is part of his speech.', '17–18':None},
21:{'01–09':'The laughter word-family links Isaac’s name, Sarah’s joy, and the action she sees in Hagar’s son. In v06 “laugh with me” may also be heard as laugh at me. In v09 the Hebrew gives no object or companion for the laughing.', '10–14':'Verse 14 compresses bread, water skin, shoulder, and child into one sentence. The supplies are understood here as placed on Hagar’s shoulder and the child given into her care; another reading attaches the child to the shoulder phrase too.', '15–21':'“Child” and “boy” do not establish a precise age here.', '22–34':'The covenant with Abimelech uses the same term as the divine covenants. Beersheba is linked with both the seven lambs and the oath.'},
22:{'01–03':'“Your only one” stands alongside the earlier account of Ishmael. The call to go recalls 12:1.', '20–24':None},
23:{'01–04':None, '17–20':None},
24:{'10–22':'“The city of Nahor” may identify a place by name or association. The ring weighs half a shekel, and the two bracelets weigh ten shekels together. The ring is explicitly placed on the nose in v47.'},
25:{'01–11':'Being gathered to one’s people is a death idiom distinct from the subsequent burial scene.', '12–18':'Ishmael’s twelve leaders recall 17:20. The final clause in v18 is difficult: its verb usually means fall and has been read as settlement or death. Settlement with a collective referent is understood here. “Facing” recalls 16:12; hostility is another understanding of the phrase.'},
26:{'34':'The names of Esau’s wives and their fathers differ in 36:2–3.'},
27:{'23–27':None},
29:{'02–10':None, '05':'Hebrew can call a later descendant a “son.” The genealogy identifies Laban as Nahor’s grandson.'},
30:{'01–13':None, '27':None, '32–36':None, '40':'The wording about facing the flock toward marked animals is difficult; the precise arrangement is uncertain.'},
31:{'10–13':'Jacob’s dream attributes the marked offspring and protection from Laban to God. Compare the branch and breeding practices in 30:37–42.', '14–16':None, '43':None, '47–53':'Jegar-sahadutha is Aramaic and Galeed is related to Hebrew; both mean “heap of witness.” Mizpah means watchpost. The monument marks a boundary under divine witness.', '55':'English Genesis 31:55 corresponds to Hebrew Genesis 32:1.'},
32:{'01–32':'English Genesis 32:1–32 corresponds to Hebrew Genesis 32:2–33. Hebrew Genesis 32:1 appears as English 31:55.', '09':'Hebrew calls Abraham Jacob’s father, using a broad ancestral term; Abraham is Jacob’s grandfather.', '20':'The Hebrew repeats “face” four times: Jacob seeks to appease Esau’s face with a gift sent before his own face, then see Esau’s face, hoping Esau will lift his face.', '25, 31–32':'The anatomical expression refers to the socket or hollow of the upper thigh or hip; its exact modern anatomical identification is uncertain.'},
33:{'01–02':None, '09, 11':'Esau says he has “plenty”; Jacob says he has “everything.”'},
34:{'01–05':'The same name identifies both the man Shechem and, in this context, his city.', '03–12':None, '05, 13, 27':'“Defiled” describes Shechem’s act against Dinah.', '13–17':None, '21–23':None, '25–29':'Verse 25 names Simeon and Levi; v27 names Jacob’s sons without specifying whether Simeon and Levi are included again.', '31':None},
35:{'02–04':None, '05':None, '11–12':None, '22':'“Jacob had twelve sons” is part of the Hebrew verse and introduces the list that follows.', '25–26':'Verse 26 summarizes these as sons born in Paddan-aram, although the preceding account places Benjamin’s birth on the way to Ephrath.', '29':None},
36:{'02–03':'The names and family relationships of Esau’s wives differ from those given in 26:34 and 28:9.', '15–19':'Chief translates alluf, a title for a clan or tribal leader. Korah appears among Oholibamah’s sons in v14 and among the chiefs descended from Eliphaz in v16.', '20–30':None, '31':None, '32–39':None, '39':'The Masoretic Text reads Hadar; Hadad appears in related textual traditions.', '40–43':None},
38:{'8–10':'The repeated action describes Onan preventing conception because the offspring would count as his brother’s.', '11, 14':None, '24':None},
39:{'1–6':None, '6':'The exception involving Potiphar’s food may be literal or euphemistic.', '7–12':None, '14, 17':None, '21':'Hesed means loyal kindness or steadfast love; it does not by itself assert a formal covenant.'},
40:{'5':None, '8':None, '23':None},
41:{'1':None, '43':'The shouted word, abrekh, is uncertain. Proposals include “Bow the knee,” “Attention,” and an Egyptian command to make way.'},
42:{'15–20':None},
43:{'07':'The brothers report questions about their family that are not included in the earlier narrated exchange.', '34':'The final verb can mean to become drunk.'},
44:{'02–05':None, '09–10':None, '18–34':None, '21–22':'“Set my eyes on him” may mean simply see him or show him attention. In v22 Hebrew says “he will die”; the father is understood here, as in vv30–31, though the pronoun could refer to the son.', '27':None},
45:{'03':None, '15':None, '19':'Pharaoh addresses Joseph in the singular, then gives plural instructions for the brothers.'},
47:{'29':'Placing a hand under the thigh accompanies the oath, as in 24:2–9.'},
48:{'15–16':'The blessing places “God” and “the angel” in parallel descriptions without explaining their relationship here.'},
49:{'28':'The narrator calls the whole set blessings, including its rebukes and judgments.'},
50:{'10–11':'The site “beyond the Jordan” is uncertain. Abel-mizraim sounds like the Hebrew phrase for “mourning of Egypt.”'}
}
# Remove only this workflow sentence from an otherwise useful uncertainty note.
trims={16:{'13–14':' The draft keeps the encounter open to further review.'}}
inputs=json.loads((A/'input-chapters.json').read_text()); decisions=[]; changes=[]
for c in inputs:
 keys=set(re.findall(r'^v([^:]+):',c['text'].split('## Notes',1)[1].split('## Vocabulary',1)[0],re.M))
 assert set(E.get(c['chapter'],{}))<=keys,(c['chapter'],set(E.get(c['chapter'],{}))-keys)
 assert (R/c['path']).read_text()==c['text'],c['path']
for c in inputs:
 p=R/c['path']; old=p.read_text(); assert old==c['text']
 pre,tail=old.split('## Notes',1); notes,vocab=tail.split('## Vocabulary',1)
 out=[];seen=set()
 for block in re.split(r'\n\s*\n',notes.strip()):
  m=re.match(r'^v([^:]+): (.*)$',block,re.S); assert m, (c['chapter'],block)
  key,body=m.groups(); revised=E.get(c['chapter'],{}).get(key,body)
  if key in E.get(c['chapter'],{}):seen.add(key)
  if key in trims.get(c['chapter'],{}):
   frag=trims[c['chapter']][key];assert frag in revised;revised=revised.replace(frag,'')
  newkey=re.sub(r'\d+',lambda m:m[0].zfill(2),key)
  new=None if revised is None else f'v{newkey}: {revised}'
  status='REMOVE' if new is None else 'REWRITE' if new!=block else 'KEEP'
  reason={'REMOVE':'Routine narrative summary or interpretive/application material; no distinct textual alternative is removed.', 'REWRITE':'Condense existing textual help, remove drafting/defensive language, or standardize verse-label formatting; no new source reading claimed.', 'KEEP':'Retain contextual linguistic, literary, cultural, or textual help; source-accuracy closure remains subject to the full bilingual pass.'}[status]
  decisions.append(dict(chapter=c['chapter'],path=c['path'],section='Notes',reference=key,decision=status,before=block,after=new,reason=reason))
  if new:out.append(new)
 assert seen==set(E.get(c['chapter'],{})),(c['chapter'],set(E.get(c['chapter'],{}))-seen)
 vout=[]
 for block in re.split(r'\n\s*\n',vocab.strip()):
  assert re.match(r'^v\d',block),block
  new=re.sub(r'^v([^:]+):',lambda m:'v'+re.sub(r'\d+',lambda n:n[0].zfill(2),m[1])+':',block)
  decisions.append(dict(chapter=c['chapter'],path=c['path'],section='Vocabulary',reference=block.split(':',1)[0][1:],decision='KEEP' if new==block else 'REWRITE',before=block,after=new,reason='Retain contextual lexical help; verse-label padding only where needed. Full linguistic and cross-book terminology review remains open.'))
  vout.append(new)
 new=pre+'## Notes\n\n'+'\n\n'.join(out)+'\n\n## Vocabulary\n\n'+'\n\n'.join(vout)+'\n'
 # Avoid unrelated whitespace-only changes for unchanged chapters.
 if notes.strip()=='\n\n'.join(out) and vocab.strip()=='\n\n'.join(vout):new=old
 assert verse_texts(old)==verse_texts(new)
 assert old.split('## Notes',1)[0]==new.split('## Notes',1)[0]
 if new!=old:
  p.write_text(new);changes.append(dict(path=c['path'],chapter=c['chapter'],before_sha256=sha(old.encode()),after_sha256=sha(new.encode()),reasons=['Genesis apparatus scope and clarity pass; all Scripture, headings and paragraph markup preserved.']))
qpath=R/'audit/fluent-revision/WORK_QUEUE.json';q=json.loads(qpath.read_text()); bypath={c['path']:c for c in changes}; affected=[]
for scope in q['completed_draft_scopes']:
 lp=R/scope['ledger'];l=json.loads(lp.read_text());hit=False
 for ch in l['chapters']:
  if ch['path'] not in bypath:continue
  hit=True;rec=bypath[ch['path']];assert ch['after_sha256']==rec['before_sha256'];ch['after_sha256']=rec['after_sha256'];rec['ledger']=scope['ledger']
  cp=R/'audit/exegetical-core/fluent-production/genesis'/(Path(ch['path']).stem+'_review.json');cr=json.loads(cp.read_text());cr['chapter_binding']=copy.deepcopy(ch)
  cr.setdefault('subsequent_editorial_audits',[]).append(dict(audit=str(A.relative_to(R))+'/apparatus-decisions.json',base_commit=BASE,previous_chapter_sha256=rec['before_sha256'],scope='apparatus editorial scope; Scripture unchanged',editorial_status='REVIEW_PENDING'));dump(cp,cr)
 if hit:
  affected.append(scope['ledger']);l.setdefault('subsequent_editorial_audits',[]).append(dict(audit=str(A.relative_to(R))+'/apparatus-decisions.json',base_commit=BASE,scope='apparatus editorial scope; Scripture unchanged',editorial_status='REVIEW_PENDING'));dump(lp,l)
dump(A/'apparatus-decisions.json',dict(base_commit=BASE,coverage='All Notes and Vocabulary entries in Genesis 1–50 read for editorial scope; not a fresh full bilingual review',entries=decisions))
dump(A/'corrections.json',dict(base_commit=BASE,status='APPARATUS_EDITS_APPLIED',chapters=changes,verse_changes=[],affected_ledgers=affected,publication_allowed=False))
q.setdefault('completed_editorial_passes',[]).append(dict(scope='Genesis 1–50 apparatus editorial scope and clarity',criteria=['F07','F10'],status='SELF_REVIEW_COMPLETE_WITH_OPEN_ISSUES',report=str(A.relative_to(R))+'/Genesis-Editorial-Review.md',source_accuracy_pass='PENDING_FULL_BILINGUAL_REVIEW',independent_editorial_review='REVIEW_PENDING',publication_allowed=False))
q['next_work'].insert(0,dict(scope='Genesis 1–50 complete editorial block',action='Use FLUENT_EDITORIAL_STANDARD.md and EDITORIAL_PROGRESS.json. Finish continuous reading and fresh full source comparison, resolve Genesis open issues, then proceed through subsequent 50-chapter blocks without routine approval. Apparatus scope review alone is not full block completion.'))
dump(qpath,q)
from collections import Counter
print(json.dumps(dict(changed_chapters=len(changes),affected_ledgers=len(affected),notes=Counter(x['decision'] for x in decisions if x['section']=='Notes'),vocabulary=Counter(x['decision'] for x in decisions if x['section']=='Vocabulary')),indent=2))
