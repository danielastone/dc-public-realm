---
name: adaptive-knowledge-schema
description: Evaluate and safely implement ontology/schema changes when new evidence cannot be represented without information loss. Use after an epistemic source audit reports a schema mismatch, before adding predicates, entity types, enums, provenance relationships, or changing evidence rules.
---

# Adaptive knowledge schema

Read `../epistemic-core/SKILL.md` and the source-audit review first.

## Principle
Schema inadequacy is a research finding. Adapt the ontology to meaningful evidence distinctions; never adapt evidence to an inadequate ontology merely to make validation pass.

## Gate 1 — Confirm mismatch
State the proposition in plain language and show exactly what information would be lost, conflated or falsely implied under the current schema.

If the current schema represents it faithfully, reject the migration request and use the existing model.

## Gate 2 — Test alternatives in order
1. EXISTING_REPRESENTATION — an existing predicate/entity already fits.
2. QUALIFIED_REPRESENTATION — existing predicate plus supported temporal/role qualifier is sufficient.
3. RELATIONSHIP_COMPOSITION — multiple existing atomic predicates preserve the distinction.
4. SCHEMA_EXTENSION — a genuinely new reusable distinction is required.

Choose the earliest adequate option. Convenience is not a reason for extension.

## Gate 3 — Reusability/materiality test
A schema extension must satisfy at least one:
- prevents a materially misleading assertion;
- represents a conceptually important distinction;
- is likely to recur;
- is necessary for source genealogy or evidence independence;
- separates propositions with different epistemic rules.

Do not create a predicate because one source uses unusual wording.

## Gate 4 — Impact analysis
Before changing schema enumerate:
- overlapping predicates/entity types;
- affected assertions;
- affected evidence edges;
- affected predicate/status rules;
- affected research tasks;
- validators and JSON schemas;
- site/API/JSON-LD output;
- transaction builder behavior;
- regression fixtures;
- backward compatibility and migration needs.

No migration proceeds with unknown affected canonical assertions.

## Gate 5 — Migration design
Assign a migration ID and schema-version transition. Define deterministic before/after semantics and an explicit mapping for every affected record.

A migration record should include:
- migration_id;
- from_schema_version;
- to_schema_version;
- rationale;
- new/changed/deprecated concepts;
- affected record IDs;
- transformation rules;
- expected epistemic deltas;
- rollback/rebuild method;
- regression tests.

Never silently reinterpret old assertions under a new predicate meaning.

## Gate 6 — Validation
Require:
- structural validation;
- epistemic invariants;
- migration completeness/no orphan references;
- baseline + migrations + transactions deterministic rebuild;
- regression fixtures;
- site/output build.

If a migration changes computed statuses, report each status delta and its causal rule change. If status does not change but source roots, independence, or proposition specificity improve, report that epistemic delta too.

## Hard stops
Stop if:
- a new enum is proposed only to make one transaction validate;
- migration semantics cannot be stated deterministically;
- affected assertions are unknown;
- old and new predicate meanings overlap ambiguously;
- a role distinction such as modeled/cast/fabricated/authored would be collapsed;
- a migration would erase a preserved contradiction;
- rollback/rebuild cannot reproduce the prior state.
