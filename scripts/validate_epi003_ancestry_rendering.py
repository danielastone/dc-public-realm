#!/usr/bin/env python3
"""EPI-003 acceptance: canonical ancestry fields survive multi-source publication."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
evidence=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
by_assertion={}
for row in evidence: by_assertion.setdefault(row['assertion_id'],[]).append(row)
errors=[]; checked=0; unknown_checked=0
for oid,slug in SLUGS.items():
 text=(SITE/'objects'/slug/'index.html').read_text(encoding='utf-8')
 for a in [x for x in assertions if x.get('subject_id')==oid]:
  rows=by_assertion.get(a['assertion_id'],[])
  if len(rows)<2: continue
  for row in rows:
   checked+=1; eid=row['assertion_evidence_id']; origin=row.get('claim_origin','UNKNOWN') or 'UNKNOWN'; dep=row.get('dependency_status','UNKNOWN') or 'UNKNOWN'; inherited=row.get('inherits_claim_from_source_ids') or []
   m=re.search(rf'<li[^>]*data-assertion-evidence-id="{re.escape(eid)}"[^>]*>(.*?)</li>',text,re.S)
   if not m: errors.append(f'{oid}/{eid}: evidence relationship missing'); continue
   block=m.group(1)
   if f'data-claim-origin="{origin}"' not in block: errors.append(f'{oid}/{eid}: claim_origin {origin} not preserved')
   if f'data-canonical-dependency-status="{dep}"' not in block: errors.append(f'{oid}/{eid}: dependency_status {dep} not preserved')
   if f'data-inherited-source-count="{len(inherited)}"' not in block: errors.append(f'{oid}/{eid}: inherited source count not preserved')
   for source_id in inherited:
    if source_id not in block: errors.append(f'{oid}/{eid}: inherited source {source_id} not visible')
   if not inherited and 'none recorded; this does not establish independence' not in block:
    errors.append(f'{oid}/{eid}: empty inheritance list lost its uncertainty qualifier')
   if origin=='UNKNOWN' or dep=='UNKNOWN':
    unknown_checked+=1
    if 'UNKNOWN' not in block: errors.append(f'{oid}/{eid}: unknown ancestry disappeared')
if checked==0: errors.append('no multi-source evidence relationships exercised')
if unknown_checked==0: errors.append('no canonical UNKNOWN ancestry case exercised in reference corpus')
if errors:
 print('EPI-003 FAIL')
 for e in errors: print('-',e)
 raise SystemExit(1)
print(f'EPI-003 PASS: {checked} evidence relationships checked; {unknown_checked} preserve explicit UNKNOWN ancestry.')
