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
  "operations": []
}
```

Supported tables: `entities`, `sources`, `assertions`, `assertion_evidence`, `predicate_rules`, and `research_tasks`. Supported actions: `add`, `update`, and `delete`. Updates and deletes should include `before_sha256` as an optimistic-locking precondition.

## Collaboration resolution

A transaction that moves a collaboration task to `INCORPORATED` must include a `resolves` block:

```json
"resolves": {
  "task_id": "ARG-SM-001",
  "submission_ref": "https://github.com/.../issues/123",
  "contributor": "Contributor name or stable attribution",
  "review_record": "qualification/reviews/2026-10-02-arg-sm-001.md",
  "reviewed_at": "2026-10-02"
}
```

The transaction must update the same `research_tasks` record. The linked review record must exist. This makes the chain traversable from canonical change back to review, contributor submission, and original research request. Historical transactions that predate the collaboration lifecycle do not require `resolves`.

The authoritative task vocabulary is `OPEN`, `SUBMITTED`, `REVIEWED`, `INCORPORATED`, `REJECTED`, and `CLOSED_NO_CHANGE`. Legal forward transitions are enforced by `scripts/validate_collaboration_lifecycle.py`.

## Audit semantics

A Git commit answers **who changed the repository and when**. A transaction answers **what knowledge changed, why it changed, what prior state it expected, and what epistemic effect was intended**. These are not substitutes.

Every transaction should state an `evidence_decision` in plain language. Adding another document must not be described as adding independent corroboration unless source inheritance has actually been traced. Collaboration `resolves` metadata is copied into the semantic audit manifest.

## Maintenance

Transactions are immutable after merge. Correct an erroneous transaction with a later transaction; do not rewrite the historical transaction. `supersedes` creates an explicit linear audit chain when desired.

Generated `build/` files are disposable materializations. The durable record is the frozen baseline + ordered transactions + Git history.
