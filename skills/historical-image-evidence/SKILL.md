---
name: historical-image-evidence
description: Evaluate digitized historical photographs and other archival images as provenance evidence. Use for Library of Congress, National Archives, newspaper archives, government photograph collections, museum repositories, and derivative image copies. Separates what pixels show from catalog assertions and analytical inference, and traces image/source inheritance before evidence enters the knowledge base.
---

# Historical image evidence

Read `../epistemic-core/SKILL.md` and `../epistemic-source-audit/SKILL.md` first. Historical images use the same epistemic pipeline as documents; they do not get a shortcut because they appear visually direct.

## Three-channel rule
For every image, create separate candidate propositions for:

### IMAGE_OBSERVATION
Only what is materially visible in the pixels: object presence, visible inscription, relative placement, physical condition, identifiable surrounding structure, or other observable feature. Do not infer date, creator, donor, intent, or event identity from pixels alone unless visible evidence establishes it.

### CATALOG_ASSERTION
What the repository metadata states: title, date/date range, creator/photographer, collection, location, event description, negative/print identifier, rights note, or repository attribution. Catalog metadata is evidence for the catalog assertion, not automatically an observation from the photographed scene.

### ANALYTICAL_INFERENCE
A conclusion produced by combining observations/metadata/other evidence, such as relative chronology, likely pre/post-installation state, viewpoint reconstruction, or object identity. Record the supporting proposition IDs and uncertainty. Never relabel inference as image observation.

## Image forensics
Capture repository, stable item ID, collection/series, image/negative/print identifier, digital derivative identifier when available, catalog date and date type, photographer/creator attribution, scan/derivative relationship, access URL, retrieval date, resolution/version used, and exact image/frame/page.

For LOC and NARA, prefer persistent item/catalog identifiers and collection/record-group context over search-result URLs. Newspaper-image evidence also requires issue title, date, page and image/caption relationship.

## Exact-object gate
Before using an image to support an object-specific assertion, establish why the pictured object is the exact object rather than a model, predecessor, copy, recast, similar monument, or later replacement. If identity depends on inference, preserve that inference explicitly.

## Derivative and inheritance detection
Multiple scans, crops, reposts, agency copies, newspaper reproductions, and repository mirrors of the same underlying exposure are not independent image observations. Trace to the earliest identifiable photographic exposure/negative or source publication where possible.

Record relationships such as SAME_EXPOSURE, DERIVATIVE_SCAN, CROPPED_FROM, REPRODUCED_FROM, PRINT_FROM_NEGATIVE, or UNKNOWN_IMAGE_LINEAGE as review metadata. If the current schema cannot represent a material lineage distinction, invoke adaptive-schema review rather than inventing a predicate.

## Temporal reasoning
Distinguish:
- exposure date established by contemporaneous record;
- repository-assigned exact date;
- repository date range;
- publication date;
- scan/digitization date;
- inferred terminus ante/post quem.

A catalog date range does not become an exact exposure date. Publication proves the image existed by publication, not necessarily that the exposure occurred that day.

## Government and newspaper records
Use photographs to create cross-source tests, not merely illustrations. A dated government construction photograph can constrain installation chronology; a newspaper image/caption can independently document public presentation only if its claim lineage is independent. Government provenance does not make every caption historically infallible.

## Required output
Return the standard source-audit review plus:
- `image_forensics`;
- `pixel_observations`;
- `catalog_assertions`;
- `analytical_inferences`;
- `image_lineage`;
- `exact_object_assessment`;
- `temporal_constraints`;
- `recommended_comparison_images`.

## Hard stops
Stop object-level ingestion when image identity is material but unresolved, only a thumbnail/search-result surrogate was inspected, catalog metadata is being used as if visible in pixels, derivative copies are being counted as independent, or an inferred date/identity would have to be stored as direct observation.
