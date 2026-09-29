---
name: provenance-transaction-builder
description: Convert approved epistemic reviews and schema decisions into auditable provenance-database transactions. Use only after source audit and schema-fit approval; never use it to decide historical truth or force evidence into the ontology.
---

# Provenance transaction builder

Read `../epistemic-core/SKILL.md`, `../epistemic-source-audit/SKILL.md`, `../adaptive-knowledge-schema/SKILL.md`, and `../github-research-change-control/SKILL.md` first.

## Boundary
This skill is a mutation compiler, not an epistemic judge. Input must identify approved propositions/evidence and any required schema migration. If approval or schema fit is unresolved, stop.

## Preflight
1. Materialize current state from baseline + ordered migrations/transactions.
2. Allocate IDs only after checking all current namespaces.
3. Capture before-state hashes for every updated/deleted record.
4. Identify all assertions whose status, source roots, independence, specificity, or conflicts could change.
5. State expected epistemic deltas before writing.

## Transaction requirements
Every transaction must contain a unique `transaction_id`, purpose, ordered operations, and explicit preconditions for updates/deletes. Operations must be atomic enough that a reviewer can identify what knowledge-state transition each performs.

Prefer add/update evidence edges and assertions over rewriting unrelated canonical records. Do not combine unrelated research findings merely to reduce transaction count.

## Epistemic delta manifest
For every affected assertion record:
- assertion_id;
- before computed status;
- after computed status;
- before source roots/independence where relevant;
- after source roots/independence;
- change type;
- causal operations/evidence;
- explanation.

Report meaningful changes even when status is unchanged. Replacing a late derivative root with a contemporary primary root is an epistemic improvement even if both states compute SUPPORTED.

## Determinism
A clean rebuild from frozen baseline + ordered schema migrations + ordered transactions must reproduce the same semantic database hash. Build timestamps are metadata and must not be used as semantic hash inputs.

## Hard stops
Stop on ID collision, stale precondition, unresolved schema mismatch, unexplained status delta, missing referenced record, migration-version mismatch, or non-deterministic rebuild. Never bypass these by editing canonical data directly.

## GitHub handoff
Write on an isolated branch, run all semantic/fixture/materialization gates, validate the current PR head, then merge using the minimal safe connector payload with `expected_head_sha`. Omit optional merge fields unless required.
