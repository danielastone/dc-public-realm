#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
BASE = "/dc-public-realm"

OBJECTS = {
    "OBJ-0001": "jose-gervasio-artigas",
    "OBJ-0002": "jose-de-san-martin",
    "OBJ-0003": "cuban-american-friendship-urn",
}

tasks = json.loads((DATA / "research-tasks.json").read_text(encoding="utf-8"))["tasks"]
open_by_object = {oid: [] for oid in OBJECTS}
for task in tasks:
    if task.get("status") == "OPEN" and task.get("object_entity_id") in open_by_object:
        open_by_object[task["object_entity_id"]].append(task)

for oid, slug in OBJECTS.items():
    page = SITE / "objects" / slug / "index.html"
    text = page.read_text(encoding="utf-8")
    expected = open_by_object[oid]

    missing = [
        t["task_id"] for t in expected
        if f'href="{BASE}/tasks/{t["task_id"].lower()}/"' not in text
    ]
    if missing:
        raise SystemExit(
            f"PUB-003: {slug} is missing canonical open research tasks: {', '.join(missing)}"
        )

    count = len(expected)
    summary = (
        f'<p class="task-summary" data-open-task-count="{count}">'
        f'{count} open research mission{"s" if count != 1 else ""}</p>'
    )
    text = re.sub(
        r'<p class="task-summary" data-open-task-count="\d+">.*?</p>',
        '',
        text,
        flags=re.S,
    )

    research_heading = re.search(
        r'(<(?:section\b[^>]*id="research"[^>]*>.*?<h2>Research notes</h2>|<h2>Research missions</h2>))',
        text,
        flags=re.S,
    )
    if not research_heading:
        raise SystemExit(f"PUB-003: no research section found on {slug}")
    insert_at = research_heading.end()
    text = text[:insert_at] + summary + text[insert_at:]
    page.write_text(text, encoding="utf-8")

# Publish the same canonical counts on the homepage cards when those object links appear.
home = SITE / "index.html"
text = home.read_text(encoding="utf-8")
for oid, slug in OBJECTS.items():
    count = len(open_by_object[oid])
    marker = (
        f'<span class="open-task-count" data-object-id="{oid}" '
        f'data-open-task-count="{count}">{count} open research mission'
        f'{"s" if count != 1 else ""}</span>'
    )
    text = re.sub(
        rf'<span class="open-task-count" data-object-id="{re.escape(oid)}"[^>]*>.*?</span>',
        '',
        text,
        flags=re.S,
    )
    link = re.search(
        rf'(<a[^>]+href="{re.escape(BASE)}/objects/{re.escape(slug)}/"[^>]*>.*?</a>)',
        text,
        flags=re.S,
    )
    if link:
        text = text[:link.end()] + marker + text[link.end():]
home.write_text(text, encoding="utf-8")

print("PUB-003: canonical open-task counts stamped and object task sets verified")
