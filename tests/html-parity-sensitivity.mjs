import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { assertHtmlParity, normalizeHtml } from '../lib/html-parity.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const page = path.join(ROOT, 'site', 'objects', 'jose-gervasio-artigas', 'index.html');
const html = fs.readFileSync(page, 'utf8');

// Registered normalizations only: CRLF/LF and trailing whitespace.
const crlf = html.replace(/\n/g, '\r\n') + '   \n';
assertHtmlParity(html, crlf, 'line-ending/trailing-whitespace normalization');

function mustFail(label, mutated) {
  let failed = false;
  try { assertHtmlParity(html, mutated, label); }
  catch (err) {
    failed = true;
    if (!String(err.message).includes('parity failed at offset')) throw err;
  }
  if (!failed) throw new Error(`${label}: comparator failed to detect mutation`);
}

const tagMutation = html.replace('<main>', '<section>');
if (tagMutation === html) throw new Error('fixture lacks <main> mutation target');
mustFail('tag mutation', tagMutation);

const attrMutation = html.replace('class="assertion"', 'class="assertion changed"');
if (attrMutation === html) throw new Error('fixture lacks assertion-class mutation target');
mustFail('attribute mutation', attrMutation);

const textMutation = html.replace('Diplomatic Gifts in Washington', 'Diplomatic Gifts in Washington!');
if (textMutation === html) throw new Error('fixture lacks text mutation target');
mustFail('text mutation', textMutation);

if (normalizeHtml(html).includes('\r')) throw new Error('normalizer left CR characters');
console.log('HTML parity sensitivity PASS: exact/registered-normalization equivalence; tag/attribute/text mutations rejected');
