#!/usr/bin/env python3
"""Derive public claim-evidence dependency state without overstating independence."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def derive(record: dict) -> str:
    inherited=record.get('inherits_claim_from_source_ids') or []
    status=record.get('dependency_status','UNKNOWN')
    origin=record.get('claim_origin','UNKNOWN')
    if status == 'DEPENDENT' or inherited:
        return 'DEPENDENT'
    # Independence requires an affirmative dependency classification AND an
    # affirmative claim-origin classification. Source-family difference and an
    # empty inheritance list are deliberately insufficient.
    if status == 'INDEPENDENT' and origin in {'ORIGINAL_TO_SOURCE','INDEPENDENT_CLAIM_ROOT'}:
        return 'INDEPENDENT'
    return 'INDEPENDENCE_NOT_ESTABLISHED'

def main() -> None:
    payload=json.loads((ROOT/'data'/'assertion-evidence.json').read_text(encoding='utf-8'))
    rows=payload['assertion_evidence']
    counts={k:0 for k in ('DEPENDENT','INDEPENDENCE_NOT_ESTABLISHED','INDEPENDENT')}
    for row in rows: counts[derive(row)]+=1
    print(json.dumps(counts,sort_keys=True))

if __name__=='__main__': main()
