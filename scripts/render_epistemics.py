#!/usr/bin/env python3
"""Pure render helpers for assertion-level epistemic publication state.

These functions render from canonical/materialized records. They do not read or
mutate generated HTML.
"""
from __future__ import annotations
import html
from derive_dependency_state import derive
from trace_claim_lineage import build_index, trace_row, ROOT, UNRESOLVED, BROKEN, CYCLE
from detect_material_conflicts import conflict_index, validate_conflict_records

LABELS={ROOT:'Established claim root',UNRESOLVED:'Unresolved ancestry',BROKEN:'Broken lineage reference',CYCLE:'Lineage cycle detected'}

def esc(x): return html.escape(str(x),quote=True)

def terminal_nodes(t):
    if t.get('terminal'): return [t]
    out=[]
    for branch in t.get('branches',[]): out.extend(terminal_nodes(branch))
    return out

def trace_summary(t):
    labels=[]
    for x in terminal_nodes(t):
        label=LABELS[x['terminal']]
        if label not in labels: labels.append(label)
    return '; '.join(labels)

def ancestry_detail(row):
    origin=row.get('claim_origin','UNKNOWN') or 'UNKNOWN'
    dependency=row.get('dependency_status','UNKNOWN') or 'UNKNOWN'
    inherited=row.get('inherits_claim_from_source_ids') or []
    inherited_text=', '.join(inherited) if inherited else 'none recorded; this does not establish independence'
    return (f'<dl class="ancestry-state"><dt>Claim origin</dt><dd data-claim-origin="{esc(origin)}">{esc(origin)}</dd>'
            f'<dt>Dependency status</dt><dd data-canonical-dependency-status="{esc(dependency)}">{esc(dependency)}</dd>'
            f'<dt>Inherited claim from</dt><dd data-inherited-source-count="{len(inherited)}">{esc(inherited_text)}</dd></dl>')

def dependency_block(aid,rows,rules):
    if len(rows)<2: return ''
    items=[]
    for row in rows:
        state=derive(row); rule=rules[state]
        items.append(f'<li data-assertion-evidence-id="{esc(row["assertion_evidence_id"])}" data-source-id="{esc(row["source_id"])}" data-dependency-state="{esc(state)}"><strong>{esc(row["source_id"])}</strong>: {esc(rule["public_label"])}. {esc(rule["explanation"])}{ancestry_detail(row)}</li>')
    return f'<details class="evidence-independence" data-for-assertion-id="{esc(aid)}"><summary>Source relationship</summary><p>Corroboration is not automatically independent. Claim origin and dependency status below reproduce the canonical ancestry state; UNKNOWN means the project has not established that part of the lineage.</p><ul>{"".join(items)}</ul></details>'

def lineage_item(row,index,source_by_id):
    source=source_by_id.get(row['source_id'])
    if not source: raise SystemExit(f'{row["assertion_evidence_id"]}: source {row["source_id"]} missing from sources.json')
    trace=trace_row(row,index); parents=row.get('inherits_claim_from_source_ids') or []
    parent_text=', '.join(parents) if parents else 'none recorded'
    evidence_note=row.get('evidence_note') or 'No evidence note recorded.'
    inheritance_note=row.get('inheritance_note') or 'No inheritance note recorded.'
    locator=row.get('locator') or 'no locator recorded'; role=row.get('evidence_role') or 'UNSPECIFIED'
    label=f'{source["source_id"]} — {source.get("title","Untitled source")}'
    url=source.get('url'); source_html=f'<a href="{esc(url)}">{esc(label)}</a>' if url else esc(label)
    summary=trace_summary(trace)
    return f'<li class="claim-lineage-evidence" data-assertion-evidence-id="{esc(row["assertion_evidence_id"])}" data-source-id="{esc(row["source_id"])}" data-lineage-terminal="{esc(summary)}"><div><strong>{esc(row["assertion_evidence_id"])}</strong> · {esc(role)}</div><div>Source: {source_html}</div><div>Locator: {esc(locator)}</div><div>Evidence note: {esc(evidence_note)}</div><div>Direct inherited claim source(s): {esc(parent_text)}</div><div>Lineage terminus: <strong>{esc(summary)}</strong></div><div class="small">Inheritance note: {esc(inheritance_note)}</div></li>'

def lineage_block(aid,rows,index,source_by_id):
    if not rows: return ''
    return f'<details class="claim-lineage" data-for-assertion-id="{esc(aid)}"><summary>Trace this claim</summary><p>Assertion <strong>{esc(aid)}</strong>. This trace follows claim ancestry, not merely document provenance. An unresolved terminus means the project has not established the upstream claim root.</p><ol>{"".join(lineage_item(r,index,source_by_id) for r in rows)}</ol></details>'

def conflict_warning(aid,rows):
    if not rows: return ''
    items=''.join(f'<li data-conflict-evidence-id="{esc(r["assertion_evidence_id"])}" data-source-id="{esc(r["source_id"])}"><strong>{esc(r["source_id"])}</strong>, {esc(r["locator"])}: {esc(r["evidence_note"])}</li>' for r in rows)
    return f'<aside class="material-conflict" data-conflict-assertion-id="{esc(aid)}" role="note"><strong>Conflicting evidence.</strong> The canonical record contains evidence that contradicts this assertion. The displayed value should not be read as uncontested.<ul>{items}</ul></aside>'

def build_context(evidence,sources):
    errors=validate_conflict_records(evidence)
    if errors: raise SystemExit('EPI-005 invalid canonical conflict rows: '+'; '.join(errors))
    return {'lineage_index':build_index(evidence),'source_by_id':{s['source_id']:s for s in sources},'conflicts':conflict_index(evidence)}

def render_epistemics(aid,rows,dependency_rules,context):
    return (conflict_warning(aid,context['conflicts'].get(aid,[]))+
            dependency_block(aid,rows,dependency_rules)+
            lineage_block(aid,rows,context['lineage_index'],context['source_by_id']))
