# Provenance-Linked Semantic Model — v0.3

## Design principle

The canonical unit is a **provenance-bearing assertion**, not an object-page record.

An assertion expresses a semantic relationship or literal claim and links that claim to evidence. Objects, people, governments, institutions, places, events, and predecessor works are entities referenced by assertions. Object pages are generated views over those assertions.

Conceptually:

`source evidence → assertion → semantic relationship → publication view`

Example:

`OBJ-0001 → GIFT_FROM → AG-0006 (People of Uruguay)`

is not publishable merely because the triple exists. The assertion must also identify its supporting source(s), source language, status, and where practical a locator or evidence note.

## 1. Entities

Every reusable subject or object receives a stable identifier.

Entity classes used during alpha:

- `PhysicalObject` — the three Washington objects and predecessor objects when needed
- `Person`
- `Government`
- `GovernmentAgency`
- `Organization`
- `PeopleNation` — wording such as “people of Uruguay” when the source makes that distinction material
- `Place`
- `Event`

Core fields:

- `entity_id`
- `entity_type`
- `canonical_name`
- `native_name`
- `language`
- `country`
- `external_identifiers` where useful
- `notes`

The three alpha physical objects retain `OBJ-0001`, `OBJ-0002`, and `OBJ-0003` as stable entity IDs.

## 2. Sources

Sources are first-class records rather than bibliography strings.

Core fields:

- `source_id`
- `title`
- `publisher_or_creator`
- `language`
- `source_type`
- `url_or_archive_reference`
- `publication_date`
- `accessed_or_reviewed_date`
- `authority_scope`
- `notes`

`authority_scope` describes what the source is particularly competent to establish. Authority is claim-specific: congressional evidence may establish legal acceptance; donor-country museum or government evidence may better establish originating-work attribution; a field photograph may establish a currently visible inscription.

## 3. Assertions

Assertions are the central table/collection.

Core fields:

- `assertion_id`
- `subject_id`
- `predicate`
- `object_entity_id` **or** `literal_value`
- `literal_language` when applicable
- `status`
- `interpretation_note`
- `reviewed_date`

A semantic assertion normally forms a triple:

`subject_id → predicate → object_entity_id`

Literal assertions use `literal_value` instead.

Examples:

- `OBJ-0001 → GIFT_FROM → AG-0006`
- `OBJ-0001 → DEPICTS → AG-0001`
- `OBJ-0001 → CURRENT_CUSTODIAN → AG-0007`
- `OBJ-0003 → DERIVED_FROM_MATERIAL → OBJ-PRE-0001`

### Assertion status

Minimum alpha vocabulary:

- `VERIFIED` — supported sufficiently for publication
- `PARTIALLY_VERIFIED` — core relationship supported but material detail remains open
- `CONTESTED` — credible sources conflict
- `UNRESOLVED` — research gap; do not infer a value
- `FIELD_OBSERVED` — directly established by a dated field observation

Status is part of the published semantics. It must survive export to JSON and any structured representation.

## 4. Assertion evidence

This is the key provenance join. Do not store evidence only as a semicolon-separated list on the assertion in the publication model.

Core fields:

- `assertion_evidence_id`
- `assertion_id`
- `source_id`
- `evidence_role`
- `locator`
- `source_language`
- `original_text` when short, necessary, and legally appropriate
- `translation_or_summary`
- `evidence_note`

Suggested `evidence_role` values:

- `PRIMARY_SUPPORT`
- `CORROBORATION`
- `CONTRADICTS`
- `QUALIFIES`
- `FIELD_VERIFICATION`

This structure allows two sources to support different aspects of the same relationship without pretending they are interchangeable.

## 5. Events

Events are entities with temporal semantics. They should not substitute for assertions.

Core fields:

- `event_id`
- `event_type`
- `date_start`
- `date_end`
- `date_precision`
- `place_id`
- `description`

Assertions connect objects and agents to events, for example:

- `OBJ-0001 → SUBJECT_OF_EVENT → EVT-0007`
- `EVT-0007 → EVENT_TYPE → LegalAcceptanceAuthorization`
- `AG-0008 → AUTHORIZED_ACCEPTANCE_IN → EVT-0007`

During alpha, a denormalized event export is acceptable for page generation, but the semantic meaning must remain explicit.

## 6. Object-specific publication attributes

Physical-object convenience fields such as coordinates, current location, object type, and slug may be retained in a compact object index for build performance. They are **publication projections**, not a competing source of truth for historical relationships.

Where a convenience field represents a material factual claim, it should resolve back to an assertion.

## 7. Multilingual semantics

Original-language evidence is part of provenance.

Rules:

1. Record the source language.
2. Preserve the original wording when it materially affects interpretation and quotation is appropriate.
3. Store English translation/summary separately.
4. Do not replace a Spanish-language entity name or source with its English rendering.
5. Link semantically equivalent entities across languages through stable IDs rather than duplicate records.
6. Record uncertainty introduced by translation in `interpretation_note` or `evidence_note`.

## 8. Relationship vocabulary

Predicates should be narrow enough to preserve meaning. Alpha examples include:

- `DIPLOMATIC_GIFT_FROM`
- `FORMAL_OFFER_BY`
- `PRESENTED_BY`
- `RECEIVED_BY`
- `DEPICTS`
- `ORIGINAL_DESIGN_BY`
- `COMPLETED_BY`
- `MODELED_BY`
- `CAST_BY`
- `CURRENT_CUSTODIAN`
- `LOCATED_AT`
- `DERIVED_FROM_MATERIAL`
- `DERIVED_FROM_DESIGN`
- `SUBJECT_OF_EVENT`

Do not use a generic `CREATOR` relationship when evidence distinguishes design, completion, modeling, casting, or reproduction.

## 9. Conflicts and unknowns

Never resolve disagreement merely to produce a cleaner page.

If sources conflict, retain both evidence records and mark the assertion `CONTESTED` or create competing assertions where necessary. If the Washington-specific caster is unknown, encode the research gap; do not create an `UNKNOWN` agent simply to complete a triple.

## 10. Human and machine publication

The same assertion layer must generate:

- object pages;
- country/entity pages;
- creator/agent pages when useful;
- timelines;
- source/evidence displays;
- canonical JSON;
- JSON-LD or other structured metadata where established vocabularies can express the relationship accurately.

Do not force project-specific semantics into an inaccurate Schema.org property. Preserve the richer canonical JSON even when public structured-data vocabularies are less expressive.

## 11. Alpha constraints

- Three Washington objects only.
- No graph database is required; graph semantics do not require graph infrastructure.
- JSON/CSV is sufficient if referential integrity is validated during build.
- No CMS or user-account layer.
- New predicates require an actual claim in the three-object corpus, not hypothetical future needs.

## 12. Validation rules

The build should fail when:

- an assertion references a missing entity;
- evidence references a missing assertion or source;
- a published `VERIFIED` assertion has no supporting evidence;
- a material source lacks language metadata;
- an object page contains a material historical claim with no assertion ID;
- an unresolved/contested assertion is emitted as an unqualified machine-readable fact;
- duplicate stable IDs occur.

This validation layer is more important to the alpha than adding additional records.
