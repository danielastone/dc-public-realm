# JS object renderer parity — branch contract

Branch: `js-object-renderer-parity`

This file exists to make the migration branch visible to pull-request CI before renderer code is added.

## Acceptance contract

1. Python production code, Python validators, deployment behavior, and the existing DOM contract remain unchanged.
2. JS renderer output is written only under `build/`; it is never written into `site/` on this branch.
3. Artigas is the first implementation target, but merge acceptance covers every published object enumerated by `publishedObjects()` / `pathFor()`.
4. Every JS object page must match the final Python object page under only the normalization rules already recorded in `docs/audits/html-parity-normalization.md`.
5. A mismatch is a renderer defect unless a new normalization is separately justified and recorded; comparison is not loosened merely to obtain parity.
6. Static completeness is durable: required page content — title, image, provenance fields, and navigation — must exist in prerendered HTML. Runtime JavaScript must not be required to populate it.
7. Current-state check: generated object pages contain no `<script>` elements. This is not a permanent ban on progressive enhancement.
8. The branch is ready for review only after all published objects satisfy parity and static-completeness gates in CI.

Golden-file freezing remains deferred until Python retirement.
