#!/usr/bin/env python3
"""Reproduce the scoped correction checks; never publish or grant approval.

Run from anywhere with Python 3.10+:
  python tools/verify_critical_corrections.py --repo . --json-out verification.json
The whole Fluent candidate and seven named TSW chapters are required. The tests
are snapshot-specific. Later editorial changes need an updated, reviewed contract;
do not modify historical ledgers merely to make a checksum test green.
"""
from __future__ import annotations
from pathlib import Path
import argparse,collections,hashlib,json,re,sys,tempfile,unittest,xml.etree.ElementTree as ET
from critical_text_model import ContentError,parse_chapter,frontmatter,parse_targets,vocabulary_fields,oshb_single_qere,greek_markup,sha256

from critical_spacing_overlay import resolve_correction_snapshot,validate_spacing_record
from tsw_format_apparatus import validate as validate_apparatus

REPO=Path(__file__).resolve().parents[1]
AUDIT=Path('audit/corrections/2026-10-15')

def english_words(text:str)->list[str]:
    return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?",text.lower().replace('*','').replace('’',"'"))

def body_words(text:str)->list[str]:
    _,body=frontmatter(text);body=body.split('## Notes')[0]
    lines=[]
    for s in body.splitlines():
        if re.match(r'^(?:\s*#|\s*</?p|---|book:|chapter:|testament:|translation:)',s):continue
        lines.append(re.sub(r'^v\d+:\s*','',s))
    return english_words(' '.join(lines))

def git_blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def tree_from_contract(records:list[dict])->str:
    root={}
    for record in records:
        if not record['path'].startswith('translations/fluent/'):continue
        parts=Path(record['path']).parts[2:];node=root
        for part in parts[:-1]:node=node.setdefault(part,{})
        node[parts[-1]]=record['before_git_blob']
    def recurse(node:dict)->str:
        data=b''
        for name,value in sorted(node.items(),key=lambda kv:(kv[0]+('/' if isinstance(kv[1],dict) else '')).encode()):
            isdir=isinstance(value,dict)
            data+=(b'40000' if isdir else b'100644')+b' '+name.encode()+b'\0'+bytes.fromhex(recurse(value) if isdir else value)
        return hashlib.sha1(b'tree '+str(len(data)).encode()+b'\0'+data).hexdigest()
    return recurse(root)

class CorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=REPO/AUDIT
        cls.contract,cls.ledger,cls.spacing_followup=resolve_correction_snapshot(REPO)
        cls.records=cls.contract['chapters']
        cls.parsed={r['path']:parse_chapter(REPO/r['path']) for r in cls.records}
        cls.source={r['reference']:r for r in json.loads((cls.audit/'SOURCE_EVIDENCE.json').read_text())['passages']}
    def path(self,translation,slug,chapter):
        return next(p for p,c in self.parsed.items() if c['book_slug']==slug and c['chapter']==chapter and str(c['meta']['translation']).lower()==translation)
    def chapter(self,t,s,c):return self.parsed[self.path(t,s,c)]
    def verse(self,t,s,c,v):return next(x['text'] for x in self.chapter(t,s,c)['verses'] if x['number']==v)
    def before(self,path):return (self.audit/'fixtures/before'/path).read_text()
    def source_xml(self,ref):return ET.fromstring(self.source[ref]['content'])
    def assert_bad_document(self,body,fragment=''):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample.md';p.write_text('---\nbook: Sample\ntestament: OT\nchapter: 1\ntranslation: TSW\n---\n'+body)
            with self.assertRaisesRegex(ContentError,fragment):parse_chapter(p)

    def test_01_before_and_after_hashes(self):
        self.assertEqual(len(self.ledger['files']),18)
        for r in self.ledger['files']:
            with self.subTest(path=r['path']):
                b=(self.audit/'fixtures/before'/r['path']).read_bytes();a=(REPO/r['path']).read_bytes()
                self.assertEqual(sha256(b),r['before_sha256']);self.assertEqual(git_blob(b),r['before_git_blob'])
                self.assertEqual(sha256(a),r['after_sha256']);self.assertEqual(git_blob(a),r['after_git_blob'])
    def test_02_baseline_fluent_tree(self):
        self.assertEqual(tree_from_contract(self.records),'91847a55745e1095d38c35242e35bbde430ecf1e')
    def test_03_every_candidate_file_matches_contract(self):
        for r in self.records:
            with self.subTest(path=r['path']):self.assertEqual(sha256((REPO/r['path']).read_bytes()),r['candidate_sha256'])
    def test_04_scope_counts(self):
        counts=collections.defaultdict(collections.Counter)
        for c in self.parsed.values():
            counts[c['meta']['translation'].lower()].update(chapters=1,verses=len(c['verses']),notes=len(c['notes']),vocabulary=len(c['vocabulary']))
        self.assertEqual(dict(counts['fluent']),{'chapters':1189,'verses':31083,'notes':4680,'vocabulary':2880})
        self.assertEqual(dict(counts['tsw']),{'chapters':7,'verses':189,'notes':76,'vocabulary':82})
    def test_05_labels_and_flat_block_roundtrip(self):
        for r in self.records:
            c=self.parsed[r['path']]
            with self.subTest(path=r['path']):
                self.assertEqual([v['number'] for v in c['verses']],r['verse_labels'])
                self.assertEqual([v for b in c['blocks'] if b['type']=='paragraph' for v in b['verses']],c['verses'])
                self.assertEqual(len(c['verses']),len({v['number'] for v in c['verses']}))
                self.assertTrue(all(v['text'].strip() for v in c['verses']))
    def test_06_fluent_word_sequences_preserved_against_reader_archive(self):
        for r in self.records:
            if not r['path'].startswith('translations/fluent/'):continue
            c=self.parsed[r['path']];words=[(v['number'],english_words(v['text'])) for v in c['verses']]
            checksum=sha256(json.dumps(words,ensure_ascii=False,separators=(',',':')).encode())
            with self.subTest(path=r['path']):self.assertEqual(checksum,r['comparison_reader_words_sha256'])
    def test_07_genesis_24_complete_departure_and_alignment(self):
        self.assertIn('spent the night there',self.verse('tsw','genesis',24,54))
        self.assertIn('arose in the morning',self.verse('tsw','genesis',24,54))
        self.assertTrue(self.verse('tsw','genesis',24,55).startswith('Her brother and her mother said'))
        self.assertIn('Do not delay me',self.verse('tsw','genesis',24,56))
        self.assertIn('Let us call the young woman',self.verse('tsw','genesis',24,57))
        self.assertIn('I will go',self.verse('tsw','genesis',24,58))
        self.assertEqual(self.verse('tsw','genesis',24,59),'So they sent away Rebekah their sister and her nurse, and Abraham’s servant and his men.')
        self.assertIn('they blessed Rebekah',self.verse('tsw','genesis',24,60))
        self.assertEqual(len(self.chapter('tsw','genesis',24)['verses']),67)
        nurse=next(w for w in self.source_xml('Gen.24.59') if w.get('lemma')=='3243')
        self.assertEqual(nurse.get('morph'),'HVhrfsc/Sp3fs')
    def test_08_genesis_24_restoration_is_only_added_scripture(self):
        p=self.path('tsw','genesis',24);new=(REPO/p).read_text()
        new=re.sub(r'^v59:.*\n','',new,count=1,flags=re.M)
        self.assertEqual(body_words(self.before(p)),body_words(new))
    def test_09_genesis_24_vocabulary_reference_repairs(self):
        vocab=self.chapter('tsw','genesis',24)['vocabulary']
        self.assertEqual(next(e['verses'] for e in vocab if e['term']=='אֱמֶת'),[27])
        self.assertEqual(next(e['verses'] for e in vocab if e['term']=='שָׁתָה'),[14])
    def test_10_revelation_4_alignment(self):
        for verse,phrase in {6:'full of eyes in front and behind',7:'first living creature like a lion',8:'six wings',9:'give glory and honor and thanks',10:'They cast their crowns',11:'Worthy are you'}.items():
            self.assertIn(phrase,self.verse('tsw','revelation',4,verse))
        self.assertIn('Holy, holy, holy',self.verse('tsw','revelation',4,8))
    def test_11_revelation_4_scripture_word_conservation(self):
        p=self.path('tsw','revelation',4);self.assertEqual(body_words(self.before(p)),body_words((REPO/p).read_text()))
    def test_12_altar_height(self):
        self.assertIn('twenty cubits long, twenty cubits wide, and ten cubits high',self.verse('tsw','2chronicles',4,1))
        self.assertIn('c/6235',self.source['2Chr.4.1']['content'])
        self.assertNotIn('comparator has twenty',(REPO/self.path('fluent','2chronicles',4)).read_text())
    def test_13_genesis_spousal_possessives(self):
        self.assertEqual(self.verse('tsw','genesis',2,24),'Therefore a man leaves his father and his mother and clings to his wife, and they become one flesh.')
        words={w.get('lemma'):w for w in self.source_xml('Gen.2.24') if w.tag.endswith('}w')}
        self.assertIn('376',words)
        for lemma in ['1','517','b/802']:self.assertTrue(words[lemma].get('morph').endswith('/Sp3ms'))
    def test_14_genesis_2_continuations_preserved(self):
        self.assertIn('On the day that the LORD God made',self.verse('tsw','genesis',2,4))
        self.assertIn('bone of my bones',self.verse('tsw','genesis',2,23))
        p=self.audit/'fixtures/before'/self.path('tsw','genesis',2)
        with self.assertRaisesRegex(ContentError,'Unowned'):parse_chapter(p)
    def test_15_genesis_35_continuation_and_word_conservation(self):
        self.assertIn('Now the sons of Jacob were twelve.',self.verse('tsw','genesis',35,22))
        p=self.path('tsw','genesis',35);self.assertEqual(body_words(self.before(p)),body_words((REPO/p).read_text()))
        with self.assertRaisesRegex(ContentError,'Unowned'):parse_chapter(self.audit/'fixtures/before'/p)
    def test_16_micah_continuation_and_word_conservation(self):
        s=self.verse('tsw','micah',5,5);self.assertIn('he shall be their peace',s);self.assertIn('When the Assyrian comes',s);self.assertIn('eight princes',s)
        p=self.path('tsw','micah',5);self.assertEqual(body_words(self.before(p)),body_words((REPO/p).read_text()))
        with self.assertRaisesRegex(ContentError,'Unowned'):parse_chapter(self.audit/'fixtures/before'/p)
    def test_17_ezekiel_qere_replaces_not_appends(self):
        q=oshb_single_qere(self.source_xml('Ezek.42.16'))
        self.assertEqual(len(q['alternatives']),1);v=q['alternatives'][0]
        self.assertEqual(v['ketiv']['surface'],'אמות');self.assertIn('3967',v['qere']['lemma'])
        self.assertEqual(len(q['written_tokens']),len(q['reading_tokens']))
        self.assertNotIn('אמות',[w['surface'] for w in q['reading_tokens']])
        self.assertIn('five hundred reeds',self.verse('tsw','ezekiel',42,16));self.assertNotIn('five cubits',self.verse('tsw','ezekiel',42,16))
    def test_18_qere_unpaired_rejected(self):
        with self.assertRaisesRegex(ContentError,'Unpaired'):
            oshb_single_qere(ET.fromstring('<verse><w type="x-ketiv">x</w><w>y</w></verse>'))
    def test_19_qere_complex_rejected(self):
        e=self.source_xml('Ezek.42.16');ns='{http://www.bibletechnologies.net/2003/OSIS/namespace}'
        rdg=e.find(f'.//{ns}rdg');w=ET.SubElement(rdg,ns+'w');w.text='extra'
        with self.assertRaisesRegex(ContentError,'Multiword'):oshb_single_qere(e)
    def test_20_corinthians_source_claim_not_silent_text_change(self):
        raw=self.source['1Cor 13:3']['content'];self.assertIn('καυθήσομαι',raw);self.assertNotIn('καυχήσωμαι',raw)
        self.assertIn('so that I may boast',self.verse('fluent','1corinthians',13,3))
        note=next(n['text'] for n in self.chapter('fluent','1corinthians',13)['notes'] if n['ref']=='v03')
        self.assertIn('alternative reading',note);self.assertIn('bound SBLGNT text itself reads',note);self.assertIn('καυθήσομαι',note)
        self.assertTrue(self.ledger['open_decisions']);self.assertFalse(self.ledger['publication_allowed'])
    def test_21_luke_apparatus_not_doubt(self):
        for ch,v in [(22,43),(22,44),(23,34),(24,6),(24,12)]:
            source=greek_markup(self.source[f'Luke {ch}:{v}']['content'])
            self.assertFalse(source['has_square_doubt_brackets']);self.assertTrue(source['has_apparatus_unit_markers'])
            candidate=self.verse('fluent','luke',ch,v);self.assertNotIn('[',candidate);self.assertNotIn(']',candidate)
    def test_22_luke_genuine_doubt_marks_retained(self):
        for ch,v in [(22,19),(22,20),(24,40),(24,51),(24,52)]:
            self.assertTrue(greek_markup(self.source[f'Luke {ch}:{v}']['content'])['has_square_doubt_brackets'])
            candidate=self.verse('fluent','luke',ch,v);self.assertIn('[',candidate);self.assertIn(']',candidate)
    def test_23_luke_supper_narrator_quote_boundary(self):
        a=self.verse('fluent','luke',22,19);b=self.verse('fluent','luke',22,20);c=self.verse('fluent','luke',22,21)
        self.assertTrue(a.endswith('me].”'));self.assertTrue(b.startswith('[And in the same way'))
        self.assertEqual(b.index('“'),b.index('“This cup'));self.assertTrue(b.endswith('you.”]'));self.assertTrue(c.startswith('“But look'))
    def test_24_duplicate_clauses_removed_only_from_orphan_position(self):
        cases=[('acts',9,19,'For several days Saul stayed with the disciples in Damascus.'),('john',19,16,'They took Jesus,'),('1corinthians',14,33,'As in all the churches of the holy ones,'),('2corinthians',11,21,'But whatever anyone else dares to boast of—I am speaking in foolishness—I also dare.')]
        for slug,ch,v,orphan in cases:
            p=self.path('fluent',slug,ch);before=self.before(p);after=(REPO/p).read_text()
            self.assertIn('\n'+orphan+'\n',before)
            self.assertNotIn('\n'+orphan+'\n',after.split('## Notes')[0])
            self.assertEqual(body_words(before.replace('\n'+orphan+'\n','\n',1)),body_words(after))
            self.assertTrue(self.verse('fluent',slug,ch,v))
    def test_25_embedded_metadata_removed(self):
        for ch in [15,20]:
            p=self.path('fluent','revelation',ch)
            self.assertEqual((REPO/p).read_text().count('translation:'),1)
            with self.assertRaisesRegex(ContentError,'Embedded metadata'):parse_chapter(self.audit/'fixtures/before'/p)
    def test_26_cross_chapter_note_numbers_22(self):
        n=next(n for n in self.chapter('fluent','numbers',22)['notes'] if n['ref']=='v41; 23:13')
        self.assertEqual(n['verses'],[41]);self.assertEqual(n['targets'],[{'book_slug':'numbers','chapter':22,'verse':41},{'book_slug':'numbers','chapter':23,'verse':13}]);self.assertFalse(n['text'].startswith('13:'))
    def test_27_all_vocabulary_definitions_and_raw_text_present(self):
        for p,c in self.parsed.items():
            for e in c['vocabulary']:
                with self.subTest(path=p,ref=e['ref']):
                    self.assertTrue(e['term']);self.assertTrue(e['definition']);self.assertTrue(e['raw_text'])
                    self.assertIn(e['raw_text'],(REPO/p).read_text())
    def test_28_term_transliteration_definition_normalization(self):
        a=vocabulary_fields('**ἀγάπη (agapē)**: Love expressed in committed regard and action.')
        self.assertEqual((a['term'],a['transliteration'],a['definition']),('ἀγάπη','agapē','Love expressed in committed regard and action.'))
        b=vocabulary_fields('רָקִיעַ (raqia)\nDome or expanse.');self.assertEqual(b['definition'],'Dome or expanse.')
    def test_29_reject_orphan(self):self.assert_bad_document('<p>\nv01: One.\n</p>\n## Heading\nUnowned words.','Unowned')
    def test_30_reject_empty_verse(self):self.assert_bad_document('<p>\nv01:\n</p>','Empty verse')
    def test_31_reject_duplicate_verse(self):self.assert_bad_document('<p>\nv01: One.\nv01: Another.\n</p>','Duplicate')
    def test_32_reject_embedded_metadata(self):self.assert_bad_document('---\ntranslation: TSW\n---\n<p>\nv01: One.\n</p>','Embedded')
    def test_33_reject_unclosed_paragraph(self):self.assert_bad_document('<p>\nv01: One.','Unclosed')
    def test_34_reject_unsupported_html(self):self.assert_bad_document('<p>\nv01: <script>alert(1)</script>\n</p>','Unsupported')
    def test_35_reject_bad_reference(self):
        for ref in ['v01x','v5-2','v1; 0:3','v1; x:3']:
            with self.subTest(ref=ref):
                with self.assertRaises(ContentError):parse_targets(ref,'sample',1)
    def test_36_no_editorial_approval_inherited(self):
        for r in self.ledger['files']:
            c=self.parsed[r['path']]
            self.assertFalse(c['meta']['publication_allowed']);self.assertEqual(c['meta']['editorial_status'],'REVIEW_PENDING')
        supersession=json.loads((self.audit/'REVIEW_SUPERSESSION.json').read_text())
        self.assertEqual(len(supersession['records']),18);self.assertTrue(all(not r['previous_approval_inherited'] for r in supersession['records']))
    def test_37_companion_impacts_not_marked_complete(self):
        impact=json.loads((self.audit/'COMPANION_IMPACT.json').read_text());self.assertEqual(len(impact['records']),11)
        for r in impact['records']:
            self.assertEqual(r['current_candidate_status'],'REVIEW_AND_REBIND_REQUIRED');self.assertFalse(r['resource_changed']);self.assertFalse(r['publication_allowed'])
    def test_38_source_fixture_integrity(self):
        self.assertEqual(len(self.source),33)
        for r in self.source.values():self.assertEqual(sha256(r['content'].encode()),r['serialized_content_sha256'])
    def test_39_relocated_commentary_is_preserved_not_published(self):
        candidates=json.loads((self.audit/'COMMENTARY_CANDIDATES.json').read_text())
        self.assertIn('garden resists possession',json.dumps(candidates,ensure_ascii=False))
        self.assertIn('access granted rather than achieved',json.dumps(candidates,ensure_ascii=False))
        self.assertNotIn('garden resists possession',(REPO/self.path('tsw','genesis',2)).read_text())


    def test_40_targeted_tsw_apparatus_spacing_is_canonical(self):
        for record in self.records:
            if record['path'].startswith('books/'):
                path=REPO/record['path']
                with self.subTest(path=record['path']):
                    self.assertEqual(validate_apparatus(path,path.read_text()),[])
    def test_41_spacing_followup_preserves_original_audit_documents(self):
        self.assertIsNotNone(self.spacing_followup)
        for filename,digest in self.spacing_followup['preserved_documents_sha256'].items():
            self.assertEqual(sha256((self.audit/filename).read_bytes()),digest)
    def test_42_spacing_followup_preserves_parsed_chapter_content(self):
        for record in self.spacing_followup['records']:
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/record['path']
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(record['before_text'],encoding='utf-8')
                before=parse_chapter(path)
                after=dict(self.parsed[record['path']])
                before.pop('source_sha256');after.pop('source_sha256')
                self.assertEqual(before,after)
    def test_43_spacing_followup_rejects_changed_before_evidence(self):
        record=dict(self.spacing_followup['records'][0])
        record['before_text']+='Unexpected words.\n'
        with self.assertRaisesRegex(ContentError,'before evidence'):
            validate_spacing_record(record)
    def test_44_spacing_followup_rejects_unbound_after_hash(self):
        record=dict(self.spacing_followup['records'][0])
        record['after_sha256']='0'*64
        with self.assertRaisesRegex(ContentError,'after evidence'):
            validate_spacing_record(record)

class RecordingResult(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.passed=[]
    def addSuccess(self,test):super().addSuccess(test);self.passed.append(test.id())

def main():
    global REPO
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=REPO);p.add_argument('--json-out',type=Path);args=p.parse_args();REPO=args.repo.resolve()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CorrectionTests)
    result=unittest.TextTestRunner(verbosity=2,resultclass=RecordingResult).run(suite)
    payload={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'tests_passed':len(result.passed),'failures':len(result.failures),'errors':len(result.errors),'passed':result.passed,'failure_details':[{'test':t.id(),'detail':d} for t,d in result.failures+result.errors],'scope':'1196 chapter files: 1189 Fluent and 7 selected TSW. Structural checks plus named content/source regressions, not whole-Bible linguistic certification.','publication_allowed':False,'independent_human_approval':False}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True,exist_ok=True);args.json_out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k not in ['passed','failure_details']},indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
if __name__=='__main__':main()
