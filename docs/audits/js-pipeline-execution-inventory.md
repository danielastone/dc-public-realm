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

## I1 artifact verification — workflow run #395 (2026-10-18)

The manually dispatched `Build and deploy alpha site` workflow run [39138620565](https://github.com/danielastone/dc-public-realm/actions/runs/39138620565) on branch `audit-js-pipeline-dependencies`, head `e6af309bd235a28ab7581b7193e0512c6c28d89e`, produced two downloadable artifacts. The GitHub Actions artifact API identified `publication-artifact-inventory` (artifact ID `12140434226`, ZIP SHA-256 `e0fb2e1755aa06340feb914768f494430921b21fc101c106311b3ca6911e98bc`) and `site` (artifact ID `12140608325`, ZIP SHA-256 `384059de01b6a57ba2586898a18d137e7e8ffa2727457e213d57360c8388b677`). These are archive digests, not hashes of individual contents.

Both ZIPs were retrieved. The inventory ZIP contains `publication-artifacts.json`, with extracted-file SHA-256 `8901e6054c2d715bfc1fe9a58fbfe97624c30ae046d55a476856cc8f96b33c15`. Its `publication-artifact-inventory-v1` manifest enumerates 24 distinct paths. The site ZIP contains 24 files; each path, file length, and SHA-256 matches its manifest entry. `review/artigas/index.html` is present. No unmatched or duplicate paths were found. This closes **the final-tree artifact inspection subtask** for this commit and confirms the missing-review-page defect is absent from these artifacts.

**Limit:** this is a verified build snapshot, not a committed or independently specified publication baseline, a live-site availability test, or proof of complete validator coverage. The larger I1 gate remains open pending individual validator classification, canonical expected-ID reconciliation, and a baseline/intentional-change policy. No JS authority transfer is authorized by this verification.

## I1 validator scope classification — source inspection (2026-10-18)

This classification is based on reading the named validator implementations at the PR branch, **not** on executing a fourth-object mutation. “Fail-open” here means that a newly published fourth object can be omitted from that validator's *page loop* while the existing three still pass; it does not claim the entire CI pipeline would accept the new object.

| Validator | Actual page/ID enumeration | Fourth-object scope behavior | Independent safeguard retained |
| --- | --- | --- | --- |
| `validate_overview_data.py` | Requires overview ID set exactly `OBJ-0001/0002/0003` | **Fail-closed for an added fourth overview**; rejects extra overview IDs rather than testing them | Required overview fields and record-type-specific metadata |
| `validate_epi001_status_rules.py` | Fixed `SLUGS` dictionary of three objects; iterates assertions for each | **Fail-open for fourth-page status/rule rendering**; global methodology rule checks still run | Per-assertion status identity and resolvable rule links on three pages |
| `validate_epi002_dependency_rendering.py` | Fixed three-object `SLUGS`; requires at least one multi-source assertion in aggregate | **Fail-open for fourth-page dependency disclosures** | Canonical evidence-to-rendered dependency relationships on three pages |
| `validate_epi003_ancestry_rendering.py` | Fixed three-object `SLUGS`; aggregate nonzero multi-source and UNKNOWN checks | **Fail-open for fourth-page ancestry disclosures** | Explicit origin, dependency, inherited-source count, and uncertainty wording on three pages |
| `validate_data001_assertion_reconciliation.py` | `main()` constructs `pages` from fixed three-object `OBJECTS` | **Fail-open for fourth-page assertion reconciliation**, despite `reconcile()` itself being generic over supplied pages | Canonical assertion IDs, exactly-once rendering, and cross-object detection for pages supplied |

**Important distinction:** `validate_overview_data.py` would block adding a corresponding fourth overview in the current workflow, but that is a hard-coded growth constraint, not proof that the other rendered validators cover future pages. Conversely, `DATA-001`'s generic `reconcile()` helper does not make its CLI scope dynamic; the hard-coded caller decides which pages get checked.

**Required migration design:** derive expected public objects and routes from the materialized publication index, independently reconcile that index to canonical publication eligibility, and run each rendered-page invariant over the derived complete set. Include a synthetic fourth object with (a) missing page, (b) missing assertion identity, (c) incorrect status/rule, (d) omitted dependency/UNKNOWN ancestry, and (e) malformed overview metadata. Assert each intended gate fails. This proposed test matrix is **not yet executed**.

**Next source-inspection batch:** remaining EPI-004/005, DATA-002, PUB-002/003/004, and publication consistency validators; record fixed-scope vs dynamically enumerated behavior before deciding implementation order.

## Overview completeness and fourth-object sequencing (source inspection, 2026-10-18)

Publication eligibility is `publication.publish === true` (JS and Python publication indexes); overview presence is not part of eligibility. The fixed-ID overview validator therefore does not enforce published-object-to-overview completeness. Page existence is already guarded by derived scope: PUB-001 compares missing/orphan pages against `published_objects()`, and final JS-to-Python parity checks the route set against `publishedObjects()`. A published fourth object that the legacy builder does not render fails closed.

The fail-open validators EPI-001/002/003 and DATA-001 have **latent content coverage gaps** that become live when `build_site.py`'s fixed object list is made dynamic. **Sequencing rule:** do not change the legacy builder's object list or relax the overview ID check until (1) the invariant `published IDs = expected object pages = required overviews` is enforced (PUB-001 already covers page existence), (2) rendered content validators derive scope from the same published-object set, and (3) a fourth-object fixture fails each validator with its own specific diagnostic, rather than merely failing an upstream check. Malformed overview metadata must fail for its malformed field, not only for an extra object ID.

## I1 validator scope classification — second source inspection (2026-10-18)

The following conclusions concern each script's own checked scope, not a demonstrated end-to-end fourth-object run.

| Validator | Scope in code | Fourth-object consequence |
| --- | --- | --- |
| `validate_epi004_rendered_lineage.py` | Fixed three-object `SLUGS` loop | Fourth object's lineage disclosures are not checked; aggregate nonzero coverage only checks existing objects |
| `validate_epi005_warning_placement.py` | Fixed three-object `SLUGS` loop | Fourth object's conflict warning placement is not checked |
| `validate_data002_summary_reconciliation.py` | Fixed three-object `OBJECTS` plus exact homepage card-set equality | A fourth homepage card fails the exact-set gate, but a fourth page's summary is not inspected; another expansion blocker, not dynamic content coverage |
| `validate_pub002_navigation.py` | Static front-door pages plus `published_objects()` / `path_for()` | Derived object-page navigation checks include a fourth published object |
| `validate_pub003_tasks.py` | `published_objects()` and per-object task count/link checks | Derived object-page task checks include a fourth published object |
| `validate_pub004_internal_links.py` | All `site/**/*.html` and in-scope internal `href` targets | Checks internal links in a fourth page if that page exists; does not establish that page's required content or existence independently |
| `validate_publication_consistency.py` | `published_objects()` and direct assertions from published JSON | Fourth page is checked for each direct assertion's ID and computed-status marker; does not substitute for rule, dependency, ancestry, lineage, or conflict checks |

**Updated cutover constraint:** `validate_data002_summary_reconciliation.py` is a second fixed-set growth blocker alongside `validate_overview_data.py`. Before permitting the legacy builder to produce a fourth object, make both checks derive expected object IDs, make EPI-001/002/003/004/005 and DATA-001 cover derived scope, and test specific failure diagnostics for each invariant. Keep PUB-001, PUB-002/003/004, publication consistency, and JS/Python route parity as independent existing guards; their coverage is complementary, not interchangeable.

## I1 third batch — golden checks and second CI workflow (2026-10-18)

**Correction to earlier summary:** EPI-004 and EPI-005 are families of scripts, not single fixed-scope validators. The earlier batches classified only their named rendered/placement scripts. Do not infer all EPI-004/005 scripts should become dynamically scoped.

| CI script | Observed role and scope | Migration treatment |
| --- | --- | --- |
| `validate_overview_rendering.py` | Fixed three slugs and per-object expected text strings; also checks canonical assertion references and rendered trace markers on those pages | **Mixed:** preserve object-specific golden expectations; add derived-scope generic overview/traceability validation |
| `validate_epi004_corpus_lineage.py` | Filters canonical assertions to three reference IDs; requires unresolved ancestry coverage and rejects broken/cyclic traces within that subset | **Reference-corpus regression:** preserve the reference expectations; add separate derived/all-published-object corpus integrity check |
| `validate_epi004_san_martin_conflict.py` | Pins `A-0106` San Martín Daumas/Dumont evidence and public trace | **Golden case:** retain fixed regression; derived lineage coverage belongs in a separate generic validator |
| `validate_epi005_conflict_inventory.py` | Pre-materialization frozen seed counts and exact IDs for three objects; also tests synthetic detector semantics | **Frozen baseline/golden:** retain exact expected counts and IDs for seed fixture; do not replace with dynamic counts; separately check all materialized published conflicts |
| `validate_epi005_rendered_conflicts.py` | Reconciles canonical/rendered conflict set only within fixed three `SLUGS` | **Generic coverage gap:** make a derived-scope counterpart for all published objects; preserve current assertions as needed |
| `validate_data002_synthetic.py` | Six mutations of fixed current objects; requires exit code 1 but does not inspect failure message | **Mutation regression:** retain existing fixtures; extend future fourth-object tests to assert precise diagnostics, not merely nonzero exit |

**Second production workflow found:** `.github/workflows/validate-data.yml` (`Validate semantic data`) has independent push/PR path filters and `workflow_dispatch`. It runs Python 3.12; validates epistemic/acquisition fixtures, source-audit qualifications, frozen data, research tasks, and collaboration lifecycle; builds the transaction materialization; revalidates materialized data, tasks, publication identity and index; requires audit manifests; then rebuilds and byte-compares the deterministic semantic manifest. It does **not** publish site pages. Its paths include fixtures, schemas and qualification directories absent from the `build-site.yml` trigger set. Both workflows must be inventoried before I1 closure.

| Additional validator | Inspected contract | Classification |
| --- | --- | --- |
| `validate_epistemic_fixtures.py` | Validates fixture schema, uniqueness, required named regression objects and acquisition scenario classes | **Golden fixture metadata**, intentionally pinned reference coverage |
| `validate_source_audits.py` | Discovers all `qualifications/source-audits/*.json`; checks proposition schema-fit, inheritance, evidence and action constraints | **Dynamic qualification validation**, not object-page scope |
| `validate_research_tasks.py` | Iterates all tasks from selected canonical/materialized data; validates status, target references, lineage exceptions and evidence-effect rule | **Dynamic task validation**; fixed predecessor IDs are explicit lineage exceptions, not page enumeration |
| `validate_collaboration_lifecycle.py` | Replays transaction task transitions and resolving review records; exercises valid and missing-review fixtures | **Dynamic lifecycle + synthetic regression**, not object-page scope |

**Updated sequencing:** preserve golden regression cases unchanged while adding generic derived-scope counterparts where they do not cover new published objects. In particular, migrate EPI-005 rendered conflict coverage separately from frozen EPI-005 conflict inventory. Do not design the fourth-object harness until the workflow-wide validator inventory is complete; assert the specific failure source and diagnostic in each negative case. This batch is source inspection, not execution evidence.
