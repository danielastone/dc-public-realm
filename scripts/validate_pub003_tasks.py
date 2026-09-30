#!/usr/bin/env python3
from __future__ import annotations

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

errors = []
home = (SITE / "index.html").read_text(encoding="utf-8")

for oid, slug in OBJECTS.items():
    expected = open_by_object[oid]
    expected_ids = {t["task_id"] for t in expected}
    expected_count = len(expected)
    page_path = SITE / "objects" / slug / "index.html"
    if not page_path.exists():
        errors.append(f"missing object page: {slug}")
        continue
    text = page_path.read_text(encoding="utf-8")

    m = re.search(r'class="task-summary" data-open-task-count="(\d+)"', text)
    if not m:
        errors.append(f"missing task summary: {slug}")
    elif int(m.group(1)) != expected_count:
        errors.append(
            f"object task count mismatch: {slug}: published={m.group(1)} canonical={expected_count}"
        )

    found = set(
        x.upper()
        for x in re.findall(
            rf'href="{re.escape(BASE)}/tasks/([^/]+)/"',
            text,
        )
    )
    missing = sorted(expected_ids - found)
    if missing:
        errors.append(f"missing open task links on {slug}: {missing}")

    # Canonical task links may coexist with noncanonical research links, but
    # every canonical OPEN task must be public and linkable.
    for task in expected:
        task_page = SITE / "tasks" / task["task_id"].lower() / "index.html"
        if not task_page.exists():
            errors.append(f"missing task detail page: {task['task_id']}")

    hm = re.search(
        rf'data-object-id="{re.escape(oid)}" data-open-task-count="(\d+)"',
        home,
    )
    if hm and int(hm.group(1)) != expected_count:
        errors.append(
            f"homepage task count mismatch: {oid}: published={hm.group(1)} canonical={expected_count}"
        )

if errors:
    raise SystemExit("PUB-003 FAILED\n- " + "\n- ".join(errors))

counts = ", ".join(f"{oid}={len(open_by_object[oid])}" for oid in OBJECTS)
print(f"PUB-003 PASS: canonical OPEN tasks reconcile ({counts})")
