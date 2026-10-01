#!/usr/bin/env python3
"""Synthetic EPI-005 publication invariants independent of current corpus counts."""
from detect_material_conflicts import conflict_index, validate_conflict_records

def r(eid,aid,role,note='note',locator='loc'):
 return {'assertion_evidence_id':eid,'assertion_id':aid,'source_id':'SRC-'+eid,'evidence_role':role,'locator':locator,'evidence_note':note}
# conflict
rows=[r('1','A','PRIMARY_SUPPORT'),r('2','A','CONTRADICTS','opposing wording')]
if set(conflict_index(rows))!={'A'}: raise SystemExit('EPI-005 SYNTHETIC FAIL: conflict not detected')
# non-conflict / qualification
rows=[r('3','B','PRIMARY_SUPPORT'),r('4','B','QUALIFIES','narrows scope')]
if conflict_index(rows): raise SystemExit('EPI-005 SYNTHETIC FAIL: QUALIFIES promoted to conflict')
# multiple support sources are not conflict
rows=[r('5','C','PRIMARY_SUPPORT'),r('6','C','CORROBORATION')]
if conflict_index(rows): raise SystemExit('EPI-005 SYNTHETIC FAIL: source plurality promoted to conflict')
# missing contradictory detail must fail validation
rows=[r('7','D','CONTRADICTS',note='')]
if not validate_conflict_records(rows): raise SystemExit('EPI-005 SYNTHETIC FAIL: detail-free contradiction accepted')
# normalization-with-conflict: canonical preferred value does not erase explicit contradiction marker.
rows=[r('8','E','PRIMARY_SUPPORT','preferred normalized form'),r('9','E','CONTRADICTS','source gives alternate form')]
if 'E' not in conflict_index(rows): raise SystemExit('EPI-005 SYNTHETIC FAIL: normalized value erased contradiction')
print('EPI-005 synthetic PASS: conflict, non-conflict, incomplete contradiction, and normalization cases.')
