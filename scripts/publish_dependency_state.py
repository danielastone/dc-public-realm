#!/usr/bin/env python3
"""Publish conservative dependency state beside claim evidence/provenance entries."""
from __future__ import annotations
import html,json,re
from pathlib import Path
from derive_dependency_state import derive
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
a=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
ae=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
rules=json.loads((ROOT/'data'/'publication_dependency_rules.json').read_text(encoding='utf-8'))['rules']
by_assertion={}
for row in ae: by_assertion.setdefault(row['assertion_id'],[]).append(row)
for oid,slug in SLUGS.items():
 p=SITE/'objects'/slug/'index.html'; text=p.read_text(encoding='utf-8')
 for assertion in [x for x in a if x.get('subject_id')==oid]:
  aid=assertion['assertion_id']; rows=by_assertion.get(aid,[])
  # Publish only where corroboration can be mistaken for independence: two or more evidence records.
  if len(rows)<2: continue
  items=[]
  for row in rows:
   state=derive(row); r=rules[state]; inherited=row.get('inherits_claim_from_source_ids') or []
   ancestry=('; inherits claim from '+', '.join(inherited)) if inherited else ''
   items.append(f'<li data-assertion-evidence-id="{html.escape(row["assertion_evidence_id"])}" data-source-id="{html.escape(row["source_id"])}" data-dependency-state="{state}"><strong>{html.escape(row["source_id"])}</strong>: {html.escape(r["public_label"])}. {html.escape(r["explanation"]+ancestry)}</li>')
  block=f'<details class="evidence-independence" data-assertion-id="{html.escape(aid)}"><summary>Source relationship</summary><p>Corroboration is not automatically independent. These labels describe claim ancestry for this assertion, not the source as a whole.</p><ul>{"".join(items)}</ul></details>'
  # Attach to the canonical rendered assertion container introduced by EPI-001.
  m=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
  if not m: raise SystemExit(f'{oid}/{aid}: canonical assertion container missing')
  if f'class="evidence-independence" data-assertion-id="{aid}"' in text: continue
  # Insert before the closing tag of an article; list-item claims get the block before their closing li.
  tag='article' if m.group(0).startswith('<article') else 'li'; close=text.find(f'</{tag}>',m.end())
  if close<0: raise SystemExit(f'{oid}/{aid}: assertion close tag missing')
  text=text[:close]+block+text[close:]
 p.write_text(text,encoding='utf-8'); print('Published dependency state',oid)
