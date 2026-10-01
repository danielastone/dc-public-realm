#!/usr/bin/env python3
"""Reconcile materialized canonical conflicts to visible public warnings."""
from __future__ import annotations
import html,json,re
from pathlib import Path
from detect_material_conflicts import conflict_index
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
rows=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
idx=conflict_index(rows); errors=[]; checked=0
reference_assertion_ids={a['assertion_id'] for a in assertions if a.get('subject_id') in SLUGS}
expected_conflicts={aid for aid in idx if aid in reference_assertion_ids}
rendered_conflicts=set()
for oid,slug in SLUGS.items():
 text=(SITE/'objects'/slug/'index.html').read_text(encoding='utf-8')
 object_assertions=[a for a in assertions if a.get('subject_id')==oid]
 for a in object_assertions:
  aid=a['assertion_id']; cr=idx.get(aid,[])
  marker=f'data-conflict-assertion-id="{aid}"'
  if cr:
   checked+=1
   if marker not in text:
    errors.append(f'{oid}/{aid}: canonical conflict has no visible warning'); continue
   rendered_conflicts.add(aid)
   m=re.search(rf'<aside class="material-conflict" data-conflict-assertion-id="{re.escape(aid)}"[^>]*>(.*?)</aside>',text,re.S)
   if not m:
    errors.append(f'{oid}/{aid}: malformed conflict warning'); continue
   block=m.group(1)
   if 'Conflicting evidence.' not in block or 'should not be read as uncontested' not in block:
    errors.append(f'{oid}/{aid}: warning does not visibly qualify assertion')
   for r in cr:
    for value,label in [(r['assertion_evidence_id'],'evidence ID'),(r['source_id'],'source ID'),(r['locator'],'locator'),(r['evidence_note'],'evidence note')]:
     if html.escape(value) not in m.group(0): errors.append(f'{oid}/{aid}/{r["assertion_evidence_id"]}: {label} missing')
  elif marker in text:
   errors.append(f'{oid}/{aid}: rendered conflict invented without canonical CONTRADICTS evidence')
if rendered_conflicts != expected_conflicts:
 errors.append(f'canonical/rendered conflict set mismatch: canonical={sorted(expected_conflicts)}, rendered={sorted(rendered_conflicts)}')
if errors:
 print('EPI-005 RENDERING FAIL')
 for e in errors: print('-',e)
 raise SystemExit(1)
print(f'EPI-005 rendering PASS: {checked} materialized canonical conflict assertions visibly qualified; no warning invented outside canonical conflict state.')
