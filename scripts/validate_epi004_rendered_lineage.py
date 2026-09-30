#!/usr/bin/env python3
"""Reconcile public claim traces to canonical assertion-evidence and source records."""
from __future__ import annotations
import html,json,re
from pathlib import Path
from trace_claim_lineage import build_index, trace_row

ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
rows=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
sources=json.loads((SITE/'data'/'sources.json').read_text(encoding='utf-8'))['sources']
source_ids={s['source_id'] for s in sources}; index=build_index(rows)
by_assertion={}
for r in rows: by_assertion.setdefault(r['assertion_id'],[]).append(r)
errors=[]; checked_assertions=0; checked_evidence=0

def terminal_labels(t):
 if t.get('terminal'): return [t['terminal']]
 out=[]
 for b in t.get('branches',[]): out.extend(terminal_labels(b))
 return out

for oid,slug in SLUGS.items():
 text=(SITE/'objects'/slug/'index.html').read_text(encoding='utf-8')
 for a in [x for x in assertions if x.get('subject_id')==oid]:
  aid=a['assertion_id']; ars=by_assertion.get(aid,[])
  if not ars: continue
  checked_assertions+=1
  if f'class="claim-lineage" data-assertion-id="{aid}"' not in text:
   errors.append(f'{oid}/{aid}: claim-lineage disclosure missing')
  for r in ars:
   checked_evidence+=1; eid=r['assertion_evidence_id']; sid=r['source_id']
   if sid not in source_ids: errors.append(f'{oid}/{aid}/{eid}: source {sid} missing canonically')
   m=re.search(rf'<li class="claim-lineage-evidence"[^>]*data-assertion-evidence-id="{re.escape(eid)}"[^>]*>(.*?)</li>',text,re.S)
   if not m:
    errors.append(f'{oid}/{aid}/{eid}: rendered evidence trace missing'); continue
   block=m.group(1)
   if f'data-source-id="{sid}"' not in m.group(0):
    errors.append(f'{oid}/{aid}/{eid}: rendered source ID mismatch')
   if html.escape(r.get('locator') or 'no locator recorded') not in block:
    errors.append(f'{oid}/{aid}/{eid}: locator missing')
   for parent in r.get('inherits_claim_from_source_ids') or []:
    if parent not in block: errors.append(f'{oid}/{aid}/{eid}: parent {parent} missing')
   terms=terminal_labels(trace_row(r,index))
   for term in terms:
    public={'ESTABLISHED_ROOT':'Established claim root','UNRESOLVED_ANCESTRY':'Unresolved ancestry','BROKEN_REFERENCE':'Broken lineage reference','CYCLE':'Lineage cycle detected'}[term]
    if public not in block: errors.append(f'{oid}/{aid}/{eid}: terminal {public} missing')
if checked_assertions==0 or checked_evidence==0: errors.append('reference corpus not exercised')
if errors:
 print('EPI-004 RENDERING FAIL')
 for e in errors: print('-',e)
 raise SystemExit(1)
print(f'EPI-004 rendering PASS: {checked_assertions} assertions / {checked_evidence} evidence relationships traced across three reference objects.')
