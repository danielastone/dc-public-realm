# Diplomatic Gifts in Washington

A provenance-linked semantic publication about foreign gift sculpture and commemorative objects in Washington, DC.

## Core proposition

The project's value is not simply identifying diplomatic-gift objects. Existing government, museum, archival, and donor-country sources already describe many of them.

The value is to make **semantic relationships explicit and attach provenance to each relationship**.

A public object can therefore be traversed as a set of evidenced claims:

`physical object → diplomatic gift from → country / people / government`

`physical object → depicts → historical person`

`physical object → designed / completed / cast by → specific agents in specific roles`

`physical object → accepted / sited / relocated / restored through → documented events`

`physical object → derived from → predecessor object or design`

Each relationship should answer: **What is being asserted? Who or what supports it? In which source and language? What is the evidentiary status?**

Object pages, country pages, creator pages, timelines, JSON, and structured metadata are different projections of that provenance-bearing semantic layer.

## Alpha scope

The alpha is deliberately limited to three publicly viewable objects:

1. **OBJ-0001 — José Gervasio Artigas Memorial** — Uruguay
2. **OBJ-0002 — José de San Martín Memorial** — Argentina
3. **OBJ-0003 — Cuban American Friendship Urn** — Cuba

No fourth object will be added until the website is public and the discovery/analytics experiment is running.

## Why this matters

Evidence for one object may be fragmented across Congress, the State Department, NPS, NCPC, CFA, Smithsonian collections, donor-country institutions, original-language sources, inscriptions, and field observations. Conventional catalogs often publish a flattened record. This project preserves the distinctions among those sources and exposes the relationships they support.

The alpha therefore tests whether a small semantic evidence layer can improve:

- provenance: where a claim came from and how strongly it is supported;
- semantics: what entities are related and the precise nature of the relationship;
- multilingual reconciliation: linking donor-country evidence to U.S. records without discarding the original language;
- ambiguity: preserving conflicting, incomplete, or role-specific attribution rather than forcing one clean value;
- machine use: allowing search engines and language models to retrieve relationships together with their evidence;
- human research: allowing a reader to move from a concise claim to the underlying source.

## Publication pipeline

`sources → provenance-bearing assertions → semantic relationships → human and machine representations → discovery measurement`

The physical object is an important entity in the graph, but it is **not the intellectual product by itself**. The reusable product is the sourced relationship layer around it.

See [`docs/diplomatic-gifts-alpha-launch.md`](docs/diplomatic-gifts-alpha-launch.md) for launch gates and stop rules and [`docs/data-model.md`](docs/data-model.md) for the canonical evidence model.

## Active repository structure

- `data/` — canonical entities, sources, assertions, semantic relationships, events, and field observations
- `docs/` — evidence model, publication/field protocol, and alpha launch specification
- website source — generated from the canonical semantic layer during the alpha build

Earlier public-realm experiments are preserved on the `archive/pre-diplomatic-gifts-alpha` branch and are outside the active project.

## Evidence rules

1. Assertions are atomic and source-traceable.
2. Semantic relationships are published only with their provenance and evidentiary status.
3. One physical viewable object receives one stable object ID.
4. Gift, shipment, legal acceptance, siting, installation, relocation, restoration, and dedication remain distinct when the evidence distinguishes them.
5. Creative attribution is role-specific.
6. Original-language evidence is retained and language-labelled; translation does not replace the source text.
7. Conflicts and unknowns remain explicit rather than being silently normalized.
8. Field observations establish current physical conditions, not historical provenance.
9. Human-readable and machine-readable representations derive from the same canonical assertions.

## Alpha definition of done

Alpha is launched when the three objects and their material semantic relationships are publicly reachable at stable URLs, each published relationship is traceable to evidence, machine-readable representations preserve provenance/status, analytics/search instrumentation is live, and a frozen discovery-query panel has a recorded baseline.
