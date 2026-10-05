# JS object driver contract

This document supplements `js-object-renderer-parity.md` for unit #60 and supersedes its earlier one-materialized-input inventory. The renderer driver has exactly two positive input categories and no side channel.

## Declared inputs

Materialized datasets, read only from `build/data/`: `entities`, `assertions`, `assertion_evidence`, `sources`, `research_tasks`, `predicate_rules`, `object_overviews`.

Static configuration, read only from `data/`: `publication_dependency_rules`, `publication_status_rules`, `external_records`.

The loader resolves logical names only through `lib/renderer-input-policy.mjs`; callers cannot supply paths, directories, environment overrides, or CLI input overrides. The entry point verifies the complete 7 + 3 logical-name set before loading anything.

The orchestrator accepts already-loaded values and an output root. It performs no input I/O. Its only filesystem writes are contained beneath that output root. Production invokes it with the fixed root `build/js-site/`; tests may use a temporary output root with in-memory synthetic inputs.

All inputs and eager contexts are loaded/validated before any page is rendered. This is the JS driver boundary; exact cross-stage Python exception precedence is not a parity claim.

Published objects and routes come only from `publishedObjects()` / `pathFor()`. A published object that cannot be resolved is fatal. Production has no hard-coded object IDs or routes and does not read Python-rendered HTML. The CI driver runs after materialization and before Python publication/staging so `site/` and Python determinism snapshots are not renderer inputs.
