#!/usr/bin/env python3
"""Single publication entrypoint.

The base catalog builder remains import-compatible legacy code. Traceable
overviews and assertion-level epistemic presentation are owned here so CI has
one publication construction stage followed by read-only validators.
"""
from __future__ import annotations
import json,re
from pathlib import Path

# Legacy module executes the base static build on import.
import build_site  # noqa: F401,E402
from overview_renderer import OVERVIEW_CSS, render_overview
from publication_index import path_for, published_objects
from render_epistemics import build_context, render_epistemics

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
SITE=ROOT/'site'

def load(name,key):
    return json.loads((DATA/name).read_text(encoding='utf-8'))[key]

assertion_rows=load('assertions.json','assertions')
assertions={a['assertion_id']:a for a in assertion_rows}
entities={e['entity_id']:e for e in load('entities.json','entities')}
overviews=load('object-overviews.json','object_overviews')
evidence=load('assertion-evidence.json','assertion_evidence')
sources=load('sources.json','sources')
dependency_rules=json.loads((DATA/'publication_dependency_rules.json').read_text(encoding='utf-8'))['rules']
by_assertion={}
for row in evidence: by_assertion.setdefault(row['assertion_id'],[]).append(row)
epistemic_context=build_context(evidence,sources)

# Overview publication is integrated here rather than a later CI mutator.
for o in overviews:
    path=SITE/path_for(o['object_entity_id'],DATA)
    text=path.read_text(encoding='utf-8')
    if 'class="record-overview"' in text:
        raise SystemExit(f'{path}: overview unexpectedly pre-rendered')
    marker='</h1>'; at=text.find(marker)
    if at<0: raise SystemExit(f'{path}: h1 not found')
    at+=len(marker)
    text=text[:at]+render_overview(o,assertions,entities)+text[at:]
    text=text.replace('</head>',f'<style>{OVERVIEW_CSS}</style></head>',1)
    path.write_text(text,encoding='utf-8')

# Assertion epistemics are rendered during publication construction. This
# replaces three independent post-render CI mutators while preserving their
# established HTML contract for the EPI validators.
for entity in published_objects(DATA):
    oid=entity['entity_id']; path=SITE/path_for(oid,DATA)
    text=path.read_text(encoding='utf-8')
    for assertion in [a for a in assertion_rows if a.get('subject_id')==oid]:
        aid=assertion['assertion_id']; rows=by_assertion.get(aid,[])
        block=render_epistemics(aid,rows,dependency_rules,epistemic_context)
        if not block: continue
        m=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
        if not m: raise SystemExit(f'{oid}/{aid}: canonical assertion container missing')
        # Conflict warnings must remain immediately visible after the assertion
        # opening; relationship/lineage details belong at the end of the claim.
        conflict=''; rest=block
        if block.startswith('<aside class="material-conflict"'):
            end=block.find('</aside>')
            if end<0: raise SystemExit(f'{oid}/{aid}: malformed conflict warning')
            end+=len('</aside>'); conflict=block[:end]; rest=block[end:]
            text=text[:m.end()]+conflict+text[m.end():]
            m=re.search(rf'<(?:article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',text)
        tag='article' if m.group(0).startswith('<article') else 'li'
        close=text.find(f'</{tag}>',m.end())
        if close<0: raise SystemExit(f'{oid}/{aid}: assertion close tag missing')
        text=text[:close]+rest+text[close:]
    path.write_text(text,encoding='utf-8')

print('Built publication with integrated overviews and epistemic state')
