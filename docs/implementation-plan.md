# Diplomatic Gifts — Implementation Plan

Status: **frozen implementation backlog**  
Owner/reviewer: **Daniel**  
Scope: recenter the repository on evidence-grounded research into diplomatic gifts and foreign-sponsored objects in the public realm.  
Constraints: ethics gate remains in force; Python is deprecated in favor of the JS rebuild; Daniel is the sole reviewer.

## Governing rule

Do not add a new subsystem unless work on an actual diplomatic-object record demonstrates that the existing architecture cannot represent the evidence or lifecycle correctly. New architectural ideas otherwise go to a parking lot.

Critical path: **definition → corrected role ontology → classification derivation → alpha migration/test → JS renderer → website**.

## Tracker

| ID | Action | Owner | Status | Dependency | Decision / finding | Closure evidence |
|---|---|---|---|---|---|---|
| 0.1 | Write versioned `DEFINITION.md`: working definition, three roles, financing, core/periphery/excluded classes, UNESCO anchor and limits, scholarly basis | Daniel | Open | — | Classification must cite a criteria version | Committed definition with criteria version |
| 0.2 | Add licenses for data and code, separate from per-image rights | Daniel | Open | — | Repo root must state terms for each | License files committed |
| 0.3 | Fix classification statuses: `core`, `periphery`, `excluded`, `undetermined` | Daniel | Open | 0.1 | Four-status vocabulary | Definition commit |
| 1.4 | Retire `DIPLOMATIC_GIFT_FROM`; add gift framing, `FUNDED_BY`, `PRESENTED_BY`, `ACCEPTED_FROM`, `AUTHORIZED_PLACEMENT`, retain `DONOR_ATTRIBUTION`; migrate A-0001/A-0101/A-0201 via ledger transactions | Daniel | Blocked | 0.1–0.3 | Classification cannot be encoded as an assertion label | Migration transactions + validator; no classification assertion remains |
| 1.5 | Restrict `ACCEPTED_FROM` counterparty to a foreign polity or its representative | Daniel | Blocked | 1.4 | Domestic authorization is not acceptance | Validator test rejects domestic authorization as acceptance |
| 1.6 | Add financing, occasion, `reciprocal_of`, and general lifecycle event replacing `RELOCATED_IN` | Daniel | Blocked | 1.4 | Model missing independent dimensions | Schema + validation tests |
| 1.7 | Derive classification from role claims and evidence status | Daniel | Blocked | 1.4–1.6 | Classification is computed, not asserted | Three alpha objects reproduce approved alpha results automatically |
| 1.8 | Map external standards: Wikidata IDs for objects/parties; CIDOC CRM acquisition-event alignment; check Getty terminology for “diplomatic gifts” | Daniel | Blocked | 0.1, 1.4 | Mapping may close as documented non-alignment/absence | IDs/mapping or explicit documented absence for each object |
| 2.9 | Add `resolves` block to transactions: task, submission, contributor/role, review-record path | Daniel | Blocked | 1.4 | Transaction must trace collaboration lifecycle | Builder rejects broken links |
| 2.10 | Unify task-status vocabulary and validate materialized data | Daniel | Open | — | Documentation and validator must share one vocabulary | `collaboration.md` + validator agree and tests pass |
| 2.11 | Add review-record type: criteria version, rationale, `self_review`, dissent references | Daniel | Blocked | 0.1 | Every incorporated change needs review provenance | Schema + every incorporated change has a review record |
| 2.12 | Add assertion propagation track with downstream targets and status | Daniel | Blocked | 2.11 | NPS notices remain gated; Wikidata edits do not | Schema + validation |
| 3.13 | Render computed classification badge and “why” panel from role claims | Daniel | Blocked | 1.7, JS rebuild | Page title/UI must not presuppose diplomatic-gift status | San Martín and Artigas render `undetermined` when derivation says so |
| 3.14 | Render definition page from `DEFINITION.md` | Daniel | Blocked | 0.1, JS rebuild | Definition has one canonical source | Generated page verified |
| 3.15 | Rewrite front door around: what is this; is it true; how sure are we; how can I help | Daniel | Blocked | JS rebuild | Keep internal vocabulary off landing page | Generated front door reviewed |
| 3.16 | Show queue age/reviewer on task pages; add contributor credit pages | Daniel | Blocked | 2.9–2.11, JS rebuild | Collaboration state should be visible | Generated pages verified |
| 3.17 | Prepare global information architecture; Washington remains first node; routes by giver, recipient, country | Daniel | Blocked | 1.7, JS rebuild | Repo/domain rename remains deferred | Routes generated and tested |
| 4.18 | Test whether S.2591 accepts the Artigas gift or only authorizes placement; run result through full lifecycle as self-review | Daniel | Ready | 0.1 and transaction design as available | This is the first live ontology test | Source finding → task/submission → review → transaction → derived classification documented |
| 4.19 | Send ARG-SM-001 research request to Argentine archive | Daniel | Ready | — | Ordinary research; not steward outreach | Reply or non-reply logged |

## Phase gates

### Phase 0 — Definition and governance
No ontology migration is considered complete until classification criteria are versioned and statuses fixed.

### Phase 1 — Ontology
Language-agnostic JSON precedes the JS website rebuild. Preserve history through ledger transactions; do not rewrite baselines to hide prior modeling decisions.

### Phase 2 — Collaboration engine
The lifecycle is: **claim → evidence → gap → request → response → review → accepted evidence → canonical update → provenance trail**. Changes must be traceable across it.

### Phase 3 — Website
The JS rebuild consumes the corrected ontology. Python implementation is deprecated rather than duplicated. Public language should explain evidence and uncertainty without exposing unnecessary internal terminology.

### Phase 4 — Prove the lifecycle
Use real research cases to test the architecture. Artigas is the first live test. After the alpha migration, expand the corpus rather than continuing architecture review.

## Ethics gate

The ethics gate remains open. Do not initiate steward outreach or downstream notices to agencies such as the National Park Service until cleared. Ordinary archival research requests may proceed. Wikidata edits are outside that outreach hold unless a later ethics decision changes the boundary.

## Success measure

Primary measure: **materially researched objects whose significant public claims can be traced to evidence, with uncertainty represented explicitly**.

Page views, repository complexity, source counts, and Google Maps photo exposure are not primary success measures.

## Parking lot

Place proposed generalized photo auditing, GIS platforms, API-surveillance layers, ontology expansion, repo/domain renaming, and other new infrastructure here until an object-level research case establishes a concrete requirement.
