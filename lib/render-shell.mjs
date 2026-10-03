// Shared publication shell for the JS migration.
// Views provide complete body markup; this module performs no I/O.
export function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#x27;');
}

export function renderShell({ title, body, basePath }) {
  const esc = escapeHtml;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} | Diplomatic Gifts in Washington</title><link rel="stylesheet" href="${esc(basePath)}/assets/style.css"></head><body><header><div class="kicker">Diplomatic Gifts in Washington</div><nav><a href="${esc(basePath)}/">Explore</a><a href="${esc(basePath)}/collaborate/">Research missions</a><a href="${esc(basePath)}/methodology/">About the research</a><a href="${esc(basePath)}/data/">Data</a></nav></header><main>${body}</main><footer>Research submissions do not change the public record until the underlying source is reviewed.</footer></body></html>`;
}
