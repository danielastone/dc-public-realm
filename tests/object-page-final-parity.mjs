import assert from 'node:assert/strict';
import { cp, mkdtemp, readFile, readdir, rm, unlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { publishedObjects, pathFor } from '../lib/publication-index.mjs';

const PYTHON_ROOT = 'site';
const JS_ROOT = 'build/js-site';

async function objectRoutes(root) {
  const entries = await readdir(join(root, 'objects'), { withFileTypes: true });
  const routes = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const route = `objects/${entry.name}/index.html`;
    try {
      await readFile(join(root, route));
      routes.push(route);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
  }
  return routes.sort();
}

function setDifference(left, right) {
  const rightSet = new Set(right);
  return left.filter(value => !rightSet.has(value));
}

function firstDifference(a, b) {
  const limit = Math.min(a.length, b.length);
  for (let i = 0; i < limit; i += 1) if (a[i] !== b[i]) return i;
  return a.length === b.length ? -1 : limit;
}

export async function compareObjectTrees(pythonRoot, jsRoot, entitiesPayload) {
  const pythonRoutes = await objectRoutes(pythonRoot);
  const jsRoutes = await objectRoutes(jsRoot);
  const missingInJs = setDifference(pythonRoutes, jsRoutes);
  const extraInJs = setDifference(jsRoutes, pythonRoutes);
  if (missingInJs.length || extraInJs.length) {
    throw new Error(`object-page route-set mismatch: missing in JS [${missingInJs.join(', ')}]; extra in JS [${extraInJs.join(', ')}]`);
  }

  const publishedRoutes = publishedObjects(entitiesPayload)
    .map(object => pathFor(object.entity_id, entitiesPayload))
    .sort();
  assert.deepEqual(pythonRoutes, publishedRoutes, 'Python object-page tree differs from publishedObjects() route set');
  assert.deepEqual(jsRoutes, publishedRoutes, 'JS object-page tree differs from publishedObjects() route set');

  const pages = [];
  for (const route of pythonRoutes) {
    const pythonBytes = await readFile(join(pythonRoot, route));
    const jsBytes = await readFile(join(jsRoot, route));
    if (!pythonBytes.equals(jsBytes)) {
      const offset = firstDifference(pythonBytes, jsBytes);
      throw new Error(`object-page byte mismatch: ${route} at byte offset ${offset} (Python ${pythonBytes.length} B; JS ${jsBytes.length} B)`);
    }
    pages.push({ route, bytes: pythonBytes.length });
  }
  return pages;
}

const entitiesPayload = JSON.parse(await readFile('build/data/entities.json', 'utf8'));
const pages = await compareObjectTrees(PYTHON_ROOT, JS_ROOT, entitiesPayload);
console.log(`object-page final parity PASS: route sets equal (${pages.length} routes); raw bytes identical`);
for (const page of pages) console.log(`object-page final parity page: ${page.route} ${page.bytes} bytes`);

const sensitivityRoot = await mkdtemp(join(tmpdir(), 'object-page-final-parity-'));
const pythonCopy = join(sensitivityRoot, 'python');
const jsCopy = join(sensitivityRoot, 'js');
try {
  await cp(PYTHON_ROOT, pythonCopy, { recursive: true });
  await cp(JS_ROOT, jsCopy, { recursive: true });

  const removedRoute = pages[0].route;
  await unlink(join(jsCopy, removedRoute));
  await assert.rejects(
    () => compareObjectTrees(pythonCopy, jsCopy, entitiesPayload),
    error => error instanceof Error && error.message.includes(`route-set mismatch: missing in JS [${removedRoute}]`),
  );
  console.log(`object-page final parity sensitivity PASS: deleted JS route rejected first (${removedRoute})`);

  await rm(jsCopy, { recursive: true, force: true });
  await cp(JS_ROOT, jsCopy, { recursive: true });
  const changedRoute = pages[0].route;
  const changedPath = join(jsCopy, changedRoute);
  const changed = Buffer.from(await readFile(changedPath));
  const offset = Math.min(32, changed.length - 1);
  changed[offset] ^= 0x01;
  await writeFile(changedPath, changed);
  await assert.rejects(
    () => compareObjectTrees(pythonCopy, jsCopy, entitiesPayload),
    error => error instanceof Error && error.message.includes(`byte mismatch: ${changedRoute} at byte offset ${offset}`),
  );
  console.log(`object-page final parity sensitivity PASS: flipped JS byte rejected (${changedRoute} offset ${offset})`);
} finally {
  await rm(sensitivityRoot, { recursive: true, force: true });
}
