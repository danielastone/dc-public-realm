#!/usr/bin/env python3
"""DATA-001: exact object-page assertion reconciliation.

Expected publication scope is structural, not a hand-maintained exception list:
for each public reference object, every materialized canonical assertion whose
subject_id equals that object must render exactly once on that object's page.
Assertions about predecessor/research-graph objects are outside that page's
required factual-assertion set.
"""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
OBJECTS={
 'OBJ-0001':'jose-gervasio-artigas',
 'OBJ-0002':'jose-de-san-martin',
 'OBJ-0003':'cuban-american-friendship-urn',
}

def canonical_index(assertions):
    ids=[a.get('assertion_id') for a in assertions]
    dup=[aid for aid,n in Counter(ids).items() if aid and n>1]
    missing=[i for i,a in enumerate(assertions) if not a.get('assertion_id')]
    errors=[]
    if dup: errors.append('duplicate canonical assertion IDs: '+', '.join(sorted(dup)))
    if missing: errors.append('canonical assertions missing assertion_id at indexes: '+', '.join(map(str,missing)))
    return {a['assertion_id']:a for a in assertions if a.get('assertion_id')},errors

def rendered_ids(text):
    return re.findall(r'data-assertion-id=["\']([^"\']+)["\']',text)

def reconcile(assertions,pages):
    idx,errors=canonical_index(assertions)
    for oid,text in pages.items():
        actual=rendered_ids(text); counts=Counter(actual)
        expected={a['assertion_id'] for a in assertions if a.get('subject_id')==oid}
        actual_set=set(actual)
        for aid,n in sorted(counts.items()):
            if aid not in idx:
                errors.append(f'{oid}/{aid}: rendered assertion ID absent from canonical data')
                continue
            if idx[aid].get('subject_id')!=oid:
                errors.append(f'{oid}/{aid}: cross-object assertion belongs to {idx[aid].get("subject_id")}')
            if n!=1:
                errors.append(f'{oid}/{aid}: rendered {n} times; expected exactly once')
        for aid in sorted(expected-actual_set):
            errors.append(f'{oid}/{aid}: canonical object assertion missing from rendered page')
        for aid in sorted(actual_set-expected):
            if aid in idx and idx[aid].get('subject_id')==oid:
                continue
            # unknown/cross-object cases are reported above; this keeps exact-set semantics explicit.
        
    return errors

def main():
    assertions=json.loads((SITE/'data'/'assertions.json').read_text(encoding='utf-8'))['assertions']
    pages={oid:(SITE/'objects'/slug/'index.html').read_text(encoding='utf-8') for oid,slug in OBJECTS.items()}
    errors=reconcile(assertions,pages)
    if errors:
        print('DATA-001 RECONCILIATION FAIL')
        for e in errors: print('-',e)
        raise SystemExit(1)
    counts={oid:sum(1 for a in assertions if a.get('subject_id')==oid) for oid in OBJECTS}
    print('DATA-001 reconciliation PASS:', ', '.join(f'{oid}={n}' for oid,n in counts.items()), 'canonical object assertions rendered exactly once.')

if __name__=='__main__': main()
