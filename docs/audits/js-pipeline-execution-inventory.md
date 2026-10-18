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

## I1 follow-up — final-site artifact gate and validator samples

`tests/publication-artifact-inventory.mjs` inventories the final `site/` tree (all regular files, including HTML, JSON, CSS, and other assets) in sorted relative-path order, recording byte counts and SHA-256 digests. Symlinks and non-file entries fail. A repeated inventory is compared for equality, and a deliberately mutated fixture is rejected. The workflow now writes `build/audit/publication-artifacts.json` **after** the existing publication validators and **before** required-artifact checks and artifact upload. The new manifest is a CI diagnostic, not a published file or a substitute for the validators. CI execution and the resulting count are not yet verified.

Inspected validator contracts:

| Validator | Reads | Invariant |
| --- | --- | --- |
| `validate_pub004_internal_links.py` | Every `site/**/*.html` page | Internal `href` under `/dc-public-realm` resolves to a file, including directory-index links; rejects paths escaping site root |
| `validate_pub002_navigation.py` | Homepage, methodology, collaboration, data index, every published object page | Exact primary navigation links and exactly one Alpha state in each audited header |
| `validate_publication_consistency.py` | `site/data/assertions.json`, published object HTML, staged publication metadata | Every direct object assertion exposes the machine-readable computed status in HTML |
| `publication_chrome.py` | No file reads; pure string functions | Supplies shared navigation and Alpha state for generators and enforcement pass |

**Remaining I1 work:** review the other EPI, DATA, PUB, image, localization and materialization validators individually; verify the new manifest gate in CI; capture its actual output count and route list. No claim of exhaustive validation coverage is made yet.

## I1 follow-up — CI evidence and validator trace

GitHub Actions run `39134164000` at commit `9be4b1ed` passed. Build job `117695189279` confirms: final object parity 3 routes / identical raw bytes; PUB-004 checked 169 internal links across 16 HTML pages; artifact inventory sensitivity rejected a byte mutation; final inventory recorded **23 regular files**. Deploy job was skipped on this PR.

Additional sampled validators:

| Validator | Inputs and principal check | Migration implication |
| --- | --- | --- |
| `validate_epi004_rendered_lineage.py` | Published assertion/evidence JSON, staged sources and three hard-coded object pages; reconciles lineage blocks, source IDs, locators, ancestry terminals | Port trace semantics and remove fixed-object enumeration |
| `validate_epi005_warning_placement.py` | Published assertions/evidence, conflict index, three fixed pages; requires conflict warning before optional lineage disclosure | Preserve placement semantics and derive published route set |
| `validate_data002_summary_reconciliation.py` | Staged entities/evidence and final homepage/object HTML; checks names, countries, routes, headings and source counts for three fixed objects | Port semantic reconciliation, avoid hard-coded object list |
| `validate_pub003_tasks.py` | Staged research tasks and published-object metadata; final homepage, object pages and task pages; reconciles OPEN counts and links | Port as independent task-route contract |
| `validate_image_rights.py` | Canonical object overviews; checks required image metadata, CC license link and Wikimedia creator attribution | Preserve rights requirements in JS input validation |
| `validate_localization.py` | Localization schema, all locale JSON files and canonical overviews; checks allowed fields, language/status, and review metadata for published translations | Preserve schema-bound localization validation |

**Design finding:** several legacy validators are hard-coded to the same three reference objects that `build_site.py` hard-codes, while the newer publication index derives published routes. A future fourth object could bypass some legacy rendered checks. The JS replacements must enumerate published objects from materialized metadata and use mutation tests for newly introduced objects, rather than simply reproduce the fixed list.

**I1 gate remains open:** the remaining validators have not all been individually traced; the 23-file manifest was generated successfully but its individual file entries have not yet been reviewed here.

## I1 correction — independent audit of inventory semantics

An independent review at `14978eb` identified an overstatement in this document's earlier wording: **the inventory is observational, not an enforcement baseline**. The script compares two immediate reads of the same tree, and its mutation sensitivity uses an isolated fixture. It does **not** compare the site against a committed baseline, a prior approved run, or an independently specified route set. Its live-site assertions only require a homepage, CSS and absence of symlinks/non-files. Therefore a changed, added, or missing other publication artifact does not automatically fail this step.

Correction: the 23-file result is a **measured snapshot/count**, not an enforced publication baseline. The initial workflow did not upload `build/audit/publication-artifacts.json`; it uploaded only `site/`. This PR now separately uploads the JSON inventory with `actions/upload-artifact@v4` and `if-no-files-found: error`, so its individual entries can be inspected after CI. Upload success and artifact contents still require verification on the new commit.

The previous description of object-page parity as limited to three hard-coded routes was also inaccurate as a statement of its **test design**: `object-page-final-parity.mjs` derives the expected route set using `publishedObjects()` and compares both trees against it. The current corpus happens to contain three routes. That parity test does not independently establish the completeness of the publication index itself.

The independent audit found approximately eleven validators referencing fixed `OBJ-0001`/`OBJ-0002`/`OBJ-0003` sets across EPI-001/002/003/004/005, DATA-001/002 and overview checks. **Fail-open versus fail-closed must be classified per validator**, not inferred from the presence of a constant: `validate_overview_data.py` reportedly requires an exact object-set match (fail-closed), while several rendered-page checks iterate only those three and may skip a fourth object (fail-open). This classification remains to be confirmed script by script.

**Open design gates:** (1) independently reconcile expected published-object IDs against canonical materialized entities; (2) choose whether full-site byte parity compares JS against Python as a temporary oracle, an approved stored snapshot, or both; (3) establish intentional-change review/update procedure for any committed baseline. Do not claim I1 closed before these decisions and evidence checks.

## Post-PR #79 integration (pending CI verification)

PR #79 was merged to `main` at `be583177`, correcting the determinism test's destructive rebuild. This branch now incorporates the isolated test, the required Artigas review route gate immediately before site upload, and shared use of `inventory()`/`compareInventories()` from this PR's inventory module. These changes are reconciled into the PR branch; **the Git ancestry has not yet been rebased or merged onto `be583177`**. Do not describe this as a completed rebase.

The prior 23-file inventory is preserved as evidence of the defect, not as a baseline. The expected corrected count is 24, pending fresh CI manifest and site artifact inspection. Required-route existence is enforced, but full-site baseline parity and canonical expected-ID completeness remain open gates.

## Workflow trigger scope and production verification

The workflow's `push` trigger is limited to `main` and paths `data/**`, `transactions/**`, `migrations/**`, `skills/**`, `scripts/**`, `lib/**`, `tests/**`, and `.github/workflows/build-site.yml`. Changes solely to documentation (such as `docs/**`) do not trigger the push workflow. The `pull_request` trigger uses the same path filters. The `workflow_dispatch` trigger permits manual runs. On push to `main`, the workflow runs the build and Pages deployment; on pull requests, deployment is deliberately skipped.

A GitHub mobile screenshot of PR #79's checks shows successful `build (push)` and `deploy (push)` jobs following its merge. The exact production run ID was not independently retrieved through the available commit lookup. Live HTTP loading of `/dc-public-realm/review/artigas/` also remains unverified through the available web access. Distinguish successful CI artifact checks and deployment-job status from confirmation of live page availability and from historical evidence that the prior defect reached users.
