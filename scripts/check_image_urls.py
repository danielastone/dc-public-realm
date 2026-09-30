#!/usr/bin/env python3
"""Static checks for image URL provenance.

Network availability is intentionally not a publication gate: Commons or other hosts may
be temporarily unavailable. This check enforces that the public asset and rights record
are HTTPS and that Commons-backed assets point to a Commons file page for provenance.
"""
import json
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data'/'object-overviews.json').read_text(encoding='utf-8'))['object_overviews']
errors=[]
for o in rows:
 oid=o['object_entity_id']
 for k in ('image_url','image_source_url'):
  u=o.get(k,''); p=urlparse(u)
  if p.scheme!='https' or not p.netloc: errors.append(f'{oid}: {k} must be an absolute HTTPS URL')
 if 'commons.wikimedia.org' in o.get('image_url','') and 'commons.wikimedia.org/wiki/File:' not in o.get('image_source_url',''):
  errors.append(f'{oid}: Commons image requires a Commons File: provenance page')
if errors: raise SystemExit('Image URL validation failed:\n- '+'\n- '.join(errors))
print(f'Image URL validation passed for {len(rows)} object overviews')
