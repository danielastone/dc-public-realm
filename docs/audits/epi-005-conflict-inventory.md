# EPI-005 material-conflict inventory

Generated control baseline for the three alpha reference objects. Canonical conflict means an assertion-evidence relationship explicitly uses `evidence_role = CONTRADICTS`; no conflict is inferred from source plurality, `QUALIFIES`, uncertainty, or wording variation alone.

| Object | Canonical conflict assertions | Control treatment |
|---|---:|---|
| Artigas (`OBJ-0001`) | 0 | Negative control: no public material-conflict warning may be invented. |
| San Martín (`OBJ-0002`) | 1 (`A-0106`) | Daumas/Dumont disagreement must remain visibly qualified and traceable. |
| Cuban Urn (`OBJ-0003`) | 2 (`A-0201`, `A-0201B`) | Government-of-Cuba / citizens-of-Cuba donor disagreement must remain visibly qualified and traceable in both canonical formulations. |

This inventory is enforced mechanically by `scripts/validate_epi005_conflict_inventory.py`; it is not a manually maintained publication source. If canonical conflict state changes, the validator must force an explicit review of this baseline rather than allowing the public presentation to drift silently.
