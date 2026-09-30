#!/usr/bin/env python3
"""Regression tests for conservative EPI-004 lineage traversal."""
from trace_claim_lineage import build_index, trace_row, ROOT, UNRESOLVED, BROKEN, CYCLE

def row(eid, source, *, assertion='A-X', parents=None, dep='UNKNOWN', origin='UNKNOWN'):
    return {
        'assertion_evidence_id': eid,
        'assertion_id': assertion,
        'source_id': source,
        'inherits_claim_from_source_ids': parents or [],
        'dependency_status': dep,
        'claim_origin': origin,
    }

def terminals(trace):
    if trace.get('terminal'):
        return [trace['terminal']]
    out=[]
    for branch in trace.get('branches',[]): out.extend(terminals(branch))
    return out

cases=[]
# Empty parent list + UNKNOWN is unresolved, never a root.
r1=row('AE-U','SRC-U')
cases.append(('unknown-empty',r1,[r1],UNRESOLVED))
# Original-to-source alone is still unresolved without affirmative independence.
r2=row('AE-O','SRC-O',origin='ORIGINAL_TO_SOURCE')
cases.append(('original-not-independent',r2,[r2],UNRESOLVED))
# Affirmative independent root is a root.
r3=row('AE-R','SRC-R',dep='INDEPENDENT',origin='ORIGINAL_TO_SOURCE')
cases.append(('established-root',r3,[r3],ROOT))
# Recorded parent absent from assertion graph is broken, not unresolved/root.
r4=row('AE-B','SRC-B',parents=['SRC-MISSING'],dep='DEPENDENT')
cases.append(('broken-parent',r4,[r4],BROKEN))
# Child reaches established parent root.
root=row('AE-P','SRC-P',dep='INDEPENDENT',origin='ORIGINAL_TO_SOURCE')
child=row('AE-C','SRC-C',parents=['SRC-P'],dep='DEPENDENT')
cases.append(('dependent-to-root',child,[child,root],ROOT))
# Cycle must be detected.
a=row('AE-A','SRC-A',parents=['SRC-B'],dep='DEPENDENT')
b=row('AE-B2','SRC-B',parents=['SRC-A'],dep='DEPENDENT')
cases.append(('cycle',a,[a,b],CYCLE))

for name,start,rows,expected in cases:
    got=terminals(trace_row(start,build_index(rows)))
    if expected not in got:
        raise SystemExit(f'EPI-004 FAIL {name}: terminals={got}, expected {expected}')
print(f'EPI-004 traversal PASS: {len(cases)} root/unresolved/broken/cycle cases')
