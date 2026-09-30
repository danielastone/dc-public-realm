#!/usr/bin/env python3
"""Trace claim ancestry without inventing roots.

The graph is claim-level: assertion-evidence rows point from a source carrying a
claim to any upstream source IDs recorded in inherits_claim_from_source_ids.
Terminal states are explicit so UNKNOWN never becomes a root by omission.
"""
from __future__ import annotations
from collections import defaultdict

ROOT = "ESTABLISHED_ROOT"
UNRESOLVED = "UNRESOLVED_ANCESTRY"
BROKEN = "BROKEN_REFERENCE"
CYCLE = "CYCLE"


def build_index(rows):
    by_assertion_source = defaultdict(list)
    for row in rows:
        by_assertion_source[(row["assertion_id"], row["source_id"])].append(row)
    return by_assertion_source


def _is_root(row):
    """Root requires affirmative canonical evidence, not absence of a parent."""
    return (
        row.get("dependency_status") == "INDEPENDENT"
        and row.get("claim_origin") in {"ORIGINAL_TO_SOURCE", "INDEPENDENT_CLAIM_ROOT"}
        and not (row.get("inherits_claim_from_source_ids") or [])
    )


def trace_row(row, index, stack=()):
    key = (row["assertion_id"], row["source_id"])
    if key in stack:
        return {"terminal": CYCLE, "path": [*stack, key]}
    parents = row.get("inherits_claim_from_source_ids") or []
    if parents:
        branches = []
        next_stack = (*stack, key)
        for parent_source_id in parents:
            candidates = index.get((row["assertion_id"], parent_source_id), [])
            if not candidates:
                branches.append({
                    "terminal": BROKEN,
                    "path": [*next_stack, (row["assertion_id"], parent_source_id)],
                    "missing_source_id": parent_source_id,
                })
                continue
            # Multiple rows for the same assertion/source are preserved as branches;
            # ambiguity must not be silently collapsed.
            branches.extend(trace_row(parent, index, next_stack) for parent in candidates)
        return {"terminal": None, "node": key, "branches": branches}
    if _is_root(row):
        return {"terminal": ROOT, "path": [*stack, key]}
    return {
        "terminal": UNRESOLVED,
        "path": [*stack, key],
        "claim_origin": row.get("claim_origin", "UNKNOWN") or "UNKNOWN",
        "dependency_status": row.get("dependency_status", "UNKNOWN") or "UNKNOWN",
    }


def trace_all(rows):
    index = build_index(rows)
    return {row["assertion_evidence_id"]: trace_row(row, index) for row in rows}
