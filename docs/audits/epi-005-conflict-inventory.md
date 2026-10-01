# EPI-005 material-conflict inventory

Canonical conflict means an assertion-evidence relationship explicitly uses `evidence_role = CONTRADICTS`; no conflict is inferred from source plurality, `QUALIFIES`, uncertainty, or wording variation alone.

The repository uses a frozen seed dataset plus ordered transactions. Publication is built from the **transaction-materialized** database, so that state controls the public conflict inventory. The frozen seed remains separately checked to detect unintended mutation of the baseline.

| Object | Frozen seed | Materialized publication state | Control treatment |
|---|---:|---:|---|
| Artigas (`OBJ-0001`) | 0 | 1 (`A-0004`) | Smithsonian's Montevideo-predecessor description conflicts with the canonical San José de Mayo physical lineage after `TX-20260929-002`; the public assertion must be visibly qualified and traceable. |
| San Martín (`OBJ-0002`) | 1 (`A-0106`) | 1 (`A-0106`) | Daumas/Dumont disagreement must remain visibly qualified and traceable; multiple contradictory evidence rows may attach to the same assertion. |
| Cuban Urn (`OBJ-0003`) | 2 (`A-0201`, `A-0201B`) | 2 (`A-0201`, `A-0201B`) | Government-of-Cuba / citizens-of-Cuba donor disagreement must remain visibly qualified and traceable in both canonical formulations. |

`scripts/validate_epi005_conflict_inventory.py` locks the frozen baseline. After transactions are materialized and staged into `site/data`, `scripts/validate_epi005_rendered_conflicts.py` derives the expected conflict set directly from that publication dataset and requires an exact canonical-to-rendered match. This separation prevents a stale seed-data assumption from suppressing a conflict introduced by a valid transaction.
