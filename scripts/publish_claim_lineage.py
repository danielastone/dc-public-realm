#!/usr/bin/env python3
"""Publish a claim-level provenance trace for every rendered reference-object assertion."""
from __future__ import annotations
import html,json,re
from pathlib import Path
from trace_claim_lineage import build_index, trace_row, ROOT, UNRESOLVED, BROKEN, CYCLE

ROOTDIR=Path(__file__).resolve().parents[1]; SITE=ROOTDIR/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
evidence=json.loads((SITE/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))['assertion_evidence']
sources=json.loads((ROOTDIR/'data'/'sources.json').read_text(encoding='utf-8'))['sources']
source_by_id={s['source_id']:s for s in sources}; index=build_index(evidence)
by_assertion={}
for row in evidence: by_assertion.setdefault(row['assertion_id'],[]).append(row)

LABELS={
 ROOT:'Established claim root',
 UNRESOLVED:'Unresolved ancestry',
 BROKEN:'Broken lineage reference',
 CYCLE:'Lineage cycle detected',
}

def terminal_nodes(t):
 if t.get('terminal'):
  return [t]
 out=[]
 for branch in t.get('branches',[]): out.extend(terminal_nodes(branch))
 return out

def trace_summary(t):
 terms=terminal_nodes(t)
 labels=[]
 for x in terms:
  label=LABELS[x['terminal']]
  if label not in labels: labels.append(label)
 return '; '.join(labels)

def evidence_item(row):
 s=source_by_id.get(row['source_id'])
 if not s:
  raise SystemExit(f"{row['assertion_evidence_id']}: source {row['source_id']} missing from sources.json")
 t=trace_row(row,index); parents=row.get('inherits_claim_from_source_ids') or []
 parent_text=', '.join(parents) if parents else 'none recorded'
 evidence_note=row.get('evidence_note') or 'No evidence note recorded.'
 inheritance_note=row.get('inheritance_note') or 'No inheritance note recorded.'
 locator=row.get('locator') or 'no locator recorded'
 role=row.get('evidence_role') or 'UNSPECIFIED'
 url=s.get('url')
 source_label=f'{s["source_id"]} — {s.get("title","Untitled source")}'
 source_html=(f'<a href="{html.escape(url)}">{html.escape(source_label)}</a>' if url else html.escape(source_label))
 return (
  f'<li class="claim-lineage-evidence" data-assertion-evidence-id="{html.escape(row["assertion_evidence_id"])}" '
  f'data-source-id="{html.escape(row["source_id"])}" data-lineage-terminal="{html.escape(trace_summary(t))}">'
  f'<div><strong>{html.escape(row["assertion_evidence_id"])}</strong> · {html.escape(role)}</div>'
  f'<div>Source: {source_html}</div>'
  f'<div>Locator: {html.escape(locator)}</div>'
  f'<div>Evidence note: {html.escape(evidence_note)}</div>'
  f'<div>Direct inherited claim source(s): {html.escape(parent_text)}</div>'
  f'<div>Lineage terminus: <strong>{html.escape(trace_summary(t))}</strong></div>'
  f'<div class="small">Inheritance note: {html.escape(inheritance_note)}</div>'
  f'</li>'
 )

for oid,slug in SLUGS.items():
 path=SITE/'objects'/slug/'index.html'; text=path.read_text(encoding='utf-8')
 for a in [x for x in assertions if x.get('subject_id')==oid]:
  aid=a['assertion_id']; rows=by_assertion.get(aid,[])
  if not rows: continue
  if f'class="claim-lineage" data-assertion-id="{aid}"' in text: continue
  m=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
  if not m: raise SystemExit(f'{oid}/{aid}: rendered assertion container missing')
  block=(
   f'<details class="claim-lineage" data-assertion-id="{html.escape(aid)}">'
   f'<summary>Trace this claim</summary>'
   f'<p>Assertion <strong>{html.escape(aid)}</strong>. This trace follows claim ancestry, not merely document provenance. '
   f'An unresolved terminus means the project has not established the upstream claim root.</p>'
   f'<ol>{"".join(evidence_item(r) for r in rows)}</ol></details>'
  )
  tag='article' if m.group(0).startswith('<article') else 'li'
  close=text.find(f'</{tag}>',m.end())
  if close<0: raise SystemExit(f'{oid}/{aid}: assertion close tag missing')
  text=text[:close]+block+text[close:]
 path.write_text(text,encoding='utf-8'); print('Published claim lineage',oid)
