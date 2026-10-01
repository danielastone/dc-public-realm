#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json, re, sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DEFAULT_DATA=ROOT/'data'; DEFAULT_SITE=ROOT/'site'
OBJECTS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}
def fail(msg): print(f'DATA-002 FAIL: {msg}',file=sys.stderr); raise SystemExit(1)
def attr(tag,name):
 m=re.search(rf'\b{name}="([^"]*)"',tag); return html.unescape(m.group(1)) if m else None
def strip_tags(x): return html.unescape(re.sub(r'<[^>]+>','',x)).strip()
class EvidenceSummaryParser(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True); self.stack=[]; self.current=None; self.summaries=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs); aid=a.get('data-assertion-id')
  if tag=='details' and 'evidence' in a.get('class','').split() and 'data-source-count' in a:
   if self.current is not None: fail('nested canonical evidence panels are not supported')
   owner=next((x for _,x in reversed(self.stack) if x),None)
   self.current={'owner':owner,'hook':a['data-source-count'],'depth':len(self.stack)+1,'summary':False,'text':[]}
  self.stack.append((tag,aid))
  if tag=='summary' and self.current is not None and len(self.stack)==self.current['depth']+1:
   self.current['summary']=True
 def handle_startendtag(self,tag,attrs):
  # Void/self-closing elements must not remain on the ancestry stack.
  return
 def handle_data(self,data):
  if self.current is not None and self.current['summary']: self.current['text'].append(data)
 def handle_endtag(self,tag):
  depth=len(self.stack)
  if self.current is not None:
   if tag=='summary' and self.current['summary'] and depth==self.current['depth']+1:
    self.current['summary']=False
   elif tag=='details' and depth==self.current['depth']:
    owner=self.current['owner']
    if not owner: fail('source summary is not contained by an assertion element')
    text=''.join(self.current['text']).strip(); m=re.fullmatch(r'Sources\s*·\s*([0-9]+)',text)
    if not m: fail(f'{owner}: malformed visible source summary {text!r}')
    try: hook=int(self.current['hook'])
    except ValueError: fail(f'{owner}: non-integer data-source-count {self.current["hook"]!r}')
    self.summaries.append((owner,hook,int(m.group(1)))); self.current=None
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag: del self.stack[i:]; break
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
  p=EvidenceSummaryParser(); p.feed(page); p.close(); seen=set()
  for aid,hook,visible in p.summaries:
   if aid in seen: fail(f'{oid}: duplicate source summary for {aid}')
   seen.add(aid); canonical=len(evidence.get(aid,set()))
   if hook!=visible or hook!=canonical: fail(f'{oid}/{aid}: rendered source count hook={hook}, visible={visible}, canonical={canonical}')
 print(f'DATA-002 PASS: reconciled {len(OBJECTS)} object summaries and rendered evidence-source counts')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--data-dir',type=Path,default=DEFAULT_DATA); p.add_argument('--site-dir',type=Path,default=DEFAULT_SITE); a=p.parse_args(); reconcile(a.data_dir,a.site_dir)
if __name__=='__main__': main()
