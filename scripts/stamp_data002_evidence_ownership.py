#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "site" / "objects" / "jose-gervasio-artigas" / "index.html"

page = PAGE.read_text(encoding="utf-8")
pattern = re.compile(
    r'(<details class="evidence" data-source-count="[0-9]+")(?=>)'
    r'(?P<body>.*?<a href="#provenance-(?P<aid>A-[0-9A-Z]+)">View technical record</a>.*?</details>)',
    re.S,
)

def stamp(m: re.Match[str]) -> str:
    return f'{m.group(1)} data-assertion-id="{m.group("aid")}"{m.group("body")}'

page, count = pattern.subn(stamp, page)
if count == 0:
    raise SystemExit("DATA-002: no legacy Artigas evidence panels found to stamp")
PAGE.write_text(page, encoding="utf-8")
print(f"DATA-002: stamped explicit ownership on {count} legacy Artigas evidence panels")
