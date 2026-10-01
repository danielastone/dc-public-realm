#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json, re, sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DEFAULT_DATA=ROOT/'data'; DEFAULT_SITE=ROOT/'site'
OBJECTS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
def fail(msg): print(f'DATA-002 FAIL: {msg}',file=sys.stderr); raise SystemExit(1)
def attr(tag,name):
 m=re.search(rf'\b{name}="([^"]*)"',tag); return html.unescape(m.group(1)) if m else None
def strip_tags(x): return html.unescape(re.sub(r'<[^>]+>','',x)).strip()
def reconcile(data_dir=DEFAULT_DATA,site_dir=DEFAULT_SITE):
 def load(n): return json.loads((data_dir/n).read_text(encoding='utf-8'))
 entities={x['entity_id']:x for x in load('entities.json')['entities']}; evidence=defaultdict(set)
 for r in load('assertion-evidence.json')['assertion_evidence']: evidence[r['assertion_id']].add(r['source_id'])
 missing=sorted(set(OBJECTS)-set(entities))
 if missing: fail(f'object ids missing from canonical entities: {missing}')
 hp=site_dir/'index.html'
 if not hp.exists(): fail('missing site/index.html')
 home=hp.read_text(encoding='utf-8'); cards_list=re.findall(r'<article\s+class="card"[^>]*data-object-id="[^"]+"[^>]*>',home); ids=[attr(x,'data-object-id') for x in cards_list]
 if len(ids)!=len(set(ids)): fail('homepage contains duplicate object hooks')
 cards=dict(zip(ids,cards_list))
 if set(cards)!=set(OBJECTS): fail(f'homepage object hooks differ from expected objects: {sorted(cards)}')
 for oid,slug in OBJECTS.items():
  e=entities[oid]; name=e.get('canonical_name'); country=e.get('country')
  if not name or not country: fail(f'{oid}: canonical_name and country are required')
  tag=cards[oid]; start=home.index(tag); end=home.find('</article>',start)
  if end<0: fail(f'{oid}: homepage card has no closing article tag')
  card=home[start:end+10]
  if html.escape(name) not in card: fail(f'{oid}: homepage name does not match canonical_name {name!r}')
  if html.escape(country) not in card: fail(f'{oid}: homepage country does not match canonical country {country!r}')
  if f'/dc-public-realm/objects/{slug}/' not in card: fail(f'{oid}: homepage card points to wrong object route')
  path=site_dir/'objects'/slug/'index.html'
  if not path.exists(): fail(f'missing object page {path}')
  page=path.read_text(encoding='utf-8'); h1=re.findall(r'<h1[^>]*data-object-id="[^"]+"[^>]*>.*?</h1>',page,flags=re.S)
  if len(h1)!=1: fail(f'{oid}: expected exactly one hooked object heading, found {len(h1)}')
  if attr(h1[0],'data-object-id')!=oid: fail(f'{oid}: object page hook identifies another object')
  if strip_tags(h1[0])!=name: fail(f'{oid}: rendered heading {strip_tags(h1[0])!r} != canonical_name {name!r}')
  ks=re.findall(r'<div[^>]*class="kicker"[^>]*data-object-country="[^"]+"[^>]*>.*?</div>',page,flags=re.S)
  if len(ks)!=1: fail(f'{oid}: expected exactly one hooked country kicker, found {len(ks)}')
  if attr(ks[0],'data-object-country')!=country: fail(f'{oid}: rendered country hook != canonical country {country!r}')
  if not strip_tags(ks[0]).startswith(country+' ·'): fail(f'{oid}: visible country label != canonical country {country!r}')
  panels=re.findall(r'<details\s+class="evidence"[^>]*data-evidence-assertion-id="A-[0-9A-Z]+"[^>]*data-source-count="[0-9]+"[^>]*>.*?<summary>Sources\s*·\s*[0-9]+</summary>',page,flags=re.S)
  seen=set()
  for panel in panels:
   aid=attr(panel,'data-evidence-assertion-id'); hook=attr(panel,'data-source-count')
   if aid in seen: fail(f'{oid}: duplicate source summary for {aid}')
   seen.add(aid)
   m=re.search(r'<summary>Sources\s*·\s*([0-9]+)</summary>',panel)
   if not m: fail(f'{oid}/{aid}: malformed visible source summary')
   visible=int(m.group(1)); canonical=len(evidence.get(aid,set()))
   try: hook_count=int(hook)
   except (TypeError,ValueError): fail(f'{oid}/{aid}: invalid data-source-count {hook!r}')
   if hook_count!=visible or hook_count!=canonical: fail(f'{oid}/{aid}: rendered source count hook={hook_count}, visible={visible}, canonical={canonical}')
  unowned=re.findall(r'<details\s+class="evidence"[^>]*data-source-count="[0-9]+"(?![^>]*data-evidence-assertion-id)[^>]*>',page)
  if unowned: fail(f'{oid}: {len(unowned)} evidence panels lack explicit data-evidence-assertion-id ownership')
 print(f'DATA-002 PASS: reconciled {len(OBJECTS)} object summaries and explicit evidence-source counts')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--data-dir',type=Path,default=DEFAULT_DATA); p.add_argument('--site-dir',type=Path,default=DEFAULT_SITE); a=p.parse_args(); reconcile(a.data_dir,a.site_dir)
if __name__=='__main__': main()
