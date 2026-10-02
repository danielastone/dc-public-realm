#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
assertions={a['assertion_id']:a for a in json.loads((DATA/'assertions.json').read_text(encoding='utf-8'))['assertions']}
overviews={o['object_entity_id']:o for o in json.loads((DATA/'object-overviews.json').read_text(encoding='utf-8'))['object_overviews']}
slugs={
 'OBJ-0001':'jose-gervasio-artigas',
 'OBJ-0002':'jose-de-san-martin',
 'OBJ-0003':'cuban-american-friendship-urn',
}
needles={
 'OBJ-0001':['record-overview','National Park Service','Public domain'],
 'OBJ-0002':['record-overview','October 28, 1925','October 6, 1976','AgnosticPreachersKid','CC BY-SA 3.0'],
 'OBJ-0003':['record-overview','Presented to the United States','AgnosticPreachersKid','CC BY-SA 4.0','USS Maine'],
}
required_fields={
 'person_memorial':['location','event_date','subject_dates','subject_bio'],
 'historical_object':['location','event_date','object_context'],
}
errors=[]
for oid,slug in slugs.items():
 p=ROOT/'site'/'objects'/slug/'index.html'
 if not p.exists():
  errors.append(f'{slug}: page missing')
  continue
 text=p.read_text(encoding='utf-8')
 o=overviews.get(oid)
 if not o:
  errors.append(f'{oid}: materialized overview missing')
  continue
 if f'data-object-entity-id="{oid}"' not in text:
  errors.append(f'{oid}: rendered overview missing object identity')
 for needle in needles[oid]:
  if needle not in text:
   errors.append(f'{slug}: missing {needle!r}')
 refs=o.get('assertion_refs') or {}
 for field in required_fields[o['record_type']]:
  raw=refs.get(field)
  ids=raw if isinstance(raw,list) else ([raw] if raw else [])
  if not ids:
   errors.append(f'{oid}.{field}: no assertion refs in materialized overview')
   continue
  for aid in ids:
   if aid not in assertions:
    errors.append(f'{oid}.{field}: unresolved assertion {aid}')
  marker=f'data-assertion-ids="{",".join(ids)}"'
  if marker not in text:
   errors.append(f'{oid}.{field}: rendered HTML missing traceability marker {marker}')
 if o.get('secondary_event_label'):
  aid=refs.get('secondary_event_date')
  ids=aid if isinstance(aid,list) else ([aid] if aid else [])
  marker=f'data-assertion-ids="{",".join(ids)}"' if ids else None
  if not marker or marker not in text:
   errors.append(f'{oid}.secondary_event_date: rendered HTML missing assertion traceability')
 rendered_ids=set()
 for value in re.findall(r'data-assertion-ids="([^"]+)"',text):
  rendered_ids.update(x for x in value.split(',') if x)
 unknown=sorted(rendered_ids-set(assertions))
 if unknown:
  errors.append(f'{oid}: rendered unknown assertion IDs {unknown}')
if errors:
 raise SystemExit('Overview rendering validation failed:\n- '+'\n- '.join(errors))
print('Overview rendering validation passed: all displayed overview facts carry resolvable canonical assertion IDs')
