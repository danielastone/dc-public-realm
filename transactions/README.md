# Transaction ledger

This directory is the append-only authoring interface for changes to the diplomatic-gifts knowledge base.

## Rule

Do not directly edit canonical historical state to add, revise, or remove a source, assertion, evidence edge, entity, predicate rule, or research task. Express the change as a transaction and rebuild the materialized database.

The pre-transaction `data/` directory is the frozen migration baseline. `scripts/build_database.py` applies transaction files in lexical order and writes a derived database to `build/data/` plus an audit manifest to `build/audit/manifest.json`.

## Transaction shape

```json
{
  "transaction_id": "TX-20260929-001",
  "recorded_at": "2026-09-29",
  "actor": "research",
  "purpose": "Add a newly reviewed primary source",
  "evidence_decision": "Adds documentary evidence; does not establish independent corroboration until claim ancestry is traced.",
  "supersedes": null,
  "operations": [
    {
      "table": "sources",
      "action": "add",
      "id": "SRC-EXAMPLE-001",
      "value": {"source_id": "SRC-EXAMPLE-001"}
    }
  ]
}
```

Supported tables: `entities`, `sources`, `assertions`, `assertion_evidence`, `predicate_rules`, and `research_tasks`.

Supported actions: `add`, `update`, and `delete`. Updates and deletes should include `before_sha256`, the canonical SHA-256 of the record before mutation. This is an optimistic-locking precondition: a transaction fails instead of silently overwriting an unexpected prior state.

## Audit semantics

A Git commit answers **who changed the repository and when**. A transaction answers **what knowledge changed, why it changed, what prior state it expected, and what epistemic effect was intended**. These are not substitutes.

Every transaction should state an `evidence_decision` in plain language. Adding another document must not be described as adding independent corroboration unless source inheritance has actually been traced.

## Maintenance

Transactions are immutable after merge. Correct an erroneous transaction with a later transaction; do not rewrite the historical transaction. `supersedes` creates an explicit linear audit chain when desired.

Generated `build/` files are disposable materializations. The durable record is the frozen baseline + ordered transactions + Git history.
