#!/usr/bin/env python3
"""EPI-004 regression: San Martín Daumas/Dumont disagreement must remain recoverable."""
from __future__ import annotations
import html,json,re
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
if 'class="claim-lineage" data-for-assertion-id="A-0106"' not in text:
 raise SystemExit('EPI-004 SAN MARTIN FAIL: A-0106 public lineage trace missing')
for r in support+contradict:
 eid=r['assertion_evidence_id']
 m=re.search(rf'<li class="claim-lineage-evidence"[^>]*data-assertion-evidence-id="{re.escape(eid)}"[^>]*>(.*?)</li>',text,re.S)
 if not m: raise SystemExit(f'EPI-004 SAN MARTIN FAIL: {eid} missing from public trace')
 block=m.group(1)
 if html.escape(r['source_id']) not in m.group(0): raise SystemExit(f'EPI-004 SAN MARTIN FAIL: {eid} source identity lost')
 if r.get('locator') and html.escape(r['locator']) not in block: raise SystemExit(f'EPI-004 SAN MARTIN FAIL: {eid} locator lost')
 if r.get('evidence_note') and html.escape(r['evidence_note']) not in block: raise SystemExit(f'EPI-004 SAN MARTIN FAIL: {eid} evidence note lost')
# Find the complete outer assertion container. The lineage trace contains nested <li> elements,
# so a non-greedy generic </li> regex would stop at the first evidence row rather than the assertion close.
start=re.search(r'<(?:article|li)[^>]*data-assertion-id="A-0106"[^>]*>',text)
if not start: raise SystemExit('EPI-004 SAN MARTIN FAIL: rendered A-0106 container missing')
tag='article' if start.group(0).startswith('<article') else 'li'
if tag=='article':
 end=text.find('</article>',start.end())
else:
 # For list assertions, use the next assertion opening (or enclosing list end) as the boundary,
 # because claim-lineage itself contains nested list items.
 nxt=re.search(r'<li[^>]*data-assertion-id="',text[start.end():])
 list_end=text.find('</ul>',start.end())
 candidates=[]
 if nxt: candidates.append(start.end()+nxt.start())
 if list_end>=0: candidates.append(list_end)
 end=min(candidates) if candidates else -1
if end<0: raise SystemExit('EPI-004 SAN MARTIN FAIL: rendered A-0106 close boundary missing')
container=text[start.end():end]
for term in ('Daumas','Dumont'):
 if term not in container: raise SystemExit(f'EPI-004 SAN MARTIN FAIL: rendered assertion lost {term} side of conflict')
print(f'EPI-004 San Martín PASS: A-0106 preserves Daumas support ({len(support)}) and Dumont contradiction ({len(contradict)}) with public traceability.')
