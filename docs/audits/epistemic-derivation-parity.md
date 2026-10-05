# Epistemic derivation parity schema

Scope: data-level JS↔Python parity for EPI-002 dependency derivation, EPI-004 claim lineage, and EPI-005 material-conflict derivation. This unit does not compare rendered HTML or publication labels.

## Shared fixture

Both producers read `tests/fixtures/epistemic-derivation.json`.

- Provenance is case metadata only: `case_id`, `origin`, and `origin_case`.
- Evidence rows contain only derivation inputs.
- Cases copied from frozen validators keep their original semantic inputs; `origin: "parity-extension"` identifies coverage added specifically for cross-language parity.
- Cases with `validation_only: true` are excluded from dependency and lineage derivation. This is required because missing IDs can raise before lineage output exists and duplicate IDs can collapse in Python's `trace_all()`.
- Validation-only conflict cases emit `validation` only. They do not emit or compute `index`: Python `build_context()` validates first and aborts on invalid rows, so `conflict_index()` is not reached for those inputs.
- Every lineage case must contain present, unique `assertion_evidence_id` values.
- Required branch-order extension cases are `lin-multi-parent-order` and `lin-multi-candidate-order`; both must remain present.
- Each synthetic case feeds only the output section matching its `kind`: `dependency` → `dependency`, `lineage` → `lineage`, and `conflict` → `conflicts`. Validation-only cases remain confined to `conflicts`.

DATA-001 synthetic reconciliation is intentionally not copied here because it tests rendered assertion reconciliation, not any of the three derivation outputs frozen for 64b.

## Canonical adapter output

Each producer emits the same logical JSON document:

```
{
  "dependency": {
    "real": [{"evidence_id": "...", "state": "..."}],
    "cases": [{"case_id": "...", "results": [{"evidence_id": "...", "state": "..."}]}]
  },
  "lineage": {
    "real": [{"evidence_id": "...", "trace": <trace>}],
    "cases": [{"case_id": "...", "results": [{"evidence_id": "...", "trace": <trace>}]}]
  },
  "conflicts": {
    "real": {
      "index": {"ASSERTION-ID": [<evidence row>, ...]},
      "validation": [<validation condition>, ...]
    },
    "cases": [
      {
        "case_id": "...",
        "validation_only": false,
        "index": {"ASSERTION-ID": [<evidence row>, ...]},
        "validation": []
      },
      {
        "case_id": "...",
        "validation_only": true,
        "validation": [<validation condition>, ...]
      }
    ]
  }
}
```

No coverage counters, dependency-rule labels, source metadata indexes, renderer text, or HTML appear in adapter output.

## Ordering contract

Ordering that affects Python behavior is contractual.

- Object/map keys are serialized in Unicode code-point order.
- Top-level `real` rows, case lists, and per-case `results` are sorted by stable ID using code-point order.
- Lineage `branches` preserve Python order. Python iterates `inherits_claim_from_source_ids` in recorded order and candidate rows in evidence-input order.
- `path` preserves traversal order.
- `inherits_claim_from_source_ids` remains in recorded order.
- Per-assertion conflict-row arrays preserve evidence-input order; only assertion keys are sorted.
- Do not use `localeCompare` or `Intl.Collator` in the JS implementation.

## Trace-node schema

Tuple-shaped Python keys/paths are represented as JSON two-element arrays: `[assertion_id, source_id]`.

Trace nodes are state-specific:

- Branch: `{"terminal": null, "node": [assertion_id, source_id], "branches": [...]}`. Branch nodes have no `path`.
- `ESTABLISHED_ROOT`: `{"terminal":"ESTABLISHED_ROOT","path":[...]}`.
- `CYCLE`: `{"terminal":"CYCLE","path":[...]}`.
- `BROKEN_REFERENCE`: terminal + `path` + `missing_source_id`.
- `UNRESOLVED_ANCESTRY`: terminal + `path` + `claim_origin` + `dependency_status`.

For unresolved nodes, Python uses `row.get(field, "UNKNOWN") or "UNKNOWN"`; missing, empty-string, or null values therefore serialize as `"UNKNOWN"`.

## Conflict validation schema

Python message text is not a parity requirement. Validation is normalized to structural conditions:

- Missing evidence ID: `{"evidence_id": null, "condition":"MISSING_ASSERTION_EVIDENCE_ID"}`.
- Duplicate evidence ID: `{"evidence_id":"...", "condition":"DUPLICATE_ASSERTION_EVIDENCE_ID"}`.
- Incomplete contradiction: `{"evidence_id":"...", "condition":"INCOMPLETE_CONTRADICTS", "field":"assertion_id"|"source_id"|"locator"|"evidence_note"}`.

Validation condition order follows Python's validation traversal order. A nonempty validation result is the semantic condition that later causes `build_context()` to abort; exact `SystemExit` wording is outside parity. Because validation precedes conflict indexing, validation-only cases stop at this normalized validation result and have no `index` member.

## Coverage is harness-derived

Neither adapter emits coverage. The parity harness independently walks both outputs and must require nonzero coverage for:

- `ESTABLISHED_ROOT`
- `UNRESOLVED_ANCESTRY`
- `BROKEN_REFERENCE`
- `CYCLE`
- traces containing at least one node with two or more branches

`lin-multi-parent-order` and `lin-multi-candidate-order` must both be present; structural multi-branch counting does not distinguish how branches were produced.

A zero count for any required terminal or multi-branch coverage target fails the parity run.
