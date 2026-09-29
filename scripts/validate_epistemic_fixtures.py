#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'fixtures'/'epistemic-regressions.json'

def main():
    d=json.loads(P.read_text(encoding='utf-8'))
    if d.get('schema_version')!='0.1': raise ValueError('epistemic fixtures: schema_version must be 0.1')
    fs=d.get('fixtures')
    if not isinstance(fs,list) or not fs: raise ValueError('epistemic fixtures: fixtures must be a non-empty list')
    ids=set()
    required_objects={'OBJ-0001','OBJ-0002','OBJ-0003'}
    seen_objects=set()
    for f in fs:
        fid=f.get('fixture_id')
        if not fid or fid in ids: raise ValueError(f'epistemic fixtures: missing/duplicate fixture_id {fid}')
        ids.add(fid)
        oid=f.get('object_entity_id')
        if not oid: raise ValueError(f'{fid}: missing object_entity_id')
        seen_objects.add(oid)
        if not f.get('name'): raise ValueError(f'{fid}: missing name')
        for k in ('must_preserve','failure_signals'):
            xs=f.get(k)
            if not isinstance(xs,list) or not xs or any(not isinstance(x,str) or not x.strip() for x in xs):
                raise ValueError(f'{fid}: {k} must be a non-empty list of strings')
    missing=required_objects-seen_objects
    if missing: raise ValueError(f'epistemic fixtures: missing required project regression objects {sorted(missing)}')
    print(f'EPISTEMIC FIXTURES PASSED: {len(fs)} fixtures; objects={sorted(seen_objects)}')

if __name__=='__main__': main()
