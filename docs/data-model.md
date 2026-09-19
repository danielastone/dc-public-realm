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
- `entity_status`: current map-entity resolution classification.
- `review_count_observed`: observed review count used during target assessment.
- `review_count_as_of`: date of that observation.
- `field_status`: planned, photographed, uploaded, reshoot, complete, etc.
- `notes`: concise non-sensitive observations.

The physical target is the primary object. Platform entities are attributes/relationships, not the project's master identifier.

## `data/observations.csv`

Long-form dated measurements of platform conditions and engagement. This prevents changing platform metrics from overwriting historical observations.

## Entity status vocabulary

- `preferred_exact`
- `competing_duplicate`
- `entrance_specific`
- `parent_only`
- `absent`

The vocabulary may change after the pilot if real cases demonstrate that it is insufficient.

## Design principle

Separate relatively stable facts about the physical asset from volatile observations about third-party platforms. A bridge does not become a different bridge because a map provider renames, merges, or splits a listing.