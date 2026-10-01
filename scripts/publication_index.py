#!/usr/bin/env python3
"""Shared publication-object discovery and path helpers.

This module reads materialized entity data. It intentionally fails closed when
publication metadata is absent so consumers cannot silently iterate over an
empty publication set.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data"


class PublicationIndexError(RuntimeError):
    pass


class UnknownObjectError(KeyError):
    pass


class NotPublishedError(KeyError):
    pass


def _data_dir(data_dir: str | Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return Path(os.environ.get("KNOWLEDGE_DATA_DIR", DEFAULT_DATA))


def _load_entities(data_dir: str | Path | None = None) -> list[dict]:
    path = _data_dir(data_dir) / "entities.json"
    if not path.exists():
        raise PublicationIndexError(f"entities file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    entities = payload.get("entities")
    if not isinstance(entities, list):
        raise PublicationIndexError(f"invalid entities payload: {path}")
    return entities


def _physical_objects(data_dir: str | Path | None = None) -> list[dict]:
    return [
        e for e in _load_entities(data_dir)
        if e.get("entity_type") == "PhysicalObject"
    ]


def _require_publication_contract(data_dir: str | Path | None = None) -> list[dict]:
    objects = _physical_objects(data_dir)
    missing = [e.get("entity_id", "<missing entity_id>") for e in objects
               if not isinstance(e.get("publication"), dict)]
    if missing:
        raise PublicationIndexError(
            "publication metadata missing for PhysicalObject record(s): "
            + ", ".join(sorted(missing))
        )
    return objects


def published_objects(data_dir: str | Path | None = None) -> tuple[dict, ...]:
    objects = _require_publication_contract(data_dir)
    published = [e for e in objects if e["publication"].get("publish") is True]
    if not published:
        raise PublicationIndexError("publication metadata present but no published objects found")
    return tuple(sorted(published, key=lambda e: e["entity_id"]))


def object_by_id(entity_id: str, data_dir: str | Path | None = None) -> dict:
    objects = {e["entity_id"]: e for e in _require_publication_contract(data_dir)}
    if entity_id not in objects:
        raise UnknownObjectError(entity_id)
    entity = objects[entity_id]
    if entity["publication"].get("publish") is not True:
        raise NotPublishedError(entity_id)
    return entity


def object_by_slug(slug: str, data_dir: str | Path | None = None) -> dict:
    for entity in published_objects(data_dir):
        if entity["publication"].get("slug") == slug:
            return entity
    raise UnknownObjectError(slug)


def slug_for(entity_id: str, data_dir: str | Path | None = None) -> str:
    return object_by_id(entity_id, data_dir)["publication"]["slug"]


def path_for(entity_id: str, data_dir: str | Path | None = None) -> Path:
    return Path("objects") / slug_for(entity_id, data_dir) / "index.html"


def href(entity_id: str, base: str = "", data_dir: str | Path | None = None) -> str:
    base = base.rstrip("/")
    return f"{base}/objects/{slug_for(entity_id, data_dir)}/"


def featured_object(data_dir: str | Path | None = None) -> dict:
    featured = [
        e for e in published_objects(data_dir)
        if e["publication"].get("featured") is True
    ]
    if len(featured) != 1:
        ids = ", ".join(e["entity_id"] for e in featured) or "none"
        raise PublicationIndexError(
            f"expected exactly one featured published object; found {len(featured)} ({ids})"
        )
    return featured[0]


__all__ = (
    "PublicationIndexError",
    "UnknownObjectError",
    "NotPublishedError",
    "published_objects",
    "object_by_id",
    "object_by_slug",
    "slug_for",
    "path_for",
    "href",
    "featured_object",
)
