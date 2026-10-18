# Fourth-object harness results

- Clean reference: 60/60 steps pass
- Unpatched control: 39/60; publication exit 1: `KeyError: 'OBJ-9104'`
- S0 (temp-patched): 57/60; 28 site files; real object pages identical to clean: True
- S0 baseline failures (kept separate from row outcomes):
  - Build and verify JS object-page driver: `AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:`
  - Verify AUD-10 JS status rule against frozen materialized oracle: `throw new Error(`golden assertion set changed; missing=${missing.join(',')} extra=${extra.join(',')}`);`
  - Verify DATA-002 canonical summary reconciliation: `DATA-002 FAIL: homepage object hooks differ from expected objects: ['OBJ-0001', 'OBJ-0002', 'OBJ-0003', 'OBJ-9104']`

Real repository unchanged: True

| Row | Side | Intended validator | Mutation reached | Base exit | Mutated exit | Computed | Expected | Discrepancy | Newly failing elsewhere |
|---|---|---|---|---|---|---|---|---|---|
| S0a-unpatched | baseline | Build publication from materialized database | — | — | {'Build publication from materialized database': 1} | BLOCKED | BLOCKED | no | — |
| S0a-patched | baseline | Build publication from materialized database | — | — | {'Build publication from materialized database': 0} | PASS | PASS | no | — |
| S0b | baseline | Validate materialized overview records | — | — | {'Validate materialized overview records': 0} | PASS | PASS | no | — |
| S0c | baseline | Validate overview data | — | — | {'Validate overview data': 0} | PASS | PASS | no | — |
| S0d | baseline | Verify DATA-002 canonical summary reconciliation | — | — | {'Verify DATA-002 canonical summary reconciliation': 1} | BLOCKED | BLOCKED | no | — |
| S0e | baseline | Verify PUB-001 canonical-data routes, Verify PUB-002 navigation contract, Verify PUB-003 research-task reconciliation, Verify PUB-004 internal link integrity, Verify publication status consistency, Verify final JS-Python object-page parity | — | — | {'Verify PUB-001 canonical-data routes': 0, 'Verify PUB-002 navigation contract': 0, 'Verify PUB-003 research-task reconciliation': 0, 'Verify PUB-004 internal link integrity': 0, 'Verify publication status consistency': 0, 'Verify final JS-Python object-page parity': 0} | PASS | PASS | no | — |
| S0f | baseline | Verify EPI-004 San Martin Daumas-Dumont conflict, Inventory EPI-005 canonical material conflicts, Validate rendered object overviews | — | — | {'Verify EPI-004 San Martin Daumas-Dumont conflict': 0, 'Inventory EPI-005 canonical material conflicts': 0, 'Validate rendered object overviews': 0} | PASS | PASS | no | — |
| S0g | baseline | Build and verify JS object-page driver, Verify AUD-10 JS status rule against frozen materialized oracle | — | — | {'Build and verify JS object-page driver': 1, 'Verify AUD-10 JS status rule against frozen materialized oracle': 1} | BLOCKED | BLOCKED | no | — |
| D1 | OBJ-9104 | Verify PUB-001 canonical-data routes | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify publication status consistency, Verify PUB-001 canonical-data routes, Verify PUB-002 navigation contract, Verify PUB-003 research-task reconciliation, Verify PUB-004 internal link integrity |
| D1 | positive-control OBJ-0003 | Verify PUB-001 canonical-data routes | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify publication status consistency, Verify EPI-001 public status rule contract, Verify EPI-002 rendered dependency state, Verify EPI-003 ancestry remains explicit, Verify EPI-004 rendered claim lineage, Verify EPI-005 rendered material conflicts, Verify EPI-005 warning placement, Verify DATA-001 exact rendered assertion reconciliation, Verify DATA-002 canonical summary reconciliation, Verify DATA-002 stale-summary mutation rejection, Verify PUB-001 canonical-data routes, Verify PUB-002 navigation contract, Verify PUB-003 research-task reconciliation, Verify PUB-004 internal link integrity |
| D2 | OBJ-9104 | Verify DATA-001 exact rendered assertion reconciliation | True | 0 | 0 | UNEXPECTED_ACCEPT | UNEXPECTED_ACCEPT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify publication status consistency |
| D2 | positive-control OBJ-0003 | Verify DATA-001 exact rendered assertion reconciliation | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify publication status consistency, Verify EPI-001 public status rule contract, Verify DATA-001 exact rendered assertion reconciliation |
| D3 | OBJ-9104 | Verify EPI-001 public status rule contract | True | 0 | 0 | UNEXPECTED_ACCEPT | UNEXPECTED_ACCEPT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify publication status consistency |
| D3 | positive-control OBJ-0003 | Verify EPI-001 public status rule contract | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify publication status consistency, Verify EPI-001 public status rule contract |
| D4 | OBJ-9104 | Verify EPI-002 rendered dependency state | True | 0 | 0 | UNEXPECTED_ACCEPT | UNEXPECTED_ACCEPT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity |
| D4 | positive-control OBJ-0003 | Verify EPI-002 rendered dependency state | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify EPI-002 rendered dependency state |
| D5 | OBJ-9104 | Verify EPI-003 ancestry remains explicit | True | 0 | 0 | UNEXPECTED_ACCEPT | UNEXPECTED_ACCEPT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity |
| D5 | positive-control OBJ-0003 | Verify EPI-003 ancestry remains explicit | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify EPI-003 ancestry remains explicit |
| D6 | OBJ-9104 | Verify EPI-004 rendered claim lineage | True | 0 | 0 | UNEXPECTED_ACCEPT | UNEXPECTED_ACCEPT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity |
| D6 | positive-control OBJ-0003 | Verify EPI-004 rendered claim lineage | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify EPI-004 rendered claim lineage |
| D7a | OBJ-9104 | Verify EPI-005 rendered material conflicts | True | 0 | 0 | UNEXPECTED_ACCEPT | UNEXPECTED_ACCEPT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity |
| D7a | positive-control OBJ-0003 | Verify EPI-005 rendered material conflicts | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify EPI-005 rendered material conflicts, Verify EPI-005 warning placement |
| D7b | OBJ-9104 | Verify EPI-005 warning placement | True | 0 | 0 | UNEXPECTED_ACCEPT | UNEXPECTED_ACCEPT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity |
| D7b | positive-control OBJ-0003 | Verify EPI-005 warning placement | True | 0 | 0 | UNEXPECTED_ACCEPT | INTENDED_REJECT | **YES** | Prove Python object-page build determinism, Verify final JS-Python object-page parity |
| D8 | OBJ-9104 | Validate materialized overview records | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Validate materialized overview records, Prove materialized overview validation sensitivity |
| D8 | positive-control OBJ-0003 | Validate materialized overview records | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Validate materialized overview records, Prove materialized overview validation sensitivity |
| D8b | OBJ-9104 | Validate materialized image rights | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Validate materialized image rights, Prove materialized overview validation sensitivity |
| D8b | positive-control OBJ-0003 | Validate materialized image rights | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Validate materialized image rights, Prove materialized overview validation sensitivity |
| D9 | OBJ-9104 | Verify DATA-002 canonical summary reconciliation | True | 1 | 1 | BLOCKED | BLOCKED | no | — |
| D9 | positive-control OBJ-0003 | Verify DATA-002 canonical summary reconciliation | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Verify DATA-002 canonical summary reconciliation |
| D10 | OBJ-9104 | Verify PUB-004 internal link integrity | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify PUB-004 internal link integrity |
| D10 | positive-control OBJ-0003 | Verify PUB-004 internal link integrity | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify PUB-004 internal link integrity |
| D11 | OBJ-9104 | Verify PUB-002 navigation contract | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify PUB-002 navigation contract |
| D11 | positive-control OBJ-0003 | Verify PUB-002 navigation contract | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Prove Python object-page build determinism, Verify final JS-Python object-page parity, Verify PUB-002 navigation contract |
| D12 | OBJ-9104 | Verify PUB-001 canonical-data routes | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Verify final JS-Python object-page parity, Verify PUB-001 canonical-data routes |
| D12 | positive-control OBJ-0003 | Verify PUB-001 canonical-data routes | True | 0 | 1 | INTENDED_REJECT | INTENDED_REJECT | no | Verify final JS-Python object-page parity, Verify PUB-001 canonical-data routes |

## Intended-validator diagnostics

- **D1 / OBJ-9104** (INTENDED_REJECT): `- missing published object page(s): ['synthetic-fixture-monument']`
- **D1 / positive-control OBJ-0003** (INTENDED_REJECT): `- missing published object page(s): ['cuban-american-friendship-urn']`
- **D2 / OBJ-9104** (UNEXPECTED_ACCEPT): `DATA-001 reconciliation PASS: OBJ-0001=8, OBJ-0002=8, OBJ-0003=15 canonical object assertions rendered exactly once.`
- **D2 / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003/A-0203: canonical object assertion missing from rendered page`
- **D3 / OBJ-9104** (UNEXPECTED_ACCEPT): `EPI-001 PASS: 63 canonical assertions checked; 5 status rules resolvable across three reference objects.`
- **D3 / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003/A-0203: computed status does not match canonical SUPPORTED`
- **D4 / OBJ-9104** (UNEXPECTED_ACCEPT): `EPI-002 rendering PASS: 11 multi-source assertions reconciled across three reference objects.`
- **D4 / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003/A-0203/AE-0211: expected dependency state INDEPENDENT`
- **D5 / OBJ-9104** (UNEXPECTED_ACCEPT): `EPI-003 PASS: 27 evidence relationships checked; 25 preserve explicit UNKNOWN ancestry.`
- **D5 / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003/AE-0205: empty inheritance list lost its uncertainty qualifier`
- **D6 / OBJ-9104** (UNEXPECTED_ACCEPT): `EPI-004 rendering PASS: 31 assertions / 47 evidence relationships traced across three reference objects.`
- **D6 / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003/A-0201/AE-0201: terminal Unresolved ancestry missing`
- **D7a / OBJ-9104** (UNEXPECTED_ACCEPT): `EPI-005 rendering PASS: 4 materialized canonical conflict assertions visibly qualified; no warning invented outside canonical conflict state.`
- **D7a / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003/A-0201: canonical conflict has no visible warning`
- **D7b / OBJ-9104** (UNEXPECTED_ACCEPT): `EPI-005 placement PASS: every conflict warning precedes optional claim-lineage disclosure.`
- **D7b / positive-control OBJ-0003** (UNEXPECTED_ACCEPT): `EPI-005 placement PASS: every conflict warning precedes optional claim-lineage disclosure.`
- **D8 / OBJ-9104** (INTENDED_REJECT): `- OBJ-9104: missing location_source_url`
- **D8 / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003: missing location_source_url`
- **D8b / OBJ-9104** (INTENDED_REJECT): `- OBJ-9104: Creative Commons image missing image_license_url`
- **D8b / positive-control OBJ-0003** (INTENDED_REJECT): `- OBJ-0003: Creative Commons image missing image_license_url`
- **D9 / OBJ-9104** (BLOCKED): `DATA-002 FAIL: homepage object hooks differ from expected objects: ['OBJ-0001', 'OBJ-0002', 'OBJ-0003', 'OBJ-9104']` — intended validator already fails on the unmutated baseline
- **D9 / positive-control OBJ-0003** (INTENDED_REJECT): `DATA-002 FAIL: OBJ-0003: homepage name does not match canonical_name 'Cuban American Friendship Urn'`
- **D10 / OBJ-9104** (INTENDED_REJECT): `- objects/synthetic-fixture-monument/index.html: href '/dc-public-realm/does-not-exist-fixture/' -> expected site/does-not-exist-fixture/index.html (missing)`
- **D10 / positive-control OBJ-0003** (INTENDED_REJECT): `- objects/cuban-american-friendship-urn/index.html: href '/dc-public-realm/does-not-exist-fixture/' -> expected site/does-not-exist-fixture/index.html (missing)`
- **D11 / OBJ-9104** (INTENDED_REJECT): `- missing primary navigation: objects/synthetic-fixture-monument/index.html`
- **D11 / positive-control OBJ-0003** (INTENDED_REJECT): `- missing primary navigation: objects/cuban-american-friendship-urn/index.html`
- **D12 / OBJ-9104** (INTENDED_REJECT): `- orphan object page(s): ['synthetic-orphan-page']`
- **D12 / positive-control OBJ-0003** (INTENDED_REJECT): `- orphan object page(s): ['synthetic-orphan-page']`
