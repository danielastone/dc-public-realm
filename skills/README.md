# Provenance research skill stack

This directory turns lessons from the diplomatic-art provenance project into reusable controls. Skills are modular but share `epistemic-core` and one ingestion/write pipeline.

## Governing pipeline

`source -> forensic audit -> atomic propositions -> schema-fit gate -> evidence genealogy -> epistemic decision -> transaction/migration -> GitHub validation -> merge -> recomputed knowledge state -> research priorities`

Historical images and collaborator submissions enter this pipeline; neither bypasses it.

## Build order

### Sprint 1 — Control plane
1. `epistemic-core` — shared invariants and stop conditions.
2. `github-research-change-control` — deterministic branch/write/CI/PR/merge workflow.
3. Regression fixtures for Artigas, San Martin and the Cuban Friendship Urn.

### Sprint 2 — Reasoning plane
4. `epistemic-source-audit` — source forensics, atomic propositions, genealogy and evidence consequences.
5. `adaptive-knowledge-schema` — lossy-mapping detection, ontology extensions and migration impact analysis.

### Sprint 3 — Mutation plane
6. `provenance-transaction-builder` — approved decisions to auditable state transitions.
7. Schema migrations and epistemic-delta reports.

### Sprint 4 — Acquisition plane
8. `historical-image-evidence` — separate pixel observation, catalog assertion and interpretation.
9. `archive-collaboration-planner` — epistemic defects to bounded external research tasks.
10. Epistemic-leverage prioritization.

## Required regression fixtures

### Artigas
Preserve San Jose/Montevideo conflict, exact-object distinction, Smithsonian source-root uncertainty, commission vs fabrication, and model/authorship/casting distinctions.

### San Martin
Preserve Daumas/Dumont conflict, statutory wording without treating Congress as art-historical authority, Argentine source inheritance, and Revista Legado root retrieval.

### Cuban Friendship Urn
Preserve Republic-of-Cuba/citizens-of-Cuba donor formulations, legal acceptance vs financing/presentation, object inscription vs transcription witness, Maine-marble provenance, archival asymmetry, and absence-of-record discipline.

## Definition of done
Before resuming large-scale source ingestion, the integrated stack must be able to receive an unfamiliar archival source and correctly choose among:
- ingest;
- preserve contradiction;
- trace upstream source;
- request schema adaptation;
- create a new assertion;
- leave the graph unchanged;
- stop because the evidence cannot yet be represented honestly.

An approved change must then pass transaction/migration generation, epistemic validation, site/build validation, PR validation on the current head, and a protected merge without bypassing concurrency or safety controls.
