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

## RT-2026-10-02-03 — Whole-file workflow rewrites can silently reduce CI coverage

- **Found:** 2026-10-02 while adding object-page parity and determinism gates.
- **Status:** Fixed on `js-object-page-parity`; standing process control adopted.
- **Defect:** a complete rewrite of `.github/workflows/build-site.yml` changed the `Validate public image rights metadata` command to `check_image_urls.py` and removed the separate `Validate image provenance URLs` step. CI could therefore have gone green with less validation coverage.
- **Fix:** restored both main-branch steps exactly, then limited branch workflow changes to the two intended parity/determinism steps.
- **Standing rule:** after any workflow edit, diff the complete workflow against `main` and enumerate every added, removed, or command-changed step before accepting the change.
- **Verification rule:** after CI runs, confirm each restored/added step appears in the job step log as executed successfully; YAML presence alone is insufficient.
- **Future hardening:** if automated, protect the expected step-name → command mapping rather than step names alone; a name-only check would not detect command substitution.
- **Impact:** caught before merge; no reduction in `main` CI coverage occurred.

## RT-2026-10-03-01 — Overview raise-site scanner miscounted its frozen oracle

- **Found:** 2026-10-03 while freezing the Python `render_overview()` error-condition inventory for the JS renderer migration.
- **Status:** Fixed on `js-object-renderer-parity` in commit `4a1fa59`; the corrected 11-site set is frozen.
- **Defect:** the first simple source scanner bounded function blocks incorrectly and did not reliably exclude nested helper bodies from the enclosing `render_overview()` scan. The instrumentation therefore miscounted/misattributed raise sites even though the Python source and hand-compiled condition table were unchanged.
- **Detection:** the declared-site set and scanner-discovered set disagreed. The migration's stop-and-inspect rule treated that discrepancy as an instrumentation defect to investigate rather than evidence that the table should be renumbered.
- **Fix:** function blocks now end at the first non-blank line at the same or lesser indentation, and nested `def` bodies are skipped while scanning an enclosing function. The corrected local run discovers exactly 11 sites, the declared table contains exactly 11 unique sites, and the sets are equal.
- **Standing rule:** a change in the discovered raise-site set is a review event. Do not renumber `helper#ordinal` IDs merely to make the tripwire green. The scanner remains a heuristic for inventory completeness, not proof that semantic mappings are correct.
- **Evidence:** frozen sites are `render_overview#1`–`render_overview#7`, `refs#1`–`refs#2`, `require_subject#1`, and `fact#1`; duplicate declared IDs: none; exact set comparison: equal.
- **Impact:** no renderer or publication behavior was affected. The defect was confined to migration instrumentation and was caught before the tripwire entered CI.


## RT-2026-10-04-01 — Synthetic base-page fixture hid dropped status reasons

- **Found:** 2026-10-04 during the first full object-page diagnostic comparison for #175.
- **Status:** Fixed on `js-object-renderer-parity`; regression coverage added.
- **Defect:** `computeStatus()` already returned `[status, reason]`, but `deriveAssertions()` in `lib/render-tasks.mjs` destructured only the status and discarded the reason. `renderObjectPage()` later read `assertion.status_reason`, so all rendered status-reason spans became `undefined`.
- **Why the semantic test missed it:** the synthetic base-page fixture manually supplied `status_reason`, bypassing the upstream derivation boundary that production rendering uses.
- **Detection:** the preregistered #195 full-page diagnostic reported 36 otherwise-identical regions, all at `status-reason` spans. Tracing the producer boundary reduced them to one propagation defect rather than 36 renderer defects.
- **Fix:** preserve both values from `computeStatus()` as `computed_status` and `status_reason`; render object-page assertions with those derived fields; make the base-page semantic test derive them instead of supplying them manually.
- **Regression gate:** `tests/status-reason-parity.mjs` compares JS `(status, reason)` tuples for the full materialized corpus against Python's generated `site/data/assertions.json` after `build_publication.py`. The historical AUD-10 frozen status oracle remains unchanged and status-only.
- **Standing rule:** renderer fixtures must not manually provide fields that an upstream JS producer is responsible for computing when the purpose of the test is to exercise that producer-renderer boundary.
- **Impact:** caught before JS publication cutover. The first diagnostic showed every other #175-owned object-page region byte-identical; only status reasons were wrong.
