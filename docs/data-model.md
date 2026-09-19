# Data Model

The pilot deliberately uses simple CSV files. A database or application is premature until field work shows that the structure is inadequate.

## `data/targets.csv`

One row per physical target.

Key fields:

- `target_id`: stable project identifier, independent of any platform listing.
- `name`: preferred human-readable asset name.
- `category`: bridge, Metro entrance, public art, etc.
- `area`: broad public geographic context.
- `pilot`: field series or experiment to which the target belongs.
- `entity_status`: current Google map-entity resolution classification retained for the pilot.
- `review_count_observed`: observed review count used during target assessment.
- `review_count_as_of`: date of that observation.
- `field_status`: planned, photographed, uploaded, reshoot, complete, etc.
- `notes`: concise non-sensitive observations.

The physical target is the primary object. Platform entities are relationships, not the project's master identifier.

## `data/representations.csv`

Long-form crosswalk between a project target and external representations. Do not add Google, OSM, agency, or Wikidata IDs as competing master keys in `targets.csv`.

Each row records one representation of one physical target. Initial `source_system` values are:

- `authoritative_agency`
- `openstreetmap`
- `google_maps`

Additional systems such as Wikidata or DC GIS may be added when they provide useful independent identity or attributes.

Important fields:

- `source_object_type`: for OSM this is normally `node`, `way`, or `relation`; for an agency source it may be an asset class or dataset type.
- `source_object_id`: the external identifier, such as an OSM element ID, Google Place ID, or agency asset ID.
- `source_name`: name exposed by that source.
- `representation_status`: how well the external representation corresponds to the physical target.
- `geometry_status`: whether mapped geometry agrees with the authoritative source/field observation where geometry is relevant.
- `access_status`: whether entrance/access representation agrees where access is relevant.
- `checked_on`: date the representation was checked.
- `evidence_url`: source page or API endpoint used for the check when appropriate.

### Representation status vocabulary

- `preferred_exact`
- `competing_duplicate`
- `entrance_specific`
- `parent_only`
- `absent`
- `ambiguous`
- `not_checked`

### Geometry status vocabulary

- `consistent`
- `material_difference`
- `insufficient_evidence`
- `not_applicable`
- `not_checked`

### Access status vocabulary

- `consistent`
- `material_difference`
- `insufficient_evidence`
- `not_applicable`
- `not_checked`

## `data/observations.csv`

Long-form dated measurements of platform conditions and engagement. This prevents changing platform metrics from overwriting historical observations.

## Authority hierarchy

For project execution, use this order conceptually:

1. authoritative agency/source data for official identity and asset facts;
2. the project's stable `target_id` as the cross-platform identity;
3. OpenStreetMap for open geographic representation and field/GIS workflow;
4. Google Maps for public discovery, entity behavior, review themes, photographic coverage, and engagement observations.

This hierarchy does not mean authoritative data are automatically current. Field observations can expose stale official data; discrepancies should be recorded rather than silently resolved.

## Representation disagreement

The project should preserve disagreements among sources. Useful classes include:

- all representations materially agree;
- Google missing or parent-only;
- OSM missing or overly coarse;
- duplicate/alias conflict;
- mapped geometry differs materially;
- entrance/access representation differs;
- authoritative source appears stale relative to field observation.

A discrepancy is an observation to investigate, not permission to assume one source is correct.

## OSM editing rule

Do not edit OpenStreetMap merely to make it agree with this project or with Google. Any OSM contribution must be independently supportable under OSM's own sourcing and verifiability rules. Project field observations may support an edit when they are suitable evidence, but Google-derived information must not be copied into OSM.

## Design principle

Separate relatively stable facts about the physical asset from volatile observations about third-party platforms. A bridge does not become a different bridge because a map provider renames, merges, or splits a listing.