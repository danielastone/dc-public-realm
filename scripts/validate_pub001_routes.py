#!/usr/bin/env python3
"""Validate the final PUB-001 canonical-data publication contract."""
from pathlib import Path

from publication_index import path_for, published_objects, slug_for

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
BASE = "/dc-public-realm"

failures: list[str] = []

def require_file(path: Path) -> str:
    if not path.is_file():
        failures.append(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")

def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        failures.append(f"missing {label}: {needle!r}")

index = require_file(SITE / "data" / "index.html")
require(index, "<h1>Canonical data</h1>", "canonical-data heading")

for filename in (
    "assertions.json",
    "entities.json",
    "assertion-evidence.json",
    "research-tasks.json",
    "claim-modes.json",
    "external-records.json",
):
    require_file(SITE / "data" / filename)
    require(index, f"{BASE}/data/{filename}", f"data-index link for {filename}")

home = require_file(SITE / "index.html")
require(home, f'href="{BASE}/data/"', "home canonical-data route")

objects = published_objects(DATA)
expected_slugs = {slug_for(entity["entity_id"], DATA) for entity in objects}
objects_dir = SITE / "objects"
actual_slugs = {
    page.parent.name
    for page in objects_dir.glob("*/index.html")
    if page.is_file()
}
missing = sorted(expected_slugs - actual_slugs)
orphans = sorted(actual_slugs - expected_slugs)
if missing:
    failures.append(f"missing published object page(s): {missing}")
if orphans:
    failures.append(f"orphan object page(s): {orphans}")

for entity in objects:
    oid = entity["entity_id"]
    slug = slug_for(oid, DATA)
    page = require_file(SITE / path_for(oid, DATA))
    require(page, f'href="{BASE}/data/"', f"{slug} canonical-data route")
    require(page, ">Canonical data</a>", f"{slug} canonical-data label")

if failures:
    print("PUB-001 ROUTE VALIDATION FAILED")
    for failure in failures:
        print(f"- {failure}")
    raise SystemExit(1)

print(f"PUB-001 route validation PASS: data index, six JSON outputs, home route, and {len(objects)} object routes; object-page bijection exact")
