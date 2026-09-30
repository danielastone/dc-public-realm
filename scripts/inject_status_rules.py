#!/usr/bin/env python3
"""Publish the canonical status-rule contract on the methodology page."""
from __future__ import annotations
import html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'
rules=json.loads((ROOT/'data'/'publication_status_rules.json').read_text(encoding='utf-8'))['rules']
path=SITE/'methodology'/'index.html'; text=path.read_text(encoding='utf-8')
start=text.find('<h2>Status rules</h2>')
if start<0: raise SystemExit('methodology: Status rules section not found')
end=text.find('<h2>',start+4)
if end<0: raise SystemExit('methodology: section after Status rules not found')
blocks=[]
for status,r in rules.items():
 rid=html.escape(r['rule_id']); label=html.escape(r['public_label']); explanation=html.escape(r['explanation'])
 blocks.append(f'<article class="status-rule-definition" id="rule-{rid}" data-status="{html.escape(status)}" data-status-rule="{rid}"><h3>{label}</h3><p>{explanation}</p><div class="meta">Rule {rid}</div></article>')
section='<h2>Status rules</h2><p>Each public status is generated from the canonical evidence model. The stable rule identifier shown beside a claim links to the explanation used for that status; it is not a confidence score.</p>'+''.join(blocks)
text=text[:start]+section+text[end:]
path.write_text(text,encoding='utf-8')
print('Published epistemic status rules',path)
