"""Regression checks for the documented, pre-existing Nehemiah public-label gap."""
from pathlib import Path
import argparse,copy,json,sys
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from audit_fluent_revision import audit
p=argparse.ArgumentParser();p.add_argument('--source-directory',type=Path,required=True);sd=p.parse_args().source_directory
lp=R/'audit/fluent-revision/2026-09-15-nehemiah-1-13/nehemiah-verse-review.json';l=json.loads(lp.read_text());s=(sd/'nehemiah-pinned-hebrew.xml').read_bytes()
assert audit(R,l,s)==[]
for mode in ['undeclared','wrong_label','unexplained','duplicate','out_of_range','missing_source_record']:
 x=copy.deepcopy(l);ch=x['chapters'][6]
 if mode=='undeclared':del ch['source_omitted_public_labels']
 elif mode=='wrong_label':ch['source_omitted_public_labels']=[67]
 elif mode=='unexplained':ch['source_omission_reason']=''
 elif mode=='duplicate':ch['source_omitted_public_labels']=[68,68]
 elif mode=='out_of_range':ch['source_omitted_public_labels']=[74]
 else:x['verses']=[v for v in x['verses']if v['reference']!='Nehemiah 7:69']
 errors=audit(R,x,s);assert errors,mode
 if mode=='missing_source_record':assert 'ledger/source coverage differs'in errors
# The unchanged contiguous-label behavior remains valid for the prior Ezra batch.
e=json.loads((R/'audit/fluent-revision/2026-09-15-ezra-1-10/ezra-verse-review.json').read_text());assert audit(R,e,(sd/'ezra-pinned-hebrew.xml').read_bytes())==[]
print('source-gap regression checks passed')
