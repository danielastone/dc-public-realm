# JavaScript pipeline migration — execution and dependency inventory (pass 1)

Status: **inventory only**. No production authority transfer, CI changes, or Python removal.

## Target

A transparent, deterministic JavaScript pipeline from canonical data, ordered migrations, and transactions to published static files and an auditable provenance manifest. The renderer parity merged in PR #77 covers published object HTML only, not the complete publication system.

## Observed CI execution order

Source: `.github/workflows/build-site.yml` on `main`.

| Stage | Current entry points | Reads / writes | Migration boundary |
| --- | --- | --- | --- |
| Pre-materialization checks | `validate_data.py`, `validate_claim_modes.py`, `validate_overview_data.py`, `validate_localization.py`, `validate_image_rights.py`, `check_image_urls.py`, EPI-002/004/005 and DATA-001 validators | Canonical `data/`, supporting rules and evidence; checks only by workflow intent | Inventory each predicate and its failure semantics before porting |
| Transaction materialization | `scripts/build_database.py` | Reads baseline `data/`, sorted `migrations/*.json`, sorted `transactions/*.json`; writes seven `build/data/*.json` datasets, `build/audit/manifest.json`, `semantic-manifest.json` | Port ordered ledger operations, precondition hashes, integrity, epistemic deltas, and deterministic semantic manifest; volatile `built_at_utc` separately accounted for |
| JS object-page candidate | `scripts/build_object_pages.mjs`, `lib/object-page-driver.mjs` | Reads declared materialized datasets and static configuration; writes `build/js-site/objects/*/index.html` | **Already implemented**; Python parity is checked later |
| Materialized data validation | `validate_data.py`, `validate_publication_identity.py`, `validate_publication_index.py`, `validate_claim_modes.py` | `KNOWLEDGE_DATA_DIR=build/data` | Independent JS validations required; do not substitute renderer parity |
| Publication staging | Workflow shell commands | Copies static policy files to `/tmp`, replaces `data/` with `build/data/`, restores four static files | Remove mutation of the source directory in a future stage; stage into an isolated publication input tree |
| Python publication | `scripts/build_publication.py` imports `build_site.py` (which **executes on import**), then `overview_renderer.py`, `render_epistemics.py`, `frontdoor_renderer.py` | Writes `site/` pages, injects overviews and epistemic blocks, writes home and collaboration pages | Split implicit base build, object pages, and other routes into explicit JS stages |
| Post-publication mutations | `inject_external_records.py`, `build_smithsonian_review.py`, `enforce_navigation_contract.py` | Mutates/adds publication HTML after initial build | Identify every resulting route and make each output owned by one JS builder |
| Final gates | Python determinism, JS↔Python object-page parity, entity literal scan; publication consistency, EPI/DATA/PUB validators; required artifacts | Reads `site/`, `build/js-site/`, materialized data and manifest | Preserve independent semantic and route/link checks; retire Python comparisons only after equivalent independent oracles exist |
| Delivery | Upload `site/` artifact; Pages deployment only on `main` push | Publishes `site/` | Change authority in separately approved cutover |

## Confirmed Python materializer semantics

`scripts/build_database.py` defines seven logical datasets: entities, sources, assertions, assertion evidence, predicate rules, research tasks, and object overviews. It sorts migration and transaction filenames; applies add/update/delete operations with optional `before_sha256` preconditions; checks referential integrity after each ledger item; enforces transaction `supersedes` continuity; records before/after database hashes and epistemic assertion deltas. Canonical hashing uses sorted JSON keys, compact separators and UTF-8 with non-ASCII characters unescaped. Output datasets are pretty-printed JSON with a trailing newline. The semantic manifest is deterministic; the separate full manifest includes a build timestamp and is not byte-deterministic by design.

## Existing JavaScript coverage

`lib/publication-index.mjs` derives published routes; `lib/renderer-input-policy.mjs` and loader declare/read inputs; `lib/derive-epistemics.mjs`, status, overview, tasks, external records and shell renderers support object-page output. PR #77 proved exact final byte parity for three published object pages and failure sensitivity. This does **not** prove parity for homepage, collaboration, methodology, data, research tasks, review brief, static assets, or complete site route set.

## Risks and unresolved inventory items

1. **Implicit execution:** `build_site.py` executes during `build_publication.py` import. Capture its complete output tree and data dependencies before replacing it.
2. **Source mutation:** staging deletes/replaces `data/` in the CI workspace. A JS pipeline should not need to overwrite canonical inputs.
3. **Post-build writers:** external records, Smithsonian brief, and navigation enforcement run after the main publication entry point. Their writes must be classified as builders versus validators.
4. **Validation coverage:** the workflow names many validators, but this first pass does not establish their complete read/write sets or mutation sensitivity. No validator can be declared redundant solely because output parity passes.
5. **Reproducibility:** distinguish deterministic semantic artifacts from timestamped diagnostic artifacts and from environmental/network checks.
6. **Site scope:** capture a manifest of every published route and static asset before attempting full-site parity.

## Proposed gated sequence

- **I1 — Complete inventory:** inspect every production Python script and its imports; record read/write sets, side effects, validations and failure behavior. Generate a current-site route/artifact manifest. No behavior changes.
- **I2 — JS materialization parity:** replay the same frozen baseline and ordered ledger; compare seven datasets, semantic manifest, error/mutation cases. Preserve Python as oracle.
- **I3 — JS full-site candidate:** implement explicit builders for all non-object pages, assets and post-build outputs into a separate tree; compare full route sets and bytes.
- **I4 — Independent JS validation:** port and test canonical, materialized, and published invariants with deliberately invalid fixtures. Do not treat Python-vs-JS equality as sufficient validation.
- **I5 — Authority transfer:** separate approval changes artifact upload to JS output; keep Python comparison and rollback until proven stable.
- **I6 — Retirement:** remove Python from production workflow only after equivalent provenance, determinism, validation and publication coverage are demonstrated.

**Gate for this PR:** reviewers agree the observed workflow stages and open inventory tasks are accurately bounded. This document is a first pass, not a claim that every Python dependency has been traced.

## I1 follow-up — traced publication writers

The following is a source-level inventory of the core publication writers, not yet a complete validator inventory.

| Script | Read dependencies | Write/side effects | Route ownership |
| --- | --- | --- | --- |
| `build_site.py` | `data/{entities,assertions,assertion-evidence,sources,predicate-rules,research-tasks,publication_status_rules,claim-modes,external-records}.json` | **On import**, recursively deletes `site/`, writes CSS, HTML, and public JSON | `assets/style.css`; `index.html`; hard-coded three `objects/<slug>/index.html`; `tasks/<task_id lowercase>/index.html` for every task; `collaborate/index.html`; `methodology/index.html`; `data/index.html`; six `data/*.json` exports |
| `build_publication.py` | Imports `build_site` and rendering modules; reads staged assertions, entities, overviews, evidence, sources, dependency rules, tasks through imported renderer | Mutates each overview object HTML; appends epistemic blocks to published object HTML; **overwrites** `index.html`; writes `collaborate/artigas/index.html` | Existing object routes plus homepage and Artigas collaboration |
| `frontdoor_renderer.py` | Entities through publication index, object overviews, research tasks | Pure rendering function returns two HTML strings | Homepage and Artigas collaboration; fails if featured object differs from `OBJ-0001` |
| `inject_external_records.py` | `data/external-records.json`, publication index; reads Artigas page | Inserts section before sole `</main>` and rewrites page | Artigas object page only; hard-coded object and subject IDs |
| `build_smithsonian_review.py` | `data/sources.json`, publication index | Writes HTML page | `review/artigas/index.html`; hand-authored review content, not general-purpose entity rendering |
| `enforce_navigation_contract.py` | `publication_chrome.py`, recursively reads `site/**/*.html` | **Rewrites every HTML page containing a header**, replacing/inserting nav and alpha state | All HTML routes, including review brief |

**Ordering hazard:** the homepage from `build_site.py` is overwritten by `build_publication.py`; object pages are first created by the former and then changed by the latter, the external-record injector, and navigation enforcement. Full-site byte parity must compare final output **after all writers**, not any intermediate stage.

**Exact output enumeration:** `build_site.py` emits one task route per record in `research-tasks.json` (not only OPEN tasks), and six public data exports: `assertions.json`, `entities.json`, `assertion-evidence.json`, `research-tasks.json`, `claim-modes.json`, `external-records.json`. The final site also includes the Artigas collaboration and Smithsonian review routes. These are route *patterns*, not a verified current artifact count. A CI-generated final tree manifest is still required to confirm actual paths, sizes and hashes.

**Scope warning:** `build_site.py` currently uses hard-coded published-object IDs and slugs, while JS `publishedObjects()/pathFor()` derives them. This difference is hidden by the three-object current dataset; future additions must not be constrained by the old constants. The Artigas-specific front door, external-record injector and Smithsonian brief are deliberate editorial exceptions requiring explicit ownership rather than a general entity-rendering rule.

## I1 remaining evidence

Inspect each Python validator's imports, input reads, output writes, mutation behavior and expected failure; inspect `publication_chrome.py` and any auxiliary writers. Then capture a final-tree artifact manifest in CI, including all HTML, JSON and CSS files, with deterministic hashes and a sensitivity test. Until then, the inventory remains **in progress** and is not a complete migration gate.
