#!/usr/bin/env python3
"""Audit canonical reference-object lineage without requiring invented roots."""
from __future__ import annotations
import json
from pathlib import Path
from trace_claim_lineage import build_index, trace_row, ROOT, UNRESOLVED, BROKEN, CYCLE

ROOTDIR=Path(__file__).resolve().parents[1]
rows=json.loads((ROOTDIR/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
assertions=json.loads((ROOTDIR/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
ref_ids={a['assertion_id'] for a in assertions if a.get('subject_id') in {'OBJ-0001','OBJ-0002','OBJ-0003'}}
rows=[r for r in rows if r['assertion_id'] in ref_ids]
index=build_index(rows)

def terminals(t):
 if t.get('terminal'): return [t['terminal']]
 out=[]
 for b in t.get('branches',[]): out.extend(terminals(b))
 return out

counts={ROOT:0,UNRESOLVED:0,BROKEN:0,CYCLE:0}
for r in rows:
 ts=terminals(trace_row(r,index))
 for t in ts: counts[t]+=1
 if BROKEN in ts or CYCLE in ts:
  raise SystemExit(f'EPI-004 corpus FAIL {r["assertion_evidence_id"]}: {ts}')
if not rows: raise SystemExit('EPI-004 corpus FAIL: no reference-object evidence rows')
if counts[UNRESOLVED]==0: raise SystemExit('EPI-004 corpus FAIL: expected real unresolved ancestry coverage')
print(f'EPI-004 corpus PASS: {len(rows)} evidence rows; terminals={counts}')
