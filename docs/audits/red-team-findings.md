# Red-team findings register

## RT-2026-10-02-01 — JS publication ordering used locale-sensitive comparison

- **Found:** 2026-10-02 during JS↔Python publication-index parity work.
- **Introduced:** PR #74 (`lib/publication-index.mjs`).
- **Status:** Fixed on `js-object-render-parity`; inert on `main` because no production path consumed the JS index.
- **Contract:** Python `published_objects()` sorts `entity_id` with `sorted(..., key=lambda e: e["entity_id"])`, i.e. Unicode code-point string order. The JS port must not use `localeCompare` or `Intl.Collator`.
- **Fix:** relational string comparator plus an executable printable-ASCII ID precondition in the cross-language parity test.
- **Detection:** parity-first migration review before any JS renderer consumed the index.
- **Regression gate:** `tests/publication-index-parity.mjs` compares ordered entity IDs, slugs, paths, hrefs, and featured object against the read-only Python dump adapter using the same materialized `build/data`.
- **Impact:** latent only; no rendered publication output was affected.

## RT-2026-10-02-02 — Merge gate is procedural, not platform-enforced

- **Found:** 2026-10-02 while validating the publication-index parity gate.
- **Status:** Accepted risk for the current sole-reviewer workflow.
- **Observed control state:** repository rulesets API returns no rulesets. Classic branch-protection status checks could not be verified through the GitHub integration because that endpoint returned 403 (insufficient integration permission).
- **Risk:** a failing CI check can remain mergeable unless `main` separately requires the workflow/job through classic branch protection or a ruleset.
- **Current control:** do not merge critical-path PRs unless the relevant CI workflow is green; treat green CI as a manual merge gate.
- **Owner follow-up:** verify Settings → Branches/Rules for `main`; optionally require the build status check so the platform enforces the gate.
- **Scope:** governance only; does not affect publication output or parity semantics.
