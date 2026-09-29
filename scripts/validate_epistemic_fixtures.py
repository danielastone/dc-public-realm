#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def nonempty_strings(xs,label):
    if not isinstance(xs,list) or not xs or any(not isinstance(x,str) or not x.strip() for x in xs):
        raise ValueError(f'{label} must be a non-empty list of strings')

def validate_epistemic():
    p=ROOT/'fixtures'/'epistemic-regressions.json'; d=json.loads(p.read_text(encoding='utf-8'))
    if d.get('schema_version')!='0.1': raise ValueError('epistemic fixtures: schema_version must be 0.1')
    fs=d.get('fixtures'); ids=set(); required={'OBJ-0001','OBJ-0002','OBJ-0003'}; seen=set()
    if not isinstance(fs,list) or not fs: raise ValueError('epistemic fixtures: fixtures must be non-empty')
    for f in fs:
        fid=f.get('fixture_id')
        if not fid or fid in ids: raise ValueError(f'epistemic fixtures: missing/duplicate fixture_id {fid}')
        ids.add(fid); oid=f.get('object_entity_id')
        if not oid: raise ValueError(f'{fid}: missing object_entity_id')
        seen.add(oid)
        if not f.get('name'): raise ValueError(f'{fid}: missing name')
        nonempty_strings(f.get('must_preserve'),f'{fid}: must_preserve'); nonempty_strings(f.get('failure_signals'),f'{fid}: failure_signals')
    if required-seen: raise ValueError(f'epistemic fixtures: missing required objects {sorted(required-seen)}')
    return len(fs)

def validate_acquisition():
    p=ROOT/'fixtures'/'acquisition-regressions.json'; d=json.loads(p.read_text(encoding='utf-8'))
    if d.get('schema_version')!='0.1': raise ValueError('acquisition fixtures: schema_version must be 0.1')
    fs=d.get('fixtures'); ids=set(); prefixes={'ACQ-IMAGE','ACQ-COLLAB','ACQ-PRIORITY'}; seen=set()
    if not isinstance(fs,list) or not fs: raise ValueError('acquisition fixtures: fixtures must be non-empty')
    for f in fs:
        fid=f.get('fixture_id')
        if not fid or fid in ids: raise ValueError(f'acquisition fixtures: missing/duplicate fixture_id {fid}')
        ids.add(fid)
        for prefix in prefixes:
            if fid.startswith(prefix): seen.add(prefix)
        if not isinstance(f.get('scenario'),str) or not f['scenario'].strip(): raise ValueError(f'{fid}: missing scenario')
        nonempty_strings(f.get('required_behavior'),f'{fid}: required_behavior')
    if prefixes-seen: raise ValueError(f'acquisition fixtures: missing behavior classes {sorted(prefixes-seen)}')
    return len(fs)

def main():
    e=validate_epistemic(); a=validate_acquisition()
    print(f'EPISTEMIC/ACQUISITION FIXTURES PASSED: epistemic={e}; acquisition={a}')

if __name__=='__main__': main()
