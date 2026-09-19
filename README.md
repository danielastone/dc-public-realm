# DC Public Realm

A field-based project documenting Washington, DC's public realm through photography, structured place data, and infrastructure research.

The project begins with bridges and other transportation infrastructure, then extends to Metro entrances, public art, historic sites, and other public-space assets.

## Why this project exists

Useful photographs of infrastructure are often hard to find even when a place receives substantial public attention. Mapping platforms can also represent one physical place through parent listings, entrances, aliases, or duplicate entities. This project treats photography and place identification as related problems.

The initial work asks:

- Which public-realm locations have meaningful public interest but weak or outdated photographic coverage?
- Which views provide information that existing galleries do not?
- How should photographs be associated with the correct map entity?
- Can a repeatable field protocol improve both photographic quality and informational value?
- Can the resulting inventory connect public-facing documentation with engineering, asset management, and capital-planning information?

## Initial scope

### Infrastructure
- Bridges
- Metro stations and entrances
- Trails and pedestrian infrastructure
- Transit stops
- Other visible public works

### Civic and cultural landscape
- Public art
- Memorials and monuments
- Historic structures and sites
- Parks and public spaces

## Rock Creek bridge pilot

The first controlled field series focuses on bridges in and around Rock Creek Park:

1. Boulder Bridge
2. Rapids Bridge
3. Bluff Bridge
4. William Howard Taft Bridge
5. Duke Ellington Memorial Bridge
6. Dumbarton Bridge

This is a pilot, not a claim that these are the most important bridges in Washington. The point is to test a consistent workflow on a coherent group of structures before expanding the inventory.

## Core workflow

1. **Identify** a candidate public-realm asset.
2. **Resolve the map entity** before uploading photographs.
3. **Audit existing coverage** for missing viewpoints, seasons, details, and context.
4. **Photograph systematically** using the field protocol.
5. **Record metadata** separately from the image itself.
6. **Publish selectively** to the appropriate platforms.
7. **Measure results** where platforms expose useful engagement information.
8. **Connect the asset** to authoritative engineering, historical, ownership, or planning sources when available.

## Entity-resolution rule

Do not treat a map search result as automatically equivalent to the physical asset.

Each target should be classified as one of:

- `preferred_exact` — clear listing for the physical asset
- `competing_duplicate` — multiple listings appear to represent the same asset
- `entrance_specific` — listing represents a particular entrance/access point
- `parent_only` — only a broader parent entity is available
- `absent` — no suitable entity found

An unresolved entity is a reason to investigate before upload, not a reason to guess.

## Photography protocol

For each infrastructure target, aim for four useful image types when access and safety permit:

1. **Whole structure** — clearest accessible view of the asset.
2. **Approach/context** — relationship to streets, trails, water, landscape, or adjacent infrastructure.
3. **Engineering/architectural detail** — structure, materials, supports, ornament, signage, or another informative detail.
4. **Identification/navigation view** — helps a visitor recognize or locate the asset.

More photographs are not automatically better. The goal is incremental information, not gallery volume.

## Privacy

The public repository should contain public-place observations, not a record of the photographer's private movements.

Do not publish home or residential location information, routine travel patterns, unnecessary precise timestamps, private-property access details, or metadata that unintentionally exposes sensitive location history. Photographs should be reviewed for embedded metadata and incidental personal information before publication here.

## Repository structure

- `data/` — structured target and observation data
- `docs/` — methods, field protocols, source notes, and project design
- `field-notes/` — non-sensitive observations from field work
- `photos/` — only photographs deliberately selected for repository publication

## Current status

**Pilot stage.** The immediate objective is to collect comparable observations and photographs for the Rock Creek bridge series before scaling the project.

The project should remain lightweight until the pilot demonstrates which data and publication workflows are actually useful.