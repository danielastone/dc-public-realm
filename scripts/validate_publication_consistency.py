#!/usr/bin/env python3
"""Fail CI when published object HTML drifts from computed assertion status.

The canonical machine-readable publication is site/data/assertions.json, emitted by
build_site.py from the materialized database. Every generic object page must expose
its assertion id and computed status in the rendered HTML. Bespoke publication
surfaces are not exempt: if they publish an assertion, they must carry the same
machine-readable marker.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ASSERTIONS = SITE / "data" / "assertions.json"
OBJECTS = {
    "OBJ-0001": SITE / "objects" / "jose-gervasio-artigas" / "index.html",
    "OBJ-0002": SITE / "objects" / "jose-de-san-martin" / "index.html",
    "OBJ-0003": SITE / "objects" / "cuban-american-friendship-urn" / "index.html",
}


def marker(aid: str, status: str) -> str:
    return f'data-assertion-id="{aid}" data-computed-status="{status}"'


def main() -> None:
    if not ASSERTIONS.exists():
        raise SystemExit("publication consistency: missing site/data/assertions.json; run build_site.py first")
    payload = json.loads(ASSERTIONS.read_text(encoding="utf-8"))
    assertions = payload.get("assertions", payload if isinstance(payload, list) else [])
    errors: list[str] = []
    for oid, path in OBJECTS.items():
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
    print(f"publication consistency PASS: checked {sum(1 for a in assertions if a.get('subject_id') in OBJECTS)} direct object assertions")


if __name__ == "__main__":
    main()
