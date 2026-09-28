#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
SCHEMA="0.5"
ROLES={"PRIMARY_SUPPORT","FIELD_VERIFICATION","CORROBORATION","CONTRADICTS","QUALIFIES"}
FIT={"DIRECT","SUPPORTING","LIMITED"}
PROX={"CONTEMPORANEOUS_PRIMARY","CONSTITUTIVE_REGISTRY_RECORD","CURRENT_ADMINISTRATIVE_RECORD","LATER_OFFICIAL_HERITAGE_RECORD","LATER_OFFICIAL_RECORD","LATER_OFFICIAL_RESEARCH","LATER_OFFICIAL_SUMMARY","LATER_INVENTORY","LATER_MUSEUM_RECORD","FIELD_OBSERVATION","UNKNOWN"}
DEPENDENCY={"INDEPENDENT","DERIVED","POSSIBLY_DERIVED","UNKNOWN"}
OBSERVATION_SCOPE={"OBJECT_IDENTITY","INSCRIPTION_TEXT","MAKER_MARK","PRESENT_LOCATION","VISIBLE_MATERIAL","VISIBLE_CONDITION","CONTEXT","OTHER_OBSERVABLE"}
POS={"PRIMARY_SUPPORT","FIELD_VERIFICATION","CORROBORATION"}
DIRECT_ROLES={"PRIMARY_SUPPORT","FIELD_VERIFICATION"}

def load(name,key):
    p=json.loads((DATA/name).read_text(encoding="utf-8"))
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
    direct=[e for e in evs if e.get("evidence_role") in DIRECT_ROLES and e.get("authority_fit")=="DIRECT"]
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
    direct=[e for e in evs if e.get("evidence_role") in DIRECT_ROLES and e.get("authority_fit")=="DIRECT"]
    corr=[e for e in evs if e.get("evidence_role")=="CORROBORATION" and e.get("authority_fit") in {"DIRECT","SUPPORTING"}]
    # Field photographs are direct evidence only of observable facts. They may never
    # bootstrap historical provenance by acting as independent corroboration.
    corr=[e for e in corr if e.get("proximity")!="FIELD_OBSERVATION"]
    return any(c.get("dependency_status")=="INDEPENDENT" for d in direct for c in corr if d.get("source_id")!=c.get("source_id"))

def compute(a,evs,rule):
    obj=a.get("object_entity_id"); lit="literal_value" in a
    if not obj and not lit and any(e.get("evidence_role")=="QUALIFIES" for e in evs):
        return "UNRESOLVED","An authoritative source explicitly records the value as unknown or unresolved."
    has_pos=any(e.get("evidence_role") in POS for e in evs)
    has_contra=any(e.get("evidence_role")=="CONTRADICTS" for e in evs)
    if has_pos and has_contra:
        return "CONTESTED","Material supporting and contradictory evidence are both present."
    if rule.get("single_source_can_verify") and qualifying_single_source(rule,evs):
        return "VERIFIED","The predicate rule permits verification from one directly authoritative source of the required proximity."
    if independent_pair(evs):
        return "VERIFIED","Direct support is independently corroborated; independence is explicitly recorded rather than inferred."
    if has_pos:
        return "SUPPORTED","Credible positive evidence exists, but the rule's verification threshold is not met."
    return ("UNRESOLVED","No resolved value is asserted.") if not obj and not lit else ("UNSUPPORTED","No adequate positive evidence is recorded.")

def main():
    errors=[]
    try:
        _,entities=load("entities.json","entities")
        _,assertions=load("assertions.json","assertions")
        _,evidence=load("assertion-evidence.json","assertion_evidence")
        _,sources=load("sources.json","sources")
        rules_payload=json.loads((DATA/"predicate-rules.json").read_text(encoding="utf-8"))
        if rules_payload.get("schema_version")!=SCHEMA: raise ValueError("predicate-rules.json: schema_version must be 0.5")
        rules=rules_payload.get("predicate_rules",{})
    except Exception as exc:
        print(f"VALIDATION FAILED\n- {exc}"); return 1

    E=index(entities,"entity_id","entities",errors); A=index(assertions,"assertion_id","assertions",errors)
    S=index(sources,"source_id","sources",errors); index(evidence,"assertion_evidence_id","assertion_evidence",errors)

    for sid,s in S.items():
        for k in ("title","publisher_or_creator","language","retrieved_at","source_family_id","source_role","credibility_note"):
            if not s.get(k): errors.append(f"{sid}: missing {k}")
        if not isinstance(s.get("derived_from_source_ids",[]),list): errors.append(f"{sid}: derived_from_source_ids must be a list")
        for parent in s.get("derived_from_source_ids",[]):
            if parent not in S: errors.append(f"{sid}: derived_from_source_ids references missing source {parent}")
        if s.get("source_type")=="FieldPhotograph":
            if s.get("source_role")!="FIELD_OBSERVATION": errors.append(f"{sid}: FieldPhotograph source_role must be FIELD_OBSERVATION")
            for k in ("captured_at","photographer_or_observer","object_entity_id"):
                if not s.get(k): errors.append(f"{sid}: field photograph missing {k}")
            if s.get("object_entity_id") not in E: errors.append(f"{sid}: field photograph references missing object entity")

    by={}
    for ev in evidence:
        eid=ev.get("assertion_evidence_id","<missing>"); aid=ev.get("assertion_id"); sid=ev.get("source_id")
        if aid not in A: errors.append(f"{eid}: references missing assertion {aid}")
        if sid not in S: errors.append(f"{eid}: references missing source {sid}")
        if ev.get("evidence_role") not in ROLES: errors.append(f"{eid}: invalid evidence_role")
        if ev.get("authority_fit") not in FIT: errors.append(f"{eid}: invalid authority_fit")
        if ev.get("proximity") not in PROX: errors.append(f"{eid}: invalid proximity")
        if ev.get("dependency_status") not in DEPENDENCY: errors.append(f"{eid}: invalid dependency_status")
        if sid in S and ev.get("source_language")!=S[sid].get("language"): errors.append(f"{eid}: source_language disagrees with {sid}")
        if sid in S and S[sid].get("source_type")=="FieldPhotograph":
            if ev.get("evidence_role")!="FIELD_VERIFICATION": errors.append(f"{eid}: field photograph must use FIELD_VERIFICATION")
            if ev.get("proximity")!="FIELD_OBSERVATION": errors.append(f"{eid}: field photograph proximity must be FIELD_OBSERVATION")
            if ev.get("observation_scope") not in OBSERVATION_SCOPE: errors.append(f"{eid}: field photograph requires valid observation_scope")
            if ev.get("dependency_status")!="INDEPENDENT": errors.append(f"{eid}: field photograph dependency_status must be INDEPENDENT for the observation itself")
        by.setdefault(aid,[]).append(ev)

    counts={}
    for aid,a in A.items():
        pred=a.get("predicate"); obj=a.get("object_entity_id"); lit="literal_value" in a
        if a.get("subject_id") not in E: errors.append(f"{aid}: missing subject entity")
        if not pred: errors.append(f"{aid}: missing predicate")
        if pred not in rules: errors.append(f"{aid}: no predicate rule for {pred}")
        if "status" in a or "computed_status" in a or "editorial_status" in a:
            errors.append(f"{aid}: canonical assertion may not store a confidence/status label")
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
    print(f"VALIDATION PASSED: {len(E)} entities, {len(A)} assertions, {len(evidence)} evidence links, {len(S)} sources")
    print("Epistemic rule: source credibility is claim-specific; UNKNOWN dependency never counts as independent corroboration.")
    print("Photography rule: field photographs directly establish only recorded observable facts and cannot independently verify historical provenance.")
    print("Computed status counts: "+", ".join(f"{k}={v}" for k,v in sorted(counts.items())))
    return 0

if __name__=="__main__": sys.exit(main())