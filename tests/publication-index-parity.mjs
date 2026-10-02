import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { featuredObject, href, pathFor, publishedObjects } from '../lib/publication-index.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATA = process.env.KNOWLEDGE_DATA_DIR || 'build/data';
const BASE = '/dc-public-realm';
const entities = JSON.parse(fs.readFileSync(path.join(ROOT, DATA, 'entities.json'), 'utf8'));

const objects = publishedObjects(entities);
for (const entity of objects) {
  const id = entity.entity_id;
  // This makes the comparator assumption executable instead of documentary.
  // ASCII IDs make JS relational string ordering identical to Python sorted(str).
  if (typeof id !== 'string' || !/^[\x20-\x7E]+$/.test(id)) {
    throw new Error(`${id}: publication entity_id must be printable ASCII for the cross-language ordering contract`);
  }
}

const jsDump = {
  ordering_contract: 'entity_id ascending by Python Unicode code-point string order',
  objects: objects.map(entity => ({
    entity_id: entity.entity_id,
    slug: entity.publication.slug,
    path: pathFor(entity.entity_id, entities),
    href: href(entity.entity_id, entities, BASE),
  })),
  featured_entity_id: featuredObject(entities).entity_id,
};

const env = { ...process.env, KNOWLEDGE_DATA_DIR: DATA };
const pythonText = execFileSync('python', ['scripts/dump_publication_index.py'], {
  cwd: ROOT,
  env,
  encoding: 'utf8',
}).trim();
const pythonDump = JSON.parse(pythonText);

if (JSON.stringify(jsDump) !== JSON.stringify(pythonDump)) {
  console.error('Python publication index:', JSON.stringify(pythonDump, null, 2));
  console.error('JS publication index:', JSON.stringify(jsDump, null, 2));
  throw new Error('AUD-11 cross-language publication-index parity failed');
}
console.log(`AUD-11 cross-language parity PASS: ${objects.length} ordered published objects; featured=${jsDump.featured_entity_id}`);
