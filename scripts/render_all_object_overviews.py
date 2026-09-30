#!/usr/bin/env python3
from __future__ import annotations
import html,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='/dc-public-realm'
OV=json.loads((ROOT/'data'/'object-overviews.json').read_text(encoding='utf-8'))['object_overviews']
SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}

def e(x): return html.escape(str(x),quote=True)
def linked(label,value,url): return f'<dt>{e(label)}</dt><dd><a href="{e(url)}">{e(value)}</a></dd>'

def block(o):
    facts=linked('Location',o['location'],o['location_source_url'])+linked(o['event_label'],o['event_date'],o['event_source_url'])
    if o.get('secondary_event_label'):
        facts+=linked(o['secondary_event_label'],o['secondary_event_date'],o['secondary_event_source_url'])
    if o['record_type']=='person_memorial':
        text=f'<h2>Subject</h2><p><strong>{e(o["subject_name"])} ({e(o["subject_dates"])})</strong> {e(o["subject_bio"])} <a href="{e(o["subject_source_url"])}">Source</a></p>'
    else:
        text=f'<h2>Object context</h2><p>{e(o["object_context"])} <a href="{e(o["object_context_source_url"])}">Source</a></p>'
    lic=f' · <a href="{e(o["image_license_url"])}">{e(o["image_rights"])}</a>' if o.get('image_license_url') else f' · {e(o["image_rights"])}'
    return f'''<section class="object-overview" aria-label="Object overview"><figure><img src="{e(o['image_url'])}" alt="{e(o['image_alt'])}" loading="eager"><figcaption>{e(o['image_credit'])}{lic} · <a href="{e(o['image_source_url'])}">Image source</a></figcaption></figure><dl class="overview-facts">{facts}</dl>{text}</section>'''

for o in OV:
    p=ROOT/'site'/'objects'/SLUGS[o['object_entity_id']]/'index.html'
    if not p.exists():
        raise SystemExit(f'Missing generated object page: {p}')
    s=p.read_text(encoding='utf-8')
    b=block(o)
    # Replace a prior overview if present; otherwise place it after the record-head lede.
    if '<section class="object-overview"' in s:
        s=re.sub(r'<section class="object-overview".*?</section>',b,s,count=1,flags=re.S)
    else:
        m=re.search(r'(<p class="lede">.*?</p>)',s,flags=re.S)
        if not m: raise SystemExit(f'No record-head lede found in {p}')
        s=s[:m.end()]+b+s[m.end():]
    p.write_text(s,encoding='utf-8')
    print('Rendered overview:',p)
