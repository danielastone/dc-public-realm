#!/usr/bin/env python3
"""Single publication entrypoint.

The base catalog builder currently remains import-compatible legacy code, but
traceable overview rendering is owned here rather than by a separate CI
post-processing step. This is the migration seam for moving the remaining
page construction into pure render functions.
"""
from __future__ import annotations
import json
from pathlib import Path

# Legacy module executes the base static build on import.
import build_site  # noqa: F401,E402
from overview_renderer import OVERVIEW_CSS, render_overview
from publication_index import path_for

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
SITE=ROOT/'site'

def load(name,key):
    return json.loads((DATA/name).read_text(encoding='utf-8'))[key]

assertions={a['assertion_id']:a for a in load('assertions.json','assertions')}
entities={e['entity_id']:e for e in load('entities.json','entities')}
overviews=load('object-overviews.json','object_overviews')

for o in overviews:
    path=SITE/path_for(o['object_entity_id'],DATA)
    text=path.read_text(encoding='utf-8')
    if 'class="record-overview"' in text:
        raise SystemExit(f'{path}: overview unexpectedly pre-rendered')
    marker='</h1>'
    at=text.find(marker)
    if at<0: raise SystemExit(f'{path}: h1 not found')
    at+=len(marker)
    text=text[:at]+render_overview(o,assertions,entities)+text[at:]
    text=text.replace('</head>',f'<style>{OVERVIEW_CSS}</style></head>',1)
    path.write_text(text,encoding='utf-8')

print('Built publication with integrated traceable overviews')
