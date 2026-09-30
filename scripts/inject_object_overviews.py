#!/usr/bin/env python3
from __future__ import annotations
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
SLUGS = {"OBJ-0001": "jose-gervasio-artigas"}

def esc(x): return html.escape(str(x), quote=True)

payload = json.loads((DATA / "object-overviews.json").read_text(encoding="utf-8"))
for o in payload["object_overviews"]:
    slug = SLUGS.get(o["object_entity_id"])
    if not slug:
        continue
    path = SITE / "objects" / slug / "index.html"
    text = path.read_text(encoding="utf-8")
    if 'class="record-overview"' in text:
        continue
    figure = f'''<figure class="record-photo"><img src="{esc(o['image_url'])}" alt="{esc(o['image_alt'])}" loading="eager"><figcaption>{esc(o['image_credit'])} · {esc(o['image_rights'])} · <a href="{esc(o['image_source_url'])}">Image record</a></figcaption></figure>'''
    overview = f'''<section class="record-overview" aria-label="Object overview">{figure}<div class="record-facts"><dl><div><dt>Location</dt><dd>{esc(o['location'])} <a class="overview-source" href="{esc(o['location_source_url'])}" aria-label="Source for location">Source</a></dd></div><div><dt>{esc(o['event_label'])}</dt><dd>{esc(o['event_date'])} <a class="overview-source" href="{esc(o['event_source_url'])}" aria-label="Source for {esc(o['event_label'])} date">Source</a></dd></div><div><dt>Subject</dt><dd><strong>{esc(o['subject_name'])}</strong> ({esc(o['subject_dates'])})</dd></div></dl><p class="subject-bio">{esc(o['subject_bio'])} <a class="overview-source" href="{esc(o['subject_source_url'])}">Subject source</a></p></div></section>'''
    h1end = text.find('</h1>')
    if h1end < 0:
        raise SystemExit(f"{path}: h1 not found")
    h1end += len('</h1>')
    text = text[:h1end] + overview + text[h1end:]
    style = '''<style>.record-overview{display:grid;grid-template-columns:minmax(240px,42%) 1fr;gap:1.5rem;margin:1.4rem 0 2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--line)}.record-photo{margin:0}.record-photo img{display:block;width:100%;height:auto;max-height:430px;object-fit:cover;background:var(--soft)}.record-photo figcaption{margin-top:.45rem;font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.72rem;line-height:1.4}.record-facts dl{margin:0}.record-facts dl>div{display:grid;grid-template-columns:6rem 1fr;gap:.65rem;padding:.55rem 0;border-bottom:1px solid var(--line)}.record-facts dt{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700;color:var(--muted)}.record-facts dd{margin:0}.subject-bio{margin:1rem 0 0;max-width:38rem}.overview-source{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.7rem;white-space:nowrap}@media(max-width:600px){.record-overview{grid-template-columns:1fr;gap:1rem}.record-photo img{max-height:none}.record-facts dl>div{grid-template-columns:5.4rem 1fr}}</style>'''
    text = text.replace('</head>', style + '</head>', 1)
    path.write_text(text, encoding="utf-8")
    print("Injected overview into", path)
