#!/usr/bin/env python3
"""Validate the final PUB-001 canonical-data publication contract."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
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

for slug in (
    "jose-gervasio-artigas",
    "jose-de-san-martin",
    "cuban-american-friendship-urn",
):
    page = require_file(SITE / "objects" / slug / "index.html")
    require(page, f'href="{BASE}/data/"', f"{slug} canonical-data route")
    require(page, ">Canonical data</a>", f"{slug} canonical-data label")

if failures:
    print("PUB-001 ROUTE VALIDATION FAILED")
    for failure in failures:
        print(f"- {failure}")
    raise SystemExit(1)

print("PUB-001 route validation PASS: data index, six JSON outputs, home route, and three object routes")
