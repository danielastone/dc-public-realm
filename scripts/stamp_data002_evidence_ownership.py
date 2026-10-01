#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJECTS_DIR = ROOT / "site" / "objects"

pattern = re.compile(
    r'(<details class="evidence" data-source-count="[0-9]+")(?=>)'
    r'(?P<body>.*?<a href="#provenance-(?P<aid>A-[0-9A-Z]+)">View technical record</a>.*?</details>)',
    re.S,
)

def stamp(m: re.Match[str]) -> str:
    return f'{m.group(1)} data-evidence-assertion-id="{m.group("aid")}"{m.group("body")}'

pages = sorted(OBJECTS_DIR.glob("*/index.html"))
if not pages:
    raise SystemExit("DATA-002: no object pages found to stamp")

total = 0
for page_path in pages:
    page = page_path.read_text(encoding="utf-8")
    page, count = pattern.subn(stamp, page)
    if count:
        page_path.write_text(page, encoding="utf-8")
        total += count
        print(f"DATA-002: stamped explicit ownership on {count} evidence panels in {page_path.parent.name}")

if total == 0:
    raise SystemExit("DATA-002: no unstamped evidence panels found across object pages")
print(f"DATA-002: stamped explicit ownership on {total} evidence panels across object pages")
