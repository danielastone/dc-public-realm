# San Martín — Argentina archival retrieval gate

## Purpose

This gate narrows the Argentine archival search to records capable of identifying the provenance of claims about the Washington San Martín monument, especially the Daumas/Dumont attribution. It does not treat finding aids as evidence for monument facts.

## Confirmed archival structure

The Archivo Histórico de Cancillería identifies **27.A. Embajada en Washington, Estados Unidos I**, covering **1869–1946**, comprising **156 boxes**, open for research, with an inventory at the conservation-unit/box level. The archive's inventories page provides an Excel inventory titled **Embajada en Washington, Estados Unidos I**.

Official finding-aid pages:
- https://www.cancilleria.gob.ar/es/institucional/patrimonio/archivo-historico-de-cancilleria/atencion-usuarios/guia-de-fondos
- https://www.cancilleria.gob.ar/es/institucional/patrimonio/archivo-historico-de-cancilleria/atencion-usuarios/inventarios

Inventory asset exposed by the official page:
- https://www.cancilleria.gob.ar/userfiles/ut/embajada_en_washington_0.xls

The web research environment identified the asset but could not parse/download the legacy XLS. Therefore **no box number, folder title, or document content is asserted yet**.

## Search window

Primary: **1921–1925**.

Expand only if the inventory requires it:
- 1920 for precursor correspondence;
- 1926 for post-dedication acknowledgments/accounting.

## Terms to inspect in the 27.A inventory

Preserve original Spanish wording and spelling. Search for:

- San Martín / San Martin
- monumento / estatua / estatua ecuestre
- Washington
- Club del Progreso
- Honorio Pueyrredón / Pueyrredon
- Felipe A. Espil
- Marcelo T. de Alvear
- Calvin Coolidge
- Daumas
- Dumont
- donación / obsequio / presente
- inauguración / dedicación
- Judiciary Square
- Comisión de Bellas Artes / Commission of Fine Arts
- Departamento de Estado / Department of State
- American Legion (ship)

## Highest-value document classes

1. Argentine instructions or cables to the Washington mission describing the gift.
2. Washington Embassy correspondence transmitting monument documentation to the U.S. State Department.
3. Enclosures, inventories, technical descriptions, captions, photographs, shipping papers, or ceremony programs that name the sculptor.
4. Correspondence with Club del Progreso or the monument subcommission.
5. Embassy reports back to Buenos Aires describing U.S. authorization, placement, dedication, or reception.
6. Press clippings only after their publication lineage is identified.

## Daumas/Dumont test

For every retrieved document that names the sculptor, record:

- exact spelling as written;
- document date;
- author/sender;
- recipient;
- archive/fond/section/box/folder/document identifier;
- whether the name occurs in the main text, enclosure, caption, annotation, or later catalog description;
- whether the document appears to copy an earlier source;
- language;
- scan/image URL or reproduction identifier when available.

Do **not** normalize `Daumas` and `Dumont` into one entity at ingestion. Preserve the literal assertion first; entity reconciliation is a separate semantic operation.

## Parallel Argentine sources

### Cancillería Memorias

The Archivo Histórico states that the Ministry's annual Memorias from 1860–1999 are digitized. Search the 1921–1925 volumes for Washington mission activity, the monument, shipment, presentation, and dedication. A Memoria is an official later compilation for the reporting period, not automatically independent of the underlying diplomatic correspondence.

Official collection:
https://www.cancilleria.gob.ar/es/institucional/patrimonio/archivo-historico-de-cancilleria/atencion-usuarios/memorias-del-ministerio

### Libros Copiadores

The inventories page separately lists **Libros Copiadores de Correspondencia enviada por el Ministerio de Relaciones Exteriores y Culto a sus Representaciones diplomáticas**. This is a high-value mirror source for instructions sent from Buenos Aires to Washington. If a copy corresponds to a 27.A received document, treat the two as the same communication lineage, not independent corroboration.

### Diplomática y Consular / División Política / Misiones al Exterior

The official guide identifies these as associated provenance groups for the Washington Embassy section. Search them only after the 27.A inventory has been screened or when a 27.A document explicitly points upstream to one of them.

### Newspaper archive route

Search Argentine newspapers for 1921–1925, but classify each item before counting it as corroboration:

- original reporting;
- official text reproduced verbatim;
- diplomatic/committee press release;
- wire copy;
- editorial/commentary;
- unknown lineage.

Because La Nación and La Prensa are reported in later Argentine institutional history as financially involved with monument bas-reliefs, their coverage should not be presumed institutionally detached from the project without further evidence.

## Epistemic rule

The archive hierarchy is not a credibility ranking. Its purpose is to get closer to the production and transmission of the claim.

Example:

`Club del Progreso record → Cancillería instruction → Washington Embassy transmission → U.S. State Department letter → presidential message → Congressional Record`

If all six repeat the same attribution from the first record, they represent one claim lineage. They are not six independent corroborations.

Conversely, a separately generated fabrication record naming the sculptor may provide genuinely independent evidence even if it sits in the same archive.

## Current gate status

**OPEN / NOT YET RESOLVED**

We have confirmed that the relevant 27.A archival section and its inventory exist, but we have not inspected the inventory rows. No claim should be upgraded on the basis of this finding aid alone.

### Next action

Obtain and parse `embajada_en_washington_0.xls`; filter 1921–1925; record candidate box/folder identifiers; then retrieve only the smallest set of underlying documents needed to trace the sculptor attribution and diplomatic transfer chain.