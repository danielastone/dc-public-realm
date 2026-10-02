#!/usr/bin/env python3
"""PUB-004: every internal site link resolves to a published file.

Scope: href attributes in site/**/*.html whose URL path is BASE or under
BASE/. External URLs and non-site schemes are ignored. Query strings and
fragments are stripped; HTML entities and percent-encoding are decoded;
directory URLs resolve to index.html.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE = "/dc-public-realm"
HREF = re.compile(r"""\bhref\s*=\s*(["'])(.*?)\1""", re.IGNORECASE | re.DOTALL)


def target_for(raw: str) -> Path | None:
    """Filesystem target for an internal href, or None if not internal."""
    parts = urlsplit(html.unescape(raw).strip())
    if parts.scheme or parts.netloc:
        return None  # external (https:, mailto:, //host, ...)
    path = unquote(parts.path)
    if path != BASE and not path.startswith(BASE + "/"):
        return None
    rel = path[len(BASE):].lstrip("/")
    target = SITE / rel
    if rel == "" or path.endswith("/"):
        target = target / "index.html"
    return target


def main() -> int:
    if not (SITE / "index.html").is_file():
        print("PUB-004 FAIL: site/ not built")
        return 1
    failures: list[str] = []
    pages = links = 0
    site_root = SITE.resolve()
    for page in sorted(SITE.rglob("*.html")):
        pages += 1
        for _, raw in HREF.findall(page.read_text(encoding="utf-8")):
            target = target_for(raw)
            if target is None:
                continue
            links += 1
            resolved = target.resolve()
            escapes = site_root not in resolved.parents and resolved != site_root
            if escapes or not resolved.is_file():
                failures.append(
                    f"{page.relative_to(SITE)}: href {raw!r} -> expected "
                    f"{target.relative_to(ROOT) if not escapes else target} "
                    f"({'escapes site/' if escapes else 'missing'})"
                )
    if failures:
        print(f"PUB-004 FAIL: {len(failures)} unresolved internal link(s)")
        for f in failures:
            print(f"- {f}")
        return 1
    print(f"PUB-004 PASS: {links} internal links across {pages} pages resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
