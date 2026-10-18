#!/usr/bin/env python3
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# KNOWLEDGE_DATA_DIR selects the materialized database (relative paths resolve
# against the working directory, as in validate_data.py). An explicit override
# never falls back to the frozen baseline in ROOT/data.
override = os.environ.get("KNOWLEDGE_DATA_DIR")
if override is not None:
    if not override.strip():
        raise SystemExit("Image-rights validation failed: KNOWLEDGE_DATA_DIR is set but empty")
    source = Path(override) / "object-overviews.json"
    if not source.is_file():
        raise SystemExit(f"Image-rights validation failed: overview file not found under KNOWLEDGE_DATA_DIR: {source}")
else:
    source = ROOT / "data" / "object-overviews.json"
print(f"Image-rights overview source: {source}")
data = json.loads(source.read_text(encoding="utf-8"))
errors = []
for record in data.get("object_overviews", []):
    oid = record.get("object_entity_id", "UNKNOWN")
    if not record.get("image_url"):
        errors.append(f"{oid}: published overview requires image_url")
        continue
    for field in ("image_alt", "image_credit", "image_rights", "image_source_url"):
        if not record.get(field): errors.append(f"{oid}: image missing {field}")
    rights = record.get("image_rights", "")
    if rights.startswith("CC ") and not record.get("image_license_url"):
        errors.append(f"{oid}: Creative Commons image missing image_license_url")
    source = record.get("image_source_url", "")
    if "commons.wikimedia.org/wiki/File:" in source and "Wikimedia Commons" in record.get("image_credit", ""):
        creator = record.get("image_credit", "").split("/")[0].strip()
        if not creator or creator == "Wikimedia Commons": errors.append(f"{oid}: Commons image must credit creator, not only repository")
if errors: raise SystemExit("Image-rights validation failed:\n- " + "\n- ".join(errors))
print(f"Image-rights validation passed for {len(data.get('object_overviews', []))} object overviews")
