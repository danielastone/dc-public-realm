# Fourth-object harness — findings (2026-10-18)

Harness: `tests/fourth-object/` (see its README). Base: `main` @ `32f5f42`.
Evidence: `tests/fourth-object/results/results.json` (two runs, byte-identical).
OBJ-9104 is a synthetic structural clone of OBJ-0003; S0 is a simulated
publisher (one temp-only change to the legacy builder's object list).

## Publication controls

| Control | Result |
|---|---|
| Clean reference | 60/60 steps |
| Unpatched builder + OBJ-9104 | 39/60; publication exit 1 `KeyError: 'OBJ-9104'` (the fixture's research tasks reach the builder's fixed slug map first; a minimal fixture without tasks failed instead with `FileNotFoundError` on the missing page) |
| S0 (temp-patched builder) | 57/60; 28 files; three real object pages byte-identical to the clean build; OBJ-9104 Python final page byte-identical to the JS page |

**S0 baseline failures — expansion blockers / migration dependencies** (unchanged
by this work; not row outcomes):
1. `tests/object-page-driver.mjs` — fixed published-object count (`4 !== 3`).
2. `tests/status-golden.mjs` (AUD-10) — golden assertion set; the fixture's
   assertions appear as `extra`. Golden by design; needs an intentional-change
   policy, not weakening.
3. DATA-002 — homepage card set must equal the three fixed IDs.

## Matrix (OBJ-9104 vs positive control on OBJ-0003)

| Row | Defect | Intended validator | OBJ-9104 | Positive control | Other gates newly failing on OBJ-9104 |
|---|---|---|---|---|---|
| D1 | object page deleted | PUB-001 | INTENDED_REJECT | INTENDED_REJECT | consistency, PUB-002/003/004 (+ method artifacts) |
| D2 | assertion render removed | DATA-001 | **UNEXPECTED_ACCEPT** | INTENDED_REJECT | **publication consistency** (+ method artifacts) |
| D3 | wrong computed status | EPI-001 | **UNEXPECTED_ACCEPT** | INTENDED_REJECT | **publication consistency** (+ method artifacts) |
| D4 | dependency state altered | EPI-002 | **UNEXPECTED_ACCEPT** | INTENDED_REJECT | method artifacts only |
| D5 | uncertainty qualifier dropped | EPI-003 | **UNEXPECTED_ACCEPT** | INTENDED_REJECT | method artifacts only |
| D6 | lineage terminal label altered | EPI-004 rendered | **UNEXPECTED_ACCEPT** | INTENDED_REJECT | method artifacts only |
| D7a | conflict warning removed | EPI-005 rendered | **UNEXPECTED_ACCEPT** | INTENDED_REJECT | method artifacts only |
| D7b | warning moved after lineage | EPI-005 placement | **UNEXPECTED_ACCEPT** | **UNEXPECTED_ACCEPT — DISCREPANCY** | method artifacts only |
| D8 | blank `location_source_url` | overview (materialized) | INTENDED_REJECT | INTENDED_REJECT | PR #80 sensitivity step |
| D8b | CC rights, no license URL | image rights (materialized) | INTENDED_REJECT | INTENDED_REJECT | PR #80 sensitivity step |
| D9 | wrong homepage card name | DATA-002 | BLOCKED (fails on S0 baseline) | INTENDED_REJECT | — |
| D10 | broken internal link | PUB-004 | INTENDED_REJECT | INTENDED_REJECT | method artifacts |
| D11 | primary nav removed | PUB-002 | INTENDED_REJECT | INTENDED_REJECT | method artifacts |
| D12 | orphan object page | PUB-001 | INTENDED_REJECT | INTENDED_REJECT | final parity |

"Method artifacts" = Python determinism and final JS↔Python parity, which
catch any post-render edit by construction (see README). D8/D8b also fail the
PR #80 sensitivity step: that test copies the workspace's `transactions/`, so its
CONTROL case inherits the invalid ledger record and correctly fails. It is a
secondary detector, not the intended control.

27 of the 28 mutation-row outcomes (14 rows × OBJ-9104 and positive control)
match expectations; the 8 S0 baseline rows all match.

## Findings

1. **Scope gaps confirmed by execution (I4 checklist).** EPI-001, EPI-002,
   EPI-003, EPI-004 rendered, EPI-005 rendered and DATA-001 each catch their
   defect on OBJ-0003 but accept it on OBJ-9104. For D2 and D3 a derived
   validator (publication consistency) still catches the fourth-object defect;
   for **D4, D5, D6 and D7a nothing outside the post-render method artifacts
   does** — those are the real coverage holes once the builder list is made
   dynamic.
2. **Validator defect (production, all objects): EPI-005 warning placement is
   fail-open.** `scripts/validate_epi005_warning_placement.py` line 18 searches
   for `class="claim-lineage" data-assertion-id="…"`; the rendered markup is
   `class="claim-lineage" data-for-assertion-id="…"` (0 vs 15 occurrences on
   the OBJ-0003 page). `trace` is therefore always −1 and "warning hidden after
   provenance disclosure" can never be reported. D7b's positive control proves
   it on a real object. Not fixed here (no validator changes authorized);
   recommended as a separate, narrowly scoped PR with its own sensitivity test.
3. **Controls that work for a fourth object today:** PUB-001 (missing and
   orphan pages), PUB-002, PUB-004, the materialized overview and image-rights
   validators (PR #80), and publication consistency for status/identity.
4. **Expansion blockers** are the three S0 baseline failures above; DATA-002
   additionally prevents evaluating its own summary check for a fourth object
   (D9 BLOCKED).

## Sequencing implications

Before `build_site.py`'s object list is generalized: fix the EPI-005 placement
selector; convert EPI-002/003/004-rendered/005-rendered (and DATA-001, EPI-001)
to derived scope while keeping their golden expectations; replace the
object-page-driver fixed count and the DATA-002 card-set check with derived
equivalents; define the AUD-10 golden-set change policy. Each D4–D7a row should
flip to INTENDED_REJECT on this harness when its validator is migrated.
