#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PAGE = ROOT / "site" / "objects" / "jose-gervasio-artigas" / "index.html"
OID = "OBJ-0001"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


entities = {x["entity_id"]: x for x in load("entities.json")["entities"]}
entity = entities[OID]
name = entity.get("canonical_name")
country = entity.get("country")
if not name or not country:
    raise SystemExit(f"DATA-002: {OID} requires canonical_name and country")

source_ids: dict[str, set[str]] = {}
for row in load("assertion-evidence.json")["assertion_evidence"]:
    source_ids.setdefault(row["assertion_id"], set()).add(row["source_id"])

page = PAGE.read_text(encoding="utf-8")

# The specialized Artigas renderer runs after the generic site builder. Restore the
# same machine-readable identity contract from canonical entity state rather than
# maintaining a second presentation truth table.
page, n = re.subn(
    r'<div class="eyebrow">OBJ-0001 · URUGUAY</div><h1>.*?</h1>',
    f'<div class="kicker" data-object-country="{html.escape(country, quote=True)}">{html.escape(country)} · {OID}</div>'
    f'<h1 data-object-id="{OID}">{html.escape(name)}</h1>',
    page,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("DATA-002: Artigas identity surface was not found exactly once")

# Normalize the specialized claim cards to the same assertion/evidence hooks used
# by the generic object pages. Keep the human-facing evidence qualifier after the
# canonical source count so differing-record/source-history context is not lost.
def normalize_claim(match: re.Match[str]) -> str:
    article = match.group(0)
    aid_match = re.search(r'href="#provenance-(A-[0-9A-Z]+)"', article)
    if not aid_match:
        raise SystemExit("DATA-002: Artigas claim lacks provenance assertion id")
    aid = aid_match.group(1)
    count = len(source_ids.get(aid, set()))
    article = article.replace(
        '<article class="claim">',
        f'<article class="assertion"><div class="kicker">{aid}</div>',
        1,
    )
    summary = re.search(
        r'<details class="evidence"><summary><span class="summary-title">Sources</span><span class="summary-meta">(.*?)</span></summary>',
        article,
        flags=re.S,
    )
    if not summary:
        raise SystemExit(f"DATA-002: {aid} lacks specialized evidence summary")
    qualifier = summary.group(1)
    replacement = (
        f'<details class="evidence" data-source-count="{count}">'
        f'<summary>Sources · {count}</summary>'
        f'<div class="summary-meta">{qualifier}</div>'
    )
    return article[: summary.start()] + replacement + article[summary.end() :]

page, claim_count = re.subn(
    r'<article class="claim">.*?</article>', normalize_claim, page, flags=re.S
)
if claim_count == 0:
    raise SystemExit("DATA-002: no Artigas claim cards found")

# Preserve the vertical-slice spacing after the semantic class normalization.
page = page.replace('.claim{', '.assertion{').replace('.claim+.', '.assertion+.').replace('.claim h3', '.assertion h3').replace('.claim-text', '.claim-text')

PAGE.write_text(page, encoding="utf-8")
print(f"DATA-002: normalized {OID} identity and {claim_count} assertion hooks")
