#!/usr/bin/env python3
"""Read-only parity adapter for the existing Python publication index.

This file is test infrastructure. It imports the production index unchanged and
serializes its public results so the JS port can be compared cross-language.
"""
from __future__ import annotations

import json
import os

from publication_index import featured_object, href, path_for, published_objects

DATA = os.environ.get("KNOWLEDGE_DATA_DIR")
BASE = "/dc-public-realm"
objects = published_objects(DATA)

payload = {
    "ordering_contract": "entity_id ascending by Python Unicode code-point string order",
    "objects": [
        {
            "entity_id": entity["entity_id"],
            "slug": entity["publication"]["slug"],
            "path": path_for(entity["entity_id"], DATA).as_posix(),
            "href": href(entity["entity_id"], BASE, DATA),
        }
        for entity in objects
    ],
    "featured_entity_id": featured_object(DATA)["entity_id"],
}
print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
