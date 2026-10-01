#!/usr/bin/env python3
"""Prove DATA-002 fails on stale or cross-object rendered summary state."""
from __future__ import annotations

import contextlib
import io
import re
import shutil
import tempfile
from pathlib import Path

from validate_data002_summary_reconciliation import reconcile, ROOT

SOURCE_DATA = ROOT / "data"
SOURCE_SITE = ROOT / "site"


def copy_fixture(tmp: Path) -> tuple[Path, Path]:
    data = tmp / "data"
    site = tmp / "site"
    data.mkdir()
    for name in ("entities.json", "assertion-evidence.json"):
        shutil.copy2(SOURCE_DATA / name, data / name)
    shutil.copytree(SOURCE_SITE, site)
    return data, site


def expect_fail(label: str, mutate) -> None:
    with tempfile.TemporaryDirectory(prefix="data002-") as raw:
        data, site = copy_fixture(Path(raw))
        mutate(data, site)
        try:
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                reconcile(data, site)
        except SystemExit as exc:
            if exc.code != 1:
                raise AssertionError(f"{label}: unexpected exit code {exc.code}") from exc
            print(f"PASS mutation rejected: {label}")
            return
        raise AssertionError(f"{label}: DATA-002 incorrectly accepted mutated publication")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) < 1:
        raise AssertionError(f"fixture token not found in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def stale_name(_data: Path, site: Path) -> None:
    p = site / "objects" / "jose-gervasio-artigas" / "index.html"
    text = p.read_text(encoding="utf-8")
    pattern = r'(<h1\b[^>]*\bdata-object-id="OBJ-0001"[^>]*>).*?(</h1>)'
    text, count = re.subn(pattern, r'\1Stale Artigas Name\2', text, count=1, flags=re.S)
    if count != 1:
        raise AssertionError(f"expected exactly one OBJ-0001 heading in {p}, found {count}")
    p.write_text(text, encoding="utf-8")


def stale_country(_data: Path, site: Path) -> None:
    p = site / "objects" / "jose-de-san-martin" / "index.html"
    replace_once(p, 'data-object-country="Argentina">Argentina ·', 'data-object-country="Uruguay">Uruguay ·')


def stale_source_count(_data: Path, site: Path) -> None:
    p = site / "objects" / "cuban-american-friendship-urn" / "index.html"
    text = p.read_text(encoding="utf-8")
    marker = 'class="evidence" data-source-count="'
    start = text.find(marker)
    if start < 0:
        raise AssertionError("no evidence source-count hook in Cuban Urn fixture")
    nstart = start + len(marker)
    nend = text.find('"', nstart)
    current = int(text[nstart:nend])
    text = text[:nstart] + str(current + 1) + text[nend:]
    p.write_text(text, encoding="utf-8")


def cross_object_binding(_data: Path, site: Path) -> None:
    p = site / "objects" / "jose-de-san-martin" / "index.html"
    replace_once(p, 'data-object-id="OBJ-0002"', 'data-object-id="OBJ-0001"')


def wrong_home_route(_data: Path, site: Path) -> None:
    p = site / "index.html"
    replace_once(p, '/objects/jose-gervasio-artigas/', '/objects/jose-de-san-martin/')


def duplicate_home_object(_data: Path, site: Path) -> None:
    p = site / "index.html"
    replace_once(p, 'data-object-id="OBJ-0002"', 'data-object-id="OBJ-0001"')


def main() -> None:
    if not SOURCE_SITE.exists():
        raise SystemExit("DATA-002 synthetic tests require a built site; run after the publication transforms")
    tests = [
        ("stale object name", stale_name),
        ("stale country", stale_country),
        ("stale evidence source count", stale_source_count),
        ("cross-object page binding", cross_object_binding),
        ("wrong homepage object route", wrong_home_route),
        ("duplicate homepage object binding", duplicate_home_object),
    ]
    for label, mutate in tests:
        expect_fail(label, mutate)
    print(f"DATA-002 synthetic PASS: {len(tests)} stale/cross-object mutations rejected")


if __name__ == "__main__":
    main()
