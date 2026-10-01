#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data"
DEFAULT_SITE = ROOT / "site"

OBJECTS = {
    "OBJ-0001": "jose-gervasio-artigas",
    "OBJ-0002": "jose-de-san-martin",
    "OBJ-0003": "cuban-american-friendship-urn",
}


def fail(message: str) -> None:
    print(f"DATA-002 FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return html.unescape(m.group(1)) if m else None


def strip_tags(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def reconcile(data_dir: Path = DEFAULT_DATA, site_dir: Path = DEFAULT_SITE) -> None:
    def load(name: str):
        return json.loads((data_dir / name).read_text(encoding="utf-8"))

    ep = load("entities.json")
    evp = load("assertion-evidence.json")
    entities = {x["entity_id"]: x for x in ep["entities"]}
    evidence = defaultdict(set)
    for row in evp["assertion_evidence"]:
        evidence[row["assertion_id"]].add(row["source_id"])

    missing = sorted(set(OBJECTS) - set(entities))
    if missing:
        fail(f"object ids missing from canonical entities: {missing}")

    home_path = site_dir / "index.html"
    if not home_path.exists():
        fail("missing site/index.html")
    home = home_path.read_text(encoding="utf-8")

    pages = {}
    for oid, slug in OBJECTS.items():
        path = site_dir / "objects" / slug / "index.html"
        if not path.exists():
            fail(f"missing object page {path}")
        pages[oid] = path.read_text(encoding="utf-8")

    card_tags = re.findall(r'<article\s+class="card"[^>]*data-object-id="[^"]+"[^>]*>', home)
    card_ids = [attr(tag, "data-object-id") for tag in card_tags]
    if len(card_ids) != len(set(card_ids)):
        fail("homepage contains duplicate object hooks")
    cards = dict(zip(card_ids, card_tags))
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
        if card_end < 0:
            fail(f"{oid}: homepage card has no closing article tag")
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

        # DATA-001 gives factual containers a stable data-assertion-id. DATA-002
        # keys off that semantic identity rather than a CSS class so specialized
        # and generic renderers can share one publication contract.
        seen_assertions = set()
        for aid in sorted(evidence):
            opener = re.search(
                rf'<(?P<tag>article|li)[^>]*data-assertion-id="{re.escape(aid)}"[^>]*>',
                page,
            )
            if not opener:
                continue
            if aid in seen_assertions:
                fail(f"{oid}: duplicate rendered assertion {aid}")
            seen_assertions.add(aid)
            tag = opener.group("tag")
            close = page.find(f'</{tag}>', opener.end())
            if close < 0:
                fail(f"{oid}/{aid}: assertion container has no closing {tag} tag")
            block = page[opener.start() : close + len(tag) + 3]
            details = re.search(
                r'<details\s+class="evidence"[^>]*data-source-count="([0-9]+)"[^>]*>.*?<summary>Sources · ([0-9]+)</summary>',
                block,
                flags=re.S,
            )
            canonical_count = len(evidence.get(aid, set()))
            if not details:
                if canonical_count:
                    fail(f"{oid}/{aid}: published source summary lacks machine-readable source count")
                continue
            hook_count, visible_count = map(int, details.groups())
            if hook_count != visible_count or hook_count != canonical_count:
                fail(f"{oid}/{aid}: rendered source count hook={hook_count}, visible={visible_count}, canonical={canonical_count}")

    print(f"DATA-002 PASS: reconciled {len(OBJECTS)} object summaries and rendered evidence-source counts")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--site-dir", type=Path, default=DEFAULT_SITE)
    args = parser.parse_args()
    reconcile(args.data_dir, args.site_dir)


if __name__ == "__main__":
    main()
