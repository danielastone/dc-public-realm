#!/usr/bin/env python3
"""Validate provenance-linked semantic data for the diplomatic-gifts alpha."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

ALLOWED_STATUS = {"VERIFIED", "PARTIALLY_VERIFIED", "CONTESTED", "UNRESOLVED", "FIELD_OBSERVED"}
SUPPORT_ROLES = {"PRIMARY_SUPPORT", "FIELD_VERIFICATION"}
ALLOWED_EVIDENCE_ROLES = SUPPORT_ROLES | {"CORROBORATION", "CONTRADICTS", "QUALIFIES"}


def load(name: str, key: str):
    path = DATA / name
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    if payload.get("schema_version") != "0.3":
        raise ValueError(f"{name}: schema_version must be 0.3")
    rows = payload.get(key)
    if not isinstance(rows, list):
        raise ValueError(f"{name}: {key} must be a list")
    return rows


def unique_index(rows, key, label, errors):
    out = {}
    for i, row in enumerate(rows, start=1):
        value = row.get(key)
        if not value:
            errors.append(f"{label}[{i}]: missing {key}")
            continue
        if value in out:
            errors.append(f"{label}: duplicate {key} {value}")
        out[value] = row
    return out


def main() -> int:
    errors = []
    try:
        entities = load("entities.json", "entities")
        assertions = load("assertions.json", "assertions")
        evidence = load("assertion-evidence.json", "assertion_evidence")
        sources = load("sources.json", "sources")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"VALIDATION FAILED\n- {exc}")
        return 1

    entity_by_id = unique_index(entities, "entity_id", "entities", errors)
    assertion_by_id = unique_index(assertions, "assertion_id", "assertions", errors)
    source_by_id = unique_index(sources, "source_id", "sources", errors)
    unique_index(evidence, "assertion_evidence_id", "assertion_evidence", errors)

    for eid, entity in entity_by_id.items():
        if not entity.get("entity_type") or not entity.get("canonical_name"):
            errors.append(f"{eid}: entity_type and canonical_name are required")

    for sid, source in source_by_id.items():
        if not source.get("language"):
            errors.append(f"{sid}: missing source language")
        if not source.get("title") or not source.get("publisher_or_creator"):
            errors.append(f"{sid}: title and publisher_or_creator are required")

    evidence_by_assertion = {}
    for ev in evidence:
        evid = ev.get("assertion_evidence_id", "<missing evidence id>")
        aid = ev.get("assertion_id")
        sid = ev.get("source_id")
        role = ev.get("evidence_role")
        if aid not in assertion_by_id:
            errors.append(f"{evid}: references missing assertion {aid}")
        if sid not in source_by_id:
            errors.append(f"{evid}: references missing source {sid}")
        if role not in ALLOWED_EVIDENCE_ROLES:
            errors.append(f"{evid}: invalid evidence_role {role}")
        if not ev.get("source_language"):
            errors.append(f"{evid}: missing source_language")
        elif sid in source_by_id and ev["source_language"] != source_by_id[sid].get("language"):
            errors.append(f"{evid}: source_language disagrees with {sid}")
        evidence_by_assertion.setdefault(aid, []).append(ev)

    for aid, assertion in assertion_by_id.items():
        subject = assertion.get("subject_id")
        obj = assertion.get("object_entity_id")
        literal = assertion.get("literal_value")
        status = assertion.get("status")
        predicate = assertion.get("predicate")

        if subject not in entity_by_id:
            errors.append(f"{aid}: references missing subject entity {subject}")
        if not predicate:
            errors.append(f"{aid}: missing predicate")
        if status not in ALLOWED_STATUS:
            errors.append(f"{aid}: invalid status {status}")
        if obj and obj not in entity_by_id:
            errors.append(f"{aid}: references missing object entity {obj}")
        if obj and literal is not None:
            errors.append(f"{aid}: cannot have both object_entity_id and literal_value")
        if status != "UNRESOLVED" and not obj and literal is None:
            errors.append(f"{aid}: resolved assertion requires object_entity_id or literal_value")
        if status == "UNRESOLVED" and (obj or literal is not None):
            errors.append(f"{aid}: UNRESOLVED assertion must not assert a resolved value")

        evs = evidence_by_assertion.get(aid, [])
        if not evs:
            errors.append(f"{aid}: has no provenance evidence")
        if status in {"VERIFIED", "FIELD_OBSERVED"} and not any(e.get("evidence_role") in SUPPORT_ROLES for e in evs):
            errors.append(f"{aid}: {status} assertion lacks PRIMARY_SUPPORT/FIELD_VERIFICATION")

    # Every evidence row should point to a live assertion; this also catches stale joins.
    stale = sorted(set(evidence_by_assertion) - set(assertion_by_id))
    for aid in stale:
        errors.append(f"assertion_evidence: stale assertion reference {aid}")

    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s)")
        for err in errors:
            print(f"- {err}")
        return 1

    print(
        "VALIDATION PASSED: "
        f"{len(entity_by_id)} entities, {len(assertion_by_id)} assertions, "
        f"{len(evidence)} evidence links, {len(source_by_id)} sources"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
