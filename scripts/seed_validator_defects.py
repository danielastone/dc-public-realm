#!/usr/bin/env python3
"""Seeded-defect verification for migrated publication validators.
Run from repo root after a full site build. Snapshots site/, seeds one defect
at a time, runs the four validators, restores site/. Not a CI step; retained
as the behavioral contract for the Phase 5 validator rewrite."""
import re,subprocess,shutil,sys,tarfile,tempfile
from pathlib import Path
W=Path(__file__).resolve().parents[1]; S=W/'site'
SNAP=Path(tempfile.mkdtemp())/'site_ref.tar'
with tarfile.open(SNAP,'w') as t: t.add(S,arcname='site')
V={'CONS':'validate_publication_consistency','P001':'validate_pub001_routes',
   'P002':'validate_pub002_navigation','P003':'validate_pub003_tasks'}
def reset():
    shutil.rmtree(S); tarfile.open(SNAP).extractall(W)
def sub(rel,pat,rep,count=1):
    p=S/rel; t=p.read_text(encoding='utf-8'); n=re.subn(pat,rep,t,count=count)
    assert n[1]>0,(rel,pat); p.write_text(n[0],encoding='utf-8')
SM='objects/jose-de-san-martin/index.html'
D={
 'D1 delete object page':(lambda:(S/SM).unlink(),'P001'),
 'D2 orphan object page':(lambda:(S/'objects/ghost').mkdir() or shutil.copy(S/SM,S/'objects/ghost/index.html'),'P001'),
 'D3 corrupt object nav':(lambda:sub(SM,r'(<nav class="primary-nav"[^>]*>.*?)>Data</a>',r'\1>Datasets</a>'),'P002'),
 'D4 alter object task count':(lambda:sub(SM,r'data-open-task-count="\d+"','data-open-task-count="9"'),'P003'),
 'D5 drop one task link':(lambda:sub(SM,r'href="/dc-public-realm/tasks/arg-sm-001/"','href="#"',count=0),'P003'),
 'D6 alter homepage task count':(lambda:sub('index.html',r'(data-object-id="OBJ-0002" data-open-task-count=")\d+',r'\g<1>9'),'P003'),
 'D7 strip status marker':(lambda:sub(SM,r'data-computed-status="[A-Z]+"','data-computed-status="X"'),'CONS'),
 'D8 remove homepage task marker':(lambda:sub('index.html',r'data-object-id="OBJ-0002" data-open-task-count="\d+"',''),'P003'),
}
missed=False
print(f"{'defect':32}"+''.join(f'{k:>6}' for k in V)+'  own')
for name,(apply,own) in D.items():
    reset()
    try: apply()
    except AssertionError as e:
        print(f'{name:32}  COULD NOT SEED: {e}'); missed=True; continue
    res={k:subprocess.run([sys.executable,v+'.py'],cwd=W/'scripts',capture_output=True).returncode for k,v in V.items()}
    ok=bool(res[own]); missed=missed or not ok
    print(f'{name:32}'+''.join(f"{'FAIL' if res[k] else 'pass':>6}" for k in V)+f"  {'OK' if ok else 'MISSED'}")
reset()
sys.exit(1 if missed else 0)
