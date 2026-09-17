"""Apply the reviewed source/fluency decisions after checkpoint 100."""
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
from difflib import SequenceMatcher
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
BASE='f59146de202775e61a608552e8564bddd46c4599';S=Path(sys.argv[1]);sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(R/'tools'))
from audit_translation_overlap import verse_texts,words

def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=R)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==BASE
E={
'Genesis 11:26':('After Terah reached 70 years of age, he became the father of Abram, Nahor, and Haran.','Terah was 70 years old, and he became the father of Abram, Nahor, and Haran.','F01/F03','Remove added after chronology from the coordinated age and fatherhood statements, consistently with 5:32. Do not assert simultaneous births or harmonize birth order.'),
'Genesis 18:19':('. Then the LORD will bring about',', so that the LORD may bring about','F01/F02','Restore the second explicit purpose connection, lemaʿan, rather than making it only a subsequent event. Preserve both purposes in the verse.'),
'Genesis 33:13':('all the animals will die.','the whole flock will die.','F01/F05','The final clause names all the tson, the flock, after distinguishing flock and cattle earlier. Avoid extending that noun to every animal.'),
'Genesis 36:25':('Anah’s children were Dishon and his daughter Oholibamah.','Anah’s children were Dishon and Oholibamah, Anah’s daughter.','F01/F02','Repeat the explicit father Anah from the source. The former English his could attach to Dishon and imply the wrong parent.'),
'Genesis 36:26':('These are the sons of Dishon:','These are the sons of Dishan:','F01/F03','The pinned Masoretic verse reads Dishan, including the vowel pointing. Restore that name rather than silently harmonizing it to Dishon in the surrounding genealogy; a new note discloses the tension.'),
'Genesis 37:8':('Do you really intend to reign over us?','Are you really going to reign over us?','F01/F02','The emphatic reign question does not separately state an intention. Preserve the incredulous question and the following rule question without supplying a mental purpose.'),
'Genesis 37:36':('Meanwhile, the Midianites sold Joseph','Meanwhile, the Medanites sold Joseph','F01/F03','The pinned Hebrew names Medanites here, distinct from Midianites in 37:28. Follow the bound source and correct the note that previously misidentified its wording; do not resolve the narrative relationship between merchant groups.'),
'Genesis 41:35':('They should gather food during the good years ahead','They should gather all the food during the good years ahead','F01/F04','Restore explicit kol, all, in the food-gathering instruction. Preserve its relation to the preceding fifth and to the corresponding all in 41:48 without silently harmonizing the scope.'),
'Genesis 42:20':('They agreed to do this.','They did so.','F01/F04','The narrator says they did so, not merely that they agreed. Retain the summary statement in its given place rather than changing the action to an agreement to smooth subsequent chronology.')}
N={
36:[('v39: The Masoretic Text reads Hadar here;', 'v26: The Hebrew reads Dishan here, although the preceding verse names Dishon. Verse 28 also names Dishan.\n\nv39: The Masoretic Text reads Hadar here;')],
37:[('v28, 36: The account names both Ishmaelites and Midianites. In verse 28 the Hebrew does not identify the subject of “pulled,” “lifted,” and “sold” unambiguously; verse 36 names Midianites as the sellers in Egypt.', 'v28, 36: The account names Ishmaelites and Midianites in verse 28; the Hebrew text used here names Medanites in verse 36. The relationship among these names is not explained. In verse 28 the subject of “pulled,” “lifted,” and “sold” is not explicitly identified, leaving the sellers’ identity open to interpretation.')]
}
# Preflight every text replacement before writing anything.
for ref,(before,after,crit,reason) in E.items():
 ch,num=map(int,ref.split()[1].split(':'));t=(R/f'translations/fluent/OT/genesis/Genesis_{ch:02}.md').read_text();assert verse_texts(t)[f'{num:02}'].count(before)==1,(ref,before)
for ch,edits in N.items():
 t=(R/f'translations/fluent/OT/genesis/Genesis_{ch:02}.md').read_text()
 for b,a in edits:assert t.count(b)==1
changes={};vchanges=[]
for ref,(before,after,crit,reason) in E.items():
 ch,num=map(int,ref.split()[1].split(':'));p=f'translations/fluent/OT/genesis/Genesis_{ch:02}.md';t=(R/p).read_text();vs=verse_texts(t);label=f'{num:02}';assert vs[label].count(before)==1
 if p not in changes:changes[p]=dict(path=p,chapter=ch,before_sha256=sha(old(p)),reasons=[])
 line=next(l for l in t.splitlines() if l.startswith(f'v{num:02}:'));assert before in line;t=t.replace(line,line.replace(before,after));(R/p).write_text(t);changes[p]['reasons'].append(reason)
 vchanges.append(dict(reference=ref,path=p,before=vs[label],after=verse_texts(t)[label],criteria=crit,rationale=reason))
notechanges=[]
for ch,edits in N.items():
 p=f'translations/fluent/OT/genesis/Genesis_{ch:02}.md';t=(R/p).read_text()
 for b,a in edits:
  t=t.replace(b,a);notechanges.append(dict(path=p,before=b,after=a))
 (R/p).write_text(t)
qpath=R/'audit/fluent-revision/WORK_QUEUE.json';q=json.loads(qpath.read_text());affected=[]
for scope in q['completed_draft_scopes']:
 lp=R/scope['ledger'];l=json.loads(lp.read_text());hit=False
 for ch in l['chapters']:
  if ch['path'] not in changes:continue
  hit=True;rec=changes[ch['path']];assert ch['after_sha256']==rec['before_sha256'];rec['after_sha256']=sha((R/ch['path']).read_bytes());rec['ledger']=scope['ledger'];ch['after_sha256']=rec['after_sha256']
  for v in l['verses']:
   if v['reference'] not in E or int(v['reference'].split()[1].split(':')[0])!=ch['chapter']:continue
   edit=next(e for e in vchanges if e['reference']==v['reference']);assert v['after']==edit['before'];edit.update(source_reference=v['source_reference'],source_verse_sha256=v['source_verse_sha256'])
   v.setdefault('subsequent_editorial_changes',[]).append(dict(audit=str(A.relative_to(R))+'/corrections.json',base_commit=BASE,previous_after=v['after'],rationale=edit['rationale']))
   v['after']=edit['after'];v['identical_words_to_tsw']=words(v['after'])==words(v['tsw_comparator']);v['word_similarity_to_tsw']=round(SequenceMatcher(None,words(v['after']),words(v['tsw_comparator']),autojunk=False).ratio(),6)
  cp=R/'audit/exegetical-core/fluent-production/genesis'/(Path(ch['path']).stem+'_review.json');cr=json.loads(cp.read_text());cr['chapter_binding']=copy.deepcopy(ch);cv={v['reference']:v for v in l['verses']}
  for field in ['key_decisions','verse_decisions']:
   if field in cr:cr[field]=[copy.deepcopy(cv[v['reference']]) if v.get('reference') in E else v for v in cr[field]]
  cr.setdefault('subsequent_editorial_audits',[]).append(dict(audit=str(A.relative_to(R))+'/corrections.json',base_commit=BASE,previous_chapter_sha256=rec['before_sha256'],scope='Genesis 11–50 source/fluency comparison',editorial_status='REVIEW_PENDING'));dump(cp,cr)
 if hit:
  affected.append(scope['ledger']);l.setdefault('subsequent_editorial_audits',[]).append(dict(audit=str(A.relative_to(R))+'/corrections.json',base_commit=BASE,scope='Genesis 11–50 source/fluency comparison',editorial_status='REVIEW_PENDING'));dump(lp,l)
observations={
11:'One lip/language, repeated come-let-us calls, descent, scattering and Babel wordplay compared. Shem through Terah ages and named relationships checked; 70-year statement corrected without inferred chronology.',
12:'Departure commands, blessing/curse distinctions, Abram age 75, households, Canaanite presence, altars, famine and Egypt speech compared. Wife/sister deception and Pharaoh accusations remain attributed to their speakers.',
13:'Return itinerary, riches, herder dispute, choice of land and separation compared. Before-destruction landscape comparison, people’s evil, renewed land/offspring promises and Hebron altar preserved.',
14:'Kings and place names, 12/13/14-year sequence, battle, Lot capture and rescue, 318 trained men and Melchizedek encounter compared. Most High titles, tenth and Abram refusal preserved; no modern monetary units added.',
15:'Shield/reward and heir complaint, stars, belief/righteousness, covenant pieces, four hundred years, fourth generation, torch and territorial peoples compared. Scope of duration and pronoun questions remain within open G03.',
16:'Sarai/Hagar agency and speech, ten years, affliction, messenger dialogue, Ishmael name, wild-donkey and brothers imagery, seeing-name and Abram age 86 compared. Difficult 13–14 seeing formulation remains provisional.',
17:'Age 99, El Shaddai, renamed Abraham/Sarah, covenant repetition, male circumcision/eight days, cut-off warning, laughter, Isaac/Ishmael distinctions and ages 100/90/13 compared. Relative-clause scope in 12 remains flagged.',
18:'Three visitors, singular/plural address, food, announced birth and both laughter speeches compared. Two purpose links in 19 retained after correction; outcry, descent and justice dialogue with 50/45/40/30/20/10 compared.',
19:'Messenger arrival, threats and violence, daughter/sons-in-law wording, warnings, hesitation, rescue, Zoar, sulfur, salt pillar and Abraham view compared. Lot daughters’ claims remain speech; no extra consent or global extinction claim added.',
20:'Abimelech’s taking without approaching Sarah, dream, innocence, conditional return, prophet/prayer, Abraham half-sister explanation, gifts and womb closing compared. Plural verb in 13 and eye-covering in 16 remain difficult readings.',
21:'Isaac birth, eight-day circumcision, Abraham age 100, laughter vocabulary and expulsion compared. Hagar shoulder/child ambiguity remains noted; hearing, water and promise, oath/seven lambs, covenant and tamarisk compared.',
22:'Test, only son, Moriah, repeated here-I-am and walked-together, sheep/ram, restraint, substitution, seeing/providing and renewed oath compared. Abraham’s return and Nahor family including Rebekah checked; no added return action for Isaac.',
23:'Sarah age 127, Kiriath-arba/Hebron, stranger/property dialogue, repeated gift language, 400 shekels weighed for merchants, field/cave/trees and transfer formulas compared. Ancient weight preserved without minted-coin claim.',
24:'All 67 verses, including extended repeated servant report, read. Thigh oath, land/family, woman’s refusal, ten camels, spring, ring/bracelets, consent, departure, blessing and Isaac encounter compared. Speech differences preserved; meditation and timing alternatives remain provisional.',
25:'Keturah family, Abraham age 175 and burial, Ishmael sons/12 leaders/137 years, Isaac age 40/60, pregnancy struggle, twins, birthright sale and meal-action sequence compared. Settlement idiom, Rebekah question and quiet/blameless Jacob remain interpretation questions.',
26:'Famine and renewed promise, sister claim, caressing, guilt warning, hundredfold crop, wealth, wells/names and dispute sequence compared. Oath/covenant, Shibah and Esau age 40/wives preserved without harmonizing names to chapter 36.',
27:'Both meal/blessing exchanges, sensory deception, Rebekah’s altered report, birthright/blessing soundplay and Esau grief compared. Repeated heartfelt rendering of nefesh is disclosed but flagged for further semantic review; preposition in 39 and verb in 40 remain provisional.',
28:'Marriage instructions and El Shaddai blessing, Esau added marriage, stone, stairway, messenger movements, LORD position and vow compared. Grandfather expansion reflects explicit genealogy; above/beside and vow connection remain disclosed alternatives.',
29:'Well gathering and stone, Rachel encounter, Laban relationship, Leah/Rachel description, seven-year periods, wedding-week timing and four births compared. Mother’s-brother repetition compressed in 10 and hated language in 31/33 flagged for whole-book voice review.',
30:'Bilhah/Zilpah wives, birth/naming speeches, mandrakes, wages, Rachel remembered and Joseph naming compared. Divination retained as Laban’s claim; animal colors, separation, branches and strong/weak breeding compared without adding a scientific explanation.',
31:'Wage complaint, dream account, women’s inheritance response, flight/theft, pursuit, warning, tent searches, 20/14/6 years, covenant and boundary witnesses compared. Pronouncement reading retains earlier evidence and alternative; plural divine wording in 53 remains for broader grammar review.',
32:'Public labels checked against Hebrew 32:2–33; prior public 31:55 is Hebrew 32:1. Camps, 400 men, prayer, exact gift counts, repeated servant message, crossing and wrestling compared. Man designation, naming, face/life, Peniel/Penuel and sinew preserved; messenger/angel terminology flagged.',
33:'Four hundred men, family order, seven bows, embrace, face comparison, blessing/gift, livestock pace, Seir promise/Succoth travel, safe-arrival alternative and qesitah purchase compared. Final flock in 13 corrected from the broader all animals.',
34:'Dinah/Shechem violence, father and brothers’ speeches, deceptive circumcision demand, third-day attack, rescue, plunder and final dispute compared. Plural active defilement wording in 27 and passive English/over-specific note remain an explicit open issue.',
35:'Foreign gods/purification, Bethel altars/naming, divine terror, plural revelation verb, Deborah burial, Rachel death/naming, Reuben report, sons and Isaac age 180 compared. Birth-list location not harmonized to Benjamin’s earlier scene; plural agreement remains open.',
36:'All family and chief lists and eight royal successions compared, including repeated Korah and differing wife names. Anah parenthood clarified; pointed Dishan in 26 restored. Jeush qere inspected; Hadar retained. Yemim and lineage tensions remain disclosed.',
37:'Age 17, bad report, distinctive robe, two dreams, brothers’ escalating response, journey, plot, pit, silver and false report compared. Intended reign removed; Medanites restored in 36 and note corrected. Subject of sale in 28 remains unresolved; active-to-passive strategy needs final review.',
38:'Judah family, Er/Onan deaths, withheld Shelah, widow clothing, pledge, delayed payment, pregnancy accusation, recognition and twins compared. Shrine language remains an open specialist question; recognition echo with 37 preserved and violence not softened.',
39:'Purchase, repeated LORD-with-Joseph and success, household authority, refusal, repeated approaches and garment accounts compared. Wife’s allegations remain her speech; master anger has no supplied object. Hand/care metaphor and success phrasing flagged for continuous reading.',
40:'Cupbearer/baker custody, each dream, three days, lifted head/from-you wordplay, Joseph plea, third-day feast and opposite outcomes compared. Bread-basket uncertainty and tree/impalement alternatives remain noted; forgotten repetition preserved.',
41:'Both dreams and retellings, two full years, seven/seven years, interpretation, fifth collection, Joseph authority/age 30, wife/sons, stored grain and famine compared. Explicit all restored in 35; shalom, abrekh and administrative expressions retained with alternatives.',
42:'Ten brothers and Benjamin absence, recognition, spy accusation, oath/testing, custody, fear of God, guilt dialogue, Simeon and silver return compared. They did so restored in 20. Difference between individual silver discovery and later collective report preserved.',
43:'Famine return, Judah guarantee, produce gift/double silver, compassion prayer, steward exchange, Simeon release, Benjamin greeting, weeping and separate meals compared. Firstborn-to-youngest order, fivefold portion and drunkenness retained.',
44:'Sack/cup instructions, pursuit, sworn penalty versus steward response, ordered search, return, Joseph accusation and full Judah speech compared. Father referent in 22 retained with previous evidence and alternative; guarantee, substitute service and final question preserved.',
45:'Private disclosure/public crying, father question, brothers’ fear, repeated God-sent claims, two/five famine years, father-to-Pharaoh title and family invitation compared. Embraces, Pharaoh gift orders, exact donkey/silver/clothes quantities and Jacob revival preserved.',
46:'Beersheba visions, divine descent/return and Joseph eyes, migration, names by mothers and 33/16/14/7/66/70 counts compared. Er/Onan deaths and Egypt-born sons retained without recalculating the received text. Judah advance, reunion and shepherd speech compared.',
47:'Five brothers, pasture request, capable herders, two blessings, Jacob age 130, Rameses and food provision compared. Silver/livestock/land transactions, cities reading, priest exception, fifth/four shares and Jacob 17/147 years and burial oath compared.',
48:'Illness, El Shaddai recollection, adoption/inheritance, Rachel memory, dim sight, knees and right/left crossed hands compared. Blessing of Joseph, God/shepherd/angel sequence, repeated I-know, nations and additional portion preserved with difficult alternatives still open.',
49:'All 33 verses compared, including the complete twelve-son poem. Person shifts, paired lines, name wordplay, lion/donkey/snake/wolf images, brief salvation prayer, divine titles and maternal imagery retained. Shiloh, weapons, saddlebags, doe/words, branch and 24–26 syntax still require specialist review.',
50:'Embalming/mourning 40/70 days, funeral oath and company, seven-day lament, cave purchase, return, brothers’ fear and message, forgiveness and intended good/harm compared. Joseph 110 years, descendants/knees, aid/bones oath and coffin ending preserved.'}
source=(S/'genesis-pinned-source.xml').read_bytes();s=source.decode();records=[]
for ch in range(11,51):
 p=f'translations/fluent/OT/genesis/Genesis_{ch:02}.md';before=verse_texts(old(p).decode());after=verse_texts((R/p).read_text())
 for label in before:
  n=int(label);ref=f'Genesis {ch}:{n}';sc,sn=(32,1) if (ch,n)==(31,55) else (32,n+1) if ch==32 else (ch,n)
  m=re.search(r'<verse\b[^>]*osisID="Gen\.'+str(sc)+r'\.'+str(sn)+r'"[^>]*>.*?</verse>',s,re.S);assert m
  records.append(dict(reference=ref,path=p,before=before[label],after=after[label],source_reference=f'Gen.{sc}.{sn}',exact_source_record=m[0],source_verse_sha256=sha(m[0].encode()),decision='REVISE' if ref in E else 'RETAIN_WITH_REVIEW_LIMITS',observation=observations[ch],rationale=E[ref][3] if ref in E else None,independent_review='PENDING'))
assert len(records)==1266
dump(A/'source-review.json',dict(base_commit=BASE,source_file='genesis-pinned-source.xml',source_file_sha256=sha(source),source_commit='6a5db284c715c18b239422e57bb89684e6a19f00',scope='Genesis 11–50, every verse compared with a simplified Hebrew word display; pointed source revisited for correction targets; source annotation inventory inspected. Author/model self-review, not independent philological certification.',chapters=40,verses=1266,cumulative_genesis_chapters=50,cumulative_genesis_verses=1533,full_genesis_review_complete=False,records=records))
dump(A/'corrections.json',dict(base_commit=BASE,chapters=list(changes.values()),verse_changes=vchanges,note_changes=notechanges,affected_ledgers=affected,publication_allowed=False))
q.setdefault('completed_editorial_passes',[]).append(dict(scope='Genesis 11–50 source comparison, 1266 verses; cumulative Genesis 1–50, 1533 verses',status='SELF_REVIEW_COMPLETE_WITH_OPEN_ISSUES',report=str(A.relative_to(R))+'/Genesis-Source-Review.md',independent_editorial_review='REVIEW_PENDING',publication_allowed=False))
q['next_work'][0]['action']='Genesis 1–50 now has fresh verse-by-verse self-review with open issues. Complete the remaining continuous-reading, specialist and editorial checks in the current issue register. Continue subsequent 50-chapter blocks without routine approval; never mark unresolved or independent review complete. Read EDITORIAL_PROGRESS.json and the latest source-review report.'
dump(qpath,q)
print(json.dumps(dict(changed_chapters=len(changes),changed_verses=len(vchanges),reviewed_verses=len(records),affected_ledgers=len(affected))))
