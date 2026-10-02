import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { assertHtmlParity } from '../lib/html-parity.mjs';
import { pathFor, publishedObjects } from '../lib/publication-index.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATA = process.env.KNOWLEDGE_DATA_DIR || 'data';
const entities = JSON.parse(fs.readFileSync(path.join(ROOT, DATA, 'entities.json'), 'utf8'));
const objects = publishedObjects(entities);
const snapshot = fs.mkdtempSync(path.join(os.tmpdir(), 'python-object-pages-'));

// Snapshot the first completed Python publication. The CI step runs only after
// build_publication + external-record injection + navigation enforcement.
for (const entity of objects) {
  const rel = pathFor(entity.entity_id, entities);
  const src = path.join(ROOT, 'site', rel);
  const dst = path.join(snapshot, rel);
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
}

function runPython(script) {
  execFileSync('python', [script], { cwd: ROOT, env: process.env, stdio: 'inherit' });
}

// Reproduce the same object-page-affecting publication passes. This rebuilds
// site/ from the same staged materialized data; it does not alter source data.
runPython('scripts/build_publication.py');
runPython('scripts/inject_external_records.py');
runPython('scripts/enforce_navigation_contract.py');

for (const entity of objects) {
  const rel = pathFor(entity.entity_id, entities);
  const first = fs.readFileSync(path.join(snapshot, rel), 'utf8');
  const second = fs.readFileSync(path.join(ROOT, 'site', rel), 'utf8');
  assertHtmlParity(first, second, `Python deterministic rebuild ${entity.entity_id}`);
}

console.log(`Python object-page determinism PASS: ${objects.length} published object pages identical across two builds`);
