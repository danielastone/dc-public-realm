#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.environ.get("KNOWLEDGE_DATA_DIR", str(ROOT/"data")))
SCHEMA="0.5"
ROLES={"PRIMARY_SUPPORT","IMAGE_EVIDENCE","CORROBORATION","CONTRADICTS","QUALIFIES"}
FIT={"DIRECT","SUPPORTING","LIMITED"}
PROX={"CONTEMPORANEOUS_PRIMARY","CONSTITUTIVE_REGISTRY_RECORD","CURRENT_ADMINISTRATIVE_RECORD","LATER_OFFICIAL_HERITAGE_RECORD","LATER_OFFICIAL_RECORD","LATER_OFFICIAL_RESEARCH","LATER_OFFICIAL_SUMMARY","LATER_INVENTORY","LATER_MUSEUM_RECORD","CONTEMPORANEOUS_IMAGE","LATER_HISTORICAL_IMAGE","UNKNOWN"}
DEPENDENCY={"INDEPENDENT","DERIVED","POSSIBLY_DERIVED","UNKNOWN"}
CLAIM_ORIGIN={"ORIGINAL_TO_SOURCE","INHERITED","MIXED","UNKNOWN"}
INHERITANCE_BASIS={"EXPLICIT_CITATION","REPRODUCED_TEXT","CREATOR_REPOSITORY_RELATION","WIRE_SERVICE","CATALOG_DERIVATION","TEXTUAL_MATCH","SCHOLARLY_INFERENCE","UNKNOWN"}
IMAGE_SCOPE={"OBJECT_IDENTITY","INSCRIPTION_TEXT","MAKER_MARK","HISTORICAL_LOCATION","HISTORICAL_APPEARANCE","VISIBLE_MATERIAL","VISIBLE_CONDITION","CONTEXT","OTHER_OBSERVABLE"}
TASK_STATUS={"OPEN","CLAIMED","SUBMITTED","REVIEWED","INCORPORATED","REJECTED","CLOSED-NO-EVIDENCE"}
POS={"PRIMARY_SUPPORT","IMAGE_EVIDENCE","CORROBORATION"}; DIRECT_ROLES={"PRIMARY_SUPPORT","IMAGE_EVIDENCE"}

def load(name,key):
 p=json.loads((DATA/name).read_text(encoding="utf-8"));
 if p.get("schema_version")!=SCHEMA: raise ValueError(f"{name}: schema_version must be {SCHEMA}")
 rows=p.get(key)
 if not isinstance(rows,list): raise ValueError(f"{name}: {key} must be a list")
 return p,rows

def index(rows,key,label,errors):
 out={}
 for i,r in enumerate(rows,1):
  v=r.get(key)
  if not v: errors.append(f"{label}[{i}]: missing {key}"); continue
  if v in out: errors.append(f"{label}: duplicate {key} {v}")
  out[v]=r
 return out

def qualifying_single_source(rule,evs):
 direct=[e for e in evs if e.get("evidence_role") in DIRECT_ROLES and e.get("authority_fit")=="DIRECT"]; standard=rule.get("standard")
 if standard=="CONTEMPORANEOUS_OR_CONSTITUTIVE": return any(e.get("proximity") in {"CONTEMPORANEOUS_PRIMARY","CONSTITUTIVE_REGISTRY_RECORD"} for e in direct)
 if standard=="CURRENT_ADMINISTRATIVE": return any(e.get("proximity")=="CURRENT_ADMINISTRATIVE_RECORD" for e in direct)
 if standard=="CONSTITUTIVE_REGISTRY": return any(e.get("proximity")=="CONSTITUTIVE_REGISTRY_RECORD" for e in direct)
 if standard=="OBJECT_LINEAGE": return any(e.get("proximity")=="CONTEMPORANEOUS_PRIMARY" for e in direct)
 return False

def effective_roots(ev,by_source,visiting=None):
 visiting=set() if visiting is None else set(visiting); sid=ev.get("source_id")
 if sid in visiting: raise ValueError(f"claim inheritance cycle involving {sid}")
 visiting.add(sid); origin=ev.get("claim_origin"); parents=ev.get("inherits_claim_from_source_ids",[])
 if origin=="UNKNOWN": return None
 if origin=="ORIGINAL_TO_SOURCE": return {sid}
 if origin not in {"INHERITED","MIXED"}: return None
 roots={sid} if origin=="MIXED" else set()
 for parent in parents:
  pev=by_source.get(parent)
  if pev is None: roots.add(parent); continue
  proots=effective_roots(pev,by_source,visiting)
  if proots is None: return None
  roots.update(proots)
 return roots or None

def independent_pair(evs):
 by_source={e.get("source_id"):e for e in evs}; direct=[e for e in evs if e.get("evidence_role") in DIRECT_ROLES and e.get("authority_fit")=="DIRECT"]; corr=[e for e in evs if e.get("evidence_role")=="CORROBORATION" and e.get("authority_fit") in {"DIRECT","SUPPORTING"}]
 for d in direct:
  dr=effective_roots(d,by_source)
  if dr is None: continue
  for c in corr:
   if d.get("source_id")==c.get("source_id"): continue
   cr=effective_roots(c,by_source)
   if cr is not None and dr.isdisjoint(cr): return True
 return False

def compute(a,evs,rule):
 obj=a.get("object_entity_id"); lit="literal_value" in a
 if not obj and not lit and any(e.get("evidence_role")=="QUALIFIES" for e in evs): return "UNRESOLVED","An authoritative source explicitly records the value as unknown or unresolved."
 has_pos=any(e.get("evidence_role") in POS for e in evs); has_contra=any(e.get("evidence_role")=="CONTRADICTS" for e in evs)
 if has_pos and has_contra: return "CONTESTED","Material supporting and contradictory evidence are both present."
 if rule.get("single_source_can_verify") and qualifying_single_source(rule,evs): return "VERIFIED","The predicate rule permits verification from one directly authoritative source of the required proximity."
 if independent_pair(evs): return "VERIFIED","Direct support is corroborated by evidence with known, disjoint effective claim roots."
 if has_pos: return "SUPPORTED","Credible positive evidence exists, but the verification threshold is not met; unknown or shared claim ancestry does not count as independent corroboration."
 return ("UNRESOLVED","No resolved value is asserted.") if not obj and not lit else ("UNSUPPORTED","No adequate positive evidence is recorded.")

def main():
 errors=[]
 try:
  _,entities=load("entities.json","entities"); _,assertions=load("assertions.json","assertions"); _,evidence=load("assertion-evidence.json","assertion_evidence"); _,sources=load("sources.json","sources")
  task_payload=json.loads((DATA/"research-tasks.json").read_text(encoding="utf-8")); tasks=task_payload.get("tasks",[])
  if task_payload.get("schema_version")!="0.2" or not isinstance(tasks,list): raise ValueError("research-tasks.json: schema_version must be 0.2 and tasks must be a list")
  rules_payload=json.loads((DATA/"predicate-rules.json").read_text(encoding="utf-8")); rules=rules_payload.get("predicate_rules",{})
  if rules_payload.get("schema_version")!=SCHEMA: raise ValueError("predicate-rules.json: schema_version must be 0.5")
 except Exception as exc: print(f"VALIDATION FAILED\n- {exc}"); return 1
 E=index(entities,"entity_id","entities",errors); A=index(assertions,"assertion_id","assertions",errors); S=index(sources,"source_id","sources",errors); index(evidence,"assertion_evidence_id","assertion_evidence",errors)
 for sid,s in S.items():
  for k in ("title","publisher_or_creator","language","retrieved_at","source_family_id","source_role","credibility_note"):
   if not s.get(k): errors.append(f"{sid}: missing {k}")
  if not isinstance(s.get("derived_from_source_ids",[]),list): errors.append(f"{sid}: derived_from_source_ids must be a list")
  for parent in s.get("derived_from_source_ids",[]):
   if parent not in S: errors.append(f"{sid}: derived_from_source_ids references missing source {parent}")
  if s.get("source_type")=="HistoricalPhotograph":
   if s.get("source_role")!="HISTORICAL_IMAGE": errors.append(f"{sid}: HistoricalPhotograph source_role must be HISTORICAL_IMAGE")
   for k in ("repository_or_host","record_url","image_date","rights_statement","object_entity_id"):
    if not s.get(k): errors.append(f"{sid}: historical photograph missing {k}")
   if s.get("object_entity_id") not in E: errors.append(f"{sid}: historical photograph references missing object entity")
 T=index(tasks,"task_id","research_tasks",errors)
 for tid,t in T.items():
  for k in ("object_entity_id","title","status","evidence_effect","research_gap","repository","collection","priority_units","critical_rule","high_value_result","instructions_path"):
   if not t.get(k): errors.append(f"{tid}: missing {k}")
  if t.get("object_entity_id") not in E: errors.append(f"{tid}: references missing object entity")
  if t.get("status") not in TASK_STATUS: errors.append(f"{tid}: invalid collaboration status {t.get('status')}")
  if t.get("evidence_effect")!="NONE_UNTIL_REVIEWED" and t.get("status") in {"OPEN","CLAIMED","SUBMITTED"}:
   errors.append(f"{tid}: pre-review collaboration task may not claim evidentiary effect")
  if not isinstance(t.get("priority_units"),list) or not t.get("priority_units"): errors.append(f"{tid}: priority_units must be a non-empty list")
 by={}
 for ev in evidence:
  eid=ev.get("assertion_evidence_id","<missing>"); aid=ev.get("assertion_id"); sid=ev.get("source_id")
  if aid not in A: errors.append(f"{eid}: references missing assertion {aid}")
  if sid not in S: errors.append(f"{eid}: references missing source {sid}")
  if ev.get("evidence_role") not in ROLES: errors.append(f"{eid}: invalid evidence_role")
  if ev.get("authority_fit") not in FIT: errors.append(f"{eid}: invalid authority_fit")
  if ev.get("proximity") not in PROX: errors.append(f"{eid}: invalid proximity")
  if ev.get("dependency_status") not in DEPENDENCY: errors.append(f"{eid}: invalid dependency_status")
  if ev.get("claim_origin") not in CLAIM_ORIGIN: errors.append(f"{eid}: invalid or missing claim_origin")
  if ev.get("inheritance_basis") not in INHERITANCE_BASIS: errors.append(f"{eid}: invalid or missing inheritance_basis")
  parents=ev.get("inherits_claim_from_source_ids")
  if not isinstance(parents,list): errors.append(f"{eid}: inherits_claim_from_source_ids must be a list"); parents=[]
  if not ev.get("inheritance_note"): errors.append(f"{eid}: missing inheritance_note")
  if ev.get("claim_origin")=="INHERITED" and not parents: errors.append(f"{eid}: INHERITED claim requires at least one upstream source")
  if ev.get("claim_origin")=="ORIGINAL_TO_SOURCE" and parents: errors.append(f"{eid}: ORIGINAL_TO_SOURCE must not inherit claim from another source")
  for parent in parents:
   if parent not in S: errors.append(f"{eid}: inherits claim from missing source {parent}")
   if parent==sid: errors.append(f"{eid}: source cannot inherit claim from itself")
  if sid in S and ev.get("source_language")!=S[sid].get("language"): errors.append(f"{eid}: source_language disagrees with {sid}")
  if sid in S and S[sid].get("source_type")=="HistoricalPhotograph":
   if ev.get("evidence_role")!="IMAGE_EVIDENCE": errors.append(f"{eid}: historical photograph must use IMAGE_EVIDENCE")
   if ev.get("proximity") not in {"CONTEMPORANEOUS_IMAGE","LATER_HISTORICAL_IMAGE"}: errors.append(f"{eid}: historical photograph requires image proximity")
   if ev.get("observation_scope") not in IMAGE_SCOPE: errors.append(f"{eid}: historical photograph requires valid observation_scope")
  by.setdefault(aid,[]).append(ev)
 for aid,evs in by.items():
  by_source={e.get("source_id"):e for e in evs}
  for ev in evs:
   try: effective_roots(ev,by_source)
   except ValueError as exc: errors.append(f"{ev.get('assertion_evidence_id')}: {exc}")
 counts={}
 for aid,a in A.items():
  pred=a.get("predicate"); obj=a.get("object_entity_id"); lit="literal_value" in a
  if a.get("subject_id") not in E: errors.append(f"{aid}: missing subject entity")
  if not pred: errors.append(f"{aid}: missing predicate")
  if pred not in rules: errors.append(f"{aid}: no predicate rule for {pred}")
  if "status" in a or "computed_status" in a or "editorial_status" in a: errors.append(f"{aid}: canonical assertion may not store a confidence/status label")
  if obj and obj not in E: errors.append(f"{aid}: missing object entity {obj}")
  if obj and lit: errors.append(f"{aid}: cannot have object_entity_id and literal_value")
  evs=by.get(aid,[])
  if not evs: errors.append(f"{aid}: has no evidence"); continue
  if pred in rules:
   status,_=compute(a,evs,rules[pred]); counts[status]=counts.get(status,0)+1
 if errors:
  print(f"VALIDATION FAILED: {len(errors)} error(s)")
  for x in errors: print(f"- {x}")
  return 1
 print(f"VALIDATION PASSED [{DATA}]: {len(E)} entities, {len(A)} assertions, {len(evidence)} evidence links, {len(S)} sources, {len(T)} collaboration tasks")
 print("Epistemic rule: independent corroboration is computed from known, disjoint effective claim roots; different repositories or source families do not establish independence.")
 print("Computed status counts: "+", ".join(f"{k}={v}" for k,v in sorted(counts.items())))
 return 0
if __name__=="__main__": sys.exit(main())
