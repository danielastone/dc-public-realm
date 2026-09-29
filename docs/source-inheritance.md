# Source inheritance and claim genealogy

## Purpose

The project normalizes epistemology at the **claim lineage** level, not the website, repository, publisher, or institution level.

A record held by the Library of Congress is not automatically an independent Library of Congress claim. A HALS report created by NPS and hosted by LOC inherits the evidentiary ancestry of the NPS/HALS report. A congressional report that reproduces a State Department letter inherits that letter for the reproduced proposition. Five newspapers carrying the same wire story are one claim lineage for the repeated proposition.

The generator should therefore answer two different questions:

1. **Custody/provenance:** where is this digital or physical record held and how was it retrieved?
2. **Epistemic ancestry:** from what earlier source(s) does the specific claim appear to derive?

Only the second question controls independence for corroboration.

## Normalized model

Source-level metadata remains useful for custody and broad genealogy, but inheritance must ultimately be recorded per assertion-evidence edge because a single document can contain both original observations and inherited claims.

Each assertion-evidence record should support these fields:

- `claim_origin`: `ORIGINAL_TO_SOURCE`, `INHERITED`, `MIXED`, or `UNKNOWN`
- `inherits_claim_from_source_ids`: source IDs from which this exact proposition derives
- `inheritance_basis`: `EXPLICIT_CITATION`, `REPRODUCED_TEXT`, `CREATOR_REPOSITORY_RELATION`, `WIRE_SERVICE`, `CATALOG_DERIVATION`, `TEXTUAL_MATCH`, `SCHOLARLY_INFERENCE`, or `UNKNOWN`
- `inheritance_note`: concise human-readable explanation

Source records retain:

- `publisher_or_creator`
- `source_family_id`
- `derived_from_source_ids`
- repository/custody metadata where known

`derived_from_source_ids` is broad document genealogy. `inherits_claim_from_source_ids` is proposition-specific genealogy. When the two disagree, the claim-specific field governs corroboration.

## Effective roots

For each assertion-evidence edge, recursively trace `inherits_claim_from_source_ids` until reaching sources for which the claim is original or ancestry is unknown. These are the **effective claim roots**.

Examples:

`HALS report hosted by LOC -> NPS/HALS underlying documentation -> cited NRHP nomination`

If the HALS sentence simply repeats the NRHP claim, HALS and NRHP share an effective root and count as one lineage for that proposition.

`Congressional report -> reproduced State Department letter -> Argentine diplomatic communication`

If Congress merely reproduces State's wording and State merely relays Argentina's description, all three may collapse to the Argentine communication for that proposition. Congress can still be independently authoritative for a different proposition, such as what Congress legally authorized.

## Independence rule

Two evidence records may count as independent corroboration only when:

1. each has adequate claim-specific authority;
2. their effective claim-root sets are known; and
3. the root sets are disjoint.

If ancestry is unknown, the generator must not infer independence from different institutions, domains, repositories, or `source_family_id` values.

Therefore:

- different URLs != independent evidence;
- different agencies != independent evidence;
- LOC custody != LOC authorship;
- later government repetition != independent government corroboration;
- five syndicated newspaper publications != five corroborations.

Unknown ancestry should reduce confidence in independence, not in the truth of the underlying claim. The appropriate state is `UNKNOWN`, not `DEPENDENT` and not `INDEPENDENT`.

## Repository inheritance

Repository and creator must be separated explicitly. For example:

- LOC manuscript item created by the Coolidge administration: LOC is repository; the administration/document author is creator.
- HABS/HALS record: LOC may be repository/distributor; NPS/HABS/HALS is creator.
- NARA diplomatic despatch: NARA is repository; the embassy/State Department is creator.
- GovInfo congressional report: GPO/GovInfo is repository/distributor; Congress/committee is creator, while quoted letters retain their own claim ancestry.

Repository authority matters for authenticity, custody, identifiers, and faithful access. It does **not** transfer substantive authority to every historical claim contained in the record.

## Claim transformation

Inheritance is not always verbatim copying. Record whether a downstream source:

- `REPEATS` the upstream proposition;
- `SUMMARIZES` it;
- `NORMALIZES` names/dates/terminology;
- `INTERPRETS` it;
- `COMBINES` multiple upstream sources;
- `CONTRADICTS` it.

Normalization is particularly important for the San Martín `Daumas` / `Dumont` problem. A later normalized spelling must not silently overwrite the spelling in the upstream document.

## Generator behavior

Computed status should use **independent effective roots**, not raw source count.

A verification rule requiring independent corroboration should fail closed when all positive evidence inherits the same root or when independence remains unknown. The public page should expose a compact lineage such as:

`Claim lineage: Argentine communication -> State Department -> Congress`

or:

`Claim lineage unresolved: NPS summary; upstream source not yet identified`

This makes epistemic uncertainty visible without pretending the historical assertion itself is false.

## Migration rule

Existing `dependency_status` values remain supported during migration. New records should prefer explicit claim inheritance. Existing `UNKNOWN` values must not be automatically upgraded to `INDEPENDENT` merely because their `source_family_id` differs.

The first migration priority is evidence already known to be inherited:

1. LOC-hosted HABS/HALS records;
2. congressional reports reproducing State Department correspondence;
3. NRHP/HALS relationships;
4. newspaper wire or official-release duplication;
5. later NPS/NCPC summaries whose upstream federal records are identifiable.
