#!/usr/bin/env python3
"""Render the project front door and Artigas collaboration page without mutating existing HTML."""
from __future__ import annotations
import html, json
from pathlib import Path
from publication_index import featured_object, href, published_objects
from publication_chrome import header

BASE='/dc-public-realm'

def esc(x): return html.escape(str(x), quote=True)

def render_frontdoor(data_dir: Path, base: str = BASE) -> tuple[str,str]:
    overviews={o['object_entity_id']:o for o in json.loads((data_dir/'object-overviews.json').read_text(encoding='utf-8'))['object_overviews']}
    tasks=json.loads((data_dir/'research-tasks.json').read_text(encoding='utf-8'))['tasks']
    open_counts={e['entity_id']:0 for e in published_objects(data_dir)}
    for task in tasks:
        oid=task.get('object_entity_id')
        if task.get('status')=='OPEN' and oid in open_counts:
            open_counts[oid]+=1
    featured=featured_object(data_dir)
    featured_id=featured['entity_id']
    if featured_id != 'OBJ-0001':
        raise SystemExit(f"Featured object {featured_id} is not supported by the current front door")
    a=overviews[featured_id]
    featured_href=href(featured_id,base,data_dir)
    artigas_href=href('OBJ-0001',base,data_dir)
    rights=esc(a['image_rights'])
    if a.get('image_license_url'):
        rights=f'<a href="{esc(a["image_license_url"])}">{rights}</a>'

    def object_card(entity):
        oid=entity['entity_id']; count=open_counts[oid]
        return (f'<article class="card" data-object-id="{esc(oid)}" data-object-country="{esc(entity["country"])}">'
                f'<div class="kicker">{esc(entity["country"]).upper()}</div>'
                f'<h3><a href="{href(oid,base,data_dir)}">{esc(entity["canonical_name"])}</a></h3>'
                f'<span class="open-task-count" data-object-id="{esc(oid)}" data-open-task-count="{count}">{count} open research mission{"s" if count != 1 else ""}</span></article>')
    object_grid=''.join(object_card(entity) for entity in published_objects(data_dir))
    chrome=header()

    home=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Diplomatic Gifts in Washington</title><link rel="stylesheet" href="{base}/assets/style.css"><style>.hero{{max-width:800px;margin:2rem 0}}.hero h1{{margin-bottom:.7rem}}.project{{border-left:4px solid #5a3d16;background:#fffdf8;padding:1rem 1.2rem;margin:2rem 0}}.project h2{{margin:.2rem 0 .8rem}}.project-object{{display:grid;grid-template-columns:minmax(220px,38%) 1fr;gap:1.4rem;align-items:start}}.project figure{{margin:0}}.project img{{display:block;width:100%;height:auto;max-height:390px;object-fit:cover}}.project figcaption{{margin-top:.4rem;font-family:ui-sans-serif,system-ui,sans-serif;color:#666;font-size:.7rem;line-height:1.4}}.object-meta{{font-family:ui-sans-serif,system-ui,sans-serif;color:#666;font-size:.86rem;margin:.2rem 0 .8rem}}.object-intro{{font-size:1.05rem;line-height:1.55}}.research-note{{margin:1.2rem 0 0;padding-top:1rem;border-top:1px solid #ddd}}.actions{{margin:1.2rem 0}}</style></head><body>{chrome}<main><section class="hero"><div class="kicker">PUBLIC ART · DIPLOMATIC HISTORY</div><h1>Diplomatic Gifts in Washington</h1><p class="lede">This project documents diplomatic monuments in Washington, D.C., and invites the public to help research their histories.</p><p>Government files, newspapers, photographs, archival collections, and museum records can clarify who made these works, how they came to Washington, and how their histories have been recorded.</p></section><section class="project"><div class="kicker">CURRENT PROJECT · {esc(featured['country']).upper()}</div><div class="project-object"><figure><img src="{esc(a['image_url'])}" alt="{esc(a['image_alt'])}"><figcaption>{esc(a['image_credit'])} · {rights} · <a href="{esc(a['image_source_url'])}">Image record</a></figcaption></figure><div><h2>{esc(featured['canonical_name'])}</h2><p class="object-meta">{esc(a['location'])} · {esc(a['event_label'])} {esc(a['event_date'])}</p><p class="object-intro"><strong>{esc(a['subject_name'])}</strong> ({esc(a['subject_dates'])}). {esc(a['subject_bio'])} <a href="{esc(a['subject_source_url'])}">Source</a></p><div class="actions"><a class="button" href="{featured_href}">View the memorial</a></div><aside class="research-note"><h3>Research in progress</h3><p>Published records differ on the predecessor monument and parts of the fabrication history.</p><p><a href="{base}/collaborate/artigas/">Help research the Artigas memorial</a></p></aside></div></div></section><section><h2>Take part in the research</h2><p>You do not need to be an art historian to contribute.</p><p><a class="button" href="{base}/collaborate/">Browse research missions</a></p></section><section><h2>Explore the records</h2><div class="grid">{object_grid}</div></section><section><h2>How the research works</h2><p>Object pages present the current catalog record. Each historical or attribution statement is linked to its sources.</p><p>The <a href="{base}/methodology/">research methodology</a> explains how sources are reviewed and how records are updated.</p></section></main><footer>Research is ongoing. Records may change when additional sources are reviewed.</footer></body></html>'''

    collab=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Artigas Research Missions</title><link rel="stylesheet" href="{base}/assets/style.css"></head><body>{header("Diplomatic Gifts in Washington · public research")}<main><div class="kicker">JOSÉ GERVASIO ARTIGAS MEMORIAL</div><h1>Help Research the Artigas Memorial</h1><p class="lede">Historical records leave several questions about the Washington monument unresolved. You can help locate the records needed to answer them.</p><p><a class="button" href="{artigas_href}">Explore the Artigas record</a></p><h2>Research missions</h2><p>Use the canonical research mission pages for current tasks.</p><p><a class="button" href="{base}/collaborate/">Browse research missions</a></p></main><footer>Public contributions support the research record. Submitted material is reviewed before publication.</footer></body></html>'''
    return home, collab
