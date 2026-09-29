# Qualification audit — San Martín / Library of Congress

Date: 2026-09-29
Purpose: exercise the integrated epistemic skill stack against real existing web evidence before further source accumulation.
Canonical mutation authorized: **none**. This is a qualification artifact only.

## Evidence selected

### QSRC-LOC-HALS-DC68
Library of Congress, Historic American Landscapes Survey, **General Jose de San Martin Memorial, Virginia Avenue & 20th Street Northwest, Washington, District of Columbia, DC**, survey HALS DC-68.

Stable item page: https://www.loc.gov/pictures/collection/hh/item/dc1246/
Survey documentation: https://tile.loc.gov/storage-services/master/pnp/habshaer/dc/dc1200/dc1246/data/dc1246data.pdf

The LOC catalog describes the structure with initial construction in 1924 and subsequent work in 1970, 1976, and 1985. The HALS historical narrative states that the statue was dedicated October 28, 1925 at Judiciary Square, disassembled in 1970 for Metro construction, and relocated to Virginia Avenue in 1976. Critically, the HALS narrative footnotes those historical statements to the National Register nomination rather than presenting them as newly independent historical research.

## Five-pass source audit

### 1. Source forensics
- repository: Library of Congress, Prints and Photographs / HABS-HAER-HALS access system
- source type: federal heritage survey/catalog plus historical narrative
- survey identifier: HALS DC-68
- relationship to event: retrospective, not contemporaneous to 1925 dedication
- digital access: LOC item page and LOC-hosted survey PDF
- upstream source explicitly visible in historical narrative: National Register of Historic Places Inventory Nomination Form for General José de San Martín

Result: the LOC/HALS source is authoritative for the existence and content of the HALS survey and useful for landscape documentation. It is **not automatically an independent source root** for the 1925/1970/1976 historical chronology when that chronology explicitly cites the National Register documentation already represented in the knowledge base as SRC-AR-003.

### 2. Atomic propositions

| Candidate | Proposition | Evidence mode | Initial disposition |
|---|---|---|---|
| QP-01 | HALS DC-68 documents the San Martín memorial at Virginia Avenue & 20th Street NW | CATALOG_ASSERTION | direct for survey/catalog fact |
| QP-02 | HALS assigns initial construction 1924 and subsequent work 1970, 1976, 1985 | CATALOG_ASSERTION | direct for catalog metadata only |
| QP-03 | memorial was dedicated 1925-10-28 at Judiciary Square | DOCUMENT_TEXT | retrospective historical statement |
| QP-04 | memorial was disassembled in 1970 because of Metro construction | DOCUMENT_TEXT | retrospective historical statement |
| QP-05 | memorial was relocated to Virginia Avenue in 1976 | DOCUMENT_TEXT | retrospective historical statement |
| QP-06 | QP-03 through QP-05 derive from/cite the National Register nomination | DOCUMENT_TEXT / SOURCE_GENEALOGY | direct evidence of inheritance |

### 3. Schema-fit gate
QP-01 through QP-05 can be represented using existing source/assertion/evidence concepts. QP-06 exposes a stronger requirement: inheritance is proposition-specific. The current database has `derived_from_source_ids` at source level and `inherits_claim_from_source_ids` at evidence-edge level. The evidence-edge field is the correct representation for QP-03 through QP-05. No schema extension is required for this case.

Decision: **EXISTING_REPRESENTATION**. Do not add a new predicate or enum.

### 4. Evidence genealogy
- QP-01: ORIGINAL_TO_SOURCE for the existence/identity of the HALS survey record.
- QP-02: ORIGINAL_TO_SOURCE as LOC/HALS catalog metadata, but not direct evidence that each underlying historical date is correct.
- QP-03–QP-05: EXPLICITLY_DERIVED for the historical claims because HALS cites the National Register nomination.
- QP-06: ORIGINAL_TO_SOURCE as an observable citation relationship in the HALS narrative.

This is the exact failure mode the epistemic architecture was designed to catch: **a prestigious federal repository does not create a second independent historical lineage when its historical narrative inherits the claim from an already-used federal heritage source.**

### 5. Epistemic consequence
- QP-01: possible CREATE_SOURCE / documentary-context candidate if HALS survey coverage is useful to the public knowledge base.
- QP-02: QUALIFY_EXISTING at most; catalog metadata should not overwrite better proposition-specific chronology.
- QP-03–QP-05: REVEAL_SHARED_LINEAGE / SUPPORT_EXISTING with zero new independent-lineage credit if added.
- QP-06: REVEAL_SHARED_LINEAGE; useful provenance information.

No canonical write is justified merely to increase source count. Adding HALS as independent corroboration for the chronology would **decrease epistemic quality** by double-counting the National Register lineage.

## Historical-image qualification
The LOC item establishes that HALS has documentation for this memorial, but this qualification pass did not inspect a specific historical image at sufficient resolution and with a specific frame/reproduction identifier. Therefore:
- no IMAGE_OBSERVATION is created;
- no visual exact-object claim is made;
- no date is inferred from pixels;
- no derivative-image independence is claimed.

This is a deliberate stop under the historical-image skill: catalog/document access is not a substitute for inspecting the actual image artifact.

## Collaboration hook generated from the audit

**Defect:** MISSING_CONTEMPORANEOUS_ROOT / UNKNOWN_SOURCE_ROOT for the 1925 dedication chronology.

**Research question:** retrieve a contemporaneous 1925 record or image documenting the Washington San Martín dedication/installation that does not merely inherit the later National Register narrative.

**Preferred targets:**
1. LOC newspaper collections or Chronicling America successor access for Washington/Argentine coverage around October 28, 1925;
2. NARA/Department of State or federal public-buildings records for gift receipt, installation, ceremony, or custody;
3. contemporaneous Argentine diplomatic/government records.

**Desired return:** page/image/record plus stable identifier, publication/office, exact date, page/frame, repository, retrieval date, and any explicit upstream attribution.

**Possible epistemic outcomes:**
- independent contemporaneous confirmation -> strengthens chronology and moves source root earlier;
- conflicting date/location -> creates/preserves contradiction;
- derivative report -> genealogy information but no independent-lineage credit;
- bounded null search -> research-planning result only.

Task completion alone must not change canonical assertions.

## Qualification result

### What worked
1. Source authority and authority fit stayed separate.
2. LOC/HALS did not receive automatic independent-source credit.
3. Source inheritance was traced at proposition level.
4. Existing schema could represent the lineage without ontology inflation.
5. Catalog metadata did not become image observation.
6. The audit produced a bounded collaboration task from an epistemic defect.

### Weakness exposed
The current regression fixtures are structural/behavioral declarations, not executable tests against a source-audit output schema. CI proves the fixture files are well formed, but it does **not yet prove that a generated audit obeys the required behaviors**.

### Required next engineering step
Define a machine-readable `source-audit.schema.json` plus a qualification fixture/output validator. The validator should require evidence mode, schema-fit classification, genealogy classification, affected assertion IDs where applicable, and an explicit `canonical_mutation_authorized` flag. Then encode this San Martín/LOC audit as the first executable qualification case.
