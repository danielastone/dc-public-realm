#!/usr/bin/env python3
"""Stamp canonical computed status and its published rule onto rendered object pages."""
from __future__ import annotations
import html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
payload=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))
assertions=payload.get('assertions',payload if isinstance(payload,list) else [])
rules_payload=json.loads((ROOT/'data'/'publication_status_rules.json').read_text(encoding='utf-8'))
rules=rules_payload['rules']

def rule(a):
 status=a['computed_status']
 if status not in rules: raise SystemExit(f'{a["assertion_id"]}: no publication status rule for {status}')
 return rules[status]
def attrs(a):
 r=rule(a)
 return f'data-assertion-id="{html.escape(a["assertion_id"])}" data-computed-status="{html.escape(a["computed_status"])}" data-status-rule="{html.escape(r["rule_id"])}"'
def badge(a):
 r=rule(a); reason=html.escape(a.get('status_reason','')); rid=html.escape(r['rule_id']); label=html.escape(r['public_label'])
 return f'<div class="canonical-status status {html.escape(a["computed_status"])}"><span class="status-label">{label}</span><span class="status-reason">{reason}</span><a class="status-rule" href="/methodology/#rule-{rid}">Why this status? <span class="rule-id">{rid}</span></a></div>'
def stamp_generic(text,oid):
 pos=0
 relevant=[x for x in assertions if x.get('subject_id')==oid]
 for a in relevant:
  start=text.find('<article class="assertion">',pos)
  if start<0: raise SystemExit(f'{oid}/{a["assertion_id"]}: shared assertion block not found')
  repl=f'<article class="assertion" {attrs(a)}>'; text=text[:start]+repl+text[start+len('<article class="assertion">'):]
  heading=text.find('</h3>',start)
  if heading<0: heading=text.find('</h2>',start)
  if heading<0: raise SystemExit(f'{oid}/{a["assertion_id"]}: assertion heading not found')
  heading+=5; b=badge(a); text=text[:heading]+b+text[heading:]; pos=heading+len(b)
 if text.count('data-assertion-id=') < len(relevant): raise SystemExit(f'{oid}: not all canonical assertions were stamped')
 return text
for oid,slug in SLUGS.items():
 path=SITE/'objects'/slug/'index.html'; text=path.read_text(encoding='utf-8'); text=stamp_generic(text,oid); path.write_text(text,encoding='utf-8'); print('Stamped',oid,path)
