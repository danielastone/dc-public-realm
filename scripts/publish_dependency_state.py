#!/usr/bin/env python3
"""Publish conservative dependency state and explicit canonical ancestry beside claim evidence."""
from __future__ import annotations
import html,json,re
from pathlib import Path
from derive_dependency_state import derive
from publication_index import path_for, published_objects
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'; DATA=ROOT/'data'
a=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
ae=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
rules=json.loads((ROOT/'data'/'publication_dependency_rules.json').read_text(encoding='utf-8'))['rules']
by_assertion={}
for row in ae: by_assertion.setdefault(row['assertion_id'],[]).append(row)

def ancestry_detail(row):
 origin=row.get('claim_origin','UNKNOWN') or 'UNKNOWN'
 dependency=row.get('dependency_status','UNKNOWN') or 'UNKNOWN'
 inherited=row.get('inherits_claim_from_source_ids') or []
 inherited_text=', '.join(inherited) if inherited else 'none recorded; this does not establish independence'
 return (f'<dl class="ancestry-state"><dt>Claim origin</dt><dd data-claim-origin="{html.escape(origin)}">{html.escape(origin)}</dd>'
         f'<dt>Dependency status</dt><dd data-canonical-dependency-status="{html.escape(dependency)}">{html.escape(dependency)}</dd>'
         f'<dt>Inherited claim from</dt><dd data-inherited-source-count="{len(inherited)}">{html.escape(inherited_text)}</dd></dl>')

for entity in published_objects(DATA):
 oid=entity['entity_id']; p=SITE/path_for(oid,DATA); text=p.read_text(encoding='utf-8')
 for assertion in [x for x in a if x.get('subject_id')==oid]:
  aid=assertion['assertion_id']; rows=by_assertion.get(aid,[])
  if len(rows)<2: continue
  items=[]
  for row in rows:
   state=derive(row); r=rules[state]
   items.append(f'<li data-assertion-evidence-id="{html.escape(row["assertion_evidence_id"])}" data-source-id="{html.escape(row["source_id"])}" data-dependency-state="{state}"><strong>{html.escape(row["source_id"])}</strong>: {html.escape(r["public_label"])}. {html.escape(r["explanation"])}{ancestry_detail(row)}</li>')
  block=f'<details class="evidence-independence" data-for-assertion-id="{html.escape(aid)}"><summary>Source relationship</summary><p>Corroboration is not automatically independent. Claim origin and dependency status below reproduce the canonical ancestry state; UNKNOWN means the project has not established that part of the lineage.</p><ul>{"".join(items)}</ul></details>'
  m=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
  if not m: raise SystemExit(f'{oid}/{aid}: canonical assertion container missing')
  if f'class="evidence-independence" data-for-assertion-id="{aid}"' in text: continue
  tag='article' if m.group(0).startswith('<article') else 'li'; close=text.find(f'</{tag}>',m.end())
  if close<0: raise SystemExit(f'{oid}/{aid}: assertion close tag missing')
  text=text[:close]+block+text[close:]
 p.write_text(text,encoding='utf-8'); print('Published dependency and ancestry state',oid)
