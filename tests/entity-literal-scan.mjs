#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { publishedObjects, pathFor } from '../lib/publication-index.mjs';

const entities = JSON.parse(await readFile('build/data/entities.json', 'utf8'));
const production = (await readdir('lib')).filter(name => name.endsWith('.mjs')).map(name => `lib/${name}`).sort();
production.push('scripts/build_object_pages.mjs');

// Each exception must name the source file, exact term, and a written reason.
// No exceptions are currently justified.
const ALLOWLIST = Object.freeze([]);

const terms = new Set();
for (const entity of entities.entities) {
  if (typeof entity.entity_id === 'string' && entity.entity_id) terms.add(entity.entity_id);
  if (typeof entity.canonical_name === 'string' && entity.canonical_name) terms.add(entity.canonical_name);
}
for (const object of publishedObjects(entities)) {
  const route = pathFor(object.entity_id, entities);
  terms.add(route.split('/')[1]);
}
const targets = [...terms].sort((a, b) => b.length - a.length || a.localeCompare(b));

function scanFile(file, source) {
  const hits = [];
  for (const term of targets) {
    let offset = source.indexOf(term);
    while (offset !== -1) {
      const exception = ALLOWLIST.find(item => item.file === file && item.term === term && item.reason.trim());
      if (!exception) {
        const line = source.slice(0, offset).split('\n').length;
        hits.push({ file, term, line });
      }
      offset = source.indexOf(term, offset + term.length);
    }
  }
  return hits;
}

async function scanProduction(override = new Map()) {
  const hits = [];
  for (const file of production) {
    const source = override.has(file) ? override.get(file) : await readFile(file, 'utf8');
    hits.push(...scanFile(file, source));
  }
  return hits;
}

const hits = await scanProduction();
if (hits.length) {
  for (const hit of hits) console.error(`entity literal: ${hit.file}:${hit.line}: ${JSON.stringify(hit.term)}`);
  throw new Error(`production entity literal scan failed: ${hits.length} hit(s)`);
}
console.log(`JS entity literal scan PASS: 0 production hits; ${targets.length} distinct terms; ${production.length} source files`);

// A non-published entity proves that this gate is wider than published-object identity.
const publishedIds = new Set(publishedObjects(entities).map(object => object.entity_id));
const nonPublished = entities.entities.find(entity =>
  typeof entity.entity_id === 'string' && entity.entity_id && !publishedIds.has(entity.entity_id));
assert.ok(nonPublished, 'sensitivity requires a non-published entity');
const file = 'scripts/build_object_pages.mjs';
const original = await readFile(file, 'utf8');
const temp = await mkdtemp(join(tmpdir(), 'entity-literal-scan-'));
try {
  const copy = join(temp, 'build_object_pages.mjs');
  await writeFile(copy, original + `\n// ${nonPublished.entity_id}\n`);
  const mutated = await readFile(copy, 'utf8');
  const failures = await scanProduction(new Map([[file, mutated]]));
  assert.ok(failures.some(hit => hit.file === file && hit.term === nonPublished.entity_id),
    'non-published entity injection must fail with file and term');
  console.log(`JS entity literal scan sensitivity PASS: injected non-published entity rejected (${file}: ${nonPublished.entity_id})`);
} finally {
  await rm(temp, { recursive: true, force: true });
}
