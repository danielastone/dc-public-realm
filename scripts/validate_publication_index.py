#!/usr/bin/env python3
"""Validate publication-index contract and report transitional hard-coded routing debt."""
from __future__ import annotations

import ast
import json
import os
import sys
import tempfile
from pathlib import Path

import publication_index as pi

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DATA = Path(os.environ.get("KNOWLEDGE_DATA_DIR", ROOT / "build" / "data"))


def fail(message: str) -> None:
    print(f"PUBLICATION INDEX ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def contract_tests() -> None:
    objects = pi.published_objects(DATA)
    ids = [e["entity_id"] for e in objects]
    if ids != sorted(ids):
        fail("published_objects() order is not deterministic by entity_id")

    for entity in objects:
        eid = entity["entity_id"]
        slug = entity["publication"]["slug"]
        if pi.object_by_id(eid, DATA)["entity_id"] != eid:
            fail(f"{eid}: object_by_id disagreement")
        if pi.object_by_slug(slug, DATA)["entity_id"] != eid:
            fail(f"{eid}: object_by_slug disagreement")
        if pi.slug_for(eid, DATA) != slug:
            fail(f"{eid}: slug_for disagreement")
        expected = Path("objects") / slug / "index.html"
        if pi.path_for(eid, DATA) != expected:
            fail(f"{eid}: path_for disagreement")
        if pi.href(eid, "/dc-public-realm", DATA) != f"/dc-public-realm/objects/{slug}/":
            fail(f"{eid}: href disagreement")

    featured = pi.featured_object(DATA)
    if featured["publication"].get("featured") is not True:
        fail("featured_object returned non-featured entity")

    try:
        pi.object_by_id("OBJ-DOES-NOT-EXIST", DATA)
    except pi.UnknownObjectError:
        pass
    else:
        fail("unknown object id did not raise UnknownObjectError")

    unpublished = next(
        e for e in json.loads((DATA / "entities.json").read_text(encoding="utf-8"))["entities"]
        if e.get("entity_type") == "PhysicalObject"
        and e.get("publication", {}).get("publish") is False
    )
    try:
        pi.object_by_id(unpublished["entity_id"], DATA)
    except pi.NotPublishedError:
        pass
    else:
        fail("unpublished object did not raise NotPublishedError")

    exported_dicts = [
        name for name, value in vars(pi).items()
        if not name.startswith("_") and isinstance(value, dict)
    ]
    if exported_dicts:
        fail("publication_index exports mapping(s): " + ", ".join(sorted(exported_dicts)))


def baseline_fail_closed_test() -> None:
    baseline = ROOT / "data" / "entities.json"
    payload = json.loads(baseline.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="publication-index-baseline-") as raw:
        d = Path(raw)
        (d / "entities.json").write_text(json.dumps(payload), encoding="utf-8")
        try:
            pi.published_objects(d)
        except pi.PublicationIndexError:
            return
        fail("publication index did not fail closed on frozen baseline")


def canonical_slugs() -> dict[str, str]:
    return {
        e["entity_id"]: e["publication"]["slug"]
        for e in pi.published_objects(DATA)
    }


def script_string_literals(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def debt_meter() -> tuple[int, int, int]:
    canonical = canonical_slugs()
    pair_count = 0
    pair_files: set[Path] = set()
    literal_files: set[Path] = set()

    for path in sorted(SCRIPTS.glob("*.py")):
        if path.name in {"publication_index.py", "validate_publication_index.py"}:
            continue
        source = path.read_text(encoding="utf-8")
        literals = script_string_literals(path)

        # Transitional pair debt is counted only when an object ID and slug are
        # coupled in the same source line. File-wide co-occurrence is not a
        # relationship and would overcount unrelated literals.
        for line in source.splitlines():
            ids_here = [eid for eid in canonical if eid in line]
            slugs_here = [slug for slug in canonical.values() if slug in line]
            for eid in ids_here:
                expected = canonical[eid]
                if expected in slugs_here:
                    pair_count += 1
                    pair_files.add(path)
                wrong = [slug for slug in slugs_here if slug != expected]
                if wrong:
                    fail(
                        f"{path.relative_to(ROOT)}: {eid} is paired with non-canonical slug "
                        f"{wrong[0]!r}; expected {expected!r}"
                    )

        for slug in canonical.values():
            if any(slug in literal for literal in literals):
                literal_files.add(path)

    print(
        "PUBLICATION INDEX DEBT: "
        f"{pair_count} id/slug pair occurrence(s) across {len(pair_files)} script(s); "
        f"slug-bearing literals in {len(literal_files)} script(s)"
    )
    return pair_count, len(pair_files), len(literal_files)


def main() -> int:
    contract_tests()
    baseline_fail_closed_test()
    pairs, pair_files, literal_files = debt_meter()
    print(
        "PUBLICATION INDEX PASS: contract valid; baseline fails closed; "
        f"transitional debt={pairs} pairs/{pair_files} scripts, literals in {literal_files} scripts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
