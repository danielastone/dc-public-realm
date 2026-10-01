# DATA-002 — public summary surface inventory

**Finding:** DATA-002  
**Issue:** #64  
**Reference objects:** OBJ-0001 Artigas; OBJ-0002 San Martín; OBJ-0003 Cuban Urn

## Control principle

A public summary is a DATA-002 concern only when it restates mutable canonical state. Such a value must be generated from the materialized canonical dataset or exactly reconciled to it. Editorial orientation prose is not converted into a pseudo-database merely to make it testable; it remains editorial but must not embed independently maintained mutable canonical facts.

This inventory distinguishes four classes:

- **DERIVED** — machine-derived from canonical state and should not have a second authoritative value.
- **CANONICAL_EDITORIAL** — authored orientation text whose canonical source is `data/object-overviews.json`; rendered HTML is disposable.
- **STATIC_PRESENTATION** — navigation, labels, or generic prose that does not restate mutable object state.
- **OUT_OF_SCOPE_ALREADY_CONTROLLED** — derived state already governed by a stronger existing exact-reconciliation control; DATA-002 must not duplicate it.

## Surface inventory

| Public surface | Published value | Classification | Canonical source / derivation | Existing control | DATA-002 action |
|---|---|---|---|---|---|
| Homepage object card | Object name | DERIVED | `entities.json` → object `canonical_name` | build generation | Add anti-drift validation that the rendered card identity/name maps to the same object record. |
| Homepage object card | Country label | DERIVED but currently code-mapped | Current `build_site.py` `COUNTRIES` mapping | none | Remove the independent authoritative mapping if canonical entity geography can supply it; otherwise explicitly document the mapping as presentation configuration and validate object binding. |
| Homepage object card | Open research mission count | OUT_OF_SCOPE_ALREADY_CONTROLLED | `research-tasks.json`: count `status == OPEN` by `object_entity_id` | PUB-003 | No duplicate DATA-002 count rule. Preserve PUB-003 as the authority. |
| Homepage object card | “Catalog record, sources, and open research questions.” | STATIC_PRESENTATION | generic build copy | none needed | No derived-state control. |
| Object page heading | Object name | DERIVED | `entities.json` → object `canonical_name` | build generation | Reconcile object identity/name. |
| Object page kicker | Country + “catalog record” | DERIVED + STATIC_PRESENTATION | country presentation mapping + static label | none | Same country treatment as homepage. |
| Object overview/orientation | Overview heading, paragraphs, key points, status note | CANONICAL_EDITORIAL | `data/object-overviews.json` | `validate_overview_data.py`; `validate_overview_rendering.py` | Treat JSON as canonical editorial source; rendered HTML must match it. Do not derive this prose from assertions. |
| Object assertion status badge | Verified / Supported / Sources differ / Unresolved / Not established | DERIVED | materialized assertions/evidence + predicate rules; computed publication status | publication consistency + EPI-001 | Do not create a second DATA-002 status algorithm. Validate any *summary* reuse against the already computed canonical status. |
| Object assertion status reason | Human-readable reason for computed status | DERIVED | same status computation | publication consistency | No independent authored copy permitted. |
| Object evidence source count | Number in “Sources · N” | DERIVED | distinct canonical evidence `source_id` values for assertion | DATA-001 covers assertion identity, not this count | Add exact source-count reconciliation if count remains public. |
| Object research section | Open mission count/links | OUT_OF_SCOPE_ALREADY_CONTROLLED | canonical OPEN tasks | PUB-003 | No duplicate rule. |
| Conflict warning | Presence and assertion association | OUT_OF_SCOPE_ALREADY_CONTROLLED | canonical `CONTRADICTS` evidence | EPI-005 | No duplicate rule. |
| Dependency/ancestry disclosure | Dependency and ancestry state | OUT_OF_SCOPE_ALREADY_CONTROLLED | canonical assertion-evidence lineage | EPI-002/EPI-003 | No duplicate rule. |
| Claim-lineage disclosure | Evidence/source ancestry trace | OUT_OF_SCOPE_ALREADY_CONTROLLED | canonical assertion-evidence/source graph | EPI-004 | No duplicate rule. |
| Data page/object links | Canonical-data route identity | OUT_OF_SCOPE_ALREADY_CONTROLLED | materialized data files | PUB-001 | No duplicate rule. |

## Findings from the inventory

### 1. DATA-002 is narrower than the original audit wording

The highest-risk summary states are already controlled by PUB-003 and EPI-001–005. Reimplementing those derivations would create parallel control logic and increase drift risk.

### 2. One genuine duplicate-state smell remains

`build_site.py` contains a hard-coded `COUNTRIES` object-to-country mapping. That is presentation configuration masquerading as object data. DATA-002 should either derive geography from canonical entities/relationships or explicitly reduce this mapping to non-authoritative display configuration whose object binding is mechanically checked.

### 3. One uncovered derived display remains

The public assertion evidence summary displays a distinct-source count. The count is generated during the build, but no acceptance control currently proves it equals the materialized assertion-evidence set after later page transforms. DATA-002 should reconcile that value exactly.

### 4. Editorial prose should stay editorial

`object-overviews.json` is intentionally the canonical orientation layer. Turning those paragraphs into assertion-derived prose would erase the distinction between sourced factual assertions and editorial synthesis. DATA-002 should instead enforce that rendered overview text comes from that canonical editorial file and does not acquire a second independently maintained HTML copy.

## Proposed DATA-002 acceptance invariant

For every reference object after all publication transforms:

1. rendered object identity and canonical name equal `entities.json`;
2. any displayed geography is bound to a declared canonical/configured source rather than an untracked duplicate fact;
3. every displayed assertion source count equals the number of distinct canonical `source_id` values attached to that assertion in the materialized publication database;
4. overview content exactly follows the canonical editorial overview source under the existing overview controls;
5. open-task, status, conflict, ancestry, lineage, and canonical-route summaries continue to be governed by their existing exact controls rather than reimplemented;
6. synthetic mutations of object name/binding, geography binding, or source count fail the DATA-002 validator.

## Non-goals

- Do not add homepage status badges solely to create a DATA-002 test target.
- Do not hard-code the current three-object counts or statuses as expected values.
- Do not create a new `summary.json` that duplicates canonical data.
- Do not infer that generic editorial prose is a factual summary requiring database derivation.
- Do not weaken PUB/EPI controls by moving their logic into DATA-002.
