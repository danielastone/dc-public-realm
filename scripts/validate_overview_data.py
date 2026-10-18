#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

parser=argparse.ArgumentParser(description='Validate object overview records.')
parser.add_argument('--scope',choices=('baseline','materialized'),default='baseline',
                    help='baseline: frozen ROOT/data with the exact three-object ID set (default); '
                         'materialized: KNOWLEDGE_DATA_DIR records, per-record checks only')
args=parser.parse_args()

if args.scope=='materialized':
 override=os.environ.get('KNOWLEDGE_DATA_DIR')
 if override is None or not override.strip():
  raise SystemExit('Overview data validation failed: --scope=materialized requires KNOWLEDGE_DATA_DIR')
 # Relative paths resolve against the working directory, as in validate_data.py.
 source=Path(override)/'object-overviews.json'
 if not source.is_file():
  raise SystemExit(f'Overview data validation failed: overview file not found under KNOWLEDGE_DATA_DIR: {source}')
else:
 source=ROOT/'data'/'object-overviews.json'
print(f'Overview data scope: {args.scope}; source: {source}')
rows=json.loads(source.read_text(encoding='utf-8'))['object_overviews']
errors=[]
if args.scope=='baseline':
 # Frozen-baseline regression: the pre-ledger corpus is exactly these three objects.
 expected={'OBJ-0001','OBJ-0002','OBJ-0003'}
 ids={x.get('object_entity_id') for x in rows}
 if ids!=expected: errors.append(f'overview IDs {sorted(ids)} do not match expected {sorted(expected)}')
common=('record_type','location','location_source_url','event_label','event_date','event_source_url')
for o in rows:
 oid=o.get('object_entity_id','UNKNOWN')
 for k in common:
  if not o.get(k): errors.append(f'{oid}: missing {k}')
 if o.get('record_type')=='person_memorial':
  for k in ('subject_name','subject_dates','subject_bio','subject_source_url'):
   if not o.get(k): errors.append(f'{oid}: missing {k}')
 elif o.get('record_type')=='historical_object':
  for k in ('object_context','object_context_source_url'):
   if not o.get(k): errors.append(f'{oid}: missing {k}')
 else: errors.append(f'{oid}: unsupported record_type {o.get("record_type")}')
if errors: raise SystemExit('Overview data validation failed:\n- '+'\n- '.join(errors))
print('Overview data validation passed')
