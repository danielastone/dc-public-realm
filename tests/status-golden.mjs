import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { computeStatus } from '../lib/status.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = p => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const assertions = read('data/assertions.json').assertions;
const evidence = read('data/assertion-evidence.json').assertion_evidence;
const rules = Object.fromEntries(read('data/predicate-rules.json').predicate_rules.map(r => [r.predicate, r]));
const golden = read('tests/fixtures/golden-assertion-status.json').statuses;
const byAssertion = new Map();
for (const edge of evidence) {
  const rows = byAssertion.get(edge.assertion_id) || [];
  rows.push(edge);
  byAssertion.set(edge.assertion_id, rows);
}

const actual = {};
for (const assertion of assertions) {
  const rule = rules[assertion.predicate];
  if (!rule) throw new Error(`${assertion.assertion_id}: missing predicate rule ${assertion.predicate}`);
  actual[assertion.assertion_id] = computeStatus(assertion, byAssertion.get(assertion.assertion_id) || [], rule)[0];
}

const expectedIds = Object.keys(golden).sort();
const actualIds = Object.keys(actual).sort();
if (JSON.stringify(actualIds) !== JSON.stringify(expectedIds)) {
  const missing = expectedIds.filter(id => !(id in actual));
  const extra = actualIds.filter(id => !(id in golden));
  throw new Error(`golden assertion set changed; missing=${missing.join(',')} extra=${extra.join(',')}`);
}
const mismatches = expectedIds.filter(id => actual[id] !== golden[id]).map(id => `${id}: expected ${golden[id]}, got ${actual[id]}`);
if (mismatches.length) throw new Error(`AUD-10 status mismatch:\n${mismatches.join('\n')}`);
console.log(`AUD-10 golden status PASS: ${expectedIds.length}/${expectedIds.length}`);
