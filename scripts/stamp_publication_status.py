#!/usr/bin/env python3
"""Stamp canonical computed status onto rendered object pages.

This is deliberately downstream of all renderers. site/data/assertions.json is the
single publication-state source. The stamp makes status visible and machine-readable
without allowing a bespoke renderer to recompute epistemic state.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
payload=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))
assertions=payload.get('assertions',payload if isinstance(payload,list) else [])
BY_ID={a['assertion_id']:a for a in assertions}


def attrs(a):
 return f'data-assertion-id="{html.escape(a["assertion_id"])}" data-computed-status="{html.escape(a["computed_status"])}"'


def badge(a):
 reason=html.escape(a.get('status_reason',''))
 return f'<div class="canonical-status status {html.escape(a["computed_status"])}"><strong>{html.escape(a["computed_status"])}</strong> · computed from published evidence <span class="status-reason">{reason}</span></div>'


def stamp_generic(text, oid):
 # Generic renderer emits direct assertions in canonical derived order.
 relevant=[a for a in assertions if a.get('subject_id')==oid]
 pos=0
 for a in relevant:
  start=text.find('<article class="assertion">',pos)
  if start < 0:
   raise SystemExit(f'{oid}/{a["assertion_id"]}: generic assertion block not found')
  replacement=f'<article class="assertion" {attrs(a)}>'
  text=text[:start]+replacement+text[start+len('<article class="assertion">'):]
  pos=start+len(replacement)
 return text


def stamp_artigas(text):
 # Bespoke Artigas claims are identified by their existing provenance anchors.
 for aid,a in BY_ID.items():
  if a.get('subject_id')!='OBJ-0001': continue
  anchor=f'href="#provenance-{aid}"'
  p=text.find(anchor)
  if p < 0:
   continue  # not every canonical assertion is narrated on the prototype page
  start=text.rfind('<article class="claim">',0,p)
  if start < 0:
   # creative-role assertions live in list items; add a compact canonical marker there.
   li=text.rfind('<li>',0,p)
   if li < 0: raise SystemExit(f'{aid}: published Artigas claim has no enclosing claim/list item')
   repl=f'<li {attrs(a)}>{badge(a)}'
   text=text[:li]+repl+text[li+4:]
   continue
  repl=f'<article class="claim" {attrs(a)}>{badge(a)}'
  text=text[:start]+repl+text[start+len('<article class="claim">'):]
 return text

for oid,slug in SLUGS.items():
 path=SITE/'objects'/slug/'index.html'; text=path.read_text(encoding='utf-8')
 text=stamp_artigas(text) if oid=='OBJ-0001' else stamp_generic(text,oid)
 path.write_text(text,encoding='utf-8')
 print('Stamped',oid,path)
