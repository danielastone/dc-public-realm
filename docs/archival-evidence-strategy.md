# Archival evidence strategy — LOC, NARA, newspapers, and government records

The three-object alpha should strengthen claims by tracing web-accessible evidence backward toward the earliest recoverable source, not by accumulating webpages.

## Core epistemic model

Maintain two linked provenance graphs:

1. **Object provenance** — what happened to the sculpture: creation, copying/recasting, gift, acceptance, installation, relocation, custody, material lineage.
2. **Knowledge provenance** — why the database believes each relationship: underlying archival record, historical image, newspaper account, later government synthesis, and any dependency among them.

A later institutional page that repeats an archival record is not an independent root.

## Evidence classes

### ARCHIVAL_GOVERNMENT_RECORD

Examples: congressional reports and acts, State Department records, Commission of Fine Arts / planning records, NPS reservation files, federal correspondence, memoranda, plans, and NARA record-group material.

Use for legal authority, acceptance, administrative chronology, custody, placement decisions, correspondence, and other facts within the creating agency's competence.

### HISTORICAL_IMAGE

Examples: Library of Congress Prints & Photographs, NARA photographs, HABS/HALS reproductions, and digitized government photographic files.

Separate three layers:
- pixels / visible content;
- catalog metadata supplied by the repository;
- historical interpretation inferred from either.

Only the first is image evidence. Catalog statements are documentary metadata.

### CONTEMPORARY_NEWSPAPER

Examples: Chronicling America newspapers and other stable newspaper archives.

Use for contemporaneous reporting of unveilings, presentations, speeches, public descriptions, names, and dates. Newspapers are event witnesses, not automatically authoritative provenance records. Record possible press-release or wire-service dependence when identifiable.

### LATER_GOVERNMENT_SYNTHESIS

Examples: HABS/HALS histories, NPS object histories, National Register nominations, later agency inventories.

Use primarily as synthesis and navigation evidence. Extract their footnotes and citations and trace material claims back to the archival source whenever possible.

## Source genealogy

`source_family_id` identifies a common underlying evidentiary lineage. `derived_from_source_ids` records known derivation. `dependency_status=UNKNOWN` never counts as independent corroboration.

A useful chain is:

`archival record -> cited by HABS/HALS -> repeated by agency web page`

This is one evidentiary root, not three votes.

A contemporary newspaper can be a second root only when there is no evidence that it merely reproduces the same government or diplomatic statement. Wire-service duplicates likewise count as one lineage.

## Search sequence per material assertion

1. Identify the material assertion and predicate-specific evidence standard.
2. Search LOC catalog / Prints & Photographs / Manuscript Division / Chronicling America.
3. Search NARA Catalog and NARA finding aids for relevant record groups and series.
4. Follow citations from HABS/HALS, National Register, NPS, Smithsonian, NCPC/CFA, or other later government synthesis.
5. Record the earliest accessible underlying source and its archival identifiers.
6. Add later sources only when they contribute independent evidence or useful documented interpretation.
7. Explicitly encode dependency; do not infer independence from different domains or agencies.

## Alpha research targets

### José de San Martín

High priority because LOC and NARA already expose a traceable archival path.

- LOC HALS DC-68 documents the memorial and identifies 1924 initial construction plus later work.
- LOC's Judiciary Square HABS history documents the statue's earlier location.
- LOC preserves Calvin Coolidge's October 28, 1925 dedication address in the Everett Sanders Papers.
- NARA's ALIC bibliography identifies James F. Vivian, “Splendid Isolation: Argentina, the United States, and the San Martin Monument in Washington, 1921–1925,” and explicitly points to Record Groups 59 and 66. Treat that citation as a research lead to the underlying federal records, not as independent evidence by itself.

Research goal: reconstruct authorization -> diplomatic transfer -> 1925 dedication -> Judiciary Square placement -> relocation using distinct archival roots.

### José Gervasio Artigas

- LOC HABS Virginia Avenue identifies the Artigas statue in Reservation 110, attributes the design to Juan M. Blanes, and records erection in 1950.
- Trace the HABS statement backward through its notes/bibliography and search NARA / State Department / planning records for gift, acceptance, fabrication/recast, shipment, and installation documentation.
- Search historical newspapers around the 1950 erection/dedication for contemporaneous reporting, while checking whether accounts derive from the same diplomatic announcement.

Research goal: distinguish what U.S. government administrative records establish from what later inventories repeat about the Uruguayan predecessor and recast.

### Cuban American Friendship Urn

- LOC's West Potomac Park HABS history provides a later government synthesis and states that the urn was in storage at the time of that documentation.
- Search LOC newspaper archives around the 1928 presentation and relevant later relocations.
- Search NARA, NPS reservation/park records, State Department material, and planning records for presentation, acceptance, location, storage, and material-history documentation.

Research goal: test the modern narrative of presentation and material lineage against contemporaneous government and newspaper records.

## Required archival metadata

For archival/government records capture, when available:
- repository
- record group / collection
- series
- box / folder / file unit
- item or catalog identifier
- creator office / agency
- document date
- title / description
- stable catalog URL
- digitized asset URL when appropriate
- retrieval date
- page / image / locator
- language
- rights / use statement
- source_family_id
- derived_from_source_ids

For newspapers additionally capture:
- newspaper title
- place of publication
- issue date
- edition
- page
- article headline
- author/byline when supplied
- wire service / syndication marker when supplied
- LOC/Chronicling America item identifier or stable issue/page URL

## Publication principle

The public record should make it possible to distinguish:

**what the source says** -> **why that source is credible for this predicate** -> **whether another source is actually independent** -> **what status the generator derives**.

The objective is not maximum verification. It is minimum hidden inference.