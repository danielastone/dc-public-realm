# Schema migration ledger

Schema/ontology changes are versioned research changes, not ad-hoc validator edits.

Each migration file must define:
- `migration_id`
- `from_schema_version`
- `to_schema_version`
- `purpose`
- `rationale`
- `affected_record_ids`
- deterministic `operations`
- `expected_epistemic_deltas`
- `regression_fixtures`

Migrations run before ordinary evidence/data transactions. A migration may add or alter a representational concept only after adaptive-schema review. It must not erase a contradiction or silently reinterpret existing assertions.

The initial checked-in database is schema version `0.1`. The absence of migration JSON files means no post-baseline ontology migration has yet been approved.
