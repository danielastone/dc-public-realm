#!/usr/bin/env python3
"""Synthetic regressions for DATA-001 exact assertion reconciliation."""
from validate_data001_assertion_reconciliation import reconcile

A=[
 {'assertion_id':'A1','subject_id':'OBJ-1'},
 {'assertion_id':'A2','subject_id':'OBJ-1'},
 {'assertion_id':'P1','subject_id':'OBJ-PRE'},
 {'assertion_id':'B1','subject_id':'OBJ-2'},
]

def page(*ids):
 return ''.join(f'<article data-assertion-id="{x}">fact</article>' for x in ids)

def expect_fail(name, assertions, pages, fragment):
 errors=reconcile(assertions,pages)
 if not any(fragment in e for e in errors):
  raise SystemExit(f'DATA-001 SYNTHETIC FAIL: {name}: expected {fragment!r}, got {errors!r}')

# Clean scope: predecessor assertion is not required on OBJ-1.
if reconcile(A,{'OBJ-1':page('A1','A2'),'OBJ-2':page('B1')}):
 raise SystemExit('DATA-001 SYNTHETIC FAIL: valid exact reconciliation rejected')
expect_fail('unknown rendered ID',A,{'OBJ-1':page('A1','A2','NOPE'),'OBJ-2':page('B1')},'absent from canonical data')
expect_fail('cross-object ID',A,{'OBJ-1':page('A1','A2','B1'),'OBJ-2':page('B1')},'cross-object assertion')
expect_fail('duplicate rendering',A,{'OBJ-1':page('A1','A1','A2'),'OBJ-2':page('B1')},'rendered 2 times')
expect_fail('missing required assertion',A,{'OBJ-1':page('A1'),'OBJ-2':page('B1')},'A2: canonical object assertion missing')
expect_fail('duplicate canonical ID',A+[{'assertion_id':'A1','subject_id':'OBJ-1'}],{'OBJ-1':page('A1','A2'),'OBJ-2':page('B1')},'duplicate canonical assertion IDs')
print('DATA-001 synthetic PASS: scope, unknown ID, cross-object ID, duplicate rendering, missing assertion, canonical uniqueness.')
