// Minimal HTML parity normalizer/comparator.
// Allowed normalization is governed by docs/audits/html-parity-normalization.md.

export function normalizeHtml(text) {
  return text
    .replace(/\r\n?/g, '\n')
    .split('\n')
    .map(line => line.replace(/[ \t]+$/g, ''))
    .join('\n')
    .replace(/\s+$/g, '');
}

export function firstDifference(expected, actual) {
  const a = normalizeHtml(expected);
  const b = normalizeHtml(actual);
  if (a === b) return null;
  const limit = Math.min(a.length, b.length);
  let i = 0;
  while (i < limit && a[i] === b[i]) i += 1;
  const contextStart = Math.max(0, i - 80);
  const contextEndA = Math.min(a.length, i + 120);
  const contextEndB = Math.min(b.length, i + 120);
  return {
    offset: i,
    expected: a.slice(contextStart, contextEndA),
    actual: b.slice(contextStart, contextEndB),
  };
}

export function assertHtmlParity(expected, actual, label = 'HTML') {
  const diff = firstDifference(expected, actual);
  if (!diff) return;
  throw new Error(`${label} parity failed at offset ${diff.offset}\nEXPECTED: ${diff.expected}\nACTUAL:   ${diff.actual}`);
}
