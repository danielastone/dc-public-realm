#!/usr/bin/env python3
"""Validate publication identity on the materialized entity database only."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "build" / "data"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_entities(data_dir: Path) -> list[dict]:
    path = data_dir / "entities.json"
    if not path.exists():
        raise SystemExit(f"PUBLICATION IDENTITY FAIL: materialized entities not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["entities"]


def validate_entities(entities: list[dict]) -> list[str]:
    errors: list[str] = []
    physical = [e for e in entities if e.get("entity_type") == "PhysicalObject"]
    published: list[dict] = []

    for entity in physical:
        eid = entity.get("entity_id", "<missing entity_id>")
        publication = entity.get("publication")
        if not isinstance(publication, dict):
            errors.append(f"{eid}: PhysicalObject requires publication object")
            continue

        publish = publication.get("publish")
        featured = publication.get("featured")
        if not isinstance(publish, bool):
            errors.append(f"{eid}: publication.publish must be boolean")
        if not isinstance(featured, bool):
            errors.append(f"{eid}: publication.featured must be boolean")

        if publish is True:
            slug = publication.get("slug")
            if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
                errors.append(
                    f"{eid}: published object requires lowercase kebab-case publication.slug"
                )
            if not isinstance(entity.get("canonical_name"), str) or not entity["canonical_name"].strip():
                errors.append(f"{eid}: published object requires canonical_name")
            if not isinstance(entity.get("country"), str) or not entity["country"].strip():
                errors.append(f"{eid}: published object requires country")
            published.append(entity)
        elif publish is False:
            if "slug" in publication:
                errors.append(f"{eid}: unpublished object must not define publication.slug")
            if featured is True:
                errors.append(f"{eid}: unpublished object cannot be featured")

    slugs: dict[str, str] = {}
    for entity in published:
        slug = entity["publication"].get("slug")
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            continue
        prior = slugs.get(slug)
        if prior:
            errors.append(
                f"{entity['entity_id']}: duplicate publication.slug {slug!r} also used by {prior}"
            )
        else:
            slugs[slug] = entity["entity_id"]

    featured = [
        e for e in published
        if e.get("publication", {}).get("featured") is True
    ]
    if len(featured) != 1:
        ids = ", ".join(e["entity_id"] for e in featured) or "none"
        errors.append(
            f"expected exactly one featured published object; found {len(featured)} ({ids})"
        )

    return errors


def main() -> int:
    data_dir = Path(os.environ.get("KNOWLEDGE_DATA_DIR", DEFAULT_DATA))
    entities = load_entities(data_dir)
    errors = validate_entities(entities)
    if errors:
        for error in errors:
            print(f"PUBLICATION IDENTITY ERROR: {error}", file=sys.stderr)
        print(
            f"PUBLICATION IDENTITY FAIL: {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1

    physical = [e for e in entities if e.get("entity_type") == "PhysicalObject"]
    published = [e for e in physical if e["publication"]["publish"]]
    featured = next(e for e in published if e["publication"]["featured"])
    print(
        "PUBLICATION IDENTITY PASS: "
        f"{len(physical)} PhysicalObject record(s), "
        f"{len(published)} published, "
        f"featured={featured['entity_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
