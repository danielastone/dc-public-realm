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
candidates = [
    '<section id="research"><h2>Research notes</h2>',
    '<section id="questions"><h2>Open questions</h2>',
]
needle = next((x for x in candidates if x in text), None)
if needle is None:
    raise SystemExit("Artigas publication insertion point not found")
text = text.replace(needle, section + needle, 1)

nav_candidates = [
    ('<a href="#sources">References</a><a href="#research">', '<a href="#sources">References</a><a href="#external-records">External records</a><a href="#research">'),
    ('<a href="#sources">Sources</a><a href="#questions">', '<a href="#sources">Sources</a><a href="#external-records">External records</a><a href="#questions">'),
]
for old, new in nav_candidates:
    if old in text:
        text = text.replace(old, new, 1)
        break

PAGE.write_text(text, encoding="utf-8")
print("Injected external interoperability records into", PAGE)
