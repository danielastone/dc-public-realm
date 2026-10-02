# Web architecture roadmap

## Objective

The public site is a **static publication of canonical research data**, not a web application.

The architecture optimizes for:

- epistemic transparency;
- low long-term maintenance cost;
- zero-JavaScript correctness;
- predictable performance on mobile and low-bandwidth connections;
- accessibility and archival durability;
- data-only addition of future objects;
- minimal custom code.

The target is deliberately boring:

```text
canonical data
  -> validate
  -> derive publication model
  -> materialize static views
  -> validate invariants
  -> deploy static files
```

No runtime API, database, framework, hydration layer, or client-side data join is part of the core system.

---

## 1. Architectural layers

### Layer A — Canonical research data

**Location:** `data/`, `transactions/`, schemas and controlled migrations.

Owns facts and research state:

- entities;
- assertions;
- assertion-evidence edges;
- sources;
- research tasks;
- external records;
- publication rules;
- object overview data;
- localization metadata.

Rules:

1. Canonical records contain no HTML.
2. Canonical records contain no page-layout assumptions.
3. Object identity, country, slug, relationships, and publication eligibility must come from data, not Python constants.
4. No browser code may reinterpret canonical research state.
5. Every public semantic state must be reproducible from versioned canonical inputs.

### Layer B — Derived publication model

This is the only layer allowed to perform joins and publication derivation.

It resolves, once at build time:

- object -> assertions;
- assertion -> evidence;
- evidence -> source;
- assertion -> computed publication status;
- source -> effective lineage/dependency state;
- assertion -> material conflict state;
- object -> research tasks;
- object/person -> external records;
- object -> overview and media metadata.

The output should be plain Python data structures. It must not contain presentation markup.

Long-term target:

```text
load_canonical_data()
derive_publication_model()
materialize_views()
```

Avoid separate scripts that independently re-derive overlapping semantic state.

### Layer C — Static view materialization

A single small materializer converts the publication model into semantic HTML.

View families may differ only when their information architecture differs:

- object view;
- country/index view;
- research-task view;
- methodology/data view;
- collaboration/review utility views.

All objects use one object-view function.

The materializer owns:

- page titles and headings;
- semantic HTML structure;
- stable data hooks;
- public status text;
- source/evidence blocks;
- conflict and lineage presentation;
- research-task presentation;
- external-record presentation;
- canonical-data links.

The materializer does **not** own epistemic decisions.

### Layer D — Shared presentation

**CSS:** one shared first-party stylesheet for public pages.

Principles:

- system fonts first;
- responsive layout without JavaScript;
- native document flow;
- accessible contrast and focus states;
- `details/summary`, lists, links, headings, tables before widgets;
- no object-specific style branches.

A small number of page-family classes is acceptable. Object IDs must never appear in CSS selectors.

### Layer E — Optional progressive enhancement

JavaScript is an enhancement over an already-complete document.

Allowed examples:

- expand/collapse all evidence;
- status/source filtering;
- copy citation or stable record link;
- lightweight client-side text search over the already-rendered page;
- optional provenance visualization derived from semantic DOM hooks.

Not allowed:

- loading core assertions after page load;
- joining canonical JSON in the browser;
- computing publication status;
- resolving lineage;
- detecting conflicts;
- deciding which evidence belongs to which assertion;
- generating core page prose;
- hiding required content behind JavaScript.

---

## 2. Dependency rule

Dependencies flow in one direction only:

```text
canonical data
    ↓
publication model
    ↓
materializer
    ↓
semantic HTML
    ↓
CSS / optional JS enhancement
```

A lower layer may not become an input to a higher layer.

Examples:

- Validators may inspect semantic HTML, but HTML may not become canonical evidence.
- JavaScript may read `data-assertion-id`, but Python publication logic may not depend on JavaScript output.
- CSS class names may change without changing research semantics.
- Page headings may change without breaking semantic validators.

This rule is the main defense against repeating the former Artigas-specific renderer problem.

---

## 3. Semantic DOM contract

The DOM is a transparent publication surface, not the database.

### Object root

Each object page must expose:

```html
<main data-object-id="OBJ-0001">
```

or an equivalent single authoritative object hook.

Required visible HTML:

- canonical name;
- country/context;
- overview;
- assertions;
- evidence;
- research tasks when present;
- external records when present.

### Assertion

```html
<article
  class="assertion"
  data-assertion-id="A-0004"
  data-computed-status="CONTESTED"
  data-status-rule="STATUS-..."
>
```

Status text is visible without JS.

### Evidence group

```html
<details
  class="evidence"
  data-evidence-assertion-id="A-0004"
  data-source-count="3"
>
```

### Source row

Where a canonical source exists:

```html
<div
  class="source-row"
  data-source-id="SRC-..."
  data-evidence-role="CONTRADICTS"
  data-claim-origin="INHERITED"
>
```

Only stable semantic identifiers belong in `data-*`. Presentation state does not.

### Conflict

A material conflict must have an explicit semantic hook associated with the assertion. The validator must not infer conflict existence from colors, headings, prose phrases, or section order.

### Research task

Each task gets one stable task identifier in the DOM and a normal link to its materialized task page.

### External record

Each external record is visible ordinary HTML with system, identifier, relationship, and URL. It is discovery/interoperability metadata unless explicitly linked as assertion evidence.

---

## 4. URL architecture

URLs should be boring, stable, and independent of JavaScript.

Target:

```text
/
  objects/<slug>/
  countries/<country-slug>/
  tasks/<task-id>/
  collaborate/
  methodology/
  data/
  review/<review-product>/
```

Rules:

- URLs are materialized files/directories.
- Internal navigation is normal `<a href>`.
- Hash fragments may target stable assertion/task sections.
- Object slugs are canonical publication metadata, not hard-coded Python dictionaries.
- A changed display name must not automatically change the slug.

---

## 5. Repository architecture target

The eventual repository should trend toward:

```text
data/
schemas/
transactions/

scripts/
  build_database.py
  validate_data.py
  materialize_site.py
  validate_publication.py

site/                 # generated, not authored
  assets/
    style.css
    site.js            # optional, dependency-free
  objects/
  countries/
  tasks/
  methodology/
  data/

docs/
  WEB-ARCHITECTURE.md
```

This is a target shape, not an immediate rename mandate.

The current numerous publication scripts are transitional debt. They should be retired by capability, not mechanically combined into one enormous file.

---

## 6. Build pipeline target

### Current problem

The present workflow materializes HTML and then performs many semantic mutations:

- overview injection;
- external-record injection;
- status stamping;
- status-rule injection;
- dependency-state publication;
- lineage publication;
- material-conflict publication;
- canonical-link preservation;
- navigation enforcement;
- task-count reconciliation.

Every mutation point creates another possible stale or cross-object state.

### Target pipeline

```text
1. validate canonical source data
2. materialize canonical transaction database
3. derive publication model
4. materialize all static views
5. validate publication invariants
6. deploy
```

Object semantics must be complete at step 4.

After materialization, no script should alter assertion/evidence/status/lineage/conflict semantics.

Site-wide packaging is acceptable after materialization only when it is semantically inert.

---

## 7. Performance budgets

These are guardrails, not optimization theater.

### Runtime

- Core page use requires **0 bytes of JavaScript**.
- No object page requires a runtime API request.
- No client framework.
- No hydration.
- No web fonts required.
- No third-party analytics blocking first render.

### First-party assets

Initial targets:

- JS: <= 20 KB uncompressed total for the entire public site.
- CSS: <= 30 KB uncompressed shared stylesheet.
- Per-page authored HTML should contain only the materialized view needed for that page.
- Images must use explicit dimensions where known and appropriate browser-native lazy loading for below-the-fold media.

### Caching

Static assets should be cacheable. If asset fingerprinting is eventually needed, prefer the smallest mechanism supported by the hosting/build system; do not introduce a bundler solely for hashing.

### Build performance

Prefer linear passes over canonical collections and precomputed indexes:

```python
assertions_by_subject
evidence_by_assertion
sources_by_id
tasks_by_object
external_records_by_entity
```

Avoid repeated scans inside nested rendering loops when the corpus grows.

---

## 8. Accessibility and resilience

The static document must work under:

- JavaScript disabled;
- CSS disabled;
- keyboard-only navigation;
- narrow mobile viewport;
- browser text zoom;
- screen-reader document navigation;
- copied/archived HTML viewed outside the original site.

Requirements:

- one logical `h1`;
- ordered heading hierarchy;
- meaningful link text;
- native controls wherever possible;
- visible focus states;
- no information encoded only by color;
- conflict/status labels represented as text;
- images have appropriate alt treatment;
- interactive enhancement preserves native semantics.

---

## 9. Future-proof extension strategy

### New objects

A new object must enter through canonical data.

The renderer discovers publishable objects from data. No new:

- Python object list;
- slug dictionary;
- country dictionary;
- workflow step;
- CSS branch;
- JS branch.

### New evidence types

Add schema/data semantics first. The materializer should render unknown-but-valid evidence roles conservatively as labeled metadata rather than fail because of styling assumptions.

### Localization

Localization should remain a data/presentation concern, not fork the renderer. Locale-specific views may be materialized later from the same publication model.

### Search

Do not add a backend search service initially.

Sequence:

1. browser/find and navigation;
2. small prebuilt static search index if corpus growth makes it necessary;
3. only consider hosted search when static indexing is demonstrably inadequate.

### Maps and spatial features

If geographic visualization becomes useful, keep coordinates canonical and materialize the textual location first. A map is optional enhancement, never the only representation of location.

### APIs

The canonical JSON publication is already the machine-readable interface.

Do not create an API server until there is a concrete need for dynamic queries or authenticated writes.

---

## 10. Architecture acceptance tests

### A. Zero-code fourth object

A synthetic `OBJ-0004` must materialize using data only and include:

- name/country/slug;
- assertions;
- verified/supported/contested or unresolved state;
- multiple evidence rows;
- inherited lineage;
- material conflict;
- research task;
- external record.

No changes to code, workflow, CSS, or JS are allowed.

### B. Zero-JS correctness

Automated build inspection must prove that all core object content exists in generated HTML before JS execution.

### C. Semantic selector test

Publication validators may use stable semantic attributes and identifiers. They must not depend on exact prose, layout order, or CSS class combinations beyond the minimal semantic contract.

### D. No post-render semantic mutation

CI should eventually fail if a workflow step after materialization rewrites assertion/evidence/status/lineage/conflict structures.

### E. Asset budget

CI may later enforce JS/CSS byte budgets once those assets stabilize.

---

## 11. Migration sequence

### Phase 1 — Generalize object discovery

Remove hard-coded object, country, and slug dictionaries from the materializer. Move publication metadata into canonical data/schema.

### Phase 2 — Establish publication model

Centralize joins and publication derivations into one build-time model consumed by every view.

### Phase 3 — Prove OBJ-0004

Add the synthetic data-only object and make it pass without renderer changes.

### Phase 4 — Absorb semantic post-processing

Move, in this order:

1. canonical status metadata;
2. evidence ownership/source identity;
3. dependency/lineage state;
4. material conflicts;
5. object overview;
6. research-task counts/links;
7. external records.

Each move should delete or reduce a post-render script.

### Phase 5 — Collapse CI

Replace chains of mutation-specific checks with:

- canonical validation;
- materialization;
- invariant validation;
- targeted epistemic regression tests.

Keep high-value mutation tests where they prove the invariant rather than the implementation.

### Phase 6 — Progressive enhancement

Only after the static architecture is complete, add small JavaScript for demonstrated interaction needs.

---

## 12. Technology decisions

### Keep

- GitHub Pages / static hosting;
- Python standard library for build/validation while sufficient;
- JSON canonical records;
- semantic HTML;
- plain CSS;
- native browser controls;
- vanilla ES modules only when needed.

### Avoid by default

- React, Vue, Svelte, Angular;
- Next.js, Nuxt, Remix;
- client-side templating;
- Node build chain;
- npm dependency graph;
- Tailwind or CSS-in-JS;
- runtime database;
- runtime API;
- GraphQL layer;
- SPA routing;
- component library;
- browser state store.

Any future introduction of one of these requires a written requirement showing why static materialization + native web platform cannot meet it.

---

## 13. Definition of architectural completion

The corrective architecture is complete when:

1. all object pages are produced by one shared materializer;
2. object enumeration is data-driven;
3. OBJ-0004 passes as data-only input;
4. object semantics are complete immediately after materialization;
5. no post-render script mutates object epistemic state;
6. core pages work with JS disabled;
7. CSS and optional JS are shared and object-agnostic;
8. publication validation uses semantic hooks rather than presentation markup;
9. CI approximates validate -> materialize -> validate -> deploy;
10. adding a normal fifth object is a data/research task, not a web-engineering task.

That is the performance and maintainability target against which implementation work should now be judged.
