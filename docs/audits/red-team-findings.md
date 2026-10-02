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
