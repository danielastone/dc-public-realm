# Overview implementation

Canonical overview content lives in `data/object-overviews.json`. `scripts/inject_object_overviews.py` renders that content into the generated object pages. Validation scripts check data completeness, image-rights metadata, URL provenance structure, and final rendered content.

Do not hand-edit overview facts into `site/objects/**/index.html`; those pages are generated outputs.
