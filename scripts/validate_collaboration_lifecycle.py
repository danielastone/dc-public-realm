#!/usr/bin/env python3
"""Validate task -> submission -> review -> transaction provenance without publishing fixtures."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TX = ROOT / "transactions"
ALLOWED = {"OPEN", "SUBMITTED", "REVIEWED", "INCORPORATED", "REJECTED", "CLOSED_NO_CHANGE"}
TRANSITIONS = {
    "OPEN": {"SUBMITTED", "CLOSED_NO_CHANGE"},
    "SUBMITTED": {"REVIEWED", "REJECTED", "CLOSED_NO_CHANGE"},
    "REVIEWED": {"INCORPORATED", "REJECTED", "CLOSED_NO_CHANGE"},
    "INCORPORATED": set(), "REJECTED": set(), "CLOSED_NO_CHANGE": set(),
}

def load(path): return json.loads(path.read_text(encoding="utf-8"))

def validate(root=ROOT, fixture=None):
    errors=[]
    if fixture:
        base=load(fixture / "research-tasks.json")
        tx_paths=sorted((fixture / "transactions").glob("*.json"))
        review_root=fixture
    else:
        base=load(DATA / "research-tasks.json")
        tx_paths=sorted(TX.glob("*.json"))
        review_root=ROOT
    tasks={t["task_id"]: t for t in base["tasks"]}
    state={tid:t.get("status") for tid,t in tasks.items()}
    incorporated_by={}
    for tid,s in state.items():
        if s not in ALLOWED: errors.append(f"{tid}: invalid status {s!r}")
    for p in tx_paths:
        tx=load(p); resolves=tx.get("resolves")
        task_updates=[]
        for op in tx.get("operations",[]):
            if op.get("table")=="research_tasks" and op.get("action")=="update":
                task_updates.append(op)
        if resolves:
            required=("task_id","submission_ref","contributor","review_record")
            for k in required:
                if not resolves.get(k): errors.append(f"{p.name}: resolves.{k} is required")
            tid=resolves.get("task_id")
            if tid not in tasks:
                errors.append(f"{p.name}: resolves unknown task {tid}")
            rr=resolves.get("review_record")
            if rr and not (review_root / rr).is_file(): errors.append(f"{p.name}: missing review record {rr}")
            if tid and not any(op.get("id")==tid for op in task_updates):
                errors.append(f"{p.name}: resolves {tid} but does not update that research task")
        for op in task_updates:
            tid=op.get("id"); new=op.get("value",{}).get("status")
            if tid not in state:
                errors.append(f"{p.name}: updates unknown task {tid}"); continue
            old=state[tid]
            if new not in ALLOWED: errors.append(f"{p.name}: {tid} invalid status {new!r}")
            elif new not in TRANSITIONS.get(old,set()): errors.append(f"{p.name}: illegal transition {tid} {old} -> {new}")
            if new=="INCORPORATED":
                if not resolves or resolves.get("task_id")!=tid:
                    errors.append(f"{p.name}: INCORPORATED {tid} requires matching resolves metadata")
                else: incorporated_by[tid]=tx.get("transaction_id")
            state[tid]=new
    for tid,s in state.items():
        if s=="INCORPORATED" and tid not in incorporated_by and tasks[tid].get("status")!="INCORPORATED":
            errors.append(f"{tid}: incorporated without a resolving transaction")
    return errors

def main():
    errors=validate()
    fixture_root=ROOT/"tests"/"fixtures"/"collaboration-lifecycle"
    valid=fixture_root/"valid"
    invalid=fixture_root/"invalid-missing-review"
    if valid.exists(): errors += ["valid fixture: "+e for e in validate(fixture=valid)]
    if invalid.exists():
        bad=validate(fixture=invalid)
        if not any("missing review record" in e for e in bad): errors.append("invalid fixture did not fail for missing review record")
    if errors:
        print(f"COLLABORATION LIFECYCLE VALIDATION FAILED: {len(errors)} error(s)")
        for e in errors: print("- "+e)
        return 1
    print(f"COLLABORATION LIFECYCLE VALIDATION PASSED: {len(load(DATA/'research-tasks.json')['tasks'])} canonical tasks; synthetic positive/negative gates passed.")
    return 0
if __name__=="__main__": raise SystemExit(main())
