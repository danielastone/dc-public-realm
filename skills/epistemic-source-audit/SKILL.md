---
name: epistemic-source-audit
description: Audit an archival, government, museum, newspaper, photographic, or scholarly source before it enters the provenance knowledge base. Use to extract atomic propositions, distinguish source from evidence, trace inheritance, assess authority fit and independence, preserve conflicts, and determine the source's possible epistemic consequence without prematurely changing canonical data.
---

# Epistemic source audit

Read `../epistemic-core/SKILL.md` first. This skill produces a review object, not canonical mutations.

## Pass 1 — Source forensics
Record: source ID candidate; creator/publisher; document type; date; repository; archival/catalog identifier; retrieval date; stable URL or access route; original/reproduction/transcription status; contemporaneous/retrospective relationship; known upstream sources; restrictions; exact pages/locators used.

Do not call a finding aid, catalog description, search result, later transcription, or repository webpage the underlying historical record unless it actually is that record.

## Pass 2 — Atomic proposition extraction
Extract only propositions actually expressed or directly observable. For each candidate record:
- subject;
- predicate candidate;
- object/value;
- temporal scope;
- exact locator;
- original wording when ambiguity matters;
- evidence mode: DOCUMENT_TEXT, IMAGE_OBSERVATION, CATALOG_ASSERTION, INSCRIPTION_OBSERVATION, or ANALYTICAL_INFERENCE.

Split conjunctions. Separate authorship, model lineage, fabrication, casting, shipment, donation, legal acceptance, installation, custody and present location unless the predicate rules explicitly combine them.

## Pass 3 — Schema-fit gate
Classify every proposition as exactly one:
- EXACT_FIT;
- FIT_WITH_QUALIFIER;
- NEW_PREDICATE_CANDIDATE;
- NEW_ENTITY_TYPE_CANDIDATE;
- PROVENANCE_RELATION_REQUIRED;
- NOT_MODELABLE_YET.

If any proposition requiring ingestion is not EXACT_FIT or FIT_WITH_QUALIFIER, stop that proposition's ingestion and invoke `adaptive-knowledge-schema`. Never coerce it into the nearest predicate.

## Pass 4 — Evidence genealogy
For each proposition independently classify claim origin/dependency as:
- ORIGINAL_TO_SOURCE;
- EXPLICITLY_DERIVED;
- PROBABLY_DERIVED;
- INDEPENDENT;
- UNKNOWN.

Record upstream source/claim when known and explain the basis. Institutional independence is not claim independence. Two publications repeating one government release are one lineage for that proposition.

Assess authority fit at proposition level. A statute is direct for enactment/acceptance but not automatically direct for art-historical authorship. A museum inventory can be direct for accession metadata but derivative for nineteenth-century fabrication.

## Pass 5 — Epistemic consequence
Only after Passes 1–4 classify each proposition's possible effect:
- CREATE_ASSERTION_CANDIDATE;
- SUPPORT_EXISTING;
- CONTRADICT_EXISTING;
- QUALIFY_EXISTING;
- REPLACE_OR_MOVE_SOURCE_ROOT;
- REVEAL_SHARED_LINEAGE;
- NO_KNOWLEDGE_CHANGE;
- RESEARCH_LEAD_ONLY.

Do not assign VERIFIED/SUPPORTED manually. Status remains computed from accepted evidence under predicate rules.

## Required review output
Produce a structured review containing:
1. `source_forensics`;
2. `propositions`;
3. `schema_fit`;
4. `inheritance`;
5. `evidence_candidates`;
6. `conflicts`;
7. `unresolved_questions`;
8. `recommended_actions`.

Every recommended write must identify the assertion/proposition affected and the exact evidence permitting the change.

## Stop conditions
Stop rather than ingest when:
- exact-object identity is unresolved and material;
- a source locator cannot be established;
- only metadata for an unseen underlying record has been retrieved;
- a source's derivation is material to status but cannot yet be classified;
- contradictory names/dates would have to be normalized to fit the database;
- the schema cannot preserve a role or relationship expressed by the source.

## Negative and null results
A bounded archive search can be recorded with repository, collection, search terms, date range, retrieval date and result. It does not create counter-evidence unless the archive itself establishes that the expected record could not or did not exist.
