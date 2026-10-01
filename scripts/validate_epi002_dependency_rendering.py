#!/usr/bin/env python3
"""EPI-002 acceptance: multi-source assertions publish canonical dependency states exactly."""
from __future__ import annotations
import json,re
from pathlib import Path
from derive_dependency_state import derive
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
evidence=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
by_assertion={}
for row in evidence: by_assertion.setdefault(row['assertion_id'],[]).append(row)
errors=[]; checked=0
for oid,slug in SLUGS.items():
 text=(SITE/'objects'/slug/'index.html').read_text(encoding='utf-8')
 for a in [x for x in assertions if x.get('subject_id')==oid]:
  aid=a['assertion_id']; rows=by_assertion.get(aid,[])
  if len(rows)<2: continue
  checked+=1
  if f'class="evidence-independence" data-for-assertion-id="{aid}"' not in text:
   errors.append(f'{oid}/{aid}: source-relationship disclosure missing')
  for row in rows:
   eid=row['assertion_evidence_id']; expected=derive(row); pattern=rf'<li[^>]*data-assertion-evidence-id="{re.escape(eid)}"[^>]*>'; m=re.search(pattern,text)
   if not m: errors.append(f'{oid}/{aid}/{eid}: rendered evidence relationship missing'); continue
   tag=m.group(0)
   if f'data-source-id="{row["source_id"]}"' not in tag: errors.append(f'{oid}/{aid}/{eid}: source identity mismatch')
   if f'data-dependency-state="{expected}"' not in tag: errors.append(f'{oid}/{aid}/{eid}: expected dependency state {expected}')
   if expected=='INDEPENDENT' and (row.get('dependency_status')!='INDEPENDENT' or row.get('claim_origin') not in {'ORIGINAL_TO_SOURCE','INDEPENDENT_CLAIM_ROOT'}): errors.append(f'{oid}/{aid}/{eid}: independence overstated')
if checked==0: errors.append('no multi-source reference assertions were exercised')
if errors:
 print('EPI-002 RENDERING FAIL'); [print('-',e) for e in errors]; raise SystemExit(1)
print(f'EPI-002 rendering PASS: {checked} multi-source assertions reconciled across three reference objects.')
