#!/usr/bin/env python3
"""Publish visible EPI-005 conflict warnings from canonical CONTRADICTS evidence."""
from __future__ import annotations
import html,json,re
from pathlib import Path
from detect_material_conflicts import conflict_index, validate_conflict_records
from publication_index import path_for, published_objects

ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'; DATA=ROOT/'data'
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
rows=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
errors=validate_conflict_records(rows)
if errors:
 raise SystemExit('EPI-005 invalid canonical conflict rows: '+ '; '.join(errors))
conflicts=conflict_index(rows)

def warning(aid, conflict_rows):
 items=[]
 for r in conflict_rows:
  items.append(
   f'<li data-conflict-evidence-id="{html.escape(r["assertion_evidence_id"])}" '
   f'data-source-id="{html.escape(r["source_id"])}">'
   f'<strong>{html.escape(r["source_id"])}</strong>, {html.escape(r["locator"])}: '
   f'{html.escape(r["evidence_note"])}</li>'
  )
 return (
  f'<aside class="material-conflict" data-conflict-assertion-id="{html.escape(aid)}" role="note">'
  f'<strong>Conflicting evidence.</strong> The canonical record contains evidence that contradicts this assertion. '
  f'The displayed value should not be read as uncontested.'
  f'<ul>{"".join(items)}</ul></aside>'
 )

for entity in published_objects(DATA):
 oid=entity['entity_id']; path=SITE/path_for(oid,DATA); text=path.read_text(encoding='utf-8')
 for a in [x for x in assertions if x.get('subject_id')==oid]:
  aid=a['assertion_id']; cr=conflicts.get(aid,[])
  if not cr: continue
  if f'data-conflict-assertion-id="{aid}"' in text: continue
  m=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
  if not m: raise SystemExit(f'EPI-005 {oid}/{aid}: rendered assertion container missing')
  # Insert immediately after the assertion opening so conflict is visible without opening provenance details.
  text=text[:m.end()]+warning(aid,cr)+text[m.end():]
 path.write_text(text,encoding='utf-8')
 print('Published material conflicts',oid)
