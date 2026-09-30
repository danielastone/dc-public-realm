#!/usr/bin/env python3
"""EPI-001 acceptance: every published canonical status identifies a resolvable rule."""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
rules=json.loads((ROOT/'data'/'publication_status_rules.json').read_text(encoding='utf-8'))['rules']
payload=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8')); assertions=payload['assertions']
method=(SITE/'methodology'/'index.html').read_text(encoding='utf-8')
errors=[]
for status,r in rules.items():
 rid=r['rule_id']
 if f'id="rule-{rid}"' not in method: errors.append(f'{status}: methodology anchor missing for {rid}')
 if r['public_label'] not in method: errors.append(f'{status}: public label missing from methodology')
for oid,slug in SLUGS.items():
 text=(SITE/'objects'/slug/'index.html').read_text(encoding='utf-8')
 relevant=[a for a in assertions if a.get('subject_id')==oid]
 for a in relevant:
  aid=a['assertion_id']; status=a['computed_status']; r=rules.get(status)
  if r is None: errors.append(f'{oid}/{aid}: unmapped status {status}'); continue
  rid=r['rule_id']
  m=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
  if not m: errors.append(f'{oid}/{aid}: rendered assertion identity missing'); continue
  tag=m.group(0)
  if f'data-computed-status="{status}"' not in tag: errors.append(f'{oid}/{aid}: computed status does not match canonical {status}')
  if f'data-status-rule="{rid}"' not in tag: errors.append(f'{oid}/{aid}: status rule does not match {rid}')
  if f'href="/methodology/#rule-{rid}"' not in text and f'href="/dc-public-realm/methodology/#rule-{rid}"' not in text: errors.append(f'{oid}/{aid}: public rule link missing for {rid}')
if errors:
 print('EPI-001 FAIL')
 for e in errors: print('-',e)
 raise SystemExit(1)
print(f'EPI-001 PASS: {len(assertions)} canonical assertions checked; {len(rules)} status rules resolvable across three reference objects.')
