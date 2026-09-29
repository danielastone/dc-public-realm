#!/usr/bin/env python3
"""Stamp canonical computed status onto rendered object pages.

Runs downstream of all renderers. site/data/assertions.json is the single
publication-state source. Bespoke pages may not silently omit canonical direct
assertions: missing Artigas assertions become visible claim cards.
"""
from __future__ import annotations
import html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
payload=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))
assertions=payload.get('assertions',payload if isinstance(payload,list) else [])

def attrs(a): return f'data-assertion-id="{html.escape(a["assertion_id"])}" data-computed-status="{html.escape(a["computed_status"])}"'
def badge(a):
 reason=html.escape(a.get('status_reason',''))
 return f'<div class="canonical-status status {html.escape(a["computed_status"])}"><strong>{html.escape(a["computed_status"])}</strong> · computed from published evidence <span class="status-reason">{reason}</span></div>'
def fallback(a):
 aid=html.escape(a['assertion_id']); title=html.escape(a.get('predicate','Research assertion').replace('_',' ').title())
 statement='The current published evidence does not establish a value for this assertion.' if a.get('value') in (None,'',[]) else f'Canonical value: {html.escape(str(a.get("value")))}.'
 if a['assertion_id']=='A-0003':
  title='Founder or caster of the Washington bronze'; statement='The current evidence does not establish the foundry or caster of the Washington bronze. A source failing to identify the founder is not evidence that the founder was historically unknown.'
 return f'<article class="claim canonical-fallback" {attrs(a)}>{badge(a)}<div class="eyebrow">CANONICAL ASSERTION</div><h3>{title}</h3><p>{statement} <a class="cite" href="#provenance-{aid}">[{aid.replace("A-","")}]</a></p><p class="small">Shown because this assertion is part of the canonical publication state.</p></article>'
def stamp_generic(text,oid):
 pos=0
 for a in [x for x in assertions if x.get('subject_id')==oid]:
  start=text.find('<article class="assertion">',pos)
  if start<0: raise SystemExit(f'{oid}/{a["assertion_id"]}: generic assertion block not found')
  repl=f'<article class="assertion" {attrs(a)}>'; text=text[:start]+repl+text[start+len('<article class="assertion">'):]; pos=start+len(repl)
 return text
def stamp_artigas(text):
 relevant=[a for a in assertions if a.get('subject_id')=='OBJ-0001']
 missing=[a for a in relevant if f'href="#provenance-{a["assertion_id"]}"' not in text]
 if missing:
  boundary='</section><section id="sources">'
  if boundary not in text: raise SystemExit('Artigas: cannot locate Evidence/Sources boundary')
  text=text.replace(boundary,''.join(fallback(a) for a in missing)+boundary,1)
 for a in relevant:
  aid=a['assertion_id']
  if f'data-assertion-id="{aid}"' in text: continue
  p=text.find(f'href="#provenance-{aid}"')
  if p<0: raise SystemExit(f'{aid}: canonical Artigas assertion remains unpublished')
  start=text.rfind('<article class="claim">',0,p)
  if start>=0:
   repl=f'<article class="claim" {attrs(a)}>{badge(a)}'; text=text[:start]+repl+text[start+len('<article class="claim">'):]; continue
  li=text.rfind('<li>',0,p)
  if li<0: raise SystemExit(f'{aid}: published Artigas claim has no enclosing claim/list item')
  repl=f'<li {attrs(a)}>{badge(a)}'; text=text[:li]+repl+text[li+4:]
 return text
for oid,slug in SLUGS.items():
 path=SITE/'objects'/slug/'index.html'; text=path.read_text(encoding='utf-8'); text=stamp_artigas(text) if oid=='OBJ-0001' else stamp_generic(text,oid); path.write_text(text,encoding='utf-8'); print('Stamped',oid,path)
