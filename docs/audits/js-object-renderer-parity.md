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
8. Page content comes only from materialized structured datasets declared in `lib/renderer-input-policy.mjs` and shared templates. Policy entries pair a stable logical dataset name with its current materialized path; the first declared dataset is `object_overviews` → `build/data/object-overviews.json`. Transaction and migration files remain upstream inputs to materialization and are not renderer inputs. Changes to the materialized-dataset policy require review and a matching update to this contract. Renderer code must not copy or embed oracle/Python-rendered HTML or fragments from it, hard-code object-specific content that belongs in structured data, or branch on object identity to patch parity differences.
9. Before this PR leaves draft, scan renderer/template source for every published object's canonical name, slug, and entity ID. Any hit must be justified as non-content test/fixture data; production renderer/template hits fail the branch contract.
10. Rendered fragments are opaque after creation: they may be concatenated or interpolated into construction-time templates, but renderer code must not search, slice, regex-match, split, or rewrite rendered HTML. Transformations such as escaping are permitted only on data before it becomes rendered HTML. The mutation-pattern scan is a heuristic tripwire, not a proof; `escapeHtml()` is an explicit reviewed exception because it transforms input data rather than rendered output.
11. `epistemicsByAssertion` and `taskHtml` are temporary migration placeholders in `renderObjectPage()`. They are not approved long-term inputs: 64b replaces the epistemic HTML input with structured data and internal rendering; 64c does the same for task HTML.
12. The branch is ready for review only after all published objects satisfy parity and static-completeness gates in CI and the object-specific-literal scan is clean.
13. Overview reconciliation preserves Python's failure semantics while adding JS type structure. Every semantic condition represented by the frozen mapping in `tests/overview-error-inventory.mjs` must abort rendering/building in JS as the corresponding Python condition does. `OVERVIEW_ERROR_CONDITIONS` is the single mapping authority for explicit Python raise site/condition → JS typed condition; this contract does not duplicate that condition list. Python also aborts implicitly on missing required mapping keys (`KeyError`) and invalid joined date values (`TypeError`); JS must preserve those aborts with `MissingRequiredFieldError` carrying `site: implicit:<field>`. These implicit sites are intentionally outside the explicit-raise inventory tripwire. Exact exception-message wording and Python's generic exception types are not parity requirements. A change in the frozen explicit Python raise-site set is a review event, not a reason to renumber site IDs until the inventory test passes.

Golden-file freezing remains deferred until Python retirement.
