#!/usr/bin/env python3
"""Build the diplomatic-gifts alpha site from canonical semantic data."""
from __future__ import annotations
import html, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
OUT=ROOT/"site"
ASSETS=OUT/"assets"

def load_payload(name):
    return json.loads((DATA/name).read_text(encoding="utf-8"))

entities_payload=load_payload("entities.json")
assertions_payload=load_payload("assertions.json")
evidence_payload=load_payload("assertion-evidence.json")
sources_payload=load_payload("sources.json")
entities=entities_payload["entities"]
assertions=assertions_payload["assertions"]
evidence=evidence_payload["assertion_evidence"]
sources=sources_payload["sources"]
E={x["entity_id"]:x for x in entities}
S={x["source_id"]:x for x in sources}
EV={}
for x in evidence: EV.setdefault(x["assertion_id"],[]).append(x)

OBJECTS=["OBJ-0001","OBJ-0002","OBJ-0003"]
SLUGS={
 "OBJ-0001":"jose-gervasio-artigas",
 "OBJ-0002":"jose-de-san-martin",
 "OBJ-0003":"cuban-american-friendship-urn",
}
COUNTRIES={"OBJ-0001":"Uruguay","OBJ-0002":"Argentina","OBJ-0003":"Cuba"}

def sources_independent(a_id,b_id):
    if a_id==b_id: return False
    a,b=S[a_id],S[b_id]
    if not a.get("source_family_id") or not b.get("source_family_id"): return False
    if a["source_family_id"]==b["source_family_id"]: return False
    if b_id in a.get("derived_from_source_ids",[]): return False
    if a_id in b.get("derived_from_source_ids",[]): return False
    return True

def compute_status(a):
    evs=EV.get(a["assertion_id"],[])
    obj=a.get("object_entity_id")
    literal_present="literal_value" in a
    if not obj and not literal_present and any(e.get("evidence_role")=="QUALIFIES" for e in evs):
        return "UNRESOLVED"
    positive={"PRIMARY_SUPPORT","FIELD_VERIFICATION","CORROBORATION"}
    if any(e.get("evidence_role") in positive for e in evs) and any(e.get("evidence_role")=="CONTRADICTS" for e in evs):
        return "CONTESTED"
    direct=[e for e in evs if e.get("evidence_role") in {"PRIMARY_SUPPORT","FIELD_VERIFICATION"} and e.get("authority_fit")=="DIRECT" and e.get("source_id") in S]
    corr=[e for e in evs if e.get("evidence_role")=="CORROBORATION" and e.get("authority_fit") in {"DIRECT","SUPPORTING"} and e.get("source_id") in S]
    if any(sources_independent(d["source_id"],c["source_id"]) for d in direct for c in corr):
        return "VERIFIED"
    if direct or any(e.get("evidence_role") in positive for e in evs):
        return "SUPPORTED"
    if not obj and not literal_present:
        return "UNRESOLVED"
    return "UNSUPPORTED"

derived_assertions=[]
for a in assertions:
    d=dict(a)
    d["computed_status"]=compute_status(a)
    derived_assertions.append(d)
A={x["assertion_id"]:x for x in derived_assertions}

if OUT.exists(): shutil.rmtree(OUT)
ASSETS.mkdir(parents=True)

css=''':root{--fg:#171717;--muted:#666;--line:#ddd;--bg:#fff;--soft:#f6f6f3;--warn:#7a3e00;--bad:#8b1e1e;--ok:#235d37}
*{box-sizing:border-box}body{margin:0;font-family:ui-serif,Georgia,serif;color:var(--fg);background:var(--bg);line-height:1.55}
main,header,footer{max-width:980px;margin:auto;padding:1.25rem}header{border-bottom:1px solid var(--line)}
nav a{margin-right:1rem}a{color:inherit;text-decoration-thickness:.08em;text-underline-offset:.15em}
h1{font-size:clamp(2rem,6vw,4.2rem);line-height:1.02;margin:.5rem 0 1rem}h2{margin-top:2.2rem}
.kicker,.meta{font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.9rem}.lede{font-size:1.2rem;max-width:760px}
.card,.assertion{border:1px solid var(--line);padding:1rem;margin:1rem 0;background:#fff}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}
.assertion code{font-size:.82rem}.status{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.04em}
.status.VERIFIED{color:var(--ok)}.status.CONTESTED{color:var(--warn)}.status.UNRESOLVED,.status.UNSUPPORTED{color:var(--bad)}.evidence{background:var(--soft);padding:.7rem;margin-top:.7rem}
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
    fit=ev.get("authority_fit","").title()
    archived=f' · <a href="{esc(s["archived_url"])}">archive</a>' if s.get("archived_url") else ""
    return f'''<div class="evidence"><strong>{esc(role)}</strong> <span class="meta">({esc(fit)} authority for this claim)</span>: <a href="{esc(s["url"])}">{esc(s["title"])}</a>
    <span class="meta"> — {esc(s["publisher_or_creator"])} · language {esc(s["language"])} · family {esc(s.get("source_family_id","unassigned"))} · retrieved {esc(s.get("retrieved_at","unknown"))}{archived} · locator: {esc(ev.get("locator","not recorded"))}</span>
    {f"<br>{esc(ev.get('evidence_note',''))}" if ev.get("evidence_note") else ""}</div>'''

def assertion_block(a):
    aid=a["assertion_id"]; value=obj_value(a)
    evhtml="".join(source_block(x) for x in EV.get(aid,[]))
    note=f'<p class="meta">{esc(a["interpretation_note"])}</p>' if a.get("interpretation_note") else ""
    status=a["computed_status"]
    return f'''<article class="assertion" id="{esc(aid)}">
      <div class="status {esc(status)}">{esc(status)} · computed</div>
      <h3>{esc(label_pred(a["predicate"]))}: {esc(value)}</h3>
      <code>{esc(a["subject_id"])} → {esc(a["predicate"])} → {esc(a.get("object_entity_id",a.get("literal_value","UNRESOLVED")))}</code>
      {note}{evhtml}
    </article>'''

def shell(title,body,desc=""):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{esc(title)} | Diplomatic Gifts in Washington</title><meta name="description" content="{esc(desc or title)}">
    <link rel="stylesheet" href="/dc-public-realm/assets/style.css"></head><body>
    <header><div class="kicker">Diplomatic Gifts in Washington · alpha</div><nav><a href="/dc-public-realm/">Home</a><a href="/dc-public-realm/methodology/">Methodology</a><a href="/dc-public-realm/data/assertions.json">Derived JSON</a></nav></header>
    <main>{body}</main><footer>Alpha scope: three objects. Claim status is computed from provenance rules; legacy editorial labels remain in canonical source data only for migration audit.</footer></body></html>'''

cards=[]
for oid in OBJECTS:
    e=E[oid]; slug=SLUGS[oid]
    cards.append(f'<article class="card"><div class="kicker">{esc(oid)} · {esc(COUNTRIES[oid])}</div><h2><a href="/dc-public-realm/objects/{slug}/">{esc(e["canonical_name"])}</a></h2><p>Explore sourced semantic relationships, conflicts, and provenance.</p></article>')
home=f'''<div class="kicker">Provenance-derived semantic publication</div><h1>Diplomatic Gifts in Washington</h1>
<p class="lede">Three objects treated as networks of claims. Each material relationship is exposed with the evidence that supports, qualifies, or contradicts it, and status is computed from those evidence records.</p>
<div class="grid">{''.join(cards)}</div>
<h2>What this alpha tests</h2><p>Whether multilingual government, archival, and museum evidence can be reconciled into machine-readable relationships without flattening uncertainty, source lineage, or attribution conflicts.</p>'''
(OUT/"index.html").write_text(shell("Home",home,"A provenance-derived semantic publication of three diplomatic gifts in Washington, DC."),encoding="utf-8")

for oid in OBJECTS:
    e=E[oid]; slug=SLUGS[oid]
    relevant=[a for a in derived_assertions if a["subject_id"]==oid]
    predecessor_ids={a.get("object_entity_id") for a in relevant if a.get("predicate") in {"RECAST_OF","COPY_OF","DERIVED_FROM_MATERIAL","RELIEF_DERIVED_FROM"}}
    lineage=[a for a in derived_assertions if a["subject_id"] in predecessor_ids]
    body=f'''<div class="kicker">{esc(oid)} · {esc(COUNTRIES[oid])}</div><h1>{esc(e["canonical_name"])}</h1>
    <p class="lede">This page is generated from the canonical assertion and evidence layers. Status is derived at build time rather than copied from an editorial label.</p>
    <h2>Direct relationships</h2>{''.join(assertion_block(a) for a in relevant)}
    {('<h2>Predecessor / lineage relationships</h2>'+''.join(assertion_block(a) for a in lineage)) if lineage else ''}
    <h2>Canonical JSON</h2><p><a href="/dc-public-realm/data/assertions.json">Derived assertions</a> · <a href="/dc-public-realm/data/assertion-evidence.json">Assertion evidence</a> · <a href="/dc-public-realm/data/entities.json">Entities</a> · <a href="/dc-public-realm/data/sources.json">Sources</a></p>'''
    d=OUT/"objects"/slug; d.mkdir(parents=True)
    (d/"index.html").write_text(shell(e["canonical_name"],body),encoding="utf-8")

for country in sorted(set(COUNTRIES.values())):
    objs=[oid for oid in OBJECTS if COUNTRIES[oid]==country]
    body=f'<div class="kicker">Country view</div><h1>{esc(country)}</h1><p class="lede">A country-level projection of the same canonical semantic layer.</p>'
    for oid in objs:
        e=E[oid]; body+=f'<div class="card"><h2><a href="/dc-public-realm/objects/{SLUGS[oid]}/">{esc(e["canonical_name"])}</a></h2></div>'
    d=OUT/"countries"/country.lower().replace(" ","-"); d.mkdir(parents=True)
    (d/"index.html").write_text(shell(country,body),encoding="utf-8")

method='''<div class="kicker">Methodology</div><h1>Provenance determines status</h1>
<p class="lede">The canonical unit is a provenance-bearing assertion. Editorial labels do not control publication status: the build derives status from evidence roles, claim-specific authority, source-family lineage, and explicit contradictions.</p>
<h2>Derived-status rule</h2><p><strong>VERIFIED</strong> requires direct support plus corroboration from a different source family with no encoded direct derivation. <strong>SUPPORTED</strong> has positive evidence but lacks qualifying independent corroboration. <strong>CONTESTED</strong> has material positive and contradictory evidence. <strong>UNRESOLVED</strong> preserves an explicit unknown rather than inventing a value.</p>
<h2>Source independence</h2><p><code>source_family_id</code> and <code>derived_from_source_ids</code> make dependency representable. Different families are a transparent generator proxy for independent provenance, not proof that two institutions conducted independent research.</p>
<h2>Reproducibility</h2><p>Every source records a retrieval date. Archived snapshots can be added through <code>archived_url</code>; null means no archived snapshot is yet recorded.</p>
<h2>Alpha scope</h2><p>José Gervasio Artigas Memorial, José de San Martín Memorial, and the Cuban American Friendship Urn only.</p>'''
d=OUT/"methodology"; d.mkdir(); (d/"index.html").write_text(shell("Methodology",method),encoding="utf-8")

sd=OUT/"data"; sd.mkdir()
public_assertions={"schema_version":"0.4","reviewed_date":assertions_payload.get("reviewed_date"),"status_rule_version":"alpha-0.1","assertions":derived_assertions}
(sd/"assertions.json").write_text(json.dumps(public_assertions,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for f in ["entities.json","assertion-evidence.json","sources.json"]:
    shutil.copy2(DATA/f,sd/f)

urls=["/dc-public-realm/","/dc-public-realm/methodology/"]+[f"/dc-public-realm/objects/{SLUGS[o]}/" for o in OBJECTS]+[f"/dc-public-realm/countries/{c.lower()}/" for c in ["Uruguay","Argentina","Cuba"]]
(OUT/"sitemap.txt").write_text("\n".join("https://danielastone.github.io"+u for u in urls)+"\n",encoding="utf-8")
(OUT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://danielastone.github.io/dc-public-realm/sitemap.txt\n",encoding="utf-8")
print(f"Built {len(urls)} public routes plus provenance-derived JSON.")
