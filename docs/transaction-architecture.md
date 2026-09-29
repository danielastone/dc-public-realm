# Transaction-based knowledge-base architecture

## Objective

Make every epistemic update reproducible, reviewable, reversible by a later transaction, and easy to maintain without turning the project into an application database.

## Layers

1. **Migration baseline — `data/`**
   - Frozen snapshot of the knowledge base at transaction-ledger adoption.
   - Exists so the entire current alpha does not need to be rewritten as invented historical transactions.
   - Direct epistemic edits stop after adoption.

2. **Ledger — `transactions/`**
   - Append-only JSON transactions.
   - Each transaction states purpose, evidence decision, and atomic operations.
   - Update/delete operations can assert the exact expected prior record hash.

3. **Builder — `scripts/build_database.py`**
   - Loads the baseline.
   - Applies transactions deterministically in filename order.
   - Fails on duplicate IDs, missing targets, failed record-hash preconditions, or broken referential integrity.
   - Writes materialized state to `build/data/`.

4. **Audit output — `build/audit/manifest.json`**
   - Records hashes of each baseline table.
   - Records each applied transaction, operation count, database hash before and after.
   - Records final database hash.

5. **Publication**
   - The website should consume the materialized database, not authoring transactions directly.
   - Publication remains a projection of the evidence graph; the transaction ledger is the history of how that graph changed.

## Why baseline + transactions

Reconstructing all existing research as retrospective transactions would create false audit precision. We know the current records, but not a complete machine-readable sequence of every historical research decision that produced them. The honest migration is therefore:

`verified current snapshot -> BASELINE -> all future changes recorded as transactions`

Git history remains available for pre-ledger archaeology.

## Epistemic transaction principles

A transaction is not merely a CRUD event. It should distinguish:

- new document discovered;
- source identity corrected;
- claim added;
- claim wording changed;
- evidence edge added/removed;
- source inheritance traced;
- contradiction discovered;
- research gap opened/closed;
- status effect produced by the rules.

The transaction records the intended epistemic effect; computed status remains derived by the rules engine.

## Source inheritance

Source independence is never inferred from transaction count, URL count, repository count, or source family. Claim-specific effective roots remain the only basis for independent corroboration.

A transaction that adds a LOC-hosted NPS/HALS record, for example, may improve custody/retrievability while adding zero independent epistemic roots.

## Update workflow

1. Researcher identifies a proposed change.
2. Create one bounded transaction.
3. Include precondition hashes for changed/deleted records.
4. Run transaction build.
5. Run semantic validation against materialized output.
6. Compare before/after audit hashes and computed statuses.
7. Review the transaction and generated diff together.
8. Merge.
9. Never edit the merged transaction; correct it with another transaction.

## Maintenance rule

Prefer small transactions organized around one research decision. Do not create giant 'cleanup' transactions combining unrelated epistemic changes. Small transactions make blame, rollback-by-compensation, review, and later LLM evaluation substantially more reliable.
