#!/usr/bin/env python3
from __future__ import annotations
import html, json
from pathlib import Path

from publication_index import path_for

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"

def esc(x): return html.escape(str(x), quote=True)

def load(name, key):
    return json.loads((DATA / name).read_text(encoding="utf-8"))[key]

assertions = {a["assertion_id"]: a for a in load("assertions.json", "assertions")}
entities = {e["entity_id"]: e for e in load("entities.json", "entities")}

def refs_for(o, field):
    raw = (o.get("assertion_refs") or {}).get(field)
    refs = raw if isinstance(raw, list) else ([raw] if raw else [])
    if not refs:
        raise SystemExit(f"{o['object_entity_id']}.{field}: displayed fact has no assertion reference")
    missing = [aid for aid in refs if aid not in assertions]
    if missing:
        raise SystemExit(f"{o['object_entity_id']}.{field}: missing canonical assertions {missing}")
    return refs

def require_subject(o, field, subject_id):
    refs = refs_for(o, field)
    wrong = [aid for aid in refs if assertions[aid].get("subject_id") != subject_id]
    if wrong:
        raise SystemExit(f"{o['object_entity_id']}.{field}: assertion subject mismatch")
    return refs

def attr(refs): return esc(",".join(refs))

def fact(o, field, label, value, source_url):
    refs = require_subject(o, field, o["object_entity_id"])
    if len(refs) != 1 or assertions[refs[0]].get("literal_value") != value:
        raise SystemExit(f"{o['object_entity_id']}.{field}: displayed value does not reconcile to canonical assertion")
    return f'''<div data-assertion-ids="{attr(refs)}"><dt>{esc(label)}</dt><dd>{esc(value)} <a class="overview-source" href="{esc(source_url)}" aria-label="Source for {esc(label)}">Source</a></dd></div>'''

payload = json.loads((DATA / "object-overviews.json").read_text(encoding="utf-8"))
for o in payload["object_overviews"]:
    oid = o["object_entity_id"]
    if oid not in entities:
        raise SystemExit(f"{oid}: overview object is not a canonical entity")

    path = SITE / path_for(oid, DATA)
    text = path.read_text(encoding="utf-8")
    if 'class="record-overview"' in text:
        continue

    if not all(o.get(k) for k in ("image_url", "image_alt", "image_credit", "image_rights", "image_source_url")):
        raise SystemExit(f"{oid}: incomplete image rights metadata")
    rights = esc(o['image_rights'])
    if o.get('image_license_url'):
        rights = f'<a href="{esc(o["image_license_url"])}">{rights}</a>'
    figure = f'''<figure class="record-photo"><img src="{esc(o['image_url'])}" alt="{esc(o['image_alt'])}" loading="eager"><figcaption>{esc(o['image_credit'])} · {rights} · <a href="{esc(o['image_source_url'])}">Image record</a></figcaption></figure>'''

    facts = fact(o, "location", "Location", o["location"], o["location_source_url"])
    facts += fact(o, "event_date", o["event_label"], o["event_date"], o["event_source_url"])
    if o.get("secondary_event_label"):
        facts += fact(o, "secondary_event_date", o["secondary_event_label"], o["secondary_event_date"], o["secondary_event_source_url"])

    if o["record_type"] == "person_memorial":
        date_refs = refs_for(o, "subject_dates")
        subjects = {assertions[aid].get("subject_id") for aid in date_refs}
        if len(subjects) != 1:
            raise SystemExit(f"{oid}.subject_dates: assertion subjects disagree")
        subject_id = next(iter(subjects))
        subject = entities.get(subject_id)
        if not subject or subject.get("entity_type") != "Person" or subject.get("canonical_name") != o["subject_name"]:
            raise SystemExit(f"{oid}.subject_name: does not reconcile to canonical person")
        if len(date_refs) != 2:
            raise SystemExit(f"{oid}.subject_dates: expected birth and death assertions")
        rendered_dates = "–".join(assertions[aid].get("literal_value", "") for aid in date_refs)
        if rendered_dates != o["subject_dates"]:
            raise SystemExit(f"{oid}.subject_dates: does not reconcile to canonical assertions")
        bio_refs = require_subject(o, "subject_bio", subject_id)
        facts += f'''<div data-assertion-ids="{attr(date_refs)}"><dt>Subject</dt><dd><strong>{esc(subject['canonical_name'])}</strong> ({esc(rendered_dates)})</dd></div>'''
        intro = f'''<section class="record-introduction" data-assertion-ids="{attr(bio_refs)}" aria-labelledby="record-introduction-heading"><h2 id="record-introduction-heading">About the memorial</h2><p>{esc(o['subject_bio'])} <a class="overview-source" href="{esc(o['subject_source_url'])}">Source</a></p></section>'''
    elif o["record_type"] == "historical_object":
        context_refs = require_subject(o, "object_context", oid)
        intro = f'''<section class="record-introduction" data-assertion-ids="{attr(context_refs)}" aria-labelledby="record-introduction-heading"><h2 id="record-introduction-heading">About the object</h2><p>{esc(o['object_context'])} <a class="overview-source" href="{esc(o['object_context_source_url'])}">Source</a></p></section>'''
    else:
        raise SystemExit(f"{oid}: unknown record_type {o['record_type']}")

    overview = f'''<section class="record-overview" data-object-entity-id="{esc(oid)}" aria-label="Object overview">{figure}<div class="record-facts"><dl>{facts}</dl>{intro}</div></section>'''
    h1end = text.find('</h1>')
    if h1end < 0:
        raise SystemExit(f"{path}: h1 not found")
    h1end += len('</h1>')
    text = text[:h1end] + overview + text[h1end:]
    style = '''<style>.record-overview{display:grid;grid-template-columns:minmax(240px,42%) 1fr;gap:1.5rem;margin:1.4rem 0 2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--line)}.record-photo{margin:0}.record-photo img{display:block;width:100%;height:auto;max-height:430px;object-fit:cover;background:var(--soft)}.record-photo figcaption{margin-top:.45rem;font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.72rem;line-height:1.4}.record-facts dl{margin:0}.record-facts dl>div{display:grid;grid-template-columns:6rem 1fr;gap:.65rem;padding:.55rem 0;border-bottom:1px solid var(--line)}.record-facts dt{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700;color:var(--muted)}.record-facts dd{margin:0}.record-introduction{margin:1.2rem 0 0;max-width:40rem}.record-introduction h2{margin:0 0 .45rem;font-size:1.05rem}.record-introduction p{margin:0}.overview-source{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.7rem;white-space:nowrap}@media(max-width:600px){.record-overview{grid-template-columns:1fr;gap:1rem}.record-photo img{max-height:none}.record-facts dl>div{grid-template-columns:5.4rem 1fr}}</style>'''
    text = text.replace('</head>', style + '</head>', 1)
    path.write_text(text, encoding="utf-8")
    print("Injected traceable overview into", path)
