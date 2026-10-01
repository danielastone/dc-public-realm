#!/usr/bin/env python3
from __future__ import annotations
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PAGE = ROOT / "site" / "objects" / "jose-gervasio-artigas" / "index.html"

def esc(x): return html.escape(str(x), quote=True)
records = json.loads((DATA / "external-records.json").read_text(encoding="utf-8"))["external_records"]
object_records = [r for r in records if r["entity_id"] == "OBJ-0001"]
subject_records = [r for r in records if r["entity_id"] == "AG-0001"]

def card(r):
    return (f'<li class="external-record"><a href="{esc(r["url"])}">{esc(r["system"])} — {esc(r["label"])}</a>'
            f'<br><span class="small">{esc(r["record_type"].replace("_", " "))} · ID {esc(r["identifier"])}</span>'
            f'<br><span class="small">{esc(r["note"])}</span></li>')

section = f'''<section id="external-records"><h2>External records</h2>
<p>Links to records for this monument, its subject, and related media in other systems. These records do not change assertion status unless a specific statement is reviewed and added to the evidence record.</p>
<h3>Monument records</h3><ul class="sources">{''.join(card(r) for r in object_records)}</ul>
<h3>José Gervasio Artigas authority records</h3><ul class="sources">{''.join(card(r) for r in subject_records)}</ul>
</section>'''

text = PAGE.read_text(encoding="utf-8")
if 'id="external-records"' in text:
    raise SystemExit("External records already rendered on Artigas page")

# Insert at the stable shared page-shell boundary rather than depending on
# headings or navigation emitted by the retired Artigas-specific renderer.
needle = "</main>"
if text.count(needle) != 1:
    raise SystemExit(f"Expected exactly one shared </main> boundary, found {text.count(needle)}")
text = text.replace(needle, section + needle, 1)

PAGE.write_text(text, encoding="utf-8")
print("Injected external interoperability records into", PAGE)
