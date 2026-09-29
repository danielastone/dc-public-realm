#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path
import validate_data as vd

ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.environ.get("KNOWLEDGE_DATA_DIR", str(ROOT/"data")))
MODES=Path(os.environ.get("CLAIM_MODE_FILE", str(ROOT/"data"/"claim-modes.json")))
ALLOWED={"DOCUMENTARY_FACT","ATTRIBUTION_RECONSTRUCTION","INTERPRETATION"}
PUBLIC={"DOCUMENTARY_FACT":"Historical record","ATTRIBUTION_RECONSTRUCTION":"Attribution","INTERPRETATION":"Interpretation"}

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    errors=[]
    payload=load_json(MODES)
    if payload.get("schema_version")!="0.1" or not isinstance(payload.get("claim_modes"),list):
        print("CLAIM MODE VALIDATION FAILED\n- claim-modes.json must use schema_version 0.1 and a claim_modes list")
        return 1
    assertions=load_json(DATA/"assertions.json")["assertions"]
    evidence=load_json(DATA/"assertion-evidence.json")["assertion_evidence"]
    sources=load_json(DATA/"sources.json")["sources"]
    rules=load_json(DATA/"predicate-rules.json")["predicate_rules"]
    A={x["assertion_id"]:x for x in assertions}; S={x["source_id"]:x for x in sources}
    by={}
    for e in evidence: by.setdefault(e.get("assertion_id"),[]).append(e)
    seen=set()
    counts={}
    for row in payload["claim_modes"]:
        aid=row.get("assertion_id"); mode=row.get("mode")
        if not aid or aid in seen: errors.append(f"duplicate or missing assertion_id {aid}"); continue
        seen.add(aid)
        if aid not in A: errors.append(f"{aid}: claim mode references missing assertion"); continue
        if mode not in ALLOWED: errors.append(f"{aid}: invalid claim mode {mode}"); continue
        if not row.get("rationale"): errors.append(f"{aid}: missing mode rationale")
        counts[mode]=counts.get(mode,0)+1
        if mode=="INTERPRETATION":
            attrs=row.get("attributed_to_source_ids",[])
            if not isinstance(attrs,list) or not attrs:
                errors.append(f"{aid}: INTERPRETATION requires attributed_to_source_ids")
            for sid in attrs:
                if sid not in S: errors.append(f"{aid}: interpretation attribution references missing source {sid}")
            pred=A[aid].get("predicate")
            if pred in rules:
                status,_=vd.compute(A[aid],by.get(aid,[]),rules[pred])
                if status=="VERIFIED":
                    errors.append(f"{aid}: INTERPRETATION may not publish as mechanically VERIFIED")
    if errors:
        print(f"CLAIM MODE VALIDATION FAILED: {len(errors)} error(s)")
        for e in errors: print(f"- {e}")
        return 1
    print(f"CLAIM MODE VALIDATION PASSED [{DATA}]: "+", ".join(f"{k}={v}" for k,v in sorted(counts.items())))
    print("Guardrail: interpretation requires named attribution and may not resolve to mechanically VERIFIED.")
    return 0

if __name__=="__main__": sys.exit(main())
