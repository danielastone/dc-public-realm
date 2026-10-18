import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
// Seed of a future expected-route contract, not an exhaustive publication baseline.
const REQUIRED = ['review/artigas/index.html'];

function verifyRequiredRoutes(site) {
  for (const rel of REQUIRED) {
    const file = path.join(site, rel);
    assert.ok(fs.existsSync(file) && fs.lstatSync(file).isFile(), `missing required publication route: ${rel}`);
  }
}
const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'required-publication-routes-'));
try {
  for (const rel of REQUIRED) {
    const file = path.join(fixture, rel);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, 'fixture');
  }
  verifyRequiredRoutes(fixture);
  fs.unlinkSync(path.join(fixture, REQUIRED[0]));
  assert.throws(() => verifyRequiredRoutes(fixture), /missing required publication route/);
  console.log('required publication routes deletion sensitivity PASS');
} finally {
  fs.rmSync(fixture, { recursive: true, force: true });
}
verifyRequiredRoutes(path.join(ROOT, 'site'));
console.log(`required publication routes PASS: ${REQUIRED.join(', ')}`);
