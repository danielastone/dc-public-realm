#!/usr/bin/env node
// Deterministic inventory of final publication artifacts; not a build or validator replacement.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstat, mkdtemp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, relative, resolve, sep } from 'node:path';

export async function inventory(root) {
  const base = resolve(root);
  const files = [];
  async function walk(dir) {
    for (const entry of (await readdir(dir, { withFileTypes: true })).sort((a,b) => a.name.localeCompare(b.name, 'en'))) {
      const full = join(dir, entry.name);
      const stat = await lstat(full);
      if (stat.isSymbolicLink()) throw new Error('symlink in publication: ' + relative(base, full));
      if (stat.isDirectory()) { await walk(full); continue; }
      if (!stat.isFile()) throw new Error('non-file publication entry: ' + relative(base, full));
      const rel = relative(base, full).split(sep).join('/');
      const bytes = await readFile(full);
      files.push({ path: rel, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
    }
  }
  await walk(base);
  files.sort((a,b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  return { format: 'publication-artifact-inventory-v1', files };
}
export function compareInventories(expected, actual, message = 'publication artifact inventory changed') {
  assert.deepEqual(actual, expected, message);
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
  const root = 'site';
  const a = await inventory(root);
  const b = await inventory(root);
  compareInventories(a, b);
  assert.ok(a.files.some(f => f.path === 'index.html'), 'missing home page');
  assert.ok(a.files.some(f => f.path === 'assets/style.css'), 'missing stylesheet');
  assert.ok(a.files.some(f => f.path === 'review/artigas/index.html'), 'missing Artigas review brief from inventory');
  const tmp = await mkdtemp(join(tmpdir(), 'publication-inventory-'));
  try {
    await mkdir(join(tmp, 'objects'), { recursive: true });
    await writeFile(join(tmp, 'index.html'), 'baseline');
    const before = await inventory(tmp);
    await writeFile(join(tmp, 'index.html'), 'mutated');
    const after = await inventory(tmp);
    assert.throws(() => compareInventories(before, after), /publication artifact inventory changed/);
    console.log('publication artifact inventory sensitivity PASS: changed bytes rejected');
  } finally { await rm(tmp, { recursive: true, force: true }); }
  await mkdir('build/audit', { recursive: true });
  await writeFile('build/audit/publication-artifacts.json', JSON.stringify(a, null, 2) + '\n');
  console.log('publication artifact inventory PASS: ' + a.files.length + ' files; build/audit/publication-artifacts.json');
}
