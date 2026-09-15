"""Regression checks for a source record split across public verse labels."""
from pathlib import Path
import argparse,copy,json,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from audit_fluent_revision import audit

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-text',type=Path,required=True);a=p.parse_args()
 ledger=json.loads((Path(__file__).parent/'psalms-verse-review.json').read_text());src=a.source_text.read_bytes()
 assert not audit(ROOT,ledger,src)
 def row(d,ref):return next(v for v in d['verses']if v['reference']==ref)
 cases={}
 for name,mutate in [
  ('undeclared_duplicate',lambda d:row(d,'Psalms 13:6').pop('source_partition')),
  ('all_partitions_removed',lambda d:[row(d,r).pop('source_partition')for r in ['Psalms 13:5','Psalms 13:6']]),
  ('overlapping_words',lambda d:row(d,'Psalms 13:6')['source_partition'].update(word_start=6)),
  ('missing_word',lambda d:row(d,'Psalms 13:6')['source_partition'].update(word_start=8)),
  ('out_of_range',lambda d:row(d,'Psalms 13:6')['source_partition'].update(word_end=12)),
  ('noninteger_range',lambda d:row(d,'Psalms 13:6')['source_partition'].update(word_start='7')),
  ('missing_explanation',lambda d:row(d,'Psalms 13:6')['source_partition'].update(reason='')),
  ('changed_original_hash',lambda d:row(d,'Psalms 13:6').update(source_verse_sha256='0'*64)),
  ('missing_title_record',lambda d:row(d,'Psalms 3:1').pop('source_segments')),
  ('title_hash_corrupted',lambda d:row(d,'Psalms 3:1')['source_segments'][0].update(source_verse_sha256='0'*64))]:
  d=copy.deepcopy(ledger);mutate(d);errors=audit(ROOT,d,src);assert errors,name;cases[name]={'rejected':True,'errors':errors}
 result={'status':'PASSED','valid_psalm_titles_and_split_record_accepted':True,'malformed_cases':cases,'scope':'Source binding validation only, not editorial review.'}
 (Path(__file__).parent/'partition-regression-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASSED','invalid_cases_rejected':len(cases)}))
if __name__=='__main__':main()
