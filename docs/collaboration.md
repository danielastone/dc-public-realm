# Collaboration and archival research

This project is designed so unresolved provenance questions can be handed to collaborators without weakening the distinction between a research lead and evidence.

## How to contribute

Use a GitHub issue for each bounded research task. A task should identify:

- object and assertion or research question;
- repository / archive;
- exact collection, record group, series, box, folder, or call number when known;
- date range and name / spelling variants;
- what would count as a useful result;
- what must be captured to preserve provenance;
- current canonical task status: `OPEN`, `SUBMITTED`, `REVIEWED`, `INCORPORATED`, `REJECTED`, or `CLOSED_NO_CHANGE`.

A finding aid, catalog entry, or archive referral is a **research lead**, not evidence for the underlying historical assertion. Evidence enters the knowledge base only after the underlying record has been examined, reviewed, and incorporated through a transaction.

## Collaboration lifecycle

Collaboration status is deliberately separate from assertion status. The canonical machine-readable lifecycle is:

`OPEN → SUBMITTED → REVIEWED → INCORPORATED / REJECTED / CLOSED_NO_CHANGE`

`REJECTED` and `CLOSED_NO_CHANGE` may also follow `SUBMITTED` when review determines that no canonical knowledge-graph change is warranted. `OPEN` may move directly to `CLOSED_NO_CHANGE` when a bounded search is completed without a submission requiring evidentiary review.

- **OPEN** — the bounded research task is unresolved. Assignment or active work may be tracked in the GitHub issue, but `CLAIMED` is not a canonical database status.
- **SUBMITTED** — a collaborator has returned records, citations, scans, links, or a documented search result for project review.
- **REVIEWED** — the project has checked archival identity, completeness, claim fit, chronology, source inheritance, contradictions, and reproducibility, and recorded that review.
- **INCORPORATED** — a resolving transaction has made the authorized canonical change and links backward to the task, contributor submission, and review record.
- **REJECTED** — the submission was reviewed and does not justify the proposed canonical change. The submission and review remain part of the research audit trail.
- **CLOSED_NO_CHANGE** — the bounded task is closed without a canonical knowledge-graph change. This includes completed searches with no relevant evidence. It is a research result, not evidence that the historical proposition is false.

Operational labels such as `CLAIMED`, `RETRIEVED`, `INGESTED`, or `NO EVIDENCE` may appear in issue discussion or older documentation, but they must not be written to `research-tasks.json`. In particular, retrieval is not review, and review is not incorporation.

A collaborator does **not** assign `VERIFIED`, `SUPPORTED`, or any other assertion status. Assertion status is computed only from canonical evidence after review and transaction ingestion.

Each public task receives a stable route at `/tasks/<task-id>/`. The task page is the handoff surface: it defines the archive target, acceptable result, evidence boundary, capture standard, and submission link.

## Contributor capture standard

For every relevant archival record, capture enough context for another researcher to reproduce the finding:

1. repository and collection / record group;
2. series, box, folder, item or other archival identifiers;
3. document title or supplied description;
4. document date, preserving uncertainty exactly;
5. creator / sender and recipient when stated;
6. complete relevant pages, including versos or enclosures when material;
7. neighboring folder/document context when needed to interpret the record;
8. original wording and spelling for disputed names;
9. researcher name and retrieval date;
10. archive-imposed reproduction or publication restrictions;
11. stable catalog URL when one exists;
12. file hashes after digital capture when files are contributed to the project.

Do not submit a transcription alone when images/scans can legally be obtained. Do not crop away archival identifiers or page context in the evidentiary master.

## Current collaborator tasks

### ARG-SM-001 — San Martín: Argentina–Washington correspondence, 1921–1925

**Goal:** locate the earliest Argentine diplomatic documentation that names the sculptor or describes the Washington copy, and reconstruct what Argentina transmitted to the United States.

**Archive:** Archivo Histórico de Cancillería, Argentina — Fondo/section `Embajada en Washington, Estados Unidos I (27.A)`.

**Priority archival units:**

- `AH/0023/1` — Departamento de Estado - Entradas, 1921–1924
- `AH/0035/1` — Departamento de Estado Salidas, 1921–1924
- `AH/0002/2` — RREE - Entradas, 1924
- `AH/0030/1` — RREE, 1925

**Search concepts:** José de San Martín; monumento; estatua; monumento ecuestre; copia; reproducción; obsequio; donación; Washington; Club del Progreso; Daumas; Dumont; escultor; fundición; Arsenal Esteban de Luca; American Legion.

**Critical extraction rule:** preserve `Daumas`, `Dumont`, or any other attribution exactly as written. Do not silently normalize names.

**High-value result:** a dated Argentine-origin record identifying the sculptor, original work, fabrication/copy process, donor, or information formally transmitted to the U.S. government.

**Status:** OPEN — underlying records not examined.

[Open a GitHub issue for ARG-SM-001](https://github.com/danielastone/dc-public-realm/issues/new?title=ARG-SM-001%20%E2%80%94%20Retrieve%20San%20Mart%C3%ADn%20Argentina%E2%80%93Washington%20correspondence&body=Task%3A%20ARG-SM-001%0A%0AArchive%3A%20Archivo%20Hist%C3%B3rico%20de%20Canciller%C3%ADa%2C%20Embajada%20en%20Washington%20%2827.A%29%0A%0APriority%20units%3A%20AH%2F0023%2F1%3B%20AH%2F0035%2F1%3B%20AH%2F0002%2F2%3B%20AH%2F0030%2F1%0A%0AGoal%3A%20Find%20the%20earliest%20Argentine%20record%20that%20names%20the%20sculptor%20or%20describes%20the%20Washington%20copy.%20Preserve%20Daumas%2FDumont%20spelling%20exactly.%0A%0AWorkflow%3A%20Use%20the%20issue%20to%20record%20assignment%2Fwork-in-progress.%20Canonical%20status%20remains%20OPEN%20until%20a%20result%20is%20submitted.%0A%0AResult%3A%20SUBMITTED%20%2F%20completed%20search%20with%20no%20relevant%20evidence%0A%0AFindings%3A%0A%0AArchival%20citations%3A%0A%0AFiles%2Fimages%3A%0A)

## Archive request — ready to send

**Subject:** Consulta de investigación — Monumento a José de San Martín en Washington, 1921–1925

> Estimados/as responsables del Archivo Histórico de Cancillería:
>
> Estoy investigando la documentación relativa al monumento ecuestre al General José de San Martín enviado desde la Argentina a Washington y dedicado en 1925. El inventario de la sección Embajada en Washington, Estados Unidos I (27.A) identifica las siguientes unidades que parecen pertinentes:
>
> - AH/0023/1 — Departamento de Estado - Entradas, 1921–1924
> - AH/0035/1 — Departamento de Estado Salidas, 1921–1924
> - AH/0002/2 — RREE - Entradas, 1924
> - AH/0030/1 — RREE, 1925
>
> Busco especialmente correspondencia sobre el ofrecimiento, aceptación, fabricación/copia, envío, instalación y dedicación del monumento, así como cualquier documento que identifique al escultor o la obra original. Son de particular interés las variantes de nombre “Daumas” y “Dumont”, el Club del Progreso, el Arsenal Esteban de Luca y el transporte del monumento a Washington.
>
> ¿Sería posible confirmar si estas unidades contienen documentación pertinente y cuáles son las opciones para consulta, reproducción digital o solicitud de copias por un investigador que no se encuentra actualmente en la Argentina? Si existe una descripción más detallada a nivel de carpeta o expediente, agradecería también esa referencia.
>
> Muchas gracias.

## Other collaboration hooks

Create separate issues rather than expanding ARG-SM-001 when work moves to another archival lineage. Planned task families:

- `US-SM-*` — NARA RG 59 / RG 66 and other U.S. San Martín records;
- `NEWS-SM-*` — Argentine and U.S. contemporary newspaper lineage and wire-copy analysis;
- `IMG-SM-*` — LOC/NARA/Argentine historical-image provenance;
- `CUBA-*` — Cuban American Friendship Urn archival and newspaper provenance;
- `ARTIGAS-*` — Artigas diplomatic, fabrication, installation, and historical-image provenance.

A collaborator should be able to take responsibility for one issue without needing to understand the entire database architecture. Assignment is issue-level workflow metadata, not an epistemic state.

## Review and ingestion gate

Submission does not automatically change an assertion's status. Retrieved material must be reviewed for:

- authenticity / archival identity;
- authority for the specific claim;
- temporal proximity;
- source dependency and shared ancestry;
- contradictions or qualifications;
- exact assertion(s) actually supported;
- reproducibility of the archival citation and submitted record.

Record that decision using `qualification/review-record-template.md`. If canonical change is authorized, the subsequent transaction must include a `resolves` block identifying the task, contributor submission, and review record, and must move the task to `INCORPORATED`. The build copies that provenance into the semantic audit manifest.

If review does not justify a canonical change, close the task as `REJECTED` or `CLOSED_NO_CHANGE` as appropriate. Neither status changes the historical proposition merely because a search or submission failed to produce usable evidence.

Only a resolving transaction may update the evidence graph or other canonical historical state.