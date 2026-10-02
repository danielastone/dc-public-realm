#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.environ.get('KNOWLEDGE_DATA_DIR', ROOT/'data'))
tasks=json.loads((DATA/'research-tasks.json').read_text())['tasks']
assertions={x['assertion_id']:x for x in json.loads((DATA/'assertions.json').read_text())['assertions']}
ALLOWED_STATUS={'OPEN','SUBMITTED','REVIEWED','INCORPORATED','REJECTED','CLOSED_NO_CHANGE'}
errors=[]
for t in tasks:
    tid=t.get('task_id','<missing>')
    if t.get('status') not in ALLOWED_STATUS:
        errors.append(f"{tid}: status must be one of {sorted(ALLOWED_STATUS)}")
    targets=t.get('epistemic_targets')
    questions=t.get('inheritance_questions')
    if not isinstance(targets,list) or not targets:
        errors.append(f'{tid}: epistemic_targets must be a non-empty list')
        continue
    if not isinstance(questions,list) or not questions:
        errors.append(f'{tid}: inheritance_questions must be a non-empty list')
    seen=set()
    for i,x in enumerate(targets,1):
        aid=x.get('assertion_id'); proposition=x.get('proposition')
        if bool(aid)==bool(proposition): errors.append(f'{tid} target {i}: provide exactly one of assertion_id or proposition')
        if aid:
            if aid not in assertions: errors.append(f'{tid} target {i}: missing assertion {aid}')
            elif assertions[aid].get('subject_id')!=t.get('object_entity_id') and assertions[aid].get('subject_id') not in {'OBJ-PRE-0001','OBJ-PRE-0002','OBJ-PRE-0101'}:
                errors.append(f'{tid} target {i}: assertion {aid} is not in the task object/lineage scope')
        key=aid or proposition
        if key in seen: errors.append(f'{tid}: duplicate epistemic target {key}')
        seen.add(key)
        for k in ('problem','desired_evidence','desired_effect'):
            if not x.get(k): errors.append(f'{tid} target {i}: missing {k}')
    if t.get('evidence_effect')!='NONE_UNTIL_REVIEWED': errors.append(f'{tid}: collaboration task cannot itself change epistemic state')
if errors:
    print(f'RESEARCH TASK VALIDATION FAILED: {len(errors)} error(s)')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'RESEARCH TASK VALIDATION PASSED: {len(tasks)} tasks; status vocabulary and epistemic targets are valid.')
