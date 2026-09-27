# Diplomatic Gifts — Alpha Launch Plan

Status: **alpha preparation**  
Scope freeze: **3 objects only**

- OBJ-0001 — José Gervasio Artigas Memorial
- OBJ-0002 — José de San Martín Memorial
- OBJ-0003 — Cuban American Friendship Urn

## Alpha objective

Publish a small but complete vertical slice demonstrating that fragmented multilingual evidence can be transformed into **provenance-bearing semantic relationships**, exposed to both humans and machines, and tested for discovery.

The alpha is not a comprehensive inventory of Washington diplomatic gifts. Its test is whether three heterogeneous objects are enough to prove the evidence-to-semantics-to-publication pipeline.

## Core pipeline

`sources → assertion evidence → assertions → semantic relationships → publication views → discovery measurement`

Object pages are one view of the semantic layer, not the canonical data model itself.

## Launch gates

### A1 — Semantic model freeze

**Status: model rewritten; data migration required**

Canonical model v0.3 centers assertions and assertion-evidence joins. Before site generation:

- [ ] all reusable subjects/objects have stable entity IDs;
- [ ] all material relationships are atomic assertions;
- [ ] evidence is normalized from source lists into assertion-evidence records;
- [ ] source language is populated;
- [ ] assertion status is explicit;
- [ ] creator roles use specific predicates;
- [ ] conflicts/unknowns remain explicit;
- [ ] referential-integrity validation passes.

No new object research is required to complete this migration.

### A2 — Publication QA

**Status: open**

Required before public launch for each object:

- [ ] public summary reconciled to canonical assertions;
- [ ] coordinates checked against authoritative source or field observation;
- [ ] gift/provenance relationship has authoritative evidence;
- [ ] creator/production roles are not flattened;
- [ ] visible inscriptions transcribed from field photographs when available;
- [ ] current public visibility/access confirmed;
- [ ] current-condition note recorded or explicitly marked not assessed;
- [ ] at least one publishable image with rights/license recorded;
- [ ] unresolved or contested relationships visibly labelled;
- [ ] all outbound evidence links resolve.

### A3 — Alpha site

Build the smallest public site that exposes provenance **and** semantics.

Required routes:

- `/diplomatic-gifts/`
- `/diplomatic-gifts/objects/jose-gervasio-artigas/`
- `/diplomatic-gifts/objects/jose-de-san-martin/`
- `/diplomatic-gifts/objects/cuban-american-friendship-urn/`
- `/diplomatic-gifts/countries/uruguay/`
- `/diplomatic-gifts/countries/argentina/`
- `/diplomatic-gifts/countries/cuba/`
- `/diplomatic-gifts/methodology/`

Object-page minimum:

1. identity and stable ID;
2. field image;
3. concise narrative generated/reconciled from assertions;
4. provenance chain shown as explicit relationships;
5. creator/production relationships;
6. event timeline;
7. original-language evidence where material;
8. current location;
9. evidence attached to individual claims/relationships;
10. unresolved/contested assertions;
11. last-reviewed date;
12. link to canonical machine-readable record.

A generic bibliography at the bottom is insufficient as the only provenance interface.

### A4 — Machine-readable publication

Each public page must have a stable machine-readable representation derived from the same assertion layer.

Minimum:

- semantic HTML;
- canonical URL;
- stable entity/assertion/source IDs;
- language metadata;
- canonical JSON exposing assertions and evidence links;
- JSON-LD only where established vocabularies express the semantics accurately;
- sitemap;
- robots.txt;
- Open Graph metadata;
- descriptive title/meta description.

Machine output must preserve assertion status. `UNRESOLVED`, `CONTESTED`, and qualified claims must never become unqualified facts merely because a target vocabulary is less expressive.

### A5 — Analytics and crawler observability

Instrument before launch.

Track separately:

1. human page visits;
2. search impressions/clicks;
3. known crawler requests from server/CDN logs where available;
4. AI-product referrals when provided;
5. outbound clicks to evidence sources;
6. interactions that reveal use of provenance, such as source expansion/clicks where measurable.

Minimum launch integrations:

- Google Search Console;
- Bing Webmaster Tools;
- one site analytics platform;
- CDN/server request logs if hosting supports them.

AI referral traffic is not evidence that an AI system cited or semantically used the site.

### A6 — Semantic discovery experiment

Freeze the query panel before post-launch checking.

The panel should test relationship retrieval, not merely whether pages rank for their titles.

Query families:

- object → donor;
- object → depicted person;
- object → creator role;
- object → predecessor/material lineage;
- object → event/location history;
- country → gifted object;
- cross-language relationship retrieval;
- questions where existing sources flatten or disagree on attribution.

Example probes:

- Who gave the Artigas statue in Washington to the United States?
- Who designed, completed, and executed the Artigas monument tradition?
- ¿Quién regaló el monumento a Artigas en Washington a Estados Unidos?
- What Cuban gift in Washington was made from the Maine memorial?
- What is the material relationship between the Cuban Friendship Urn and the Havana Maine monument?
- Was the San Martín statue in Washington always in its present location?

Record baseline and repeated observations without changing query wording.

## Alpha metrics

Keep the dashboard small:

- indexed entity/object pages;
- search impressions;
- organic clicks;
- object-page entrances;
- evidence/source-link clicks;
- known crawler requests by family;
- AI referrals;
- query-panel relationship retrieval/citation observations;
- assertions failing publication QA;
- semantic/provenance corrections discovered after launch.

## Stop rules

Until alpha measurement is operational:

- no fourth diplomatic-gift object;
- no comprehensive DC inventory;
- no graph database merely because the model is graph-shaped;
- no CMS/user accounts;
- no elaborate map application;
- no SEO content expansion unrelated to the three records;
- no new predicate unless required by an actual alpha assertion.

A feature must improve evidence integrity, semantic precision, publication accessibility, discoverability measurement, or reproducibility. Otherwise defer it.

## Immediate execution order

1. Migrate the existing three-object canonical data to v0.3 assertions + assertion-evidence records.
2. Run referential-integrity and provenance validation.
3. Close remaining field/publication QA.
4. Generate repository-managed canonical JSON.
5. Build the eight required alpha routes from that data.
6. Add canonical JSON and conservative structured metadata.
7. Deploy to a public URL and verify accessibility, links, sitemap, and crawlability.
8. Connect analytics/Search Console/Bing and retain server/CDN logs where available.
9. Capture the frozen query-panel baseline and repeated observations.

## Alpha definition of done

Alpha is launched when all three objects and their material semantic relationships are publicly reachable, every published material relationship is traceable to evidence, status/language/provenance survive machine-readable export, analytics/search instrumentation is live, and the frozen semantic-discovery query panel has a recorded baseline.
