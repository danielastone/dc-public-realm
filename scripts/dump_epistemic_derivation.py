#!/usr/bin/env python3
"""Read-only parity adapter for frozen EPI-002/EPI-004/EPI-005 derivation.

Test infrastructure only. It imports the frozen Python derivation functions
unchanged and serializes their results to the schema frozen in
docs/audits/epistemic-derivation-parity.md.

Representation normalization only: tuple -> two-element array, code-point key
ordering, stable-ID ordering of top-level collections, validation message ->
structural condition, deterministic JSON. Branch order, path order and
per-assertion conflict-row order pass through untouched.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from derive_dependency_state import derive
from trace_claim_lineage import trace_all
from detect_material_conflicts import conflict_index, validate_conflict_records

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("KNOWLEDGE_DATA_DIR", ROOT / "build" / "data"))
FIXTURE = ROOT / "tests" / "fixtures" / "epistemic-derivation.json"

MISSING = re.compile(r"^conflict/evidence row missing assertion_evidence_id$")
DUPLICATE = re.compile(r"^(?P<eid>.+): duplicate assertion_evidence_id$")
INCOMPLETE = re.compile(r"^(?P<eid>.+): CONTRADICTS row missing (?P<field>assertion_id|source_id|locator|evidence_note)$")


def to_json_shape(value):
    """Representation only: tuples become lists; nothing is reordered."""
    if isinstance(value, tuple):
        return [to_json_shape(v) for v in value]
    if isinstance(value, list):
        return [to_json_shape(v) for v in value]
    if isinstance(value, dict):
        return {k: to_json_shape(v) for k, v in value.items()}
    return value


def normalize_validation(messages):
    out = []
    for msg in messages:
        if MISSING.match(msg):
            out.append({"evidence_id": None, "condition": "MISSING_ASSERTION_EVIDENCE_ID"})
        elif (m := DUPLICATE.match(msg)):
            out.append({"evidence_id": m["eid"], "condition": "DUPLICATE_ASSERTION_EVIDENCE_ID"})
        elif (m := INCOMPLETE.match(msg)):
            out.append({"evidence_id": m["eid"], "condition": "INCOMPLETE_CONTRADICTS", "field": m["field"]})
        else:
            raise SystemExit(f"adapter: unrecognized validation message (frozen Python changed?): {msg!r}")
    return out


def dependency_results(rows):
    res = [{"evidence_id": r["assertion_evidence_id"], "state": derive(r)} for r in rows]
    return sorted(res, key=lambda x: x["evidence_id"])


def lineage_results(rows):
    traces = trace_all(rows)
    return [{"evidence_id": eid, "trace": to_json_shape(traces[eid])} for eid in sorted(traces)]


def conflict_block(rows, validation_only):
    validation = normalize_validation(validate_conflict_records(rows))
    if validation_only:
        return {"validation_only": True, "validation": validation}
    idx = conflict_index(rows)
    return {
        "validation_only": False,
        "index": {aid: to_json_shape(idx[aid]) for aid in sorted(idx)},
        "validation": validation,
    }


def main():
    real = json.loads((DATA / "assertion-evidence.json").read_text(encoding="utf-8"))["assertion_evidence"]
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]

    real_validation = normalize_validation(validate_conflict_records(real))
    real_idx = conflict_index(real) if not real_validation else {}

    dep_cases, lin_cases, conf_cases = [], [], []
    for case in sorted(cases, key=lambda c: c["case_id"]):
        kind, vo = case["kind"], case.get("validation_only", False)
        if kind == "conflict":
            conf_cases.append({"case_id": case["case_id"], **conflict_block(case["rows"], vo)})
        elif vo:
            raise SystemExit(f"adapter: validation_only case {case['case_id']} has kind {kind}")
        elif kind == "dependency":
            dep_cases.append({"case_id": case["case_id"], "results": dependency_results(case["rows"])})
        elif kind == "lineage":
            ids = [r.get("assertion_evidence_id") for r in case["rows"]]
            if not all(ids) or len(ids) != len(set(ids)):
                raise SystemExit(f"adapter: lineage case {case['case_id']} needs present, unique evidence IDs")
            lin_cases.append({"case_id": case["case_id"], "results": lineage_results(case["rows"])})
        else:
            raise SystemExit(f"adapter: unknown case kind {kind!r}")

    payload = {
        "dependency": {"real": dependency_results(real), "cases": dep_cases},
        "lineage": {"real": lineage_results(real), "cases": lin_cases},
        "conflicts": {
            "real": {"index": {aid: to_json_shape(real_idx[aid]) for aid in sorted(real_idx)}, "validation": real_validation},
            "cases": conf_cases,
        },
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
