#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
checks={
 'jose-gervasio-artigas':['record-overview','National Park Service','Public domain'],
 'jose-de-san-martin':['record-overview','October 28, 1925','October 6, 1976','AgnosticPreachersKid','CC BY-SA 3.0'],
 'cuban-american-friendship-urn':['record-overview','Presented to the United States','AgnosticPreachersKid','CC BY-SA 4.0','USS Maine'],
}
errors=[]
for slug,needles in checks.items():
 p=ROOT/'site'/'objects'/slug/'index.html'
 if not p.exists():
  errors.append(f'{slug}: page missing'); continue
 text=p.read_text(encoding='utf-8')
 for needle in needles:
  if needle not in text: errors.append(f'{slug}: missing {needle!r}')
if errors: raise SystemExit('Overview rendering validation failed:\n- '+'\n- '.join(errors))
print('Overview rendering validation passed for all three public object records')
