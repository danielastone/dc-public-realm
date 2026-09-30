#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "/dc-public-realm"

NAV = (
    f'<nav class="primary-nav" aria-label="Primary">'
    f'<a href="{BASE}/">Explore</a>'
    f'<a href="{BASE}/collaborate/">Research missions</a>'
    f'<a href="{BASE}/methodology/">About the research</a>'
    f'<a href="{BASE}/data/">Data</a>'
    f'</nav>'
)
ALPHA = '<span class="site-state" aria-label="Site status: alpha">Alpha</span>'

# Public HTML is produced by several generators. Until those generators are
# consolidated, this final publication transform is the contract boundary.
for path in SITE.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    if "<header" not in text:
        continue

    # Replace the first primary-looking nav in the header. Object-local tabs
    # and in-page navigation outside the header remain untouched.
    header_match = re.search(r"(<header\b[^>]*>)(.*?)(</header>)", text, flags=re.S)
    if not header_match:
        raise SystemExit(f"PUB-002: malformed header: {path.relative_to(SITE)}")
    header = header_match.group(2)
    if re.search(r"<nav\b[^>]*>.*?</nav>", header, flags=re.S):
        header = re.sub(r"<nav\b[^>]*>.*?</nav>", NAV, header, count=1, flags=re.S)
    else:
        header += NAV

    # Alpha is a site-level publication state, not page-specific copy.
    header = re.sub(r'<span class="site-state"[^>]*>.*?</span>', '', header, flags=re.S)
    header = ALPHA + header
    replacement = header_match.group(1) + header + header_match.group(3)
    text = text[:header_match.start()] + replacement + text[header_match.end():]
    path.write_text(text, encoding="utf-8")

print("PUB-002: shared primary navigation and alpha state enforced")
