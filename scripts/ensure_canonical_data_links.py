#!/usr/bin/env python3
"""Ensure transformed public object pages retain the canonical-data route.

Some object pages are rebuilt after build_site.py. This post-build guard repairs the
navigation contract without changing research content or assertion presentation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "/dc-public-realm"
PAGES = (
    SITE / "objects" / "jose-gervasio-artigas" / "index.html",
    SITE / "objects" / "jose-de-san-martin" / "index.html",
    SITE / "objects" / "cuban-american-friendship-urn" / "index.html",
)
LINK = f'<a href="{BASE}/data/">Canonical data</a>'

for page in PAGES:
    text = page.read_text(encoding="utf-8")
    if f'href="{BASE}/data/"' in text and ">Canonical data</a>" in text:
        continue

    # Prefer the site navigation when present. Otherwise place the link at the
    # beginning of main content. Both locations keep the data route discoverable.
    if "</nav>" in text:
        text = text.replace("</nav>", f" {LINK}</nav>", 1)
    elif "<main>" in text:
        text = text.replace("<main>", f"<main><p>{LINK}</p>", 1)
    else:
        raise SystemExit(f"Cannot place canonical-data link in {page}")

    page.write_text(text, encoding="utf-8")
    print(f"Ensured canonical-data link: {page}")
