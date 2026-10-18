#!/usr/bin/env python3
from __future__ import annotations
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
# Localization records and schema are not ledger-managed: always ROOT/data/localization.
# Canonical overview membership comes from KNOWLEDGE_DATA_DIR (materialized database)
# when set; an explicit override never falls back to the frozen baseline.
override = os.environ.get("KNOWLEDGE_DATA_DIR")
if override is not None:
    if not override.strip():
        raise SystemExit("Localization validation failed: KNOWLEDGE_DATA_DIR is set but empty")
    OVERVIEW_SOURCE = Path(override) / "object-overviews.json"
    if not OVERVIEW_SOURCE.is_file():
        raise SystemExit(f"Localization validation failed: overview file not found under KNOWLEDGE_DATA_DIR: {OVERVIEW_SOURCE}")
else:
    OVERVIEW_SOURCE = DATA / "object-overviews.json"
print(f"Localization records/schema source: {DATA / 'localization'}")
print(f"Localization overview-membership source: {OVERVIEW_SOURCE}")
SCHEMA = json.loads((DATA / "localization" / "schema.json").read_text(encoding="utf-8"))
OVERVIEWS = json.loads(OVERVIEW_SOURCE.read_text(encoding="utf-8"))["object_overviews"]
OBJECT_IDS = {o["object_entity_id"] for o in OVERVIEWS}

errors = []
loc_root = DATA / "localization"
records = []
for path in sorted(loc_root.glob("*.json")):
    if path.name == "schema.json":
        continue
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        errors.append(f"{path}: localization file must contain a list")
        continue
    records.extend((path, r) for r in payload)

for path, r in records:
    missing = [k for k in SCHEMA["required_record_fields"] if k not in r]
    if missing:
        errors.append(f"{path}: missing fields {missing}")
        continue
    oid = r["object_entity_id"]
    if oid not in OBJECT_IDS:
        errors.append(f"{path}: unknown canonical object {oid}")
    if r["language"] not in SCHEMA["supported_languages"]:
        errors.append(f"{path}: unsupported language {r['language']}")
    if r["translation_status"] not in SCHEMA["translation_statuses"]:
        errors.append(f"{path}: invalid translation status {r['translation_status']}")
    fields = r["canonical_fields"]
    if not isinstance(fields, dict):
        errors.append(f"{path}: canonical_fields must be an object")
        continue
    bad = sorted(set(fields) - set(SCHEMA["allowed_canonical_fields"]))
    if bad:
        errors.append(f"{path}: forbidden localized fields {bad}")
    if r["translation_status"] == "PUBLISHED":
        for key in ("reviewed_by", "reviewed_at"):
            if not r.get(key):
                errors.append(f"{path}: PUBLISHED record requires {key}")

if errors:
    raise SystemExit("Localization validation failed:\n- " + "\n- ".join(errors))
print(f"Localization validation passed: {len(records)} localized record(s)")
