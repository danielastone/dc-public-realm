#!/usr/bin/env python3
"""Regression tests for EPI-002 dependency-state derivation."""
from derive_dependency_state import derive

cases=[
    ({'dependency_status':'UNKNOWN','claim_origin':'UNKNOWN','inherits_claim_from_source_ids':[]},'INDEPENDENCE_NOT_ESTABLISHED','unknown ancestry'),
    ({'dependency_status':'UNKNOWN','claim_origin':'ORIGINAL_TO_SOURCE','inherits_claim_from_source_ids':[]},'INDEPENDENCE_NOT_ESTABLISHED','original-to-source alone does not prove independence'),
    ({'dependency_status':'UNKNOWN','claim_origin':'UNKNOWN','inherits_claim_from_source_ids':['SRC-X']},'DEPENDENT','encoded inherited source'),
    ({'dependency_status':'DEPENDENT','claim_origin':'UNKNOWN','inherits_claim_from_source_ids':[]},'DEPENDENT','explicit dependency'),
    ({'dependency_status':'INDEPENDENT','claim_origin':'ORIGINAL_TO_SOURCE','inherits_claim_from_source_ids':[]},'INDEPENDENT','affirmatively established independent root'),
    ({'dependency_status':'INDEPENDENT','claim_origin':'UNKNOWN','inherits_claim_from_source_ids':[]},'INDEPENDENCE_NOT_ESTABLISHED','independent flag without claim-root evidence'),
]
for row,expected,name in cases:
    actual=derive(row)
    if actual!=expected: raise SystemExit(f'EPI-002 FAIL {name}: {actual} != {expected}')
print(f'EPI-002 derivation PASS: {len(cases)} conservative lineage cases')
