# Diplomatic Gifts — Alpha Launch Plan

Status: **alpha preparation**  
Scope freeze: **3 objects only**

- OBJ-0001 — José Gervasio Artigas Memorial
- OBJ-0002 — José de San Martín Memorial
- OBJ-0003 — Cuban American Friendship Urn

## Alpha objective

Publish a small but complete vertical slice proving that the project can turn multilingual government and archival evidence into public, traceable, machine-readable object records and then measure whether humans, search engines, and AI systems discover them.

Alpha is not a comprehensive inventory of Washington diplomatic gifts. Do not add a fourth object before the alpha measurement cycle is running.

## Launch gates

### A1 — Canonical data freeze

**Status: complete**

Canonical model v0.2 contains objects, agents, events, assertions, sources, object relationships, field observations, controlled vocabulary, and publication status.

Rule: factual web copy must trace to a canonical assertion/source. Unknowns remain explicit rather than inferred.

### A2 — Publication QA

**Status: open**

Required before public launch for each object:

- [ ] Public summary reconciled to canonical assertions
- [ ] Coordinates checked against authoritative source
- [ ] Gift/provenance claim has primary or authoritative government support
- [ ] Creator/production roles are not flattened where evidence distinguishes them
- [ ] Visible inscriptions transcribed from field photographs when available
- [ ] Current public visibility/access confirmed
- [ ] Current-condition note recorded or explicitly marked not assessed
- [ ] At least one publishable image with rights/license recorded
- [ ] Unresolved research questions labeled as unresolved
- [ ] All outbound citations resolve

Field gaps do **not** justify reopening population research.

### A3 — Alpha site

Build the smallest public site that exposes the evidence model.

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

1. Canonical title and object ID
2. Country and object type
3. Field image
4. Short public summary
5. Gift/provenance chain
6. Creator/production roles
7. Event timeline
8. Original-language evidence where useful
9. Current location and coordinates
10. Sources attached to claims
11. Explicit unresolved questions
12. Last-reviewed date

No decorative content sections merely to increase page length.

### A4 — Machine-readable publication

Each object page must have a stable machine-readable representation generated from the same canonical record as the human page.

Minimum:

- Semantic HTML
- Canonical URL
- Stable object ID
- `lang` metadata and language labels for non-English evidence
- JSON endpoint or embedded canonical JSON
- JSON-LD using established Schema.org types/properties where they fit; do not invent unsupported semantics
- Sitemap
- robots.txt
- Open Graph metadata
- Descriptive title/meta description

The machine layer must preserve assertion status and source URLs. Do not turn unresolved claims into definitive structured data.

### A5 — Analytics and crawler observability

Instrument before launch, not afterward.

Track separately:

1. Human page visits
2. Search impressions/clicks
3. Known crawler requests from server/CDN logs where available
4. AI-product referrals when a referrer is provided
5. Outbound clicks to source documents

Minimum launch integrations:

- Google Search Console
- Bing Webmaster Tools
- One site analytics platform
- CDN/server request logs if hosting supports them

Do not treat AI referral traffic as a proxy for AI citation or crawler retrieval.

### A6 — Alpha discovery experiment

Freeze a query panel **before** checking post-launch results.

Query families:

- exact object identity
- gift/donor provenance
- creator attribution
- object history/relocation
- cross-language queries
- cross-object/category queries

Example probes:

- Who gave the Artigas statue in Washington to the United States?
- Who sculpted the Washington Artigas monument?
- ¿Quién regaló el monumento a Artigas en Washington a Estados Unidos?
- What Cuban gift in Washington was made from the Maine memorial?
- Why was the Cuban American Friendship Urn made from an earlier monument?
- Was the San Martín statue in Washington always in its present location?

Record baseline and repeated observations without changing query wording.

## Alpha metrics

Keep the dashboard small:

- indexed object pages
- search impressions
- organic search clicks
- object-page entrances
- source-link clicks
- known crawler requests by family
- AI referrals
- query-panel retrieval/citation observations
- pages with unresolved publication QA
- data/source corrections discovered after launch

## Stop rules

Until alpha measurement is operational:

- no fourth diplomatic-gift object
- no comprehensive DC inventory
- no new database technology
- no graph database
- no user accounts/CMS
- no elaborate map application
- no SEO content expansion unrelated to the three canonical records

A new feature must either improve evidence integrity, publication accessibility, discoverability measurement, or reproducibility. Otherwise defer it.

## Immediate execution order

1. Close publication QA for the three objects.
2. Export canonical records into repository-managed structured data.
3. Build the eight required alpha routes.
4. Add machine-readable output and technical discovery files.
5. Deploy to a public URL.
6. Verify accessibility, links, structured output, sitemap, and crawlability.
7. Connect analytics/Search Console/Bing.
8. Capture pre/post-launch query-panel observations.
9. Run alpha for a fixed observation period before expanding scope.

## Alpha definition of done

Alpha is launched when all three object records are publicly reachable from a stable URL, their material factual claims are source-traceable, structured representations are generated from the same canonical data, analytics/search instrumentation is live, and the frozen discovery-query panel has a recorded baseline.
