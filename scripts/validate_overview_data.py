#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data'/'object-overviews.json').read_text(encoding='utf-8'))['object_overviews']
expected={'OBJ-0001','OBJ-0002','OBJ-0003'}
ids={x.get('object_entity_id') for x in rows}
errors=[]
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
