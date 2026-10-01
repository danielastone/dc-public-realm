#!/usr/bin/env python3
"""Canonical EPI-005 material-conflict detection.

Conflict is data-driven. A CONTRADICTS assertion-evidence relationship is a
material conflict marker. QUALIFIES, uncertainty, multiple sources, or wording
differences do not become conflicts by inference.
"""
from __future__ import annotations
from collections import defaultdict

CONFLICT_ROLE = "CONTRADICTS"


def conflict_index(rows):
    by_assertion = defaultdict(list)
    for row in rows:
        if row.get("evidence_role") == CONFLICT_ROLE:
            by_assertion[row["assertion_id"]].append(row)
    return dict(by_assertion)


def has_material_conflict(assertion_id, rows):
    return assertion_id in conflict_index(rows)


def validate_conflict_records(rows):
    """Return errors for conflict rows too incomplete to publish honestly."""
    errors = []
    seen = set()
    for row in rows:
        eid = row.get("assertion_evidence_id")
        if not eid:
            errors.append("conflict/evidence row missing assertion_evidence_id")
            continue
        if eid in seen:
            errors.append(f"{eid}: duplicate assertion_evidence_id")
        seen.add(eid)
        if row.get("evidence_role") != CONFLICT_ROLE:
            continue
        for field in ("assertion_id", "source_id", "locator", "evidence_note"):
            if not row.get(field):
                errors.append(f"{eid}: CONTRADICTS row missing {field}")
    return errors
