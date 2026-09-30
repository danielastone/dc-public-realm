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

def task_card(task):
    task_id = html.escape(task["task_id"])
    title = html.escape(task["title"])
    gap = html.escape(task["research_gap"])
    slug = task["task_id"].lower()
    return (
        f'<article class="task canonical-research-task" data-task-id="{task_id}">'
        f'<div class="kicker">Research mission · OPEN</div>'
        f'<h3><a href="{BASE}/tasks/{slug}/">{title}</a></h3>'
        f'<p>{gap}</p>'
        f'<a class="button" href="{BASE}/tasks/{slug}/">Research task</a>'
        f'</article>'
    )

for oid, slug in OBJECTS.items():
    page = SITE / "objects" / slug / "index.html"
    text = page.read_text(encoding="utf-8")
    expected = open_by_object[oid]
    count = len(expected)
    summary = (
        f'<p class="task-summary" data-open-task-count="{count}">'
        f'{count} open research mission{"s" if count != 1 else ""}</p>'
    )

    # Remove any previous PUB-003 summary before restamping.
    text = re.sub(
        r'<p class="task-summary" data-open-task-count="\d+">.*?</p>',
        '',
        text,
        flags=re.S,
    )

    # Determine which canonical OPEN tasks are already represented.
    missing = [
        t for t in expected
        if f'href="{BASE}/tasks/{t["task_id"].lower()}/"' not in text
    ]

    research_heading = re.search(
        r'(<(?:section\b[^>]*id="research"[^>]*>.*?<h2>Research notes</h2>|<h2>Research missions</h2>))',
        text,
        flags=re.S,
    )

    if research_heading:
        insert_at = research_heading.end()
        text = text[:insert_at] + summary + text[insert_at:]
        # If downstream transforms dropped individual canonical tasks, restore them
        # inside the existing research area rather than merely reporting a count.
        if missing:
            cards = ''.join(task_card(t) for t in missing)
            if '<section' in research_heading.group(1):
                close = text.find('</section>', insert_at)
                if close == -1:
                    raise SystemExit(f"PUB-003: malformed research section on {slug}")
                text = text[:close] + cards + text[close:]
            else:
                # Generic pages use an h2-only research section. Insert the missing
                # tasks immediately after the summary.
                pos = insert_at + len(summary)
                text = text[:pos] + cards + text[pos:]
    else:
        # A final page with canonical OPEN tasks but no research section is a
        # publication defect. Materialize the section directly from canonical data.
        cards = ''.join(task_card(t) for t in expected)
        section = (
            f'<section id="research"><h2>Research missions</h2>{summary}'
            f'<p>These open research missions identify records that could clarify '
            f'or qualify this catalog record.</p>{cards}</section>'
        )
        if '</main>' not in text:
            raise SystemExit(f"PUB-003: no insertion point for research section on {slug}")
        text = text.replace('</main>', section + '</main>', 1)

    page.write_text(text, encoding="utf-8")

# Publish the same canonical counts on the homepage cards where object links appear.
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

print("PUB-003: canonical OPEN research tasks and counts reconciled")
