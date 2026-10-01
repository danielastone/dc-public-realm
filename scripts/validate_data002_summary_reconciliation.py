#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"

OBJECTS = {
    "OBJ-0001": "jose-gervasio-artigas",
    "OBJ-0002": "jose-de-san-martin",
    "OBJ-0003": "cuban-american-friendship-urn",
}


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def fail(message: str) -> None:
    print(f"DATA-002 FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return html.unescape(m.group(1)) if m else None


def strip_tags(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def object_pages() -> dict[str, str]:
    pages = {}
    for oid, slug in OBJECTS.items():
        path = SITE / "objects" / slug / "index.html"
        if not path.exists():
            fail(f"missing object page {path.relative_to(ROOT)}")
        pages[oid] = path.read_text(encoding="utf-8")
    return pages


def reconcile() -> None:
    ep = load("entities.json")
    evp = load("assertion-evidence.json")
    entities = {x["entity_id"]: x for x in ep["entities"]}
    evidence = defaultdict(set)
    for row in evp["assertion_evidence"]:
        evidence[row["assertion_id"]].add(row["source_id"])

    missing = sorted(set(OBJECTS) - set(entities))
    if missing:
        fail(f"object ids missing from canonical entities: {missing}")

    home_path = SITE / "index.html"
    if not home_path.exists():
        fail("missing site/index.html")
    home = home_path.read_text(encoding="utf-8")
    pages = object_pages()

    card_tags = re.findall(r'<article\s+class="card"[^>]*data-object-id="[^"]+"[^>]*>', home)
    cards = {attr(tag, "data-object-id"): tag for tag in card_tags}
    if set(cards) != set(OBJECTS):
        fail(f"homepage object hooks differ from expected objects: {sorted(cards)}")

    for oid, slug in OBJECTS.items():
        entity = entities[oid]
        name = entity.get("canonical_name")
        country = entity.get("country")
        if not name or not country:
            fail(f"{oid}: canonical_name and country are required")

        card_tag = cards[oid]
        card_start = home.index(card_tag)
        card_end = home.find("</article>", card_start)
        card = home[card_start : card_end + len("</article>")]
        if html.escape(name) not in card:
            fail(f"{oid}: homepage name does not match canonical_name {name!r}")
        if html.escape(country) not in card:
            fail(f"{oid}: homepage country does not match canonical country {country!r}")
        expected_href = f'/dc-public-realm/objects/{slug}/'
        if expected_href not in card:
            fail(f"{oid}: homepage card points to wrong object route")

        page = pages[oid]
        h1s = re.findall(r'<h1[^>]*data-object-id="[^"]+"[^>]*>.*?</h1>', page, flags=re.S)
        if len(h1s) != 1:
            fail(f"{oid}: expected exactly one hooked object heading, found {len(h1s)}")
        if attr(h1s[0], "data-object-id") != oid:
            fail(f"{oid}: object page hook identifies another object")
        if strip_tags(h1s[0]) != name:
            fail(f"{oid}: rendered heading {strip_tags(h1s[0])!r} != canonical_name {name!r}")

        kickers = re.findall(r'<div[^>]*class="kicker"[^>]*data-object-country="[^"]+"[^>]*>.*?</div>', page, flags=re.S)
        if len(kickers) != 1:
            fail(f"{oid}: expected exactly one hooked country kicker, found {len(kickers)}")
        if attr(kickers[0], "data-object-country") != country:
            fail(f"{oid}: rendered country hook != canonical country {country!r}")
        if not strip_tags(kickers[0]).startswith(country + " ·"):
            fail(f"{oid}: visible country label != canonical country {country!r}")

        articles = re.findall(r'<article\s+class="assertion">.*?</article>', page, flags=re.S)
        seen_assertions = set()
        for article in articles:
            m = re.search(r'<div\s+class="kicker">(A-[0-9]+)</div>', article)
            if not m:
                fail(f"{oid}: assertion block lacks assertion id")
            aid = m.group(1)
            if aid in seen_assertions:
                fail(f"{oid}: duplicate rendered assertion {aid}")
            seen_assertions.add(aid)
            details = re.search(r'<details\s+class="evidence"[^>]*data-source-count="([0-9]+)"[^>]*>.*?<summary>Sources · ([0-9]+)</summary>', article, flags=re.S)
            if not details:
                fail(f"{oid}/{aid}: missing machine-readable evidence source count")
            hook_count, visible_count = map(int, details.groups())
            canonical_count = len(evidence.get(aid, set()))
            if hook_count != visible_count or hook_count != canonical_count:
                fail(f"{oid}/{aid}: rendered source count hook={hook_count}, visible={visible_count}, canonical={canonical_count}")

    print(f"DATA-002 PASS: reconciled {len(OBJECTS)} object summaries and rendered evidence-source counts")


if __name__ == "__main__":
    reconcile()
