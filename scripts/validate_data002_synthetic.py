#!/usr/bin/env python3
from __future__ import annotations
import contextlib, io, re, shutil, tempfile
from pathlib import Path
from validate_data002_summary_reconciliation import reconcile, ROOT
SOURCE_DATA=ROOT/'data'; SOURCE_SITE=ROOT/'site'
def copy_fixture(tmp):
 data=tmp/'data'; site=tmp/'site'; data.mkdir()
 for name in ('entities.json','assertion-evidence.json'): shutil.copy2(SOURCE_DATA/name,data/name)
 shutil.copytree(SOURCE_SITE,site); return data,site
def expect_fail(label,mutate):
 with tempfile.TemporaryDirectory(prefix='data002-') as raw:
  data,site=copy_fixture(Path(raw)); mutate(data,site)
  try:
   with contextlib.redirect_stderr(io.StringIO()),contextlib.redirect_stdout(io.StringIO()): reconcile(data,site)
  except SystemExit as exc:
   if exc.code!=1: raise AssertionError(f'{label}: unexpected exit code {exc.code}') from exc
   print(f'PASS mutation rejected: {label}'); return
  raise AssertionError(f'{label}: DATA-002 incorrectly accepted mutated publication')
def replace_once(path,old,new):
 text=path.read_text(encoding='utf-8')
 if old not in text: raise AssertionError(f'fixture token not found in {path}: {old!r}')
 path.write_text(text.replace(old,new,1),encoding='utf-8')
def stale_name(_data,site):
 p=site/'objects'/'jose-gervasio-artigas'/'index.html'; text=p.read_text(encoding='utf-8'); pattern=r'(<h1\b[^>]*\bdata-object-id="OBJ-0001"[^>]*>).*?(</h1>)'; text,count=re.subn(pattern,r'\1Stale Artigas Name\2',text,count=1,flags=re.S)
 if count!=1: raise AssertionError('expected one OBJ-0001 heading')
 p.write_text(text,encoding='utf-8')
def stale_country(_data,site): replace_once(site/'objects'/'jose-de-san-martin'/'index.html','data-object-country="Argentina">Argentina ·','data-object-country="Uruguay">Uruguay ·')
def stale_source_count(_data,site):
 p=site/'objects'/'cuban-american-friendship-urn'/'index.html'; text=p.read_text(encoding='utf-8'); marker='class="evidence" data-source-count="'; start=text.find(marker)
 if start<0: raise AssertionError('no evidence source-count hook')
 nstart=start+len(marker); nend=text.find('"',nstart); text=text[:nstart]+str(int(text[nstart:nend])+1)+text[nend:]; p.write_text(text,encoding='utf-8')
def cross_object_binding(_data,site): replace_once(site/'objects'/'jose-de-san-martin'/'index.html','data-object-id="OBJ-0002"','data-object-id="OBJ-0001"')
def wrong_home_route(_data,site):
 p=site/'index.html'; text=p.read_text(encoding='utf-8'); m=re.search(r'<article\s+class="card"[^>]*data-object-id="OBJ-0001"[^>]*>.*?</article>',text,flags=re.S)
 if not m: raise AssertionError('OBJ-0001 homepage card not found')
 card,count=re.subn(r'href="([^"]*/objects/)jose-gervasio-artigas/([^"]*)"',r'href="\1jose-de-san-martin/\2"',m.group(0),count=1)
 if count!=1: raise AssertionError('OBJ-0001 homepage route not found')
 p.write_text(text[:m.start()]+card+text[m.end():],encoding='utf-8')
def duplicate_home_object(_data,site): replace_once(site/'index.html','data-object-id="OBJ-0002"','data-object-id="OBJ-0001"')
def main():
 tests=[('stale object name',stale_name),('stale country',stale_country),('stale evidence source count',stale_source_count),('cross-object page binding',cross_object_binding),('wrong homepage object route',wrong_home_route),('duplicate homepage object binding',duplicate_home_object)]
 for label,mutate in tests: expect_fail(label,mutate)
 print(f'DATA-002 synthetic PASS: {len(tests)} stale/cross-object mutations rejected')
if __name__=='__main__': main()
