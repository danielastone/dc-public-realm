---
name: epistemic-core
description: Shared epistemic contract for provenance research. Use whenever extracting claims, evaluating evidence, changing the ontology, creating research tasks, or writing provenance transactions.
---

# Epistemic core

## Objective
Represent no proposition more strongly or more specifically than the surviving evidence permits. Optimize for fidelity, not completeness, source count, or VERIFIED count.

## Required distinctions
Keep these separate throughout the workflow:
- source vs evidence edge;
- source authority vs authority fit for a proposition;
- publisher/source family vs claim-level independence;
- direct observation vs catalog metadata vs inference;
- contradiction vs uncertainty;
- archival gap vs negative evidence;
- research completion vs evidentiary effect;
- historical proposition vs constitutive/legal proposition;
- exact physical object vs type/copy/model relationship.

## Invariants
1. No evidence means no evidentiary status increase.
2. Publisher identity never establishes independence by itself.
3. Independence is evaluated at the proposition/evidence-edge level.
4. Contradictory evidence is preserved; never silently normalize it.
5. Metadata is evidence only for what the metadata record states, not automatically for what an image depicts.
6. A bounded unsuccessful archive search is a research result, not proof that a historical proposition is false.
7. If a proposition cannot be represented without information loss, stop ingestion and invoke adaptive schema review.
8. Collaboration-task completion never changes an assertion until evidence review and a transaction occur.
9. Every canonical state change must be reconstructable from an auditable transaction or schema migration.
10. Only a validated current PR head may be merged.
11. A source can be primary for one proposition and weak or derivative for another.
12. A later source may be useful while receiving zero independent-lineage credit.

## Universal stop conditions
Stop and diagnose rather than accommodating the data when:
- a proposition does not fit the schema;
- exact-object identity is uncertain and matters to the claim;
- source genealogy is unresolved and independence affects status;
- authoritative sources conflict;
- a transaction requires inventing an enum merely to pass validation;
- an ID collision or stale precondition occurs;
- a status change cannot be explained by explicit evidence changes;
- only catalog/finding-aid metadata has been retrieved, not the underlying cited record;
- collaborator material has not completed provenance review.

## Required audit question
Before every write ask: "What, exactly, would become more knowable after this change, and which evidence permits that change?"

If that question cannot be answered at assertion level, do not write canonical knowledge state.
