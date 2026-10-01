#!/usr/bin/env python3
"""Ensure conflict qualification is visible before optional provenance disclosure."""
from __future__ import annotations
import json,re
from pathlib import Path
from detect_material_conflicts import conflict_index
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
rows=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']; idx=conflict_index(rows)
errors=[]
for oid,slug in SLUGS.items():
 text=(SITE/'objects'/slug/'index.html').read_text(encoding='utf-8')
 for a in [x for x in assertions if x.get('subject_id')==oid and x['assertion_id'] in idx]:
  aid=a['assertion_id']
  start=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
  warn=text.find(f'data-conflict-assertion-id="{aid}"',start.end() if start else 0)
  trace=text.find(f'class="claim-lineage" data-assertion-id="{aid}"',start.end() if start else 0)
  if not start or warn<0: errors.append(f'{oid}/{aid}: warning absent from assertion')
  elif trace>=0 and warn>trace: errors.append(f'{oid}/{aid}: conflict hidden after provenance disclosure')
if errors:
 print('EPI-005 PLACEMENT FAIL'); [print('-',e) for e in errors]; raise SystemExit(1)
print('EPI-005 placement PASS: every conflict warning precedes optional claim-lineage disclosure.')
