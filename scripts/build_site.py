#!/usr/bin/env python3
from __future__ import annotations
import html,json,shutil,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; OUT=ROOT/'site'; ASSETS=OUT/'assets'; BASE='/dc-public-realm'
def load(n): return json.loads((DATA/n).read_text(encoding='utf-8'))
ep=load('entities.json'); ap=load('assertions.json'); evp=load('assertion-evidence.json'); sp=load('sources.json'); rp=load('predicate-rules.json'); tp=load('research-tasks.json')
entities=ep['entities']; assertions=ap['assertions']; evidence=evp['assertion_evidence']; sources=sp['sources']; rules=rp['predicate_rules']; tasks=tp['tasks']; E={x['entity_id']:x for x in entities}; S={x['source_id']:x for x in sources}; EV={}; TASKS={}
for x in evidence: EV.setdefault(x['assertion_id'],[]).append(x)
for x in tasks: TASKS.setdefault(x['object_entity_id'],[]).append(x)
OBJECTS=['OBJ-0001','OBJ-0002','OBJ-0003']; SLUGS={'OBJ-0001':'jose-gervasio-artigas','OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}; COUNTRIES={'OBJ-0001':'Uruguay','OBJ-0002':'Argentina','OBJ-0003':'Cuba'}; POS={'PRIMARY_SUPPORT','IMAGE_EVIDENCE','CORROBORATION'}; DIRECT={'PRIMARY_SUPPORT','IMAGE_EVIDENCE'}; REPO='https://github.com/danielastone/dc-public-realm'
def qualifying(rule,evs):
 d=[e for e in evs if e.get('evidence_role') in DIRECT and e.get('authority_fit')=='DIRECT']; s=rule.get('standard')
 if s=='CONTEMPORANEOUS_OR_CONSTITUTIVE': return any(e.get('proximity') in {'CONTEMPORANEOUS_PRIMARY','CONSTITUTIVE_REGISTRY_RECORD'} for e in d)
 if s=='CURRENT_ADMINISTRATIVE': return any(e.get('proximity')=='CURRENT_ADMINISTRATIVE_RECORD' for e in d)
 if s=='CONSTITUTIVE_REGISTRY': return any(e.get('proximity')=='CONSTITUTIVE_REGISTRY_RECORD' for e in d)
 if s=='OBJECT_LINEAGE': return any(e.get('proximity')=='CONTEMPORANEOUS_PRIMARY' for e in d)
 return False
def effective_roots(ev,by_source,visiting=None):
 visiting=set() if visiting is None else set(visiting); sid=ev.get('source_id')
 if sid in visiting:return None
 visiting.add(sid); origin=ev.get('claim_origin'); parents=ev.get('inherits_claim_from_source_ids',[])
 if origin=='UNKNOWN':return None
 if origin=='ORIGINAL_TO_SOURCE':return {sid}
 if origin not in {'INHERITED','MIXED'}:return None
 roots={sid} if origin=='MIXED' else set()
 for parent in parents:
  pev=by_source.get(parent)
  if pev is None:roots.add(parent);continue
  proots=effective_roots(pev,by_source,visiting)
  if proots is None:return None
  roots.update(proots)
 return roots or None
def independent(evs):
 by={e.get('source_id'):e for e in evs}; d=[e for e in evs if e.get('evidence_role') in DIRECT and e.get('authority_fit')=='DIRECT']; c=[e for e in evs if e.get('evidence_role')=='CORROBORATION' and e.get('authority_fit') in {'DIRECT','SUPPORTING'}]
 for x in d:
  xr=effective_roots(x,by)
  if xr is None:continue
  for y in c:
   yr=effective_roots(y,by)
   if x.get('source_id')!=y.get('source_id') and yr is not None and xr.isdisjoint(yr):return True
 return False
def compute(a):
 evs=EV.get(a['assertion_id'],[]); r=rules[a['predicate']]; obj=a.get('object_entity_id'); lit='literal_value' in a
 if not obj and not lit and any(e.get('evidence_role')=='QUALIFIES' for e in evs):return 'UNRESOLVED','An authoritative source records the value as unresolved.'
 if any(e.get('evidence_role') in POS for e in evs) and any(e.get('evidence_role')=='CONTRADICTS' for e in evs):return 'CONTESTED','The reviewed sources differ materially on this statement.'
 if r.get('single_source_can_verify') and qualifying(r,evs):return 'VERIFIED','A directly authoritative source meets the evidence rule for this statement.'
 if independent(evs):return 'VERIFIED','Direct support is independently corroborated.'
 if any(e.get('evidence_role') in POS for e in evs):return 'SUPPORTED','Credible evidence supports the statement, but the verification threshold is not met.'
 return ('UNRESOLVED','No resolved value is established.') if not obj and not lit else ('UNSUPPORTED','No adequate positive evidence is recorded.')
derived=[]
for a in assertions:
 d=dict(a); st,why=compute(a); d['computed_status']=st; d['status_reason']=why; d['evidence_standard']=rules[a['predicate']]['standard']; derived.append(d)
if OUT.exists():shutil.rmtree(OUT)
ASSETS.mkdir(parents=True)
(ASSETS/'style.css').write_text(''':root{--fg:#1b1b1b;--muted:#626262;--line:#d8d8d2;--soft:#f7f7f4;--accent:#5a3d16;--verified:#28583a;--supported:#5b4b16;--contested:#8a3d22;--unresolved:#6a3b62}*{box-sizing:border-box}body{margin:0;color:var(--fg);font-family:ui-serif,Georgia,serif;font-size:18px;line-height:1.58}a{text-underline-offset:.16em;overflow-wrap:anywhere}header,main,footer{max-width:900px;margin:auto;padding:1.25rem}header{border-bottom:1px solid var(--line);font-family:ui-sans-serif,system-ui,sans-serif;font-size:.9rem}nav{display:flex;gap:.45rem 1rem;flex-wrap:wrap}nav a{color:inherit}h1{font-size:clamp(2.35rem,7vw,4.5rem);line-height:1.03;margin:.35rem 0 1rem;letter-spacing:-.025em}h2{font-size:1.65rem;line-height:1.2;margin-top:3.3rem;border-bottom:1px solid var(--line);padding-bottom:.45rem}h3{font-size:1.3rem;line-height:1.25;margin:.2rem 0 .5rem}.kicker,.meta{font-family:ui-sans-serif,system-ui,sans-serif;color:var(--muted);font-size:.82rem}.kicker{letter-spacing:.07em;text-transform:uppercase}.lede{font-size:1.2rem;line-height:1.5;max-width:44rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}.card{border-top:3px solid var(--line);padding:1rem 0;margin:1rem 0}.assertion{margin:2rem 0 2.5rem}.assertion+.assertion{border-top:1px solid var(--line);padding-top:2rem}.status{display:flex;align-items:flex-start;gap:.65rem;margin:.45rem 0 .7rem;font-family:ui-sans-serif,system-ui,sans-serif;font-size:.82rem;line-height:1.4}.status-label{display:inline-block;white-space:nowrap;border:1px solid currentColor;border-radius:999px;padding:.16rem .5rem;font-weight:700}.status-reason{color:var(--muted);max-width:36rem}.VERIFIED .status-label{color:var(--verified)}.SUPPORTED .status-label{color:var(--supported)}.CONTESTED .status-label{color:var(--contested)}.UNRESOLVED .status-label,.UNSUPPORTED .status-label{color:var(--unresolved)}details.evidence{background:var(--soft);border:1px solid var(--line);padding:.75rem 1rem;margin:1rem 0}details summary{cursor:pointer;font-family:ui-sans-serif,system-ui,sans-serif;font-weight:650}.source-row{padding:.9rem 0;border-top:1px solid var(--line)}.source-row:first-of-type{margin-top:.7rem}.source-role{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.76rem;font-weight:700;text-transform:uppercase;color:var(--muted)}.task{border-left:4px solid var(--accent);background:#fffdf8;padding:1rem 1.1rem;margin:1.4rem 0}.button{display:inline-block;border:1px solid var(--fg);padding:.45rem .7rem;text-decoration:none;margin:.25rem .5rem .25rem 0;font-family:ui-sans-serif,system-ui,sans-serif;font-size:.86rem}footer{border-top:1px solid var(--line);margin-top:3rem;color:var(--muted);font-family:ui-sans-serif,system-ui,sans-serif;font-size:.82rem}@media(max-width:600px){body{font-size:17px;line-height:1.55}header,main,footer{padding-left:1rem;padding-right:1rem}h1{font-size:2.55rem}h2{font-size:1.45rem;margin-top:2.7rem}h3{font-size:1.22rem}.lede{font-size:1.1rem}.assertion{margin:1.6rem 0 2.1rem}.assertion+.assertion{padding-top:1.6rem}.status{display:block}.status-label{margin-bottom:.35rem}.status-reason{display:block;font-size:.78rem}details.evidence{padding:.7rem}.task{padding:.85rem}}''',encoding='utf-8')
def esc(x):return html.escape(str(x))
def pred(p):return p.replace('_',' ').title()
def value(a):return E.get(a.get('object_entity_id'),{}).get('canonical_name',a.get('object_entity_id')) if a.get('object_entity_id') else a.get('literal_value','Unresolved')
def public_status(st):return {'VERIFIED':'Verified','SUPPORTED':'Supported','CONTESTED':'Sources differ','UNRESOLVED':'Unresolved','UNSUPPORTED':'Not established'}.get(st,st.title())
def evblock(ev):
 s=S[ev['source_id']]; role={'PRIMARY_SUPPORT':'Main source','CORROBORATION':'Additional source','QUALIFIES':'Qualification','CONTRADICTS':'Differing record','IMAGE_EVIDENCE':'Image evidence'}.get(ev['evidence_role'],pred(ev['evidence_role']))
 return f'<div class="source-row"><div class="source-role">{esc(role)}</div><a href="{esc(s["url"])}">{esc(s["title"])}</a><div class="meta">{esc(ev.get("locator","Record"))}</div></div>'
def ablock(a):
 evs=EV.get(a['assertion_id'],[]); n=len({e['source_id'] for e in evs})
 return f'<article class="assertion"><div class="kicker">{esc(a["assertion_id"])}</div><h3>{esc(pred(a["predicate"]))}: {esc(value(a))}</h3><div class="status {esc(a["computed_status"])}"><span class="status-label">{esc(public_status(a["computed_status"]))}</span><span class="status-reason">{esc(a["status_reason"])}</span></div><details class="evidence"><summary>Sources · {n}</summary>{"".join(evblock(x) for x in evs)}</details></article>'
def taskurl(t):
 body=f'Task: {t["task_id"]}\nTask URL: https://danielastone.github.io/dc-public-realm/tasks/{t["task_id"].lower()}/\n\nRepository: {t["repository"]}\nCollection: {t["collection"]}\n\nFindings:\n\nCitations:\n\nFiles/images/links:\n'
 return REPO+'/issues/new?'+urllib.parse.urlencode({'title':t['task_id']+' - '+t['title'],'body':body})
def targetlabel(x):
 if x.get('assertion_id'):
  a=next((a for a in derived if a['assertion_id']==x['assertion_id']),None);return f'{x["assertion_id"]} · {pred(a["predicate"])} · {public_status(a["computed_status"])}' if a else x['assertion_id']
 return 'Potential new proposition: '+x.get('proposition','')
def targetblock(x):return f'<li><strong>{esc(targetlabel(x))}</strong><br><span class="meta">Requested evidence: {esc(pred(x["desired_evidence"]))}. Possible effect after review: {esc(pred(x["desired_effect"]))}.</span></li>'
def taskblock(t):
 targets=''.join(targetblock(x) for x in t.get('epistemic_targets',[]))
 return f'<article class="task"><div class="kicker">Research mission · {esc(t["status"])}</div><h3><a href="{BASE}/tasks/{esc(t["task_id"].lower())}/">{esc(t["title"])}</a></h3><p>{esc(t["research_gap"])}</p><p><strong>Requested result:</strong> {esc(t["high_value_result"])}</p><details><summary>Research details</summary><h4>Record affected</h4><ul>{targets}</ul><p class="meta"><strong>Repository:</strong> {esc(t["repository"])}<br><strong>Collection:</strong> {esc(t["collection"])}</p><p class="meta"><strong>Evidence requirement:</strong> {esc(t["critical_rule"])}</p></details><a class="button" href="{BASE}/tasks/{esc(t["task_id"].lower())}/">Mission details</a><a class="button" href="{esc(taskurl(t))}">Submit a finding</a></article>'
def shell(title,body):return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Diplomatic Gifts in Washington</title><link rel="stylesheet" href="{BASE}/assets/style.css"></head><body><header><div class="kicker">Diplomatic Gifts in Washington</div><nav><a href="{BASE}/">Explore</a><a href="{BASE}/collaborate/">Research missions</a><a href="{BASE}/methodology/">About the research</a><a href="{BASE}/data/">Data</a></nav></header><main>{body}</main><footer>Research submissions do not change the public record until the underlying source is reviewed.</footer></body></html>'
cards=[]
for oid in OBJECTS:
 n=len(TASKS.get(oid,[]));cards.append(f'<article class="card"><div class="kicker">{COUNTRIES[oid]} · {n} open research mission'+('s' if n!=1 else '')+f'</div><h2><a href="{BASE}/objects/{SLUGS[oid]}/">{esc(E[oid]["canonical_name"])}</a></h2><p>Catalog record, sources, and open research questions.</p></article>')
(OUT/'index.html').write_text(shell('Home',f'<h1>Diplomatic Gifts in Washington</h1><p class="lede">Research records for diplomatic monuments in Washington, D.C., with opportunities for public participation in art-historical research.</p><div class="grid">{"".join(cards)}</div>'),encoding='utf-8')
for oid in OBJECTS:
 rel=[a for a in derived if a['subject_id']==oid];preds={a.get('object_entity_id') for a in rel if a.get('predicate') in {'RECAST_OF','COPY_OF','DERIVED_FROM_MATERIAL','RELIEF_DERIVED_FROM'}};lineage=[a for a in derived if a['subject_id'] in preds]
 body=f'<div class="kicker">{COUNTRIES[oid]} · catalog record</div><h1>{esc(E[oid]["canonical_name"])}</h1><p class="lede">Current research record with each statement presented together with its status and supporting sources.</p><p><a href="{BASE}/data/">Canonical data</a></p><h2>Record</h2>{"".join(ablock(a) for a in rel)}'
 if lineage:body+='<h2>Predecessor and lineage</h2>'+''.join(ablock(a) for a in lineage)
 if TASKS.get(oid):body+='<h2>Research missions</h2><p>These missions identify records that could clarify or qualify this catalog record.</p>'+''.join(taskblock(t) for t in TASKS[oid])
 d=OUT/'objects'/SLUGS[oid];d.mkdir(parents=True);(d/'index.html').write_text(shell(E[oid]['canonical_name'],body),encoding='utf-8')
for t in tasks:
 oid=t['object_entity_id'];units=''.join(f'<li>{esc(x)}</li>' for x in t['priority_units']);targets=''.join(targetblock(x) for x in t.get('epistemic_targets',[]));inherit=''.join(f'<li>{esc(x)}</li>' for x in t.get('inheritance_questions',[]))
 body=f'<div class="kicker">Research mission · {esc(t["status"])}</div><h1>{esc(t["title"])}</h1><p class="lede">{esc(t["research_gap"])}</p><p><strong>Object:</strong> <a href="{BASE}/objects/{SLUGS[oid]}/">{esc(E[oid]["canonical_name"])}</a></p><h2>Requested records</h2><ul>{units}</ul><p><strong>Repository:</strong> {esc(t["repository"])}<br><strong>Collection:</strong> {esc(t["collection"])}</p><h2>Why this matters</h2><ul>{targets}</ul><p><strong>Useful result:</strong> {esc(t["high_value_result"])}</p><h2>Source-history questions</h2><ul>{inherit or "<li>Document whether the source is independent or repeats an earlier account.</li>"}</ul><h2>Before submitting</h2><p>{esc(t["critical_rule"])}</p><p>No catalog statement changes until the source is reviewed.</p><a class="button" href="{esc(taskurl(t))}">Submit a finding</a>'
 d=OUT/'tasks'/t['task_id'].lower();d.mkdir(parents=True);(d/'index.html').write_text(shell(t['title'],body),encoding='utf-8')
items=''.join(f'<article class="task"><div class="kicker">{esc(t["task_id"])} · {esc(COUNTRIES[t["object_entity_id"]])}</div><h3><a href="{BASE}/tasks/{esc(t["task_id"].lower())}/">{esc(t["title"])}</a></h3><p>{esc(t["research_gap"])}</p><p><strong>Useful result:</strong> {esc(t["high_value_result"])}</p></article>' for t in tasks)
d=OUT/'collaborate';d.mkdir();(d/'index.html').write_text(shell('Research missions',f'<h1>Research missions</h1><p class="lede">Help investigate unresolved questions about Washington’s diplomatic monuments. No specialized training is required; complete citations and accurately identified records are more useful than interpretation.</p>{items}<h2>What happens to a contribution</h2><p>A submitted source is checked, linked to the statement it bears on, and then used to confirm, qualify, contradict, or leave that statement unresolved. Submission alone does not change the public record.</p>'),encoding='utf-8')
body='<h1>About the research</h1><p class="lede">The project separates historical statements from the sources used to evaluate them, and keeps disagreements visible when reliable records differ.</p><h2>Evidence model</h2><p>Each statement is stored as an individual assertion. Evidence records identify whether a source supports, qualifies, or contradicts it.</p><h2>Source history</h2><p>Multiple publications do not necessarily represent independent evidence. When a later source repeats an earlier account, that relationship is recorded where it can be established.</p><h2>Status rules</h2><p><strong>Verified</strong> means the evidence meets the rule defined for that kind of statement. <strong>Supported</strong> means credible positive evidence exists but the verification threshold is not met. <strong>Sources differ</strong> means material supporting and contradictory records are both present. <strong>Unresolved</strong> means the reviewed evidence does not establish a value.</p><h2>Research and publication</h2><p>Research missions identify records that could change or qualify the catalog. Contributions are reviewed before any public assertion changes.</p><h2>Limitations</h2><p>The catalog is a research project, not an institutional collections database. Absence from the current record does not establish historical absence.</p>'
d=OUT/'methodology';d.mkdir();(d/'index.html').write_text(shell('About the research',body),encoding='utf-8')
DD=OUT/'data';DD.mkdir();(DD/'assertions.json').write_text(json.dumps({'schema_version':'alpha-0.2','assertions':derived},indent=2),encoding='utf-8');(DD/'entities.json').write_text(json.dumps(ep,indent=2),encoding='utf-8');(DD/'assertion-evidence.json').write_text(json.dumps(evp,indent=2),encoding='utf-8');(DD/'research-tasks.json').write_text(json.dumps(tp,indent=2),encoding='utf-8');(DD/'claim-modes.json').write_text(json.dumps(load('claim-modes.json'),indent=2),encoding='utf-8');(DD/'external-records.json').write_text(json.dumps(load('external-records.json'),indent=2),encoding='utf-8')
data_files=[('assertions.json','Assertions','Public assertion records with computed publication status and evidence standard.'),('entities.json','Entities','Canonical entity records used by the published catalog.'),('assertion-evidence.json','Assertion evidence','Links between assertions and their supporting, qualifying, contradicting, or image evidence.'),('research-tasks.json','Research tasks','Open research missions and their epistemic targets.'),('claim-modes.json','Claim modes','Scholarly claim-mode metadata used by the project.'),('external-records.json','External records','Identifiers and interoperability records for external systems.')]
data_items=''.join(f'<article class="card"><h2><a href="{BASE}/data/{esc(filename)}">{esc(label)}</a></h2><p>{esc(description)}</p><div class="meta">{esc(filename)}</div></article>' for filename,label,description in data_files)
(DD/'index.html').write_text(shell('Canonical data',f'<div class="kicker">Machine-readable publication</div><h1>Canonical data</h1><p class="lede">Machine-readable records underlying the public catalog. These files are published outputs of the project data pipeline; rendered object pages remain human-readable views of the same research record.</p><div class="grid">{data_items}</div>'),encoding='utf-8')
print('Built readable sitewide presentation')