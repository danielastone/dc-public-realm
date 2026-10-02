import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { publishedObjects, featuredObject, pathFor, href } from '../lib/publication-index.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATA = process.env.KNOWLEDGE_DATA_DIR || 'build/data';
const entities = JSON.parse(fs.readFileSync(path.join(ROOT, DATA, 'entities.json'), 'utf8'));
const objects = publishedObjects(entities);
if (!objects.length) throw new Error('no published objects');
for (const object of objects) {
  const slug = object.publication.slug;
  if (!slug) throw new Error(`${object.entity_id}: missing slug`);
  if (pathFor(object.entity_id, entities) !== `objects/${slug}/index.html`) throw new Error(`${object.entity_id}: path mismatch`);
  if (href(object.entity_id, entities, '/dc-public-realm') !== `/dc-public-realm/objects/${slug}/`) throw new Error(`${object.entity_id}: href mismatch`);
}
const featured = featuredObject(entities);
if (!objects.some(o => o.entity_id === featured.entity_id)) throw new Error('featured object is not published');
console.log(`AUD-11 publication index PASS: ${objects.length} published objects; featured=${featured.entity_id}`);
