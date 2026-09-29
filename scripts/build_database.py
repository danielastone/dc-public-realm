#!/usr/bin/env python3
"""Materialize the diplomatic-gifts database from a frozen baseline plus ordered transactions.

The checked-in data/ directory is the migration baseline. Future epistemic changes belong in
transactions/*.json. This builder never mutates data/. It writes build/data/ and build/audit/.
"""
from __future__ import annotations
import copy, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data'; TX=ROOT/'transactions'; OUT=ROOT/'build'/'data'; AUDIT=ROOT/'build'/'audit'
FILES={
 'entities':'entities.json','sources':'sources.json','assertions':'assertions.json',
 'assertion_evidence':'assertion-evidence.json','predicate_rules':'predicate-rules.json',
 'research_tasks':'research-tasks.json'
}
ARRAY_KEY={'entities':'entities','sources':'sources','assertions':'assertions','assertion_evidence':'assertion_evidence','research_tasks':'tasks'}
ID_KEY={'entities':'entity_id','sources':'source_id','assertions':'assertion_id','assertion_evidence':'assertion_evidence_id','research_tasks':'task_id'}

def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(x): return hashlib.sha256(canon(x)).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def index(rows,key): return {r[key]:i for i,r in enumerate(rows)}

def apply_op(db,op):
 table=op['table']; action=op['action']
 if table=='predicate_rules':
  target=db[table]['predicate_rules']; key=op['id']
  if action=='add':
   if key in target: raise ValueError(f'{table}:{key} already exists')
   target[key]=op['value']
  elif action=='update':
   if key not in target: raise ValueError(f'{table}:{key} missing')
   before=sha(target[key]); expected=op.get('before_sha256')
   if expected and before!=expected: raise ValueError(f'{table}:{key} precondition failed')
   target[key]=op['value']
  elif action=='delete':
   if key not in target: raise ValueError(f'{table}:{key} missing')
   del target[key]
  else: raise ValueError(f'unknown action {action}')
  return
 if table not in ARRAY_KEY: raise ValueError(f'unknown table {table}')
 rows=db[table][ARRAY_KEY[table]]; idkey=ID_KEY[table]; rid=op['id']; ix=index(rows,idkey)
 if action=='add':
  if rid in ix: raise ValueError(f'{table}:{rid} already exists')
  value=copy.deepcopy(op['value'])
  if value.get(idkey)!=rid: raise ValueError(f'{table}:{rid} id mismatch')
  rows.append(value)
 elif action=='update':
  if rid not in ix: raise ValueError(f'{table}:{rid} missing')
  old=rows[ix[rid]]; expected=op.get('before_sha256')
  if expected and sha(old)!=expected: raise ValueError(f'{table}:{rid} precondition failed')
  value=copy.deepcopy(op['value'])
  if value.get(idkey)!=rid: raise ValueError(f'{table}:{rid} id mismatch')
  rows[ix[rid]]=value
 elif action=='delete':
  if rid not in ix: raise ValueError(f'{table}:{rid} missing')
  expected=op.get('before_sha256')
  if expected and sha(rows[ix[rid]])!=expected: raise ValueError(f'{table}:{rid} precondition failed')
  rows.pop(ix[rid])
 else: raise ValueError(f'unknown action {action}')

def integrity(db):
 errors=[]
 E={x['entity_id'] for x in db['entities']['entities']}; S={x['source_id'] for x in db['sources']['sources']}; A={x['assertion_id'] for x in db['assertions']['assertions']}
 for a in db['assertions']['assertions']:
  if a.get('subject_id') not in E: errors.append(f"{a['assertion_id']}: missing subject")
  if a.get('object_entity_id') and a['object_entity_id'] not in E: errors.append(f"{a['assertion_id']}: missing object")
 for e in db['assertion_evidence']['assertion_evidence']:
  if e.get('assertion_id') not in A: errors.append(f"{e['assertion_evidence_id']}: missing assertion")
  if e.get('source_id') not in S: errors.append(f"{e['assertion_evidence_id']}: missing source")
  for p in e.get('inherits_claim_from_source_ids',[]):
   if p not in S: errors.append(f"{e['assertion_evidence_id']}: missing inherited source {p}")
 if errors: raise ValueError('; '.join(errors))

def main():
 db={k:load(BASE/v) for k,v in FILES.items()}
 baseline={k:sha(v) for k,v in db.items()}
 txs=[]; seen=set(); previous=None
 for p in sorted(TX.glob('*.json')) if TX.exists() else []:
  t=load(p); tid=t['transaction_id']
  if tid in seen: raise ValueError(f'duplicate transaction {tid}')
  seen.add(tid)
  if t.get('supersedes') and t['supersedes']!=previous: raise ValueError(f'{tid}: supersedes must equal prior transaction {previous}')
  before=sha(db)
  for op in t['operations']: apply_op(db,op)
  integrity(db)
  after=sha(db)
  txs.append({'transaction_id':tid,'file':str(p.relative_to(ROOT)),'purpose':t['purpose'],'before_sha256':before,'after_sha256':after,'operation_count':len(t['operations'])})
  previous=tid
 integrity(db)
 OUT.mkdir(parents=True,exist_ok=True)
 for k,f in FILES.items(): dump(OUT/f,db[k])
 manifest={'build_format':'transaction-ledger-v1','built_at_utc':datetime.now(timezone.utc).isoformat(),'baseline_sha256':baseline,'transactions':txs,'database_sha256':sha(db)}
 dump(AUDIT/'manifest.json',manifest)
 print(f"Built database from {len(txs)} transaction(s); database_sha256={manifest['database_sha256']}")
 return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as exc:
  print(f'TRANSACTION BUILD FAILED: {exc}',file=sys.stderr); raise SystemExit(1)
