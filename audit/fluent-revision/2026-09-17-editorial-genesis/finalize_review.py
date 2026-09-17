"""Record targeted Hebrew checks and finish the apparatus review evidence."""
import hashlib,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent
S=Path(sys.argv[1]);sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
d=json.loads((A/'apparatus-decisions.json').read_text());cor=json.loads((A/'corrections.json').read_text())
updates={
(31,'Notes','24, 29'):'v24, 29: The expression is literally “from good to bad.” Its scope is disputed. “Make any pronouncement” represents one interpretation; a broader rendering is “speak to Jacob, either good or bad.”',
(31,'Vocabulary','24'):'v24: טוֹב עַד־רָע (tov ad-ra)\nFrom good to bad; the scope of the speech prohibited here is disputed.',
(35,'Notes','07'):'v07: El-bethel means “God of Bethel.” The Hebrew has a plural verb with Elohim here, although rendered with singular “God.”',
(36,'Notes','39'):'v39: The Masoretic Text reads Hadar here; the parallel account in 1 Chronicles 1:50 reads Hadad.'}
for e in d['entries']:
 k=(e['chapter'],e['section'],e['reference'])
 if k in updates:
  p=R/e['path'];t=p.read_text();assert t.count(e['after'])==1;p.write_text(t.replace(e['after'],updates[k]));e['after']=updates[k];e['decision']='REWRITE';e['reason']='Targeted source check: state the grammatical fact or identify the parallel precisely, and avoid presenting a disputed interpretation as settled.'
for rec in cor['chapters']:
 p=R/rec['path'];rec['after_sha256']=sha(p.read_bytes());lp=R/rec['ledger'];l=json.loads(lp.read_text());ch=next(x for x in l['chapters'] if x['path']==rec['path']);ch['after_sha256']=rec['after_sha256'];dump(lp,l)
 cp=R/'audit/exegetical-core/fluent-production/genesis'/(p.stem+'_review.json');cr=json.loads(cp.read_text());cr['chapter_binding']=ch;dump(cp,cr)
dump(A/'apparatus-decisions.json',d);dump(A/'corrections.json',cor)
checks={
'Gen.15.6':'The source has third-person pronominal reference in the counting clause; the note preserves the alternative assignment and does not claim explicit proper names in that clause.',
'Gen.31.24':'The source has speak and from good to bad; it has no separate word meaning formal pronouncement. The note now states the scope is disputed. Main-text idiom choice remains an open item.',
'Gen.31.29':'The warning repeats speak and from good to bad. The same unresolved idiom must be treated consistently in both occurrences.',
'Gen.35.7':'Niglu is plural, alongside ha-elohim. Revised note states the grammatical fact and the English singular choice without using surrounding theology to close the question.',
'Gen.36.39':'Hadar is the source name. The prior apparatus claim about Matred being a mother was not established by the two bat relationships; the revised note no longer asserts that gender.',
'Gen.38.8':'Judah tells Onan to perform the brother-in-law duty and establish offspring for his brother; the revised note retains this local relationship.',
'Gen.38.9':'The source states that the offspring would not be his and describes repeated action to avoid giving offspring to his brother; the shortened note preserves that explanation without a modern polemic.',
'Gen.38.10':'The following clause judges what Onan did evil and reports his death; the shortened note does not remove either clause from Scripture.',
'Gen.39.21':'The source has hesed, not berit. The main text already says steadfast love; the old note said Covenant love renders hesed. Correcting the note resolves that local mismatch without changing Scripture.',
'1Chr.1.50':'The parallel names Hadad. The revised Genesis 36:39 note identifies the parallel rather than vaguely invoking textual traditions.'}
e=[]
for ref,observation in checks.items():
 fn='genesis-pinned-source.xml' if ref.startswith('Gen.') else '1chronicles-pinned-hebrew.xml';b=(S/fn).read_bytes();s=b.decode();m=re.search(r'<verse\b[^>]*osisID="'+re.escape(ref)+r'"[^>]*>.*?</verse>',s,re.S);assert m
 e.append(dict(reference=ref,source_file=fn,source_file_sha256=sha(b),exact_source_record=m[0],source_record_sha256=sha(m[0].encode()),observation=observation,scope='targeted grammatical/lexical check; not exhaustive verse certification'))
dump(A/'targeted-source-evidence.json',dict(scope='Nine Genesis verse records and one parallel in 1 Chronicles; targeted questions only',records=e,independent_review=False))
from collections import Counter
print(json.dumps({s:dict(Counter(x['decision'] for x in d['entries'] if x['section']==s)) for s in ['Notes','Vocabulary']},indent=2))
