#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
SCHEMA="0.4"
EDITORIAL={"VERIFIED","PARTIALLY_VERIFIED","CONTESTED","UNRESOLVED","FIELD_OBSERVED"}
ROLES={"PRIMARY_SUPPORT","FIELD_VERIFICATION","CORROBORATION","CONTRADICTS","QUALIFIES"}
FIT={"DIRECT","SUPPORTING","LIMITED"}
POS={"PRIMARY_SUPPORT","FIELD_VERIFICATION","CORROBORATION"}
DIRECT={"PRIMARY_SUPPORT","FIELD_VERIFICATION"}

def load(name,key):
    p=json.loads((DATA/name).read_text(encoding="utf-8"))
    if p.get("schema_version")!=SCHEMA: raise ValueError(f"{name}: schema_version must be {SCHEMA}")
    if not isinstance(p.get(key),list): raise ValueError(f"{name}: {key} must be a list")
    return p[key]

def index(rows,key,label,errors):
    out={}
    for i,r in enumerate(rows,1):
        v=r.get(key)
        if not v: errors.append(f"{label}[{i}]: missing {key}"); continue
        if v in out: errors.append(f"{label}: duplicate {key} {v}")
        out[v]=r
    return out

def independent(a,b,S):
    if a==b: return False
    x,y=S[a],S[b]
    if not x.get("source_family_id") or not y.get("source_family_id"): return False
    if x["source_family_id"]==y["source_family_id"]: return False
    if b in x.get("derived_from_source_ids",[]) or a in y.get("derived_from_source_ids",[]): return False
    return True

def compute(a,evs,S):
    obj=a.get("object_entity_id"); lit="literal_value" in a
    if not obj and not lit and any(e.get("evidence_role")=="QUALIFIES" for e in evs): return "UNRESOLVED"
    if any(e.get("evidence_role") in POS for e in evs) and any(e.get("evidence_role")=="CONTRADICTS" for e in evs): return "CONTESTED"
    direct=[e for e in evs if e.get("evidence_role") in DIRECT and e.get("authority_fit")=="DIRECT" and e.get("source_id") in S]
    corr=[e for e in evs if e.get("evidence_role")=="CORROBORATION" and e.get("authority_fit") in {"DIRECT","SUPPORTING"} and e.get("source_id") in S]
    if any(independent(d["source_id"],c["source_id"],S) for d in direct for c in corr): return "VERIFIED"
    if direct or any(e.get("evidence_role") in POS for e in evs): return "SUPPORTED"
    return "UNRESOLVED" if not obj and not lit else "UNSUPPORTED"

def main():
    errors=[]; warnings=[]
    try:
        entities=load("entities.json","entities"); assertions=load("assertions.json","assertions")
        evidence=load("assertion-evidence.json","assertion_evidence"); sources=load("sources.json","sources")
    except Exception as exc:
        print(f"VALIDATION FAILED\n- {exc}"); return 1
    E=index(entities,"entity_id","entities",errors); A=index(assertions,"assertion_id","assertions",errors)
    S=index(sources,"source_id","sources",errors); index(evidence,"assertion_evidence_id","assertion_evidence",errors)
    for sid,s in S.items():
        for k in ("title","publisher_or_creator","language","retrieved_at","source_family_id"):
            if not s.get(k): errors.append(f"{sid}: missing {k}")
        if not isinstance(s.get("derived_from_source_ids",[]),list): errors.append(f"{sid}: derived_from_source_ids must be a list")
        for parent in s.get("derived_from_source_ids",[]):
            if parent not in S: errors.append(f"{sid}: derived_from_source_ids references missing source {parent}")
    by={}
    for ev in evidence:
        eid=ev.get("assertion_evidence_id","<missing>"); aid=ev.get("assertion_id"); sid=ev.get("source_id")
        if aid not in A: errors.append(f"{eid}: references missing assertion {aid}")
        if sid not in S: errors.append(f"{eid}: references missing source {sid}")
        if ev.get("evidence_role") not in ROLES: errors.append(f"{eid}: invalid evidence_role")
        if ev.get("authority_fit") not in FIT: errors.append(f"{eid}: invalid authority_fit")
        if sid in S and ev.get("source_language")!=S[sid].get("language"): errors.append(f"{eid}: source_language disagrees with {sid}")
        by.setdefault(aid,[]).append(ev)
    for aid,a in A.items():
        obj=a.get("object_entity_id"); lit="literal_value" in a; ed=a.get("editorial_status")
        if a.get("subject_id") not in E: errors.append(f"{aid}: missing subject entity")
        if not a.get("predicate"): errors.append(f"{aid}: missing predicate")
        if ed not in EDITORIAL: errors.append(f"{aid}: invalid editorial_status {ed}")
        if "status" in a or "computed_status" in a: errors.append(f"{aid}: canonical assertion stores derived status")
        if obj and obj not in E: errors.append(f"{aid}: missing object entity {obj}")
        if obj and lit: errors.append(f"{aid}: cannot have object_entity_id and literal_value")
        if ed!="UNRESOLVED" and not obj and not lit: errors.append(f"{aid}: resolved editorial assertion lacks value")
        if ed=="UNRESOLVED" and (obj or lit): errors.append(f"{aid}: unresolved editorial assertion has value")
        evs=by.get(aid,[])
        if not evs: errors.append(f"{aid}: has no evidence"); continue
        d=compute(a,evs,S)
        if d!=ed: warnings.append(f"{aid}: editorial_status={ed}, computed_status={d}")
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s)")
        for x in errors: print(f"- {x}")
        return 1
    print(f"VALIDATION PASSED: {len(E)} entities, {len(A)} assertions, {len(evidence)} evidence links, {len(S)} sources")
    print("Status rule: VERIFIED requires direct support plus corroboration from a distinct source family with no encoded direct derivation.")
    print(f"STATUS MIGRATION: {len(warnings)} editorial/computed difference(s)")
    for w in warnings: print(f"- {w}")
    return 0

if __name__=="__main__": sys.exit(main())
