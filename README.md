# Diplomatic Gifts in Washington

A provenance-linked semantic publication about foreign gift sculpture and commemorative objects in Washington, DC.

## Core proposition

The project's value is to make **semantic relationships explicit, attach provenance to each relationship, and preserve an auditable history of how the knowledge graph changes**.

A public object is represented as evidenced claims: gift/donor relationships, depicted people, creative and fabrication roles, legal and physical events, predecessor objects, and material provenance. Each relationship should answer what is asserted, what evidence supports it, where that evidence came from, whether the claim inherits from an earlier source, and what remains unresolved.

## Alpha scope

The alpha is deliberately limited to three objects:

1. **OBJ-0001 — José Gervasio Artigas Memorial** — Uruguay
2. **OBJ-0002 — José de San Martín Memorial** — Argentina
3. **OBJ-0003 — Cuban American Friendship Urn** — Cuba

No fourth object is added until the discovery/analytics experiment is running.

## Transaction-ledger architecture

The repository now separates **historical state**, **changes to knowledge**, **materialized database state**, and **publication**.

```text
frozen migration baseline (data/)
              +
append-only epistemic transactions (transactions/)
              ↓
scripts/build_database.py
              ↓
materialized database (build/data/)
              +
audit manifest (build/audit/manifest.json)
              ↓
semantic validation
              ↓
static-site generator
              ↓
public website
```

`data/` is the verified migration baseline at adoption of the transaction system. It is not rewritten to invent a retrospective audit history that does not exist. Git history remains the record for pre-ledger development.

All future substantive knowledge changes should be expressed as small JSON transactions in `transactions/`. Transactions are append-only after merge. Corrections are later transactions, not edits to history.

The builder records table hashes for the baseline, a database hash before and after every transaction, operation counts, and the final database hash. Update/delete operations can require the exact expected prior-record hash, causing stale or conflicting updates to fail closed.

See [`docs/transaction-architecture.md`](docs/transaction-architecture.md) and [`transactions/README.md`](transactions/README.md).

## Epistemic model

Credibility is claim-specific. Repository custody, document genealogy, and claim genealogy are separate concepts. A Library of Congress-hosted NPS/HALS record does not become an independent LOC knowledge lineage merely because LOC preserves it.

Independent corroboration is computed from **effective claim roots**. Different URLs, agencies, repositories, publications, or source-family labels do not establish independence when they inherit the same proposition.

See [`docs/source-inheritance.md`](docs/source-inheritance.md).

## Active repository structure

- `data/` — frozen migration baseline
- `transactions/` — append-only epistemic update ledger
- `scripts/build_database.py` — deterministic transaction materializer
- `scripts/validate_data.py` — semantic and provenance validator; can validate baseline or materialized state
- `scripts/build_site.py` — publication generator
- `build/data/` — disposable materialized database generated in CI
- `build/audit/manifest.json` — generated build/audit manifest
- `docs/` — architecture, evidence, collaboration, and archival methodology
- `research/` — research work products and retrieval analysis

Earlier public-realm experiments remain outside the active diplomatic-gifts alpha.

## Update contract

1. Research produces a bounded proposed knowledge change.
2. Encode it as one transaction with a plain-language `purpose` and `evidence_decision`.
3. Use record-hash preconditions for updates/deletes.
4. Materialize the database.
5. Validate the materialized graph and source inheritance.
6. Review the transaction together with its before/after effect.
7. Merge.
8. Never rewrite a merged transaction; correct it with a later transaction.

Adding a source does not automatically add an independent epistemic root. Computed assertion status remains derived from evidence rules, not stored as editorial opinion.

## Publication pipeline

GitHub Actions now builds the transaction database first, validates that materialized state, stages it for the existing static-site generator, and deploys the resulting site. The site therefore reflects **baseline + all accepted transactions**, not direct hand-edits made during publication.

## Alpha definition of done

Alpha is launched when the three objects and their material semantic relationships are publicly reachable at stable URLs, each published relationship is traceable to evidence and claim ancestry where known, collaboration tasks expose unresolved research, machine-readable representations preserve provenance/status, and the discovery/analytics experiment has a recorded baseline.
