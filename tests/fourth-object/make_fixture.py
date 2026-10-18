#!/usr/bin/env python3
"""Generate the TEST-ONLY OBJ-9104 ledger transaction.

OBJ-9104 is a SYNTHETIC STRUCTURAL CLONE of OBJ-0003 (Cuban-American Friendship
Urn), not an independently sourced historical record. Its assertions, evidence,
sources, research tasks and overview are copied from OBJ-0003 into an isolated
namespace (A-T9104-*, AE-T9104-*, SRC-T9104-*, TST-9104-*) so that the fourth
object exercises the same rendering paths (multi-source dependency, UNKNOWN
ancestry, material conflicts, research tasks). Overview prose is copied
verbatim so displayed facts reconcile to assertion literals. References to real
related entities (AG-*, OBJ-PRE-0001) are inherited fixture dependencies, not
new historical claims.

The transaction must never be committed to transactions/; the harness copies
it into isolated temporary workspaces only.

usage: make_fixture.py <materialized build/data dir> <out transaction.json> <out id-map.json>
"""
import copy
import json
import sys
from collections import Counter
from pathlib import Path

SRC_OBJ, NEW = 'OBJ-0003', 'OBJ-9104'


def main(data_dir, out_tx, out_map):
    B = Path(data_dir)
    load = lambda name, key: json.loads((B / name).read_text(encoding='utf-8'))[key]
    assertions = load('assertions.json', 'assertions')
    evidence = load('assertion-evidence.json', 'assertion_evidence')
    sources = {s['source_id']: s for s in load('sources.json', 'sources')}
    tasks = load('research-tasks.json', 'tasks')
    overview = next(o for o in load('object-overviews.json', 'object_overviews') if o['object_entity_id'] == SRC_OBJ)

    a_src = sorted((a for a in assertions if a['subject_id'] == SRC_OBJ), key=lambda a: a['assertion_id'])
    amap = {a['assertion_id']: f'A-T9104-{i:02d}' for i, a in enumerate(a_src, 1)}
    ev_src = sorted((e for e in evidence if e['assertion_id'] in amap), key=lambda e: e['assertion_evidence_id'])
    emap = {e['assertion_evidence_id']: f'AE-T9104-{i:02d}' for i, e in enumerate(ev_src, 1)}

    used = set()
    for e in ev_src:
        used |= {e['source_id'], *(e.get('inherits_claim_from_source_ids') or [])}
    frontier = list(used)
    while frontier:  # ancestry closure so lineage terminals match OBJ-0003
        for parent in sources[frontier.pop()].get('derived_from_source_ids') or []:
            if parent not in used:
                used.add(parent)
                frontier.append(parent)
    smap = {s: f'SRC-T9104-{i:02d}' for i, s in enumerate(sorted(used), 1)}

    ops = [{'table': 'entities', 'action': 'add', 'id': NEW, 'value': {
        'entity_id': NEW, 'entity_type': 'PhysicalObject',
        'canonical_name': 'Synthetic Fixture Monument', 'country': 'Fixtureland',
        'publication': {'publish': True, 'slug': 'synthetic-fixture-monument', 'featured': False}}}]
    for s in sorted(used):
        v = copy.deepcopy(sources[s])
        v['source_id'] = smap[s]
        v['derived_from_source_ids'] = [smap.get(p, p) for p in v.get('derived_from_source_ids') or []]
        if v.get('source_family_id'):
            v['source_family_id'] = 'T9104_' + v['source_family_id']
        v['title'] = '[SYNTHETIC FIXTURE] ' + v.get('title', '')
        ops.append({'table': 'sources', 'action': 'add', 'id': smap[s], 'value': v})
    for a in a_src:
        v = copy.deepcopy(a)
        v['assertion_id'], v['subject_id'] = amap[a['assertion_id']], NEW
        ops.append({'table': 'assertions', 'action': 'add', 'id': v['assertion_id'], 'value': v})
    for e in ev_src:
        v = copy.deepcopy(e)
        v['assertion_evidence_id'] = emap[e['assertion_evidence_id']]
        v['assertion_id'] = amap[e['assertion_id']]
        v['source_id'] = smap[e['source_id']]
        v['inherits_claim_from_source_ids'] = [smap[p] for p in e.get('inherits_claim_from_source_ids') or []]
        ops.append({'table': 'assertion_evidence', 'action': 'add', 'id': v['assertion_evidence_id'], 'value': v})

    def remap(x):
        if isinstance(x, str):
            return amap.get(x, NEW if x == SRC_OBJ else x)
        if isinstance(x, list):
            return [remap(y) for y in x]
        if isinstance(x, dict):
            return {k: remap(v) for k, v in x.items()}
        return x

    tmap = {}
    for i, t in enumerate(sorted((t for t in tasks if t.get('object_entity_id') == SRC_OBJ), key=lambda t: t['task_id']), 1):
        v = remap(copy.deepcopy(t))
        v['task_id'] = tmap[t['task_id']] = f'TST-9104-{i:03d}'
        v['title'] = '[SYNTHETIC FIXTURE] ' + t['title']
        ops.append({'table': 'research_tasks', 'action': 'add', 'id': v['task_id'], 'value': v})
    ov = remap(copy.deepcopy(overview))
    ov['object_entity_id'] = NEW
    ops.append({'table': 'object_overviews', 'action': 'add', 'id': NEW, 'value': ov})

    tx = {'transaction_id': 'TX-TEST-OBJ-9104', 'recorded_at': '9999-12-31', 'actor': 'test-fixture',
          'purpose': f'TEST-ONLY synthetic structural clone of {SRC_OBJ}; never committed to transactions/.',
          'evidence_decision': 'Synthetic fixture; not research evidence.', 'supersedes': None, 'operations': ops}
    Path(out_tx).write_text(json.dumps(tx, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    id_map = {'object': {SRC_OBJ: NEW}, 'assertions': amap, 'evidence': emap, 'sources': smap, 'tasks': tmap}
    Path(out_map).write_text(json.dumps(id_map, indent=1) + '\n', encoding='utf-8')
    print('fixture ops:', dict(Counter(o['table'] for o in ops)))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
