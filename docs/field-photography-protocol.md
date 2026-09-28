# Field photography protocol — three-object alpha

Photography is evidence only when it records an observable fact. It is not independent proof that historical text appearing on an object is true.

## Capture set per object

Keep the alpha deliberately small: three useful photographs per object.

1. **Context / identity** — entire object plus enough surrounding setting to establish which monument was observed.
2. **Evidentiary detail** — inscription, plaque, signature, foundry mark, donor text, date, or other physically legible feature relevant to an assertion.
3. **Material / condition detail** — surface, joint, repair, relief, stone or metal feature, or other physical characteristic that matters to the record.

Do not add photographs merely to create a gallery. A fourth photograph needs a distinct evidentiary purpose.

## Capture metadata

For every retained image record:

- object_entity_id
- photographer_or_observer
- captured_at (ISO 8601 with timezone when available)
- original filename
- SHA-256 of the original file
- latitude / longitude when available from the original metadata
- heading when available
- device / camera when available
- transformation history for any published derivative (crop, resize, exposure adjustment)
- rights / license statement
- public image path only after the image is intentionally published

Preserve the original file. A web derivative is not the evidentiary master.

## Evidence semantics

A field photograph source uses:

- source_type: `FieldPhotograph`
- source_role: `FIELD_OBSERVATION`
- evidence_role: `FIELD_VERIFICATION`
- proximity: `FIELD_OBSERVATION`
- dependency_status: `INDEPENDENT` for the observation itself
- observation_scope: one of `OBJECT_IDENTITY`, `INSCRIPTION_TEXT`, `MAKER_MARK`, `PRESENT_LOCATION`, `VISIBLE_MATERIAL`, `VISIBLE_CONDITION`, `CONTEXT`, `OTHER_OBSERVABLE`

`authority_fit` is claim-specific.

### Direct

Use `DIRECT` only when the photograph itself shows the asserted observable fact: e.g. the inscription contains a specific text, a maker mark is visible, or the object is physically present at the photographed location.

### Limited

Use `LIMITED` when the photograph records a statement that makes a historical claim. Example: an inscription says that marble came from an earlier monument. The photograph directly proves the inscription text exists; it does **not** directly prove the marble's historical origin.

## Anti-inflation rule

Field photography does not count as independent corroboration for historical provenance, authorship, donor identity, dates, or material lineage merely because an inscription repeats the claim. Those historical assertions still require the applicable documentary evidence standard.

When useful, model two separate assertions:

1. an observable assertion about what the inscription says; and
2. the historical assertion to which the inscription refers.

This keeps physical observation separate from historical inference.

## Alpha shot plan

### Cuban American Friendship Urn — first priority

1. Whole-object/context image.
2. Straight-on, high-resolution inscription image sufficient to transcribe the relevant text without inference.
3. Detail of the marble / relief / physical feature most relevant to the material-lineage claim.

The inscription image should support an `INSCRIPTION_TEXT` assertion. It should not by itself upgrade `DERIVED_FROM_MATERIAL` to VERIFIED.

### José Gervasio Artigas

1. Whole-object/context image.
2. Signature, foundry mark, plaque, or identifying inscription if accessible.
3. Detail relevant to casting or physical lineage, if one is actually observable.

Do not infer Montevideo casting or the early-1940s recast date from appearance.

### José de San Martín

1. Whole-object/context image.
2. Plaque / inscription / signature detail.
3. Physical or setting detail relevant to present placement or object identification.

Do not use the photograph to resolve the Daumas/Dumont authorship conflict unless a photographed primary mark directly bears on attribution; even then, record the mark separately from the historical conclusion.

## Publication gate

A photograph enters the public site only when its metadata, rights statement, hash, object linkage, and evidentiary purpose are recorded. Otherwise retain it outside the published evidence set.