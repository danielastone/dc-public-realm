#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data" / "object-overviews.json").read_text(encoding="utf-8"))
errors = []

for record in data.get("object_overviews", []):
    oid = record.get("object_entity_id", "UNKNOWN")
    if not record.get("image_url"):
        errors.append(f"{oid}: published overview requires image_url")
        continue
    for field in ("image_alt", "image_credit", "image_rights", "image_source_url"):
        if not record.get(field):
            errors.append(f"{oid}: image missing {field}")
    rights = record.get("image_rights", "")
    if rights.startswith("CC ") and not record.get("image_license_url"):
        errors.append(f"{oid}: Creative Commons image missing image_license_url")
    source = record.get("image_source_url", "")
    if "commons.wikimedia.org/wiki/File:" in source and "Wikimedia Commons" in record.get("image_credit", ""):
        # Commons may be named as host, but creator attribution must also be present.
        creator = record.get("image_credit", "").split("/")[0].strip()
        if not creator or creator == "Wikimedia Commons":
            errors.append(f"{oid}: Commons image must credit creator, not only repository")

if errors:
    raise SystemExit("Image-rights validation failed:\n- " + "\n- ".join(errors))

print(f"Image-rights validation passed for {len(data.get('object_overviews', []))} object overviews")
