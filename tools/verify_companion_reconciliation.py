#!/usr/bin/env python3
"""Offline tests for PR 152 Companion candidates and the read-only API comparator.

Integrity and reference checks do not certify the truth of every interpretation.
No website writes, independent approvals, or whole-Companion completion claims.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,re,sys,unittest
from pathlib import Path,PurePosixPath
from critical_text_model import parse_chapter,sha256,ContentError
from check_reader_correction_targets import expected_chapter,compare_response

ROOT=Path('.')
REL=Path('audit/corrections/2026-10-15/companion-review')
EXPECTED={('1 Corinthians',13),('1 Corinthians',14),('2 Corinthians',11),('Acts',9),('John',19),
          ('Luke',22),('Luke',23),('Luke',24),('Revelation',15),('Revelation',20),('2 Chronicles',4)}

def read_json(path: Path):return json.loads(path.read_text(encoding='utf-8'))
def safe_path(repo: Path,relative: str) -> Path:
    pp=PurePosixPath(relative)
    if pp.is_absolute() or '..' in pp.parts or '.' in pp.parts or not pp.parts or pp.parts[0]=='.git':
        raise ValueError('Unsafe relative path')
    result=repo
    for part in pp.parts:
        result=result/part
        if result.is_symlink():raise ValueError('Symlink not permitted')
    return result

def split_document(raw: str) -> tuple[dict,str]:
    m=re.match(r'^---\n(.*?)\n---\n\n(.*)',raw,re.S)
    if not m:raise ValueError('Invalid Companion front matter')
    meta={}
    for line in m[1].splitlines():
        if ':' not in line:raise ValueError('Invalid metadata line')
        k,v=line.split(':',1)
        if k in meta:raise ValueError('Duplicate metadata key')
        meta[k]=v.strip()
    return meta,m[2]

def validate_record(repo: Path,r: dict) -> tuple[dict,str,dict]:
    p=safe_path(repo,r['candidate_path']);raw=p.read_text(encoding='utf-8')
    if sha256(raw.encode())!=r['candidate_sha256']:raise ValueError('Changed candidate')
    meta,body=split_document(raw)
    if sha256(body.encode())!=r['candidate_body_sha256']:raise ValueError('Changed body binding')
    source=safe_path(repo,r['source_path'])
    if sha256(source.read_bytes())!=r['reviewed_source_sha256']:raise ValueError('Changed translation source')
    for key,value in [('source',r['source_path']),('source_sha256',r['reviewed_source_sha256']),
                      ('source_commit',r['reviewed_source_commit']),('book',r['book']),('chapter',str(r['chapter']))]:
        if meta.get(key)!=value:raise ValueError('Mismatched '+key)
    if meta.get('publication_allowed')!='false' or meta.get('publication_status')!='unpublished':
        raise ValueError('Unexpected publication permission')
    return meta,body,parse_chapter(source)

class ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo=ROOT.resolve();cls.manifest=read_json(cls.repo/REL/'RECONCILIATION.json')
        cls.records=cls.manifest['records'];cls.evidence=read_json(cls.repo/REL/'SOURCE_EXCERPTS.json')
        cls.by_id={(r['book'],r['chapter']):r for r in cls.records}
    def test_exact_eleven_scope(self):
        self.assertEqual(len(self.records),11);self.assertEqual(set(self.by_id),EXPECTED)
    def test_integrity_and_current_bindings(self):
        for r in self.records:
            with self.subTest(source=r['source_path']):validate_record(self.repo,r)
    def test_source_status_not_human_approval(self):
        self.assertIs(self.manifest['publication_allowed'],False)
        self.assertEqual(self.manifest['scripture_files_changed'],0)
        for r in self.records:
            meta,_,_=validate_record(self.repo,r)
            self.assertEqual(meta['source_qa_scope'],'structural')
            self.assertEqual(meta['independent_human_review'],'not_recorded')
            self.assertEqual(meta['companion_status'],'AI_RECONCILED_REVIEW_REQUIRED')
            self.assertIs(r['canonical_companion_changed'],False)
            self.assertIs(r['publication_allowed'],False)
    def test_previous_impact_and_history_preserved(self):
        m=self.manifest
        self.assertEqual(sha256((self.repo/m['previous_correction_impact_file']).read_bytes()),m['previous_correction_impact_sha256'])
        for r in self.records:
            q=r['checkpoint18_queue_entry']
            self.assertEqual(q['resource'],r['previous_canonical_companion_path'])
            self.assertEqual(q['source'],r['source_path'])
            self.assertEqual(q['publication'],'unpublished')
    def test_complete_numbered_chapter_reading_coverage(self):
        total=0
        for r in self.records:
            _,body,model=validate_record(self.repo,r)
            self.assertEqual(r['reviewed_verse_labels'],[v['number'] for v in model['verses']])
            path=body.split('### Chapter Path\n',1)[1].split('### Watch For',1)[0]
            coverage=[]
            for c,a,b in re.findall(r'\*\*(\d+):(\d+)(?:[–-](\d+))?:',path):
                self.assertEqual(int(c),r['chapter']);coverage.extend(range(int(a),int(b or a)+1))
            self.assertEqual(len(coverage),len(set(coverage)))
            omitted={17} if (r['book'],r['chapter'])==('Luke',23) else set()
            self.assertEqual(set(coverage)-omitted,set(r['reviewed_verse_labels']))
            total+=len(r['reviewed_verse_labels'])
        self.assertEqual(total,395)
    def test_cross_reference_sources_and_excerpts(self):
        count=0
        by_source={e['source_path']:e for e in self.evidence}
        for r in self.records:
            for cross in by_source[r['source_path']]['cross_reference_evidence']:
                source=self.repo/cross['source_path'];model=parse_chapter(source)
                self.assertEqual(sha256(source.read_bytes()),cross['source_sha256'])
                vv=[v for v in model['verses'] if cross['start']<=v['number']<=cross['end']]
                self.assertEqual(vv,cross['verses'])
                absent=sorted(set(range(cross['start'],cross['end']+1))-{v['number'] for v in vv})
                self.assertEqual(absent,cross['unavailable_labels'])
                if absent:self.assertEqual((cross['book'],cross['chapter'],absent),('Luke',23,[17]))
                count+=1
        self.assertEqual(count,25)
    def test_source_excerpt_primary_text_exact(self):
        self.assertEqual(len(self.evidence),11)
        for e in self.evidence:
            m=parse_chapter(self.repo/e['source_path'])
            self.assertEqual(e['verses'],m['verses']);self.assertEqual(e['notes'],m['notes'])
    def test_two_chronicles_latest_review_preserved(self):
        snap=(self.repo/REL/'fixtures/2-chronicles-04-checkpoint18.md').read_bytes()
        self.assertEqual(sha256(snap),'5b1802c17563b0a5c780a35d16629e21de013aa43baadc274c80d1cb9c2d5d24')
        self.assertEqual(hashlib.sha1(b'blob '+str(len(snap)).encode()+b'\0'+snap).hexdigest(),'623b4e6ee67fb313388179cf85d1e14408390408')
        r=self.by_id[('2 Chronicles',4)];_,body,_=validate_record(self.repo,r)
        self.assertEqual(body,snap.decode().split('\n---\n',1)[1].lstrip())
        self.assertIs(r['previous_reviewed_body_preserved'],True)
    def test_candidate_sections_and_no_obsolete_template_attribution(self):
        for r in self.records:
            _,body,_=validate_record(self.repo,r)
            for h in ('## Before You Read','## Read the Chapter','## After You Read','### Chapter Path','### Reading Carefully'):
                self.assertIn(h,body)
            for stale in ('The translation notes especially mark','The earliest and most weighty witnesses support','The chapter’s own structure and translation notes guide this Companion’s outline.'):
                self.assertNotIn(stale,body)
    def test_open_interpretive_questions_retained(self):
        for k in [('1 Corinthians',13),('1 Corinthians',14),('Revelation',20)]:
            self.assertGreaterEqual(len(self.by_id[k]['open_questions']),2)
        _,body,_=validate_record(self.repo,self.by_id[('1 Corinthians',13)])
        self.assertIn('burning reading',body);self.assertIn('alternative boasting reading',body)
    def test_unsafe_paths_and_duplicate_metadata_rejected(self):
        for s in ('../bad','/tmp/bad','.git/config'):
            with self.assertRaises(ValueError):safe_path(self.repo,s)
        with self.assertRaises(ValueError):split_document('---\nbook: Luke\nbook: John\n---\n\nText')
    def test_tampered_manifest_candidate_hash_rejected(self):
        bad=copy.deepcopy(self.records[0]);bad['candidate_sha256']='0'*64
        with self.assertRaises(ValueError):validate_record(self.repo,bad)
    def test_api_roundtrip_all_reconciled_sources(self):
        for r in self.records:
            m=parse_chapter(self.repo/r['source_path']);identity,expected=expected_chapter(self.repo,r['source_path'])
            d={**identity,**{k:m[k] for k in ('verses','blocks','notes','vocabulary')}}
            self.assertEqual(compare_response(d,identity,expected)['status'],'TARGET_CONTENT_MATCH')
    def fixture(self):
        r=self.by_id[('Luke',24)];m=parse_chapter(self.repo/r['source_path'])
        identity,expected=expected_chapter(self.repo,r['source_path'])
        d=copy.deepcopy({**identity,**{k:m[k] for k in ('verses','blocks','notes','vocabulary')}})
        return d,identity,expected
    def test_wrong_translation_or_missing_identity_rejected(self):
        d,i,e=self.fixture();d['translation']='tsw'
        self.assertEqual(compare_response(d,i,e)['status'],'UNVERIFIABLE_RESPONSE')
        d,i,e=self.fixture();del d['book_slug']
        self.assertEqual(compare_response(d,i,e)['status'],'UNVERIFIABLE_RESPONSE')
    def test_empty_duplicate_and_mismatched_block_verses_rejected(self):
        d,i,e=self.fixture();d['verses'][0]['text']=''
        self.assertEqual(compare_response(d,i,e)['status'],'UNVERIFIABLE_RESPONSE')
        d,i,e=self.fixture();d['verses'].append(copy.deepcopy(d['verses'][0]))
        self.assertEqual(compare_response(d,i,e)['status'],'UNVERIFIABLE_RESPONSE')
        d,i,e=self.fixture();d['blocks'][1]['verses'].pop()
        self.assertEqual(compare_response(d,i,e)['status'],'UNVERIFIABLE_RESPONSE')
    def test_consistently_missing_verse_still_fails_target_match(self):
        d,i,e=self.fixture();d['verses']=[v for v in d['verses'] if v['number']!=6]
        for b in d['blocks']:
            if b['type']=='paragraph':b['verses']=[v for v in b['verses'] if v['number']!=6]
        result=compare_response(d,i,e)
        self.assertEqual(result['status'],'DIFFERS_FROM_CANDIDATE');self.assertIs(result['content_match'],False)
    def test_stale_notes_and_embedded_definitions_detected(self):
        d,i,e=self.fixture();d['notes'][0]['text']='The old false bracket claim.'
        self.assertIn('notes',compare_response(d,i,e)['different_components'])
        d,i,e=self.fixture();d['vocabulary'][0]['term']+=': '+d['vocabulary'][0]['definition'];d['vocabulary'][0]['definition']=''
        self.assertIn('vocabulary',compare_response(d,i,e)['different_components'])
    def test_live_comparison_plan_uses_38_read_only_targets(self):
        from unittest.mock import patch
        from urllib.parse import urlparse,parse_qs
        from check_reader_correction_targets import run
        def local_response(url):
            u=urlparse(url);translation=parse_qs(u.query)['translation'][0]
            slug,ch=u.path.rsplit('/',2)[1:];ch=int(ch)
            paths=list((self.repo/('books' if translation=='tsw' else 'translations/fluent')).glob('*/*/*_'+f'{ch:02d}'+'.md'))
            source=next(p for p in paths if p.parent.name==slug)
            m=parse_chapter(source)
            return {'translation':translation,'book':m['meta']['book'],'book_slug':slug,'chapter':ch,
                    **{k:m[k] for k in ('verses','blocks','notes','vocabulary')}}
        with patch('check_reader_correction_targets.retrieve',side_effect=local_response):
            report=run(self.repo,['churchcommons','mvp'])
        self.assertEqual(len(report['results']),38)
        self.assertTrue(report['all_targets_match'])
        self.assertFalse(report['publication_allowed']);self.assertFalse(report['website_changed'])
    def test_failed_network_reads_cannot_pass(self):
        from unittest.mock import patch
        from check_reader_correction_targets import run
        with patch('check_reader_correction_targets.retrieve',side_effect=OSError('Offline test')):
            report=run(self.repo,['churchcommons'])
        self.assertEqual(len(report['results']),19)
        self.assertFalse(report['all_targets_match'])
        self.assertTrue(all(x['status']=='UNVERIFIABLE_RESPONSE' for x in report['results']))
    def test_readiness_report_not_publication_approval(self):
        live=read_json(self.repo/REL/'LIVE_READER_OBSERVATIONS.json')
        self.assertIs(live['website_changed'],False);self.assertIs(live['publication_allowed'],False)
        self.assertIs(live['browser_interaction_test_completed'],False)
        self.assertEqual(live['companion_registry']['registered_ids'],['tsw-study'])


def main() -> int:
    global ROOT
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--json-out',type=Path)
    a=p.parse_args();ROOT=a.repo
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ReconciliationTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'companion_candidates':11,
            'source_verse_records':395,'cross_reference_ranges':25,
            'review_scope':'Offline integrity, reference, preservation, and comparator regression tests; not independent scholarly approval.',
            'publication_allowed':False,'website_changed':False}
    if a.json_out:a.json_out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
