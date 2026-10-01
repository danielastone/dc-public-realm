#!/usr/bin/env python3
"""Fail CI when published object HTML drifts from computed assertion status.

The canonical machine-readable publication is site/data/assertions.json, emitted by
build_site.py from the materialized database. Every published object page must expose
its assertion id and computed status in the rendered HTML.
"""
from __future__ import annotations
import json
from pathlib import Path

from publication_index import path_for, published_objects

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
ASSERTIONS = SITE / "data" / "assertions.json"


def marker(aid: str, status: str) -> str:
    return f'data-assertion-id="{aid}" data-computed-status="{status}"'


def main() -> None:
    if not ASSERTIONS.exists():
        raise SystemExit("publication consistency: missing site/data/assertions.json; run build_site.py first")
    payload = json.loads(ASSERTIONS.read_text(encoding="utf-8"))
    assertions = payload.get("assertions", payload if isinstance(payload, list) else [])
    objects = published_objects(DATA)
    object_ids = {entity["entity_id"] for entity in objects}
    errors: list[str] = []
    for entity in objects:
        oid = entity["entity_id"]
        path = SITE / path_for(oid, DATA)
        if not path.exists():
            errors.append(f"{oid}: missing published object page {path.relative_to(ROOT)}")
            continue
        html = path.read_text(encoding="utf-8")
        relevant = [a for a in assertions if a.get("subject_id") == oid]
        for a in relevant:
            aid = a["assertion_id"]
            status = a.get("computed_status")
            if not status:
                errors.append(f"{aid}: machine-readable publication lacks computed_status")
                continue
            if marker(aid, status) not in html:
                errors.append(f"{aid}: HTML does not expose canonical status {status}")
    if errors:
        raise SystemExit("publication consistency FAILED\n- " + "\n- ".join(errors))
    checked = sum(1 for a in assertions if a.get("subject_id") in object_ids)
    print(f"publication consistency PASS: checked {checked} direct object assertions")


if __name__ == "__main__":
    main()
