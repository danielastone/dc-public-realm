#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
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


class EvidenceSummaryParser(HTMLParser):
    """Associate each evidence summary with its containing assertion element."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []
        self.current_details: dict | None = None
        self.summaries: list[tuple[str, int, int]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        aid = attrs.get("data-assertion-id")
        self.stack.append((tag, aid))
        if tag == "details" and "evidence" in attrs.get("class", "").split() and "data-source-count" in attrs:
            owner = next((assertion_id for _, assertion_id in reversed(self.stack[:-1]) if assertion_id), None)
            self.current_details = {
                "owner": owner,
                "hook": attrs["data-source-count"],
                "in_summary": False,
                "summary_text": [],
            }
        elif tag == "summary" and self.current_details is not None:
            self.current_details["in_summary"] = True

    def handle_data(self, data: str) -> None:
        if self.current_details is not None and self.current_details["in_summary"]:
            self.current_details["summary_text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "summary" and self.current_details is not None:
            self.current_details["in_summary"] = False
        elif tag == "details" and self.current_details is not None:
            owner = self.current_details["owner"]
            if not owner:
                fail("source summary is not contained by an assertion element")
            text = "".join(self.current_details["summary_text"]).strip()
            m = re.fullmatch(r"Sources\s*·\s*([0-9]+)", text)
            if not m:
                fail(f"{owner}: malformed visible source summary {text!r}")
            try:
                hook = int(self.current_details["hook"])
            except ValueError:
                fail(f"{owner}: non-integer data-source-count {self.current_details['hook']!r}")
            self.summaries.append((owner, hook, int(m.group(1))))
            self.current_details = None

        if self.stack:
            # Generated pages are expected to be well nested. Pop through the matching
            # element defensively so later ownership cannot leak across malformed markup.
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break


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

        parser = EvidenceSummaryParser()
        parser.feed(page)
        parser.close()
        seen = set()
        for aid, hook_count, visible_count in parser.summaries:
            if aid in seen:
                fail(f"{oid}: duplicate source summary for {aid}")
            seen.add(aid)
            canonical_count = len(evidence.get(aid, set()))
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
