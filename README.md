# Diplomatic Gifts in Washington

A source-traceable website documenting foreign gift sculpture and commemorative objects in Washington, DC.

## Alpha scope

The alpha is deliberately limited to three publicly viewable objects:

1. **OBJ-0001 — José Gervasio Artigas Memorial** — Uruguay
2. **OBJ-0002 — José de San Martín Memorial** — Argentina
3. **OBJ-0003 — Cuban American Friendship Urn** — Cuba

No fourth object will be added until the website is public and the discovery/analytics experiment is running.

## What the project adds

Government, museum, archival, donor-country, and field evidence is often fragmented across institutions and languages. This project connects those records at the level of individual factual assertions.

Each published object record is intended to expose:

- gift and diplomatic provenance;
- creator and production roles without flattening disputed or multi-stage attribution;
- legal acceptance, siting, relocation, restoration, and dedication events;
- original-language evidence alongside English-language sources;
- current location and field observations;
- explicit unresolved research questions;
- citations attached to claims rather than a generic bibliography; and
- machine-readable data generated from the same canonical record as the human page.

## Alpha publication pipeline

`authoritative sources → canonical assertions → structured object data → public pages → machine-readable output → search/crawler/AI measurement`

The project is currently preparing the alpha publication. See [`docs/diplomatic-gifts-alpha-launch.md`](docs/diplomatic-gifts-alpha-launch.md) for launch gates and stop rules.

## Repository scope

The default branch now contains only work required for the diplomatic-gifts website launch. Earlier public-realm, bridge, Metro, photography-utility, and generalized infrastructure experiments are preserved on the `archive/pre-diplomatic-gifts-alpha` branch and are not part of the active project.

## Active repository structure

- `data/` — canonical diplomatic-gift records and publication data
- `docs/` — launch specification, evidence/data model, and field/publication protocol
- website source — added during the alpha build

## Evidence rules

1. One physical viewable object receives one stable object ID.
2. Gift, shipment, legal acceptance, siting, installation, relocation, restoration, and dedication are separate events when the evidence distinguishes them.
3. Creative attribution is role-specific.
4. Sources attach to assertions.
5. Original-language sources are retained and language-labelled.
6. Unknown or disputed facts remain explicit; the website does not silently normalize them.
7. Field observations establish current physical conditions, not historical provenance.

## Alpha definition of done

Alpha is launched when all three records are publicly reachable at stable URLs, material factual claims are source-traceable, structured representations come from the same canonical data, analytics/search instrumentation is live, and a frozen discovery-query panel has a recorded baseline.
