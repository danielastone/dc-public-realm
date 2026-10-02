# HTML parity normalization register

Purpose: record every normalization applied when comparing Python- and JS-rendered HTML. No rule is added without a demonstrated diff and a written reason that the difference is semantically irrelevant.

| Rule | Status | Justification |
|---|---|---|
| Normalize CRLF to LF | Allowed from start | Repository and CI environments may differ in line-ending convention; DOM semantics are unchanged. |
| Ignore trailing whitespace at line ends / file end | Allowed from start | Formatting-only difference with no HTML semantic effect. |

Not allowed by default: attribute reordering, entity-representation rewriting, void-element rewriting, tag-case normalization, whitespace collapsing between tags, or DOM reserialization. Add any such rule only after a concrete parity failure demonstrates that it is required and harmless.
