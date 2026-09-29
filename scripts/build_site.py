#!/usr/bin/env python3
from __future__ import annotations
import html, json, shutil, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; OUT=ROOT/'site'; ASSETS=OUT/'assets'
def load(n): return json.loads((DATA/n).read_text(encoding='utf-8'))
ep=load('entities.json'); ap=load('assertions.json'); evp=load('assertion-evidence.json'); sp=load('sources.json'); rp=load('predicate-rules.json'); tp=load('research-tasks.json')
entities=ep['entities']; assertions=ap['assertions']; evidence=evp['assertion_evidence']; sources=sp['sources']; rules=rp['predicate_rules']; tasks=tp['tasks']
E={x['entity_id']:x for x in entities}; S={x['source_id']:x for x in sources}; EV={}; TASKS={}
for x in evidence: EV.setdefault(x['assertion_id'],[]).append(x)
for x in tasks: TASKS.setdefault(x['object_entity_id'],[]).append(x)
OBJECTS=['OBJ-0001','OBJ-0002','OBJ-0003']; SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}; COUNTRIES={'OBJ-0001':'Uruguay','OBJ-0002':'Argentina','OBJ-0003':'Cuba'}
POS={'PRIMARY_SUPPORT','IMAGE_EVIDENCE','CORROBORATION'}; DIRECT={'PRIMARY_SUPPORT','IMAGE_EVIDENCE'}; REPO='https://github.com/danielastone/dc-public-realm'
def qualifying(rule,evs):
 d=[e for e in evs if e.get('evidence_role') in DIRECT and e.get('authority_fit')=='DIRECT']; s=rule.get('standard')
 if s=='CONTEMPORANEOUS_OR_CONSTITUTIVE': return any(e.get('proximity') in {'CONTEMPORANEOUS_PRIMARY','CONSTITUTIVE_REGISTRY_RECORD'} for e in d)
 if s=='CURRENT_ADMINISTRATIVE': return any(e.get('proximity')=='CURRENT_ADMINISTRATIVE_RECORD' for e in d)
 if s=='CONSTITUTIVE_REGISTRY': return any(e.get('proximity')=='CONSTITUTIVE_REGISTRY_RECORD' for e in d)
 if s=='OBJECT_LINEAGE': return any(e.get('proximity')=='CONTEMPORANEOUS_PRIMARY' for e in d)
 return False
def independent(evs):
 d=[e for e in evs if e.get('evidence_role') in DIRECT and e.get('authority_fit')=='DIRECT']; c=[e for e in evs if e.get('evidence_role')=='CORROBORATION' and e.get('authority_fit') in {'DIRECT','SUPPORTING'}]
 return any(y.get('dependency_status')=='INDEPENDENT' for x in d for y in c if x.get('source_id')!=y.get('source_id'))
def compute(a):
 evs=EV.get(a['assertion_id'],[]); r=rules[a['predicate']]; obj=a.get('object_entity_id'); lit='literal_value' in a
 if not obj and not lit and any(e.get('evidence_role')=='QUALIFIES' for e in evs): return 'UNRESOLVED','An authoritative source explicitly records the value as unknown or unresolved.'
 if any(e.get('evidence_role') in POS for e in evs) and any(e.get('evidence_role')=='CONTRADICTS' for e in evs): return 'CONTESTED','Material supporting and contradictory evidence are both present.'
 if r.get('single_source_can_verify') and qualifying(r,evs): return 'VERIFIED','The predicate rule permits verification from one directly authoritative source of the required proximity.'
 if independent(evs): return 'VERIFIED','Direct support is independently corroborated; independence is explicitly recorded.'
 if any(e.get('evidence_role') in POS for e in evs): return 'SUPPORTED',"Credible positive evidence exists, but the rule's verification threshold is not met."
 return ('UNRESOLVED','No resolved value is asserted.') if not obj and not lit else ('UNSUPPORTED','No adequate positive evidence is recorded.')
derived=[]
for a in assertions:
 d=dict(a); st,why=compute(a); d['computed_status']=st; d['status_reason']=why; d['evidence_standard']=rules[a['predicate']]['standard']; derived.append(d)
if OUT.exists(): shutil.rmtree(OUT)
ASSETS.mkdir(parents=True)
(ASSETS/'style.css').write_text(':root{--fg:#171717;--muted:#666;--line:#ddd;--soft:#f6f6f3;--warn:#7a3e00;--bad:#8b1e1e;--ok:#235d37}*{box-sizing:border-box}body{margin:0;font-family:ui-serif,Georgia,serif;color:var(--fg);line-height:1.55}main,header,footer{max-width:980px;margin:auto;padding:1.25rem}header{border-bottom:1px solid var(--line)}nav a{margin-right:1rem}a{color:inherit;text-underline-offset:.15em}h1{font-size:clamp(2rem,6vw,4.2rem);line-height:1.02}.kicker,.meta{font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.9rem}.lede{font-size:1.2rem;max-width:760px}.card,.assertion,.task{border:1px solid var(--line);padding:1rem;margin:1rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}.status{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700}.VERIFIED{color:var(--ok)}.CONTESTED{color:var(--warn)}.UNRESOLVED,.UNSUPPORTED{color:var(--bad)}.evidence{background:var(--soft);padding:.7rem;margin-top:.7rem}.task{border-left:4px solid var(--warn);background:#fffdf8}.button{display:inline-block;border:1px solid var(--fg);padding:.45rem .7rem;text-decoration:none}footer{border-top:1px solid var(--line);margin-top:3rem;color:var(--muted)}',encoding='utf-8')
def esc(x): return html.escape(str(x))
def pred(p): return p.replace('_',' ').title()
def value(a): return E.get(a.get('object_entity_id'),{}).get('canonical_name',a.get('object_entity_id')) if a.get('object_entity_id') else a.get('literal_value','Unresolved')
def evblock(ev):
 s=S[ev['source_id']]; return f'<div class="evidence"><strong>{esc(ev["evidence_role"].replace("_"," ").title())}</strong>: <a href="{esc(s["url"])}">{esc(s["title"])}</a><br><span class="meta">Authority: {esc(ev["authority_fit"])} · proximity: {esc(ev.get("proximity"))} · dependency: {esc(ev.get("dependency_status"))}</span></div>'
def ablock(a): return f'<article class="assertion"><div class="status {esc(a["computed_status"])}">{esc(a["computed_status"])} · computed</div><h3>{esc(pred(a["predicate"]))}: {esc(value(a))}</h3><p class="meta">Evidence standard: {esc(a["evidence_standard"])}. {esc(a["status_reason"])}</p>{"".join(evblock(x) for x in EV.get(a["assertion_id"],[]))}</article>'
def taskurl(t):
 body=f'Task: {t["task_id"]}\n\nArchive: {t["repository"]}\nCollection: {t["collection"]}\nPriority units: {"; ".join(t["priority_units"])}\n\nGoal: {t["high_value_result"]}\n\nStatus: CLAIMED / RETRIEVED / NO EVIDENCE\n\nFindings:\n\nArchival citations:\n\nFiles/images:\n'
 return REPO+'/issues/new?'+urllib.parse.urlencode({'title':t['task_id']+' - '+t['title'],'body':body})
def taskblock(t): return f'<article class="task"><div class="status">RESEARCH TASK · {esc(t["status"])}</div><h3>{esc(t["task_id"])} — {esc(t["title"])}</h3><p>{esc(t["research_gap"])}</p><p class="meta"><strong>Archive:</strong> {esc(t["repository"])}<br><strong>Collection:</strong> {esc(t["collection"])}<br><strong>Priority units:</strong> {esc("; ".join(t["priority_units"]))}<br><strong>Evidence effect now:</strong> none</p><a class="button" href="{esc(taskurl(t))}">Claim or report task</a></article>'
def shell(title,body): return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Diplomatic Gifts in Washington</title><link rel="stylesheet" href="/dc-public-realm/assets/style.css"></head><body><header><div class="kicker">Diplomatic Gifts in Washington · alpha</div><nav><a href="/dc-public-realm/">Home</a><a href="/dc-public-realm/methodology/">Methodology</a><a href="/dc-public-realm/collaborate/">Collaborate</a><a href="/dc-public-realm/data/assertions.json">Data</a></nav></header><main>{body}</main><footer>Research leads do not affect assertion status until the underlying record is examined and reviewed.</footer></body></html>'
cards=[]
for oid in OBJECTS:
 n=len(TASKS.get(oid,[])); tag=f' · {n} open research task' if n else ''; cards.append(f'<article class="card"><div class="kicker">{oid} · {COUNTRIES[oid]}{tag}</div><h2><a href="/dc-public-realm/objects/{SLUGS[oid]}/">{esc(E[oid]["canonical_name"])}</a></h2><p>Evidence, conflicts, provenance and research gaps.</p></article>')
(OUT/'index.html').write_text(shell('Home',f'<h1>Diplomatic Gifts in Washington</h1><p class="lede">Object provenance and knowledge provenance are published together, including what remains unknown.</p><div class="grid">{"".join(cards)}</div>'),encoding='utf-8')
for oid in OBJECTS:
 rel=[a for a in derived if a['subject_id']==oid]; preds={a.get('object_entity_id') for a in rel if a.get('predicate') in {'RECAST_OF','COPY_OF','DERIVED_FROM_MATERIAL','RELIEF_DERIVED_FROM'}}; lineage=[a for a in derived if a['subject_id'] in preds]
 body=f'<div class="kicker">{oid} · {COUNTRIES[oid]}</div><h1>{esc(E[oid]["canonical_name"])}</h1><h2>Direct relationships</h2>{"".join(ablock(a) for a in rel)}'
 if lineage: body+='<h2>Predecessor / lineage relationships</h2>'+''.join(ablock(a) for a in lineage)
 if TASKS.get(oid): body+='<h2>Open research gaps</h2><p>These tasks are research leads, not evidence currently counted above.</p>'+''.join(taskblock(t) for t in TASKS[oid])
 d=OUT/'objects'/SLUGS[oid]; d.mkdir(parents=True); (d/'index.html').write_text(shell(E[oid]['canonical_name'],body),encoding='utf-8')
for country in sorted(set(COUNTRIES.values())):
 body=f'<h1>{country}</h1>'+''.join(f'<div class="card"><h2><a href="/dc-public-realm/objects/{SLUGS[o]}/">{esc(E[o]["canonical_name"])}</a></h2></div>' for o in OBJECTS if COUNTRIES[o]==country); d=OUT/'countries'/country.lower(); d.mkdir(parents=True); (d/'index.html').write_text(shell(country,body),encoding='utf-8')
method='<h1>Methodology</h1><p class="lede">Credibility is claim-specific. Research leads, finding aids and unexamined archival units are explicitly separated from evidence.</p><h2>Research boundary</h2><p>A task can identify a promising archive without changing a claim. Status changes only after the underlying record is retrieved, its source lineage established, and its authority for the exact assertion reviewed.</p>'
d=OUT/'methodology'; d.mkdir(); (d/'index.html').write_text(shell('Methodology',method),encoding='utf-8')
collab='<h1>Collaborate</h1><p class="lede">Claim a bounded archival task, retrieve the underlying records, and return enough context for another researcher to reproduce the finding.</p>'+''.join(taskblock(t) for t in tasks)+'<h2>Contributor standard</h2><p>Return repository, collection, series, box/folder/item identifiers, document date, sender and recipient, complete relevant pages and enclosures, exact disputed spellings, retrieval date and reproduction restrictions. A transcription alone is insufficient when lawful scans or photographs can be obtained.</p><p><a href="'+REPO+'/blob/main/docs/collaboration.md">Full archive request and contributor protocol</a></p>'
d=OUT/'collaborate'; d.mkdir(); (d/'index.html').write_text(shell('Collaborate',collab),encoding='utf-8')
sd=OUT/'data'; sd.mkdir(); (sd/'assertions.json').write_text(json.dumps({'schema_version':'0.5','status_rule_version':rp['status_rule_version'],'assertions':derived},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for f in ['entities.json','assertion-evidence.json','sources.json','predicate-rules.json','research-tasks.json']: shutil.copy2(DATA/f,sd/f)
urls=['/dc-public-realm/','/dc-public-realm/methodology/','/dc-public-realm/collaborate/']+[f'/dc-public-realm/objects/{SLUGS[o]}/' for o in OBJECTS]+[f'/dc-public-realm/countries/{c.lower()}/' for c in ['Uruguay','Argentina','Cuba']]
(OUT/'sitemap.txt').write_text('\n'.join('https://danielastone.github.io'+u for u in urls)+'\n',encoding='utf-8'); (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://danielastone.github.io/dc-public-realm/sitemap.txt\n',encoding='utf-8'); print(f'Built {len(urls)} routes with collaboration hooks.')