#!/usr/bin/env node
// Sensitivity proof: ledger-authored overview metadata is validated after
// materialization. Every case runs in an isolated temporary workspace; the real
// repository's data/, build/, site/, migrations/ and transactions/ are never touched.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const COPY = ['scripts', 'data', 'migrations', 'transactions'];
const FIXTURE_TX = '9999-12-31-900-test-only-synthetic-obj-9004.json';

const ENTITY = {
  entity_id: 'OBJ-9004',
  entity_type: 'PhysicalObject',
  canonical_name: 'Synthetic Fixture Monument',
  country: 'Fixtureland',
  publication: { publish: false, slug: 'synthetic-fixture-monument', featured: false },
};

// Fully valid synthetic overview. Each failing case removes or changes exactly one field.
function validOverview() {
  return {
    object_entity_id: 'OBJ-9004',
    record_type: 'historical_object',
    location: 'Synthetic fixture location',
    location_source_url: 'https://example.invalid/fixture/location',
    event_label: 'Synthetic fixture event',
    event_date: '1900',
    event_source_url: 'https://example.invalid/fixture/event',
    object_context: 'Synthetic fixture context; not a real object.',
    object_context_source_url: 'https://example.invalid/fixture/context',
    image_url: 'https://example.invalid/fixture/image.jpg',
    image_alt: 'Synthetic fixture image',
    image_credit: 'Fixture Photographer',
    image_rights: 'CC BY-SA 4.0',
    image_license_url: 'https://creativecommons.org/licenses/by-sa/4.0/',
    image_source_url: 'https://example.invalid/fixture/source',
  };
}

function workspace() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'materialized-overview-'));
  for (const name of COPY) fs.cpSync(path.join(ROOT, name), path.join(dir, name), { recursive: true });
  return dir;
}

function addFixtureTransaction(dir, overview) {
  const tx = {
    transaction_id: 'TX-TEST-OBJ-9004',
    recorded_at: '9999-12-31',
    actor: 'test-fixture',
    purpose: 'TEST-ONLY synthetic overview for materialized validation sensitivity; never committed to transactions/.',
    evidence_decision: 'Synthetic fixture; not research evidence.',
    supersedes: null,
    operations: [
      { table: 'entities', action: 'add', id: 'OBJ-9004', value: ENTITY },
      { table: 'object_overviews', action: 'add', id: 'OBJ-9004', value: overview },
    ],
  };
  fs.writeFileSync(path.join(dir, 'transactions', FIXTURE_TX), JSON.stringify(tx, null, 2) + '\n');
}

function run(dir, args, dataDir) {
  const env = { ...process.env };
  delete env.KNOWLEDGE_DATA_DIR;
  if (dataDir !== undefined) env.KNOWLEDGE_DATA_DIR = dataDir;
  const r = spawnSync('python', args, { cwd: dir, env, encoding: 'utf8' });
  return { status: r.status, out: `${r.stdout}${r.stderr}` };
}

function materialize(dir) {
  const r = run(dir, ['scripts/build_database.py']);
  assert.equal(r.status, 0, `build_database.py must succeed in fixture workspace:\n${r.out}`);
  return path.join(dir, 'build', 'data'); // absolute path into the temp workspace
}

const OVERVIEW_M = ['scripts/validate_overview_data.py', '--scope=materialized'];
const OVERVIEW_B = ['scripts/validate_overview_data.py'];
const RIGHTS = ['scripts/validate_image_rights.py'];
const LOCALIZATION = ['scripts/validate_localization.py'];

function expectPass(label, r) {
  assert.equal(r.status, 0, `${label}: expected PASS, got exit ${r.status}\n${r.out}`);
  console.log(`  ${label}: PASS (exit 0)`);
}
function expectFail(label, r, pattern) {
  assert.notEqual(r.status, 0, `${label}: expected FAIL, got exit 0\n${r.out}`);
  assert.match(r.out, pattern, `${label}: failed for the wrong reason\n${r.out}`);
  console.log(`  ${label}: FAIL as intended (exit ${r.status}); matched ${pattern}`);
}
function caseRun(name, fn) {
  const dir = workspace();
  try { console.log(`${name}`); fn(dir); }
  finally { fs.rmSync(dir, { recursive: true, force: true }); }
}

caseRun('CONTROL no fixture transaction', dir => {
  const data = materialize(dir);
  expectPass('overview --scope=materialized', run(dir, OVERVIEW_M, data));
  expectPass('image rights (materialized)', run(dir, RIGHTS, data));
  expectPass('localization (materialized)', run(dir, LOCALIZATION, data));
});

caseRun('R1 CC rights without image_license_url', dir => {
  const o = validOverview(); delete o.image_license_url;
  addFixtureTransaction(dir, o);
  const data = materialize(dir);
  expectFail('image rights (materialized)', run(dir, RIGHTS, data),
    /OBJ-9004: Creative Commons image missing image_license_url/);
});

caseRun('R2 missing image_credit', dir => {
  const o = validOverview(); delete o.image_credit;
  addFixtureTransaction(dir, o);
  const data = materialize(dir);
  expectFail('image rights (materialized)', run(dir, RIGHTS, data), /OBJ-9004: image missing image_credit/);
});

caseRun('R3 missing location', dir => {
  const o = validOverview(); delete o.location;
  addFixtureTransaction(dir, o);
  const data = materialize(dir);
  expectFail('overview --scope=materialized', run(dir, OVERVIEW_M, data), /OBJ-9004: missing location/);
});

caseRun('R4 valid synthetic overview', dir => {
  addFixtureTransaction(dir, validOverview());
  const data = materialize(dir);
  expectPass('overview --scope=materialized (no frozen ID set)', run(dir, OVERVIEW_M, data));
  expectPass('image rights (materialized)', run(dir, RIGHTS, data));
  expectPass('overview baseline (frozen data/, unaffected by ledger)', run(dir, OVERVIEW_B));
});

caseRun('R5 localization membership follows materialized overviews', dir => {
  addFixtureTransaction(dir, validOverview());
  fs.writeFileSync(path.join(dir, 'data', 'localization', 'test-only-obj-9004.json'), JSON.stringify([{
    object_entity_id: 'OBJ-9004',
    language: 'es',
    translation_status: 'DRAFT',
    source_language: 'en',
    canonical_fields: { title: 'Monumento de prueba sintético' },
  }], null, 2) + '\n');
  const data = materialize(dir);
  expectPass('localization (materialized)', run(dir, LOCALIZATION, data));
  expectFail('localization (baseline, no override)', run(dir, LOCALIZATION), /unknown canonical object OBJ-9004/);
});

caseRun('B1 baseline exact-ID regression preserved', dir => {
  const file = path.join(dir, 'data', 'object-overviews.json');
  const payload = JSON.parse(fs.readFileSync(file, 'utf8'));
  payload.object_overviews.push(validOverview());
  fs.writeFileSync(file, JSON.stringify(payload, null, 2) + '\n');
  expectFail('overview baseline', run(dir, OVERVIEW_B),
    /overview IDs \['OBJ-0001', 'OBJ-0002', 'OBJ-0003', 'OBJ-9004'\] do not match expected \['OBJ-0001', 'OBJ-0002', 'OBJ-0003'\]/);
});

caseRun('X1 explicit override never falls back to baseline', dir => {
  const missing = path.join(dir, 'no-such-data-dir');
  expectFail('overview --scope=materialized', run(dir, OVERVIEW_M, missing), /overview file not found under KNOWLEDGE_DATA_DIR/);
  expectFail('image rights', run(dir, RIGHTS, missing), /overview file not found under KNOWLEDGE_DATA_DIR/);
  expectFail('localization', run(dir, LOCALIZATION, missing), /overview file not found under KNOWLEDGE_DATA_DIR/);
  expectFail('overview --scope=materialized without override', run(dir, OVERVIEW_M), /requires KNOWLEDGE_DATA_DIR/);
});

console.log('materialized overview validation sensitivity PASS');
