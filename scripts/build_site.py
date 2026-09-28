#!/usr/bin/env python3
from __future__ import annotations
import html, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"; OUT=ROOT/"site"; ASSETS=OUT/"assets"
def load(name): return json.loads((DATA/name).read_text(encoding="utf-8"))
ep=load("entities.json"); ap=load("assertions.json"); evp=load("assertion-evidence.json"); sp=load("sources.json"); rp=load("predicate-rules.json")
entities=ep["entities"]; assertions=ap["assertions"]; evidence=evp["assertion_evidence"]; sources=sp["sources"]; rules=rp["predicate_rules"]
E={x["entity_id"]:x for x in entities}; S={x["source_id"]:x for x in sources}; EV={}
for x in evidence: EV.setdefault(x["assertion_id"],[]).append(x)
OBJECTS=["OBJ-0001","OBJ-0002","OBJ-0003"]
SLUGS={"OBJ-0001":"jose-gervasio-artigas","OBJ-0002":"jose-de-san-martin","OBJ-0003":"cuban-american-friendship-urn"}
COUNTRIES={"OBJ-0001":"Uruguay","OBJ-0002":"Argentina","OBJ-0003":"Cuba"}
POS={"PRIMARY_SUPPORT","FIELD_VERIFICATION","CORROBORATION"}; DIRECT={"PRIMARY_SUPPORT","FIELD_VERIFICATION"}

def qualifying_single_source(rule,evs):
    direct=[e for e in evs if e.get("evidence_role") in DIRECT and e.get("authority_fit")=="DIRECT"]
    standard=rule.get("standard")
    if standard=="CONTEMPORANEOUS_OR_CONSTITUTIVE":
        return any(e.get("proximity") in {"CONTEMPORANEOUS_PRIMARY","CONSTITUTIVE_REGISTRY_RECORD"} for e in direct)
    if standard=="CURRENT_ADMINISTRATIVE":
        return any(e.get("proximity")=="CURRENT_ADMINISTRATIVE_RECORD" for e in direct)
    if standard=="CONSTITUTIVE_REGISTRY":
        return any(e.get("proximity")=="CONSTITUTIVE_REGISTRY_RECORD" for e in direct)
    if standard=="OBJECT_LINEAGE":
        return any(e.get("proximity")=="CONTEMPORANEOUS_PRIMARY" for e in direct)
    return False

def independent_pair(evs):
    direct=[e for e in evs if e.get("evidence_role") in DIRECT and e.get("authority_fit")=="DIRECT"]
    corr=[e for e in evs if e.get("evidence_role")=="CORROBORATION" and e.get("authority_fit") in {"DIRECT","SUPPORTING"}]
    return any(c.get("dependency_status")=="INDEPENDENT" for d in direct for c in corr if d.get("source_id")!=c.get("source_id"))

def compute(a):
    evs=EV.get(a["assertion_id"],[]); rule=rules[a["predicate"]]; obj=a.get("object_entity_id"); lit="literal_value" in a
    if not obj and not lit and any(e.get("evidence_role")=="QUALIFIES" for e in evs):
        return "UNRESOLVED","An authoritative source explicitly records the value as unknown or unresolved."
    if any(e.get("evidence_role") in POS for e in evs) and any(e.get("evidence_role")=="CONTRADICTS" for e in evs):
        return "CONTESTED","Material supporting and contradictory evidence are both present."
    if rule.get("single_source_can_verify") and qualifying_single_source(rule,evs):
        return "VERIFIED","The predicate rule permits verification from one directly authoritative source of the required proximity."
    if independent_pair(evs):
        return "VERIFIED","Direct support is independently corroborated; independence is explicitly recorded."
    if any(e.get("evidence_role") in POS for e in evs):
        return "SUPPORTED","Credible positive evidence exists, but the rule's verification threshold is not met."
    return ("UNRESOLVED","No resolved value is asserted.") if not obj and not lit else ("UNSUPPORTED","No adequate positive evidence is recorded.")

derived=[]
for a in assertions:
    d=dict(a); status,reason=compute(a); d["computed_status"]=status; d["status_reason"]=reason; d["evidence_standard"]=rules[a["predicate"]]["standard"]; derived.append(d)

if OUT.exists(): shutil.rmtree(OUT)
ASSETS.mkdir(parents=True)
(ASSETS/"style.css").write_text(''':root{--fg:#171717;--muted:#666;--line:#ddd;--soft:#f6f6f3;--warn:#7a3e00;--bad:#8b1e1e;--ok:#235d37}*{box-sizing:border-box}body{margin:0;font-family:ui-serif,Georgia,serif;color:var(--fg);line-height:1.55}main,header,footer{max-width:980px;margin:auto;padding:1.25rem}header{border-bottom:1px solid var(--line)}nav a{margin-right:1rem}a{color:inherit;text-underline-offset:.15em}h1{font-size:clamp(2rem,6vw,4.2rem);line-height:1.02}.kicker,.meta{font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.9rem}.lede{font-size:1.2rem;max-width:760px}.card,.assertion{border:1px solid var(--line);padding:1rem;margin:1rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}.status{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700}.VERIFIED{color:var(--ok)}.CONTESTED{color:var(--warn)}.UNRESOLVED,.UNSUPPORTED{color:var(--bad)}.evidence{background:var(--soft);padding:.7rem;margin-top:.7rem}footer{border-top:1px solid var(--line);margin-top:3rem;color:var(--muted)}''',encoding="utf-8")

def esc(x): return html.escape(str(x))
def pred(p): return p.replace("_"," ").title()
def value(a):
    if a.get("object_entity_id"): return E.get(a["object_entity_id"],{}).get("canonical_name",a["object_entity_id"])
    if "literal_value" in a: return a["literal_value"]
    return "Unresolved"

def evblock(ev):
    s=S[ev["source_id"]]; role=ev["evidence_role"].replace("_"," ").title(); fit=ev["authority_fit"].title()
    note=f"<br>{esc(ev['evidence_note'])}" if ev.get("evidence_note") else ""
    return f'<div class="evidence"><strong>{esc(role)}</strong>: <a href="{esc(s["url"])}">{esc(s["title"])}</a><br><span class="meta">Authority for claim: {esc(fit)} · proximity: {esc(ev.get("proximity"))} · dependency: {esc(ev.get("dependency_status"))} · source role: {esc(s.get("source_role"))} · retrieved {esc(s.get("retrieved_at"))} · locator: {esc(ev.get("locator","not recorded"))}</span>{note}</div>'

def ablock(a):
    status=a["computed_status"]; note=f'<p class="meta">{esc(a["interpretation_note"])}</p>' if a.get("interpretation_note") else ""
    return f'<article class="assertion"><div class="status {esc(status)}">{esc(status)} · computed</div><h3>{esc(pred(a["predicate"]))}: {esc(value(a))}</h3><p class="meta">Evidence standard: {esc(a["evidence_standard"])}. {esc(a["status_reason"])}</p><code>{esc(a["subject_id"])} → {esc(a["predicate"])} → {esc(a.get("object_entity_id",a.get("literal_value","UNRESOLVED")))}</code>{note}{"".join(evblock(x) for x in EV.get(a["assertion_id"],[]))}</article>'

def shell(title,body,desc=""):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Diplomatic Gifts in Washington</title><meta name="description" content="{esc(desc or title)}"><link rel="stylesheet" href="/dc-public-realm/assets/style.css"></head><body><header><div class="kicker">Diplomatic Gifts in Washington · alpha</div><nav><a href="/dc-public-realm/">Home</a><a href="/dc-public-realm/methodology/">Methodology</a><a href="/dc-public-realm/data/assertions.json">Derived JSON</a></nav></header><main>{body}</main><footer>Three-object alpha. No universal numeric source-credibility score; credibility is evaluated claim by claim.</footer></body></html>'

cards=[]
for oid in OBJECTS:
    e=E[oid]; cards.append(f'<article class="card"><div class="kicker">{oid} · {COUNTRIES[oid]}</div><h2><a href="/dc-public-realm/objects/{SLUGS[oid]}/">{esc(e["canonical_name"])}</a></h2><p>Explore sourced relationships, conflicts, and provenance.</p></article>')
home=f'<div class="kicker">Source-grounded provenance publication</div><h1>Diplomatic Gifts in Washington</h1><p class="lede">Credibility is evaluated from each source’s authority for the specific claim, proximity to the fact, and known dependency—not from a universal source score.</p><div class="grid">{"".join(cards)}</div><h2>What this alpha tests</h2><p>Whether multilingual government, archival, and museum evidence can be reconciled into machine-readable relationships without flattening uncertainty, source lineage, or attribution conflicts.</p>'
(OUT/"index.html").write_text(shell("Home",home),encoding="utf-8")

for oid in OBJECTS:
    e=E[oid]; relevant=[a for a in derived if a["subject_id"]==oid]
    predecessors={a.get("object_entity_id") for a in relevant if a.get("predicate") in {"RECAST_OF","COPY_OF","DERIVED_FROM_MATERIAL","RELIEF_DERIVED_FROM"}}
    lineage=[a for a in derived if a["subject_id"] in predecessors]
    body=f'<div class="kicker">{oid} · {COUNTRIES[oid]}</div><h1>{esc(e["canonical_name"])}</h1><p class="lede">Generated from canonical assertions and evidence. Status is derived at build time, not copied from an editorial label.</p><h2>Direct relationships</h2>{"".join(ablock(a) for a in relevant)}'
    if lineage: body+='<h2>Predecessor / lineage relationships</h2>'+"".join(ablock(a) for a in lineage)
    body+='<h2>Canonical JSON</h2><p><a href="/dc-public-realm/data/assertions.json">Derived assertions</a> · <a href="/dc-public-realm/data/assertion-evidence.json">Assertion evidence</a> · <a href="/dc-public-realm/data/entities.json">Entities</a> · <a href="/dc-public-realm/data/sources.json">Sources</a></p>'
    d=OUT/"objects"/SLUGS[oid]; d.mkdir(parents=True); (d/"index.html").write_text(shell(e["canonical_name"],body),encoding="utf-8")

for country in sorted(set(COUNTRIES.values())):
    body=f'<div class="kicker">Country view</div><h1>{country}</h1>'
    for oid in [o for o in OBJECTS if COUNTRIES[o]==country]: body+=f'<div class="card"><h2><a href="/dc-public-realm/objects/{SLUGS[oid]}/">{esc(E[oid]["canonical_name"])}</a></h2></div>'
    d=OUT/"countries"/country.lower(); d.mkdir(parents=True); (d/"index.html").write_text(shell(country,body),encoding="utf-8")

method='''<div class="kicker">Methodology</div><h1>Credibility is claim-specific</h1><p class="lede">Sources are not assigned universal numerical credibility scores. The same source can be decisive for one predicate and weak for another.</p><h2>What the generator evaluates</h2><p><strong>Authority fit</strong> asks whether the source is positioned to establish this claim. <strong>Proximity</strong> records whether it is contemporaneous, constitutive, current administrative, or a later inventory/research record. <strong>Dependency</strong> records whether corroboration is independently grounded, derivative, possibly derivative, or unknown.</p><h2>Status rules</h2><p>Some predicates can be verified by a single constitutive, contemporaneous, or current administrative record. Other historical attribution and provenance predicates require explicitly independent corroboration. Unknown dependency never counts as independence. Credible contradiction produces CONTESTED.</p><h2>Epistemic honesty</h2><p>SUPPORTED is not a failure state. It means the project has credible evidence but does not claim more certainty than the recorded provenance warrants.</p>'''
d=OUT/"methodology"; d.mkdir(); (d/"index.html").write_text(shell("Methodology",method),encoding="utf-8")

sd=OUT/"data"; sd.mkdir()
(sd/"assertions.json").write_text(json.dumps({"schema_version":"0.5","reviewed_date":ap.get("reviewed_date"),"status_rule_version":rp["status_rule_version"],"assertions":derived},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for f in ["entities.json","assertion-evidence.json","sources.json","predicate-rules.json"]: shutil.copy2(DATA/f,sd/f)
urls=["/dc-public-realm/","/dc-public-realm/methodology/"]+[f"/dc-public-realm/objects/{SLUGS[o]}/" for o in OBJECTS]+[f"/dc-public-realm/countries/{c.lower()}/" for c in ["Uruguay","Argentina","Cuba"]]
(OUT/"sitemap.txt").write_text("\n".join("https://danielastone.github.io"+u for u in urls)+"\n",encoding="utf-8")
(OUT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://danielastone.github.io/dc-public-realm/sitemap.txt\n",encoding="utf-8")
print(f"Built {len(urls)} routes using claim-specific source credibility rules.")
