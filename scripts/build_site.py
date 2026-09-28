#!/usr/bin/env python3
"""Build the diplomatic-gifts alpha site from canonical semantic data."""
from __future__ import annotations
import html, json, shutil
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
OUT=ROOT/"site"
ASSETS=OUT/"assets"

def load(name,key):
    return json.loads((DATA/name).read_text(encoding="utf-8"))[key]

entities=load("entities.json","entities")
assertions=load("assertions.json","assertions")
evidence=load("assertion-evidence.json","assertion_evidence")
sources=load("sources.json","sources")
E={x["entity_id"]:x for x in entities}
S={x["source_id"]:x for x in sources}
A={x["assertion_id"]:x for x in assertions}
EV={}
for x in evidence: EV.setdefault(x["assertion_id"],[]).append(x)

OBJECTS=["OBJ-0001","OBJ-0002","OBJ-0003"]
SLUGS={
 "OBJ-0001":"jose-gervasio-artigas",
 "OBJ-0002":"jose-de-san-martin",
 "OBJ-0003":"cuban-american-friendship-urn",
}
COUNTRIES={"OBJ-0001":"Uruguay","OBJ-0002":"Argentina","OBJ-0003":"Cuba"}

if OUT.exists(): shutil.rmtree(OUT)
ASSETS.mkdir(parents=True)

css=''':root{--fg:#171717;--muted:#666;--line:#ddd;--bg:#fff;--soft:#f6f6f3;--warn:#7a3e00;--bad:#8b1e1e}
*{box-sizing:border-box}body{margin:0;font-family:ui-serif,Georgia,serif;color:var(--fg);background:var(--bg);line-height:1.55}
main,header,footer{max-width:980px;margin:auto;padding:1.25rem}header{border-bottom:1px solid var(--line)}
nav a{margin-right:1rem}a{color:inherit;text-decoration-thickness:.08em;text-underline-offset:.15em}
h1{font-size:clamp(2rem,6vw,4.2rem);line-height:1.02;margin:.5rem 0 1rem}h2{margin-top:2.2rem}
.kicker,.meta{font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.9rem}.lede{font-size:1.2rem;max-width:760px}
.card,.assertion{border:1px solid var(--line);padding:1rem;margin:1rem 0;background:#fff}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}
.assertion code{font-size:.82rem}.status{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.04em}
.status.CONTESTED{color:var(--warn)}.status.UNRESOLVED{color:var(--bad)}.evidence{background:var(--soft);padding:.7rem;margin-top:.7rem}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.35rem 1rem}dt{font-weight:bold}footer{border-top:1px solid var(--line);margin-top:3rem;color:var(--muted)}
'''
(ASSETS/"style.css").write_text(css,encoding="utf-8")

def esc(x): return html.escape(str(x))
def label_pred(p): return p.replace("_"," ").title()
def obj_value(a):
    if a.get("object_entity_id"):
        x=E.get(a["object_entity_id"],{})
        return x.get("canonical_name",a["object_entity_id"])
    if "literal_value" in a: return a["literal_value"]
    return "Unresolved"

def source_block(ev):
    s=S[ev["source_id"]]
    role=ev["evidence_role"].replace("_"," ").title()
    return f'''<div class="evidence"><strong>{esc(role)}:</strong> <a href="{esc(s["url"])}">{esc(s["title"])}</a>
    <span class="meta"> — {esc(s["publisher_or_creator"])} · language {esc(s["language"])} · locator: {esc(ev.get("locator","not recorded"))}</span>
    {f"<br>{esc(ev.get('evidence_note',''))}" if ev.get("evidence_note") else ""}</div>'''

def assertion_block(a):
    aid=a["assertion_id"]; value=obj_value(a)
    evhtml="".join(source_block(x) for x in EV.get(aid,[]))
    note=f'<p class="meta">{esc(a["interpretation_note"])}</p>' if a.get("interpretation_note") else ""
    return f'''<article class="assertion" id="{esc(aid)}">
      <div class="status {esc(a["status"])}">{esc(a["status"])}</div>
      <h3>{esc(label_pred(a["predicate"]))}: {esc(value)}</h3>
      <code>{esc(a["subject_id"])} → {esc(a["predicate"])} → {esc(a.get("object_entity_id",a.get("literal_value","UNRESOLVED")))}</code>
      {note}{evhtml}
    </article>'''

def shell(title,body,desc=""):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{esc(title)} | Diplomatic Gifts in Washington</title><meta name="description" content="{esc(desc or title)}">
    <link rel="stylesheet" href="/dc-public-realm/assets/style.css"></head><body>
    <header><div class="kicker">Diplomatic Gifts in Washington · alpha</div><nav><a href="/dc-public-realm/">Home</a><a href="/dc-public-realm/methodology/">Methodology</a><a href="/dc-public-realm/data/">Canonical data</a></nav></header>
    <main>{body}</main><footer>Alpha scope: three objects. Claims are published with source-level provenance and evidentiary status.</footer></body></html>'''

# home
cards=[]
for oid in OBJECTS:
    e=E[oid]; slug=SLUGS[oid]
    cards.append(f'<article class="card"><div class="kicker">{esc(oid)} · {esc(COUNTRIES[oid])}</div><h2><a href="/dc-public-realm/objects/{slug}/">{esc(e["canonical_name"])}</a></h2><p>Explore sourced semantic relationships, conflicts, and provenance.</p></article>')
home=f'''<div class="kicker">Provenance-linked semantic publication</div><h1>Diplomatic Gifts in Washington</h1>
<p class="lede">Three objects, treated not as catalog entries but as networks of claims. Each material relationship is exposed with the source that supports, qualifies, or contradicts it.</p>
<div class="grid">{''.join(cards)}</div>
<h2>What this alpha tests</h2><p>Whether multilingual government, archival, museum, and field evidence can be reconciled into machine-readable relationships without flattening uncertainty or attribution conflicts.</p>'''
(OUT/"index.html").write_text(shell("Home",home,"A provenance-linked semantic publication of three diplomatic gifts in Washington, DC."),encoding="utf-8")

# object pages
for oid in OBJECTS:
    e=E[oid]; slug=SLUGS[oid]
    relevant=[a for a in assertions if a["subject_id"]==oid]
    # include predecessor assertions one hop out
    predecessor_ids={a.get("object_entity_id") for a in relevant if a.get("predicate") in {"RECAST_OF","COPY_OF","DERIVED_FROM_MATERIAL","RELIEF_DERIVED_FROM"}}
    lineage=[a for a in assertions if a["subject_id"] in predecessor_ids]
    body=f'''<div class="kicker">{esc(oid)} · {esc(COUNTRIES[oid])}</div><h1>{esc(e["canonical_name"])}</h1>
    <p class="lede">This page is generated from the canonical assertion layer. Relationships are shown with provenance and status rather than collapsed into a single catalog description.</p>
    <h2>Direct relationships</h2>{''.join(assertion_block(a) for a in relevant)}
    {('<h2>Predecessor / lineage relationships</h2>'+''.join(assertion_block(a) for a in lineage)) if lineage else ''}
    <h2>Canonical JSON</h2><p><a href="/dc-public-realm/data/assertions.json">Assertions</a> · <a href="/dc-public-realm/data/assertion-evidence.json">Assertion evidence</a> · <a href="/dc-public-realm/data/entities.json">Entities</a></p>'''
    d=OUT/"objects"/slug; d.mkdir(parents=True)
    (d/"index.html").write_text(shell(e["canonical_name"],body),encoding="utf-8")

# country pages
for country in sorted(set(COUNTRIES.values())):
    objs=[oid for oid in OBJECTS if COUNTRIES[oid]==country]
    body=f'<div class="kicker">Country view</div><h1>{esc(country)}</h1><p class="lede">A country-level projection of the same canonical semantic layer.</p>'
    for oid in objs:
        e=E[oid]; body+=f'<div class="card"><h2><a href="/dc-public-realm/objects/{SLUGS[oid]}/">{esc(e["canonical_name"])}</a></h2></div>'
    d=OUT/"countries"/country.lower().replace(" ","-"); d.mkdir(parents=True)
    (d/"index.html").write_text(shell(country,body),encoding="utf-8")

# methodology
method='''<div class="kicker">Methodology</div><h1>Provenance before polish</h1>
<p class="lede">The canonical unit is a provenance-bearing assertion: subject, predicate, object or literal value, evidentiary status, and one or more evidence records.</p>
<h2>Rules</h2><p>Creator roles are not flattened. Original-language evidence is retained. Contradictions remain visible. Unknowns remain unknown. Machine-readable output must preserve the same status and provenance shown to human readers.</p>
<h2>Alpha scope</h2><p>José Gervasio Artigas Memorial, José de San Martín Memorial, and the Cuban American Friendship Urn only.</p>'''
d=OUT/"methodology"; d.mkdir(); (d/"index.html").write_text(shell("Methodology",method),encoding="utf-8")

# copy canonical data into site
sd=OUT/"data"; sd.mkdir()
for f in ["entities.json","assertions.json","assertion-evidence.json","sources.json"]:
    shutil.copy2(DATA/f,sd/f)

# simple sitemap and robots for GitHub Pages project path
urls=["/dc-public-realm/","/dc-public-realm/methodology/"]+[f"/dc-public-realm/objects/{SLUGS[o]}/" for o in OBJECTS]+[f"/dc-public-realm/countries/{c.lower()}/" for c in ["Uruguay","Argentina","Cuba"]]
(OUT/"sitemap.txt").write_text("\n".join("https://danielastone.github.io"+u for u in urls)+"\n",encoding="utf-8")
(OUT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://danielastone.github.io/dc-public-realm/sitemap.txt\n",encoding="utf-8")
print(f"Built {len(urls)} public routes plus canonical JSON.")
