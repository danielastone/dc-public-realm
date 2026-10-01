#!/usr/bin/env python3
"""EPI-005 canonical conflict inventory and detector regression.

The repository keeps frozen seed data plus a transaction ledger. CI invokes this
validator before materialization, so the frozen inventory is checked here. The
rendered EPI-005 validator later reconciles the transaction-materialized state.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from detect_material_conflicts import conflict_index, validate_conflict_records

ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
assertions=json.loads((ROOT/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
subject={a['assertion_id']:a.get('subject_id') for a in assertions}
reference={'OBJ-0001':'Artigas','OBJ-0002':'San Martín','OBJ-0003':'Cuban Urn'}
ref_rows=[r for r in rows if subject.get(r.get('assertion_id')) in reference]
errors=validate_conflict_records(ref_rows)
if errors:
 print('EPI-005 INVENTORY FAIL')
 for e in errors: print('-',e)
 raise SystemExit(1)
idx=conflict_index(ref_rows)
counts=Counter(reference[subject[aid]] for aid in idx)
# Frozen seed baseline. TX-20260929-002 later changes AE-0009/A-0004 to CONTRADICTS;
# the publication validator must therefore exercise four materialized conflicts.
expected={'Artigas':0,'San Martín':1,'Cuban Urn':2}
actual={name:counts.get(name,0) for name in expected}
if actual != expected:
 raise SystemExit(f'EPI-005 INVENTORY FAIL: frozen conflict assertion counts {actual}, expected {expected}')
expected_ids={'A-0106','A-0201','A-0201B'}
if set(idx) != expected_ids:
 raise SystemExit(f'EPI-005 INVENTORY FAIL: frozen conflict assertions {sorted(idx)}, expected {sorted(expected_ids)}')
synthetic=[
 {'assertion_evidence_id':'S1','assertion_id':'A','source_id':'X','evidence_role':'PRIMARY_SUPPORT','locator':'x','evidence_note':'support'},
 {'assertion_evidence_id':'S2','assertion_id':'A','source_id':'Y','evidence_role':'QUALIFIES','locator':'y','evidence_note':'qualification'},
 {'assertion_evidence_id':'S3','assertion_id':'B','source_id':'Z','evidence_role':'CONTRADICTS','locator':'z','evidence_note':'contradiction'},
]
sidx=conflict_index(synthetic)
if 'A' in sidx or set(sidx) != {'B'}:
 raise SystemExit(f'EPI-005 INVENTORY FAIL: synthetic role semantics wrong: {sidx}')
bad=[{'assertion_evidence_id':'BAD','assertion_id':'C','source_id':'Q','evidence_role':'CONTRADICTS','locator':'q'}]
if not validate_conflict_records(bad):
 raise SystemExit('EPI-005 INVENTORY FAIL: incomplete CONTRADICTS row accepted')
print('EPI-005 frozen inventory PASS: Artigas=0, San Martín=1, Cuban Urn=2; materialized publication is reconciled separately.')
for aid in sorted(idx):
 print(aid, '=>', ', '.join(r['assertion_evidence_id'] for r in idx[aid]))
