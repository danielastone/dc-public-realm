# Diplomatic Gifts Canonical Data Model — v0.2

The website is generated from structured records for three physical diplomatic-gift objects. The model is intentionally relational in concept but may be stored as JSON/CSV during alpha.

## Core tables / collections

### Objects
One row/document per physical viewable object.

Core fields: `object_id`, `canonical_title`, `object_type`, `country`, `gift_status`, `current_custodian`, `location`, `latitude`, `longitude`, `publication_status`, `slug`.

Alpha IDs are `OBJ-0001`, `OBJ-0002`, and `OBJ-0003`.

### Agents
People, governments, institutions, organizations, and named national/public donor groups participating in assertions or events.

Core fields: `agent_id`, `agent_type`, `canonical_name`, `native_name`, `country`, `notes`.

Do not collapse materially different roles such as donor, presenter, recipient, creator, caster, custodian, or reviewing agency.

### Events
Chronological actions affecting an object.

Core fields: `event_id`, `object_id`, `event_type`, `event_date`, `place`, `description`, `participating_agent_ids`, `evidence_source_ids`, `status`.

Gift, shipment, legal acceptance, siting, installation, dedication, relocation, storage, restoration, and designation remain separate events when the evidence distinguishes them.

### Assertions
Atomic factual claims and their evidentiary status.

Core fields: `assertion_id`, `subject_id`, `predicate`, `object_or_value`, `status`, `evidence_source_ids`.

Publication rule: a material factual statement on an object page must be traceable to an assertion and identified evidence. `UNRESOLVED` claims must not be transformed into definitive web copy or structured metadata.

### Sources
Source register covering U.S. and donor-country evidence.

Core fields: `source_id`, `title`, `publisher`, `language`, `source_type`, `url`, `primary_use`.

Source authority is claim-specific. Congress may control legal acceptance evidence; planning bodies may control siting; NPS may support custody/current interpretation; donor-country institutions may be stronger for original-language production history.

### Object relationships
Relationships between physical/cultural objects rather than events.

Core fields: `relationship_id`, `subject_object_id`, `relationship_type`, `related_object`, `status`, `notes`, `evidence_source_ids`.

Alpha relationship vocabulary includes `DERIVED_FROM_MATERIAL` and `DERIVED_FROM_DESIGN`. These remain separate because physical material provenance and design/iconographic provenance are different claims.

### Field observations
Current physical observations made in the field.

Core fields: `observation_id`, `object_id`, `observation_date`, `method`, `object_present`, `publicly_viewable`, `inscription_status`, `coordinate_status`, `condition_status`, `media_status`.

Field observations establish current physical state. They do not establish historical gift provenance.

## Evidence principles

1. Stable project IDs identify the physical objects.
2. Sources attach to assertions/events, not only to a generic bibliography.
3. Creative attribution is role-specific.
4. Original-language evidence is retained with explicit language metadata.
5. Conflicting evidence is preserved rather than silently normalized.
6. Unknowns are data.
7. Human-readable and machine-readable pages must be generated from the same canonical records.
8. No fourth object is added during alpha.

## Publication model

The website should compile canonical records into both human pages and machine-readable representations. The build layer may denormalize data for performance, but generated output must retain stable IDs, source URLs, assertion status, and language metadata.

The alpha does not require a database server, graph database, CMS, or user accounts. Add infrastructure only when the three-object publication workflow demonstrates a concrete need.
