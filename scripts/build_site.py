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
def effective_roots(ev,by_source,visiting=None):
 visiting=set() if visiting is None else set(visiting); sid=ev.get('source_id')
 if sid in visiting: return None
 visiting.add(sid); origin=ev.get('claim_origin'); parents=ev.get('inherits_claim_from_source_ids',[])
 if origin=='UNKNOWN': return None
 if origin=='ORIGINAL_TO_SOURCE': return {sid}
 if origin not in {'INHERITED','MIXED'}: return None
 roots={sid} if origin=='MIXED' else set()
 for parent in parents:
  pev=by_source.get(parent)
  if pev is None: roots.add(parent); continue
  proots=effective_roots(pev,by_source,visiting)
  if proots is None: return None
  roots.update(proots)
 return roots or None
def independent(evs):
 by_source={e.get('source_id'):e for e in evs}
 d=[e for e in evs if e.get('evidence_role') in DIRECT and e.get('authority_fit')=='DIRECT']; c=[e for e in evs if e.get('evidence_role')=='CORROBORATION' and e.get('authority_fit') in {'DIRECT','SUPPORTING'}]
 for x in d:
  xr=effective_roots(x,by_source)
  if xr is None: continue
  for y in c:
   if x.get('source_id')==y.get('source_id'): continue
   yr=effective_roots(y,by_source)
   if yr is not None and xr.isdisjoint(yr): return True
 return False
def compute(a):
 evs=EV.get(a['assertion_id'],[]); r=rules[a['predicate']]; obj=a.get('object_entity_id'); lit='literal_value' in a
 if not obj and not lit and any(e.get('evidence_role')=='QUALIFIES' for e in evs): return 'UNRESOLVED','An authoritative source explicitly records the value as unknown or unresolved.'
 if any(e.get('evidence_role') in POS for e in evs) and any(e.get('evidence_role')=='CONTRADICTS' for e in evs): return 'CONTESTED','Material supporting and contradictory evidence are both present.'
 if r.get('single_source_can_verify') and qualifying(r,evs): return 'VERIFIED','The predicate rule permits verification from one directly authoritative source of the required proximity.'
 if independent(evs): return 'VERIFIED','Direct support is corroborated by evidence with known, disjoint effective claim roots.'
 if any(e.get('evidence_role') in POS for e in evs): return 'SUPPORTED',"Credible positive evidence exists, but the verification threshold is not met; unknown or shared claim ancestry does not count as independent corroboration."
 return ('UNRESOLVED','No resolved value is asserted.') if not obj and not lit else ('UNSUPPORTED','No adequate positive evidence is recorded.')
derived=[]
for a in assertions:
 d=dict(a); st,why=compute(a); d['computed_status']=st; d['status_reason']=why; d['evidence_standard']=rules[a['predicate']]['standard']; derived.append(d)
if OUT.exists(): shutil.rmtree(OUT)
ASSETS.mkdir(parents=True)
(ASSETS/'style.css').write_text(':root{--fg:#171717;--muted:#666;--line:#ddd;--soft:#f6f6f3;--warn:#7a3e00;--bad:#8b1e1e;--ok:#235d37}*{box-sizing:border-box}body{margin:0;font-family:ui-serif,Georgia,serif;color:var(--fg);line-height:1.55}main,header,footer{max-width:980px;margin:auto;padding:1.25rem}header{border-bottom:1px solid var(--line)}nav a{margin-right:1rem}a{color:inherit;text-underline-offset:.15em}h1{font-size:clamp(2rem,6vw,4.2rem);line-height:1.02}.kicker,.meta{font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.9rem}.lede{font-size:1.2rem;max-width:760px}.card,.assertion,.task{border:1px solid var(--line);padding:1rem;margin:1rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}.status{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;font-weight:700}.VERIFIED{color:var(--ok)}.CONTESTED{color:var(--warn)}.UNRESOLVED,.UNSUPPORTED{color:var(--bad)}.evidence{background:var(--soft);padding:.7rem;margin-top:.7rem}.task{border-left:4px solid var(--warn);background:#fffdf8}.button{display:inline-block;border:1px solid var(--fg);padding:.45rem .7rem;text-decoration:none;margin:.25rem .5rem .25rem 0}.task ul{padding-left:1.25rem}footer{border-top:1px solid var(--line);margin-top:3rem;color:var(--muted)}',encoding='utf-8')
def esc(x): return html.escape(str(x))
def pred(p): return p.replace('_',' ').title()
def value(a): return E.get(a.get('object_entity_id'),{}).get('canonical_name',a.get('object_entity_id')) if a.get('object_entity_id') else a.get('literal_value','Unresolved')
def evblock(ev):
 s=S[ev['source_id']]; evs=EV.get(ev['assertion_id'],[]); roots=effective_roots(ev,{x.get('source_id'):x for x in evs})
 root_label='unresolved' if roots is None else '; '.join(S.get(r,{}).get('title',r) for r in sorted(roots))
 inherited=ev.get('inherits_claim_from_source_ids',[]); inherit_label='none recorded' if not inherited else '; '.join(S.get(r,{}).get('title',r) for r in inherited)
 return f'<div class="evidence"><strong>{esc(ev["evidence_role"].replace("_"," ").title())}</strong>: <a href="{esc(s["url"])}">{esc(s["title"])}</a><br><span class="meta">Authority: {esc(ev["authority_fit"])} · proximity: {esc(ev.get("proximity"))} · claim origin: {esc(ev.get("claim_origin"))} · effective roots: {esc(root_label)}<br>Inherited from: {esc(inherit_label)} · basis: {esc(ev.get("inheritance_basis"))}</span><br><span class="meta">{esc(ev.get("inheritance_note",""))}</span></div>'
def ablock(a): return f'<article class="assertion"><div class="status {esc(a["computed_status"])}">{esc(a["computed_status"])} · computed</div><h3>{esc(pred(a["predicate"]))}: {esc(value(a))}</h3><p class="meta">Evidence standard: {esc(a["evidence_standard"])}. {esc(a["status_reason"])}</p>{"".join(evblock(x) for x in EV.get(a["assertion_id"],[]))}</article>'
def taskurl(t):
 body=f'Task: {t["task_id"]}\nTask URL: https://danielastone.github.io/dc-public-realm/tasks/{t["task_id"].lower()}/\n\nArchive/repository: {t["repository"]}\nCollection: {t["collection"]}\nPriority units:\n- '+"\n- ".join(t['priority_units'])+f'\n\nGoal: {t["high_value_result"]}\n\nCritical evidence rule: {t["critical_rule"]}\n\nWorkflow stage: CLAIMED / SUBMITTED / CLOSED-NO-EVIDENCE\n\nResearcher:\nDate claimed:\nDate checked:\n\nFindings:\n\nArchival/bibliographic citations:\n\nFiles/images/links:\n\nNotes on source dependency or likely upstream source:\n'
 return REPO+'/issues/new?'+urllib.parse.urlencode({'title':t['task_id']+' - '+t['title'],'body':body})
def taskblock(t):
 units=''.join(f'<li>{esc(x)}</li>' for x in t['priority_units']); terms=', '.join(t.get('search_terms',[])); strategy=t.get('archive_strategy','ARCHIVAL_RETRIEVAL').replace('_',' ').title()
 return f'<article class="task" id="{esc(t["task_id"])}"><div class="status">RESEARCH TASK · {esc(t["status"])} · {esc(strategy)}</div><h3><a href="/dc-public-realm/tasks/{esc(t["task_id"].lower())}/">{esc(t["task_id"])} — {esc(t["title"])}</a></h3><p>{esc(t["research_gap"])}</p><p class="meta"><strong>Repository:</strong> {esc(t["repository"])}<br><strong>Collection:</strong> {esc(t["collection"])}</p><strong>Retrieve / check</strong><ul>{units}</ul><p><strong>What would materially advance the record:</strong> {esc(t["high_value_result"])}</p><p><strong>Evidence rule:</strong> {esc(t["critical_rule"])}</p><p class="meta"><strong>Search terms:</strong> {esc(terms)}<br><strong>Current evidentiary effect:</strong> none until reviewed and ingested.</p><a class="button" href="/dc-public-realm/tasks/{esc(t["task_id"].lower())}/">Task details</a><a class="button" href="{esc(taskurl(t))}">Claim or submit result</a></article>'
def shell(title,body): return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Diplomatic Gifts in Washington</title><link rel="stylesheet" href="/dc-public-realm/assets/style.css"></head><body><header><div class="kicker">Diplomatic Gifts in Washington · alpha</div><nav><a href="/dc-public-realm/">Home</a><a href="/dc-public-realm/methodology/">Methodology</a><a href="/dc-public-realm/collaborate/">Collaborate</a><a href="/dc-public-realm/data/assertions.json">Data</a></nav></header><main>{body}</main><footer>Research leads do not affect assertion status until the underlying record is examined and reviewed.</footer></body></html>'
cards=[]
for oid in OBJECTS:
 n=len(TASKS.get(oid,[])); tag=f' · {n} open research task'+('s' if n!=1 else '') if n else ''; cards.append(f'<article class="card"><div class="kicker">{oid} · {COUNTRIES[oid]}{tag}</div><h2><a href="/dc-public-realm/objects/{SLUGS[oid]}/">{esc(E[oid]["canonical_name"])}</a></h2><p>Evidence, conflicts, provenance and research gaps.</p></article>')
(OUT/'index.html').write_text(shell('Home',f'<h1>Diplomatic Gifts in Washington</h1><p class="lede">Object provenance and knowledge provenance are published together, including what remains unknown and how collaborators can resolve it.</p><div class="grid">{"".join(cards)}</div><p><a class="button" href="/dc-public-realm/collaborate/">View all open research tasks</a></p>'),encoding='utf-8')
for oid in OBJECTS:
 rel=[a for a in derived if a['subject_id']==oid]; preds={a.get('object_entity_id') for a in rel if a.get('predicate') in {'RECAST_OF','COPY_OF','DERIVED_FROM_MATERIAL','RELIEF_DERIVED_FROM'}}; lineage=[a for a in derived if a['subject_id'] in preds]
 body=f'<div class="kicker">{oid} · {COUNTRIES[oid]}</div><h1>{esc(E[oid]["canonical_name"])}</h1><h2>Direct relationships</h2>{"".join(ablock(a) for a in rel)}'
 if lineage: body+='<h2>Predecessor / lineage relationships</h2>'+''.join(ablock(a) for a in lineage)
 if TASKS.get(oid): body+='<h2>Help resolve the open record</h2><p>Each task below is deliberately bounded. A research lead is not counted as evidence until the underlying material is retrieved and reviewed.</p>'+''.join(taskblock(t) for t in TASKS[oid])
 d=OUT/'objects'/SLUGS[oid]; d.mkdir(parents=True); (d/'index.html').write_text(shell(E[oid]['canonical_name'],body),encoding='utf-8')
for t in tasks:
 oid=t['object_entity_id']; units=''.join(f'<li>{esc(x)}</li>' for x in t['priority_units']); terms=', '.join(t.get('search_terms',[]))
 lifecycle='<p class="meta"><strong>Lifecycle:</strong> OPEN → CLAIMED → SUBMITTED → REVIEWED → INCORPORATED / REJECTED / CLOSED-NO-EVIDENCE. Claiming or submitting a task does not change any assertion status.</p>'
 body=f'<div class="kicker">COLLABORATION TASK · {esc(t["status"])}</div><h1>{esc(t["task_id"])} — {esc(t["title"])}</h1><p class="lede">{esc(t["research_gap"])}</p>'+lifecycle+f'<p><strong>Object:</strong> <a href="/dc-public-realm/objects/{SLUGS[oid]}/">{esc(E[oid]["canonical_name"])}</a></p><p><strong>Repository:</strong> {esc(t["repository"])}<br><strong>Collection:</strong> {esc(t["collection"])}</p><h2>Retrieve or check</h2><ul>{units}</ul><h2>What counts as useful</h2><p>{esc(t["high_value_result"])}</p><h2>Evidence boundary</h2><p>{esc(t["critical_rule"])}</p><p class="meta"><strong>Search terms:</strong> {esc(terms)}<br><strong>Evidence effect before review:</strong> none.</p><p><a class="button" href="{esc(taskurl(t))}">Claim or submit result</a><a class="button" href="{REPO}/blob/main/data/research-tasks.json">Machine-readable registry</a></p><h2>Submission standard</h2><p>Return the archival identifiers, document date, creator/sender and recipient when available, complete relevant pages or images where lawful, retrieval date, stable links, restrictions, and any indication that the text derives from another source. Do not assign a claim status.</p>'
 d=OUT/'tasks'/t['task_id'].lower(); d.mkdir(parents=True,exist_ok=True); (d/'index.html').write_text(shell(t['task_id'],body),encoding='utf-8')
for country in sorted(set(COUNTRIES.values())):
 body=f'<h1>{country}</h1>'+''.join(f'<div class="card"><h2><a href="/dc-public-realm/objects/{SLUGS[o]}/">{esc(E[o]["canonical_name"])}</a></h2></div>' for o in OBJECTS if COUNTRIES[o]==country); d=OUT/'countries'/country.lower(); d.mkdir(parents=True); (d/'index.html').write_text(shell(country,body),encoding='utf-8')
method='<h1>Methodology</h1><p class="lede">Credibility is claim-specific. The generator separates repository custody, document genealogy, and the ancestry of each individual claim.</p><h2>Source inheritance</h2><p>Independent corroboration is computed from effective claim roots. Different websites, agencies, repositories, or source families do not count as independent when they inherit the same proposition from a common upstream source. Unknown ancestry remains unresolved and does not count as independence.</p><h2>Research boundary</h2><p>A task can identify a promising archive without changing a claim. Status changes only after the underlying record is retrieved, its source lineage established, and its authority for the exact assertion reviewed.</p><p><a href="'+REPO+'/blob/main/docs/source-inheritance.md">Source-inheritance specification</a></p>'
d=OUT/'methodology'; d.mkdir(); (d/'index.html').write_text(shell('Methodology',method),encoding='utf-8')
collab='<h1>Open research tasks</h1><p class="lede">Choose one bounded task. Each task has a permanent public URL and a prefilled submission route so a collaborator can contribute without first learning the entire data model.</p><p class="meta"><strong>Lifecycle:</strong> OPEN → CLAIMED → SUBMITTED → REVIEWED → INCORPORATED / REJECTED / CLOSED-NO-EVIDENCE. Collaboration status and assertion status are deliberately separate.</p>'+''.join(taskblock(t) for t in tasks)+'<h2>Contributor standard</h2><p>Return repository, collection, series, box/folder/item identifiers, document date, sender and recipient where applicable, complete relevant pages and enclosures, exact disputed spellings, retrieval date and reproduction restrictions. A transcription alone is insufficient when lawful scans or photographs can be obtained.</p><h2>What happens after retrieval</h2><p>A completed task still has no automatic evidentiary effect. Material is reviewed for archival identity, claim-specific authority, temporal proximity, source dependency and contradiction before it enters the evidence graph or changes a computed assertion status.</p><p><a class="button" href="'+REPO+'/blob/main/docs/collaboration.md">Full contributor protocol</a><a class="button" href="/dc-public-realm/data/research-tasks.json">Research tasks JSON</a></p>'
d=OUT/'collaborate'; d.mkdir(); (d/'index.html').write_text(shell('Collaborate',collab),encoding='utf-8')
sd=OUT/'data'; sd.mkdir(); (sd/'assertions.json').write_text(json.dumps({'schema_version':'0.5','status_rule_version':rp['status_rule_version'],'assertions':derived},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for f in ['entities.json','assertion-evidence.json','sources.json','predicate-rules.json','research-tasks.json']: shutil.copy2(DATA/f,sd/f)
urls=['/dc-public-realm/','/dc-public-realm/methodology/','/dc-public-realm/collaborate/']+[f'/dc-public-realm/objects/{SLUGS[o]}/' for o in OBJECTS]+[f'/dc-public-realm/countries/{c.lower()}/' for c in ['Uruguay','Argentina','Cuba']]+[f'/dc-public-realm/tasks/{t["task_id"].lower()}/' for t in tasks]
(OUT/'sitemap.txt').write_text('\n'.join('https://danielastone.github.io'+u for u in urls)+'\n',encoding='utf-8'); (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://danielastone.github.io/dc-public-realm/sitemap.txt\n',encoding='utf-8'); print(f'Built {len(urls)} routes with {len(tasks)} collaboration tasks.')