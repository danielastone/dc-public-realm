import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { assertHtmlParity } from '../lib/html-parity.mjs';
import { inventory, compareInventories } from './publication-artifact-inventory.mjs';
import { pathFor, publishedObjects } from '../lib/publication-index.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SITE = path.join(ROOT, 'site');
const DATA = process.env.KNOWLEDGE_DATA_DIR || 'data';
const entities = JSON.parse(fs.readFileSync(path.resolve(ROOT, DATA, 'entities.json'), 'utf8'));
const objects = publishedObjects(entities);

const before = await inventory(SITE);
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'python-publication-determinism-'));
try {
  // Python writers derive ROOT from __file__. Copy the entire script tree and
  // staged data so imports and relative reads cannot fall back to the real repo.
  fs.cpSync(path.join(ROOT, 'scripts'), path.join(temp, 'scripts'), { recursive: true });
  fs.cpSync(path.join(ROOT, 'data'), path.join(temp, 'data'), { recursive: true });
  const env = { ...process.env, KNOWLEDGE_DATA_DIR: path.join(temp, 'data') };
  for (const script of ['build_publication.py', 'inject_external_records.py', 'enforce_navigation_contract.py']) {
    execFileSync('python', [path.join(temp, 'scripts', script)], { cwd: temp, env, stdio: 'inherit' });
  }
  for (const entity of objects) {
    const rel = pathFor(entity.entity_id, entities);
    const first = fs.readFileSync(path.join(SITE, rel), 'utf8');
    const second = fs.readFileSync(path.join(temp, 'site', rel), 'utf8');
    assertHtmlParity(first, second, `Python deterministic rebuild ${entity.entity_id}`);
  }
  console.log(`Python object-page determinism PASS: ${objects.length} published object pages identical across two builds`);
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
  compareInventories(before, await inventory(SITE), 'determinism test mutated the publication tree');
  console.log('Python determinism non-mutation PASS: site/ inventory unchanged');
}
