#!/usr/bin/env python3
from pathlib import Path
import re

from publication_index import path_for, published_objects

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
BASE = "/dc-public-realm"
EXPECTED = [
    ("Explore", f"{BASE}/"),
    ("Research missions", f"{BASE}/collaborate/"),
    ("About the research", f"{BASE}/methodology/"),
    ("Data", f"{BASE}/data/"),
]
PAGES = [
    Path("index.html"),
    Path("methodology/index.html"),
    Path("collaborate/index.html"),
    Path("data/index.html"),
] + [path_for(entity["entity_id"], DATA) for entity in published_objects(DATA)]

errors = []
for rel in PAGES:
    path = SITE / rel
    if not path.exists():
        errors.append(f"missing page: {rel}")
        continue
    text = path.read_text(encoding="utf-8")
    header = re.search(r"<header\b[^>]*>(.*?)</header>", text, flags=re.S)
    if not header:
        errors.append(f"missing header: {rel}")
        continue
    h = header.group(1)
    nav = re.search(r'<nav class="primary-nav"[^>]*>(.*?)</nav>', h, flags=re.S)
    if not nav:
        errors.append(f"missing primary navigation: {rel}")
    else:
        links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', nav.group(1))
        actual = [(label.strip(), href) for href, label in links]
        if actual != EXPECTED:
            errors.append(f"navigation mismatch: {rel}: {actual!r}")
    if h.count('class="site-state"') != 1 or '>Alpha</span>' not in h:
        errors.append(f"alpha state mismatch: {rel}")

if errors:
    raise SystemExit("PUB-002 FAILED\n- " + "\n- ".join(errors))
print(f"PUB-002 PASS: {len(PAGES)} audited pages share the primary navigation and alpha state")
