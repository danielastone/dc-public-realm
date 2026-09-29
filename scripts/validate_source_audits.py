#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDITS=ROOT/'qualifications'/'source-audits'
MODES={'DOCUMENT_TEXT','IMAGE_OBSERVATION','CATALOG_ASSERTION','INSCRIPTION_OBSERVATION','ANALYTICAL_INFERENCE'}
FITS={'EXACT_FIT','FIT_WITH_QUALIFIER','NEW_PREDICATE_CANDIDATE','NEW_ENTITY_TYPE_CANDIDATE','PROVENANCE_RELATION_REQUIRED','NOT_MODELABLE_YET'}
INHERIT={'ORIGINAL_TO_SOURCE','EXPLICITLY_DERIVED','PROBABLY_DERIVED','INDEPENDENT','UNKNOWN'}
ACTIONS={'CREATE_ASSERTION_CANDIDATE','SUPPORT_EXISTING','CONTRADICT_EXISTING','QUALIFY_EXISTING','REPLACE_OR_MOVE_SOURCE_ROOT','REVEAL_SHARED_LINEAGE','NO_KNOWLEDGE_CHANGE','RESEARCH_LEAD_ONLY'}

def present(o,k,ctx):
 if k not in o or o[k] is None: raise ValueError(f'{ctx}: missing {k}')
def nonempty(o,k,ctx):
 present(o,k,ctx)
 if o[k]=='' or o[k]==[]: raise ValueError(f'{ctx}: empty {k}')

def validate(p):
 d=json.loads(p.read_text(encoding='utf-8')); ctx=p.name
 # Some review collections are required structurally but may legitimately be empty.
 for k in ('audit_id','source_forensics','propositions','schema_fit','inheritance','evidence_candidates','conflicts','unresolved_questions','recommended_actions'): present(d,k,ctx)
 for k in ('audit_id','source_forensics','propositions','schema_fit','inheritance','recommended_actions'): nonempty(d,k,ctx)
 for k in ('evidence_candidates','conflicts','unresolved_questions'):
  if not isinstance(d[k],list): raise ValueError(f'{ctx}: {k} must be an array')
 sf=d['source_forensics']
 for k in ('source_id_candidate','title','repository','document_type','retrieved_at','locator','access_route'): nonempty(sf,k,ctx)
 props=d['propositions']; ids=[]
 for x in props:
  for k in ('proposition_id','subject','predicate_candidate','value','evidence_mode','locator'): nonempty(x,k,ctx)
  if x['evidence_mode'] not in MODES: raise ValueError(f"{ctx}:{x['proposition_id']}: invalid evidence_mode")
  ids.append(x['proposition_id'])
 if len(ids)!=len(set(ids)): raise ValueError(f'{ctx}: duplicate proposition IDs')
 ids=set(ids)
 fit={x['proposition_id']:x for x in d['schema_fit']}; inh={x['proposition_id']:x for x in d['inheritance']}
 if set(fit)!=ids or set(inh)!=ids: raise ValueError(f'{ctx}: every proposition needs exactly one schema-fit and inheritance assessment')
 for pid,x in fit.items():
  if x.get('classification') not in FITS: raise ValueError(f'{ctx}:{pid}: invalid schema fit')
 for pid,x in inh.items():
  c=x.get('classification')
  if c not in INHERIT: raise ValueError(f'{ctx}:{pid}: invalid inheritance')
  ups=x.get('upstream_source_ids',[])
  if c in {'EXPLICITLY_DERIVED','PROBABLY_DERIVED'} and not ups: raise ValueError(f'{ctx}:{pid}: derived claim requires upstream source')
  if c=='INDEPENDENT' and ups: raise ValueError(f'{ctx}:{pid}: independent claim cannot name inherited upstream source')
 for x in props:
  if x['evidence_mode']=='ANALYTICAL_INFERENCE' and not x.get('supports_proposition_ids'): raise ValueError(f"{ctx}:{x['proposition_id']}: inference requires supporting propositions")
 blocked={pid for pid,x in fit.items() if x['classification'] not in {'EXACT_FIT','FIT_WITH_QUALIFIER'}}
 mutation={'CREATE_ASSERTION_CANDIDATE','SUPPORT_EXISTING','CONTRADICT_EXISTING','QUALIFY_EXISTING','REPLACE_OR_MOVE_SOURCE_ROOT'}
 for a in d['recommended_actions']:
  if a.get('action') not in ACTIONS: raise ValueError(f'{ctx}: invalid recommended action')
  ps=a.get('proposition_ids',[])
  if not ps or not set(ps)<=ids: raise ValueError(f'{ctx}: action references unknown proposition')
  if a['action'] in mutation and set(ps)&blocked: raise ValueError(f'{ctx}: schema-blocked proposition cannot recommend canonical mutation')
 for e in d['evidence_candidates']:
  pid=e.get('proposition_id')
  if pid not in ids: raise ValueError(f'{ctx}: evidence candidate references unknown proposition')
  if inh[pid]['classification'] in {'EXPLICITLY_DERIVED','PROBABLY_DERIVED'} and e.get('independent') is True: raise ValueError(f'{ctx}:{pid}: inherited evidence cannot be independent')
 return len(ids)

def main():
 paths=sorted(AUDITS.glob('*.json'))
 if not paths: raise ValueError('no source-audit qualification files found')
 n=sum(validate(p) for p in paths)
 print(f'SOURCE AUDITS PASSED: audits={len(paths)} propositions={n}')
if __name__=='__main__':
 try: main()
 except Exception as e:
  print(f'SOURCE AUDIT VALIDATION FAILED: {e}',file=sys.stderr); raise SystemExit(1)
