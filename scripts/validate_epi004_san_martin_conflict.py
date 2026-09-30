#!/usr/bin/env python3
"""EPI-004 regression: San Martín Daumas/Dumont disagreement must remain recoverable."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
rows=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
a=next((x for x in assertions if x.get('assertion_id')=='A-0106'),None)
if not a: raise SystemExit('EPI-004 SAN MARTIN FAIL: A-0106 missing')
if a.get('subject_id')!='OBJ-0002' or a.get('predicate')!='AUTHOR_ATTRIBUTION':
 raise SystemExit('EPI-004 SAN MARTIN FAIL: A-0106 identity changed')
note=a.get('interpretation_note','')
for term in ('Daumas','Dumont','conflict'):
 if term.lower() not in note.lower(): raise SystemExit(f'EPI-004 SAN MARTIN FAIL: assertion note lost {term}')
ars=[r for r in rows if r.get('assertion_id')=='A-0106']
if len(ars)<2: raise SystemExit('EPI-004 SAN MARTIN FAIL: attribution conflict lacks multiple evidence records')
support=[r for r in ars if r.get('evidence_role') in {'PRIMARY_SUPPORT','CORROBORATION','SUPPORTS'} and 'Daumas' in r.get('evidence_note','')]
contradict=[r for r in ars if r.get('evidence_role')=='CONTRADICTS' and 'Dumont' in r.get('evidence_note','')]
if not support: raise SystemExit('EPI-004 SAN MARTIN FAIL: Daumas supporting evidence missing')
if not contradict: raise SystemExit('EPI-004 SAN MARTIN FAIL: Dumont contradictory evidence missing')
text=(SITE/'objects'/'jose-de-san-martin'/'index.html').read_text(encoding='utf-8')
if 'class="claim-lineage" data-assertion-id="A-0106"' not in text:
 raise SystemExit('EPI-004 SAN MARTIN FAIL: A-0106 public lineage trace missing')
for r in support+contradict:
 eid=r['assertion_evidence_id']
 m=re.search(rf'<li class="claim-lineage-evidence"[^>]*data-assertion-evidence-id="{re.escape(eid)}"[^>]*>(.*?)</li>',text,re.S)
 if not m: raise SystemExit(f'EPI-004 SAN MARTIN FAIL: {eid} missing from public trace')
 block=m.group(1)
 if r['source_id'] not in m.group(0): raise SystemExit(f'EPI-004 SAN MARTIN FAIL: {eid} source identity lost')
 if r.get('locator') and r['locator'] not in block: raise SystemExit(f'EPI-004 SAN MARTIN FAIL: {eid} locator lost')
# The rendered assertion itself must retain both names; a provenance drawer alone cannot repair a normalized display that erased the disagreement.
container=re.search(r'<(?:article|li)[^>]*data-assertion-id="A-0106"[^>]*>(.*?)</(?:article|li)>',text,re.S)
if not container: raise SystemExit('EPI-004 SAN MARTIN FAIL: rendered A-0106 container missing')
for term in ('Daumas','Dumont'):
 if term not in container.group(1): raise SystemExit(f'EPI-004 SAN MARTIN FAIL: rendered assertion lost {term} side of conflict')
print(f'EPI-004 San Martín PASS: A-0106 preserves Daumas support ({len(support)}) and Dumont contradiction ({len(contradict)}) with public traceability.')
