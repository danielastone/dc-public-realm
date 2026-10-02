#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from publication_chrome import primary_nav, site_state

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
NAV = primary_nav()
ALPHA = site_state()

# Transitional contract boundary. Generators are being migrated to
# publication_chrome; this pass remains until every audited page emits the
# shared header at construction time.
for path in SITE.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    if "<header" not in text:
        continue

    header_match = re.search(r"(<header\b[^>]*>)(.*?)(</header>)", text, flags=re.S)
    if not header_match:
        raise SystemExit(f"PUB-002: malformed header: {path.relative_to(SITE)}")
    header = header_match.group(2)
    if re.search(r"<nav\b[^>]*>.*?</nav>", header, flags=re.S):
        header = re.sub(r"<nav\b[^>]*>.*?</nav>", NAV, header, count=1, flags=re.S)
    else:
        header += NAV

    header = re.sub(r'<span class="site-state"[^>]*>.*?</span>', '', header, flags=re.S)
    header = ALPHA + header
    replacement = header_match.group(1) + header + header_match.group(3)
    text = text[:header_match.start()] + replacement + text[header_match.end():]
    path.write_text(text, encoding="utf-8")

print("PUB-002: shared primary navigation and alpha state enforced")
