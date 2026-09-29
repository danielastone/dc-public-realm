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
<p>These links identify this monument, its subject, or related media in other institutional and public knowledge systems. <strong>They are not automatically evidence for claims on this page.</strong> A record affects a historical claim only when the relevant statement is reviewed and explicitly connected in the evidence graph.</p>
<h3>Records for this monument</h3><ul class="sources">{''.join(card(r) for r in object_records)}</ul>
<h3>Authority records for José Gervasio Artigas</h3><ul class="sources">{''.join(card(r) for r in subject_records)}</ul>
<p class="small"><strong>Interoperability rule:</strong> identity/discovery links never change claim status by themselves. This prevents institutional authority, Wikidata repetition, or media aggregation from being mistaken for independent corroboration.</p></section>'''

text = PAGE.read_text(encoding="utf-8")
needle = '<section id="questions"><h2>Open questions</h2>'
if needle not in text:
    raise SystemExit("Artigas publication insertion point not found")
text = text.replace(needle, section + needle, 1)
text = text.replace('<a href="#sources">Sources</a><a href="#questions">', '<a href="#sources">Sources</a><a href="#external-records">External records</a><a href="#questions">', 1)
PAGE.write_text(text, encoding="utf-8")
print("Injected external interoperability records into", PAGE)
