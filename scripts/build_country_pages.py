#!/usr/bin/env python3
from __future__ import annotations
import html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; OUT=ROOT/'site'; BASE='/dc-public-realm'
def load(n): return json.loads((DATA/n).read_text(encoding='utf-8'))
def esc(x): return html.escape(str(x))
entities={x['entity_id']:x for x in load('entities.json')['entities']}
tasks=load('research-tasks.json')['tasks']
records=[('OBJ-0001','Uruguay','jose-gervasio-artigas'),('OBJ-0002','Argentina','jose-de-san-martin'),('OBJ-0003','Cuba','cuban-american-friendship-urn')]
def shell(title,body):
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Diplomatic Gifts in Washington</title><link rel="stylesheet" href="{BASE}/assets/style.css"></head><body><header><div class="kicker">Diplomatic Gifts in Washington</div><nav><a href="{BASE}/">Explore</a><a href="{BASE}/collaborate/">Research missions</a><a href="{BASE}/methodology/">About the research</a><a href="{BASE}/data/assertions.json">Data</a></nav></header><main>{body}</main><footer>Research submissions do not change the public record until the underlying source is reviewed.</footer></body></html>'''
for oid,country,slug in records:
 related=[t for t in tasks if t['object_entity_id']==oid]
 mission=''.join(f'<article class="task"><div class="kicker">Research mission · {esc(t["status"])}</div><h3><a href="{BASE}/tasks/{esc(t["task_id"].lower())}/">{esc(t["title"])}</a></h3><p>{esc(t["research_gap"])}</p></article>' for t in related)
 body=f'<div class="kicker">Country research index</div><h1>{esc(country)}</h1><p class="lede">Research records connecting {esc(country)} with diplomatic monuments in Washington, D.C. This page is an index; evidentiary status is reported on the underlying catalog record.</p><h2>Catalog record</h2><article class="card"><h3><a href="{BASE}/objects/{slug}/">{esc(entities[oid]["canonical_name"])}</a></h3><p>View statements, evidence status, sources, and source history.</p></article>'
 if related: body+=f'<h2>Research missions</h2><p>{len(related)} open mission'+('s' if len(related)!=1 else '')+' currently bear on this record.</p>'+mission
 d=OUT/'countries'/country.lower(); d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(shell(country,body),encoding='utf-8')
print('Built country research indexes')
