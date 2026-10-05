import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdir, mkdtemp, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, relative } from 'node:path';
import { promisify } from 'node:util';
import { pathFor, PublicationIndexError, publishedObjects } from '../lib/publication-index.mjs';
import { REQUIRED_RENDERER_INPUTS, pathForRendererInput } from '../lib/renderer-input-policy.mjs';
import { assertCompleteRendererInputContract, loadAllRendererInputs } from '../lib/renderer-input-loader.mjs';
import { containedOutputPath, renderPublishedObjectPages } from '../lib/object-page-driver.mjs';

const execFileAsync = promisify(execFile);

async function listFiles(root, dir = root) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await listFiles(root, path));
    else out.push(relative(root, path).replaceAll('\\', '/'));
  }
  return out.sort();
}

assert.equal(REQUIRED_RENDERER_INPUTS.length, 10);
assert.doesNotThrow(() => assertCompleteRendererInputContract());
assert.throws(() => pathForRendererInput('python_object_pages'), /undeclared renderer input/);
assert.throws(() => assertCompleteRendererInputContract(REQUIRED_RENDERER_INPUTS.slice(1)), /exactly/);
console.log('JS driver loader PASS: complete 7 + 3 allowlist required; undeclared logical input rejected');

const synthetic = { entities: { entities: [{ entity_id: 'OBJ-SYN', entity_type: 'PhysicalObject', canonical_name: 'Synthetic object', country: 'Testland', publication: { publish: true, slug: 'synthetic-route' } }] }, assertions: { assertions: [] }, assertion_evidence: { assertion_evidence: [] }, sources: { sources: [] }, research_tasks: { tasks: [] }, predicate_rules: { predicate_rules: {} }, object_overviews: { object_overviews: [] }, publication_dependency_rules: { rules: {} }, publication_status_rules: { rules: {} }, external_records: { external_records: [] } };
const temp = await mkdtemp(join(tmpdir(), 'js-object-driver-'));
try { const rendered = await renderPublishedObjectPages(synthetic, temp); assert.deepEqual(rendered.map(x => x.route), ['objects/synthetic-route/index.html']); assert.equal(await readFile(join(temp, 'objects/synthetic-route/index.html'), 'utf8'), rendered[0].html); } finally { await rm(temp, { recursive: true, force: true }); }
console.log('JS driver routing PASS: synthetic publication metadata controls object and route without production literals');

const unsafePayload = { entities: [{ entity_id: 'OBJ-X', entity_type: 'PhysicalObject', publication: { publish: true, slug: '../escape' } }] };
assert.throws(() => pathFor('OBJ-X', unsafePayload), PublicationIndexError);
assert.throws(() => containedOutputPath('/tmp/driver-root', '../escape/index.html'), /escapes root/);
assert.throws(() => containedOutputPath('/tmp/driver-root', '/absolute/index.html'), /unsafe output route/);
console.log('JS driver containment PASS: publication index and output-root guard independently reject adversarial routes');

const realInputs = await loadAllRendererInputs();
const realTemp = await mkdtemp(join(tmpdir(), 'js-object-driver-real-'));
try { const direct = await renderPublishedObjectPages(realInputs, realTemp); for (const page of direct) { const production = await readFile(join('build/js-site', page.route), 'utf8'); assert.equal(production, page.html, `${page.entityId}: entry-point bytes differ from direct structured render`); } assert.equal(direct.length, 3); } finally { await rm(realTemp, { recursive: true, force: true }); }
console.log('JS driver bytes PASS: fixed-root entry-point output equals direct structured-render bytes for 3 published objects');

const staleDir = join('build/js-site', 'objects', 'stale-object');
await mkdir(staleDir, { recursive: true });
await writeFile(join(staleDir, 'index.html'), 'stale', 'utf8');
await execFileAsync(process.execPath, ['scripts/build_object_pages.mjs']);
const expectedRoutes = publishedObjects(realInputs.entities).map(object => pathFor(object.entity_id, realInputs.entities)).sort();
assert.deepEqual(await listFiles('build/js-site'), expectedRoutes);
console.log('JS driver stale-output PASS: entry point clears old routes and leaves exactly the current publication set');

const failing = {
  ...synthetic,
  entities: { entities: [
    { entity_id: 'OBJ-A', entity_type: 'PhysicalObject', canonical_name: 'First object', country: 'Testland', publication: { publish: true, slug: 'first' } },
    { entity_id: 'OBJ-B', entity_type: 'PhysicalObject', canonical_name: 'Second object', country: '', publication: { publish: true, slug: 'second' } },
  ] },
};
const failTemp = await mkdtemp(join(tmpdir(), 'js-object-driver-fail-'));
try {
  await assert.rejects(() => renderPublishedObjectPages(failing, failTemp), /OBJ-B: canonical entity has no country/);
  assert.deepEqual(await readdir(failTemp), []);
} finally { await rm(failTemp, { recursive: true, force: true }); }
console.log('JS driver no-partial-output PASS: render failure before write leaves the output root empty');

try { await stat('site'); assert.fail('site exists before JS driver proof'); } catch (error) { if (error.code !== 'ENOENT') throw error; }
const snapshots = (await readdir(tmpdir())).filter(name => name.startsWith('python-object-pages-'));
assert.deepEqual(snapshots, [], `Python determinism snapshots exist before JS driver proof: ${snapshots.join(', ')}`);
console.log('JS driver oracle-absence PASS: site/ and python-object-pages-* are absent at the driver boundary');
