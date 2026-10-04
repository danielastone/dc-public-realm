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

export function primaryNav(basePath) {
  const esc = escapeHtml;
  return `<nav class="primary-nav" aria-label="Primary"><a href="${esc(basePath)}/">Explore</a><a href="${esc(basePath)}/collaborate/">Research missions</a><a href="${esc(basePath)}/methodology/">About the research</a><a href="${esc(basePath)}/data/">Data</a></nav>`;
}

export function siteState() {
  return '<span class="site-state" aria-label="Site status: alpha">Alpha</span>';
}

export function renderShell({ title, body, basePath, headContent = '' }) {
  const esc = escapeHtml;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} | Diplomatic Gifts in Washington</title><link rel="stylesheet" href="${esc(basePath)}/assets/style.css">${headContent}</head><body><header>${siteState()}<div class="kicker">Diplomatic Gifts in Washington</div>${primaryNav(basePath)}</header><main>${body}</main><footer>Research submissions do not change the public record until the underlying source is reviewed.</footer></body></html>`;
}
