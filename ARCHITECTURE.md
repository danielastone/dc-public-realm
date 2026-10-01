# Transparent static publication architecture

## Decision

This project publishes **materialized static views over canonical JSON**.

The browser is not an application runtime. Core content must be readable, navigable, accessible, and inspectable with JavaScript disabled.

```text
canonical JSON
    -> validate epistemic rules
    -> materialize views once
    -> semantic HTML + shared CSS
    -> optional progressive-enhancement JavaScript
    -> deploy static files
```

## Non-goals

Do not introduce a client framework, hydration, client-side templates, a runtime API, a browser database, or object-specific rendering code unless a demonstrated requirement cannot be met by the architecture above.

Do not move epistemic computation into JavaScript. Publication status, evidence ownership, source lineage, conflicts, citations, and research-task relationships are resolved before publication.

## Publication contract

The rendered DOM is a transparent public view, not a second database. Stable semantic hooks join the view back to canonical records.

### Object

Every object page exposes one root object identity through `data-object-id` and renders its canonical name and country in ordinary HTML.

### Assertion

Every published assertion is an `<article class="assertion">` with:

- `data-assertion-id`
- `data-computed-status`
- `data-status-rule` when a publication rule applies

The assertion text and public status are visible without JavaScript.

### Evidence

Evidence is ordinary HTML inside the owning assertion. Each evidence group has explicit assertion ownership. Source rows expose stable source identity where available. Evidence role, locator, and source-lineage explanation remain visible text; canonical JSON remains authoritative for the complete machine record.

### Conflicts and lineage

Material conflicts and claim ancestry are visible in the static document. JavaScript may reveal, filter, or visualize them, but may not determine whether they exist.

### Research tasks and external records

Tasks and external records are materialized from canonical data and linked to stable identifiers. Adding a new object must not require a new renderer, workflow step, CSS rule, or JavaScript branch.

## Presentation contract

Presentation markup is disposable. Validators and transforms must not depend on headings, prose labels, CSS layout, section order, or object-specific insertion points when a semantic identifier can be used instead.

One shared stylesheet provides the baseline UI. Object pages must remain usable at narrow mobile widths and with browser text enlargement.

Native HTML is preferred over custom interaction: links, headings, lists, `<details>`, and form controls before JavaScript widgets.

## JavaScript budget

JavaScript is optional progressive enhancement.

- Required JS for reading and navigation: **0 bytes**.
- Initial first-party JS budget: **20 KB uncompressed total**.
- No framework or hydration runtime.
- No ordinary object-page network request is required after HTML load.
- URL/hash and DOM state are preferred over custom state management.

Suitable JS: filtering, expand/collapse-all, citation copying, lightweight search, and optional provenance visualization.

Unsuitable JS: joining canonical records, computing status, assigning evidence, resolving lineage, detecting conflicts, generating core prose, or deciding what is published.

## Materializer requirements

The materializer performs joins once at build time and emits finished semantic HTML. It should converge toward one small shared path for object views and separate small view functions only where the information architecture is genuinely different (for example country indexes or task pages).

Post-render scripts that change object semantics are transitional debt. Each should be moved into materialization or deleted. Site-wide deployment/navigation transforms may remain only when they do not reinterpret object data.

## Zero-code object test

The architecture is not considered generalized until a synthetic fourth object can be added using canonical data only and produces a valid publication with:

- assertions and statuses;
- multiple evidence sources;
- at least one inherited source lineage;
- a material conflict or contested assertion;
- an unresolved lineage case;
- a research task;
- an external record.

The fixture must require **zero changes** to Python, JavaScript, CSS, workflow YAML, or HTML templates.

## Build target

The intended steady-state pipeline is:

```text
validate canonical data
        -> materialize static views
        -> validate publication invariants
        -> deploy
```

A new validator is not a substitute for removing a transformation. Prefer fewer mutation points and stronger invariants over accumulating compatibility checks.

## Architectural test for future changes

Before adding technology, ask:

1. Can native HTML/CSS satisfy the requirement?
2. Can the value be materialized at build time?
3. If interaction is necessary, can a small dependency-free ES module enhance the existing DOM?
4. Does the change preserve zero-JavaScript correctness and canonical-data authority?
5. Would adding another object require code changes?

If a proposed dependency fails these tests, it needs a concrete requirement strong enough to justify the additional architecture.