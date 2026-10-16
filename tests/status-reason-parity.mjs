import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

import { computeStatus } from '../lib/status.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATA = process.env.KNOWLEDGE_DATA_DIR || 'build/data';
const read = p => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));

const assertions = read(`${DATA}/assertions.json`).assertions;
const evidence = read(`${DATA}/assertion-evidence.json`).assertion_evidence;
const rules = read(`${DATA}/predicate-rules.json`).predicate_rules;
const pythonDerived = read('site/data/assertions.json').assertions;

const byAssertion = new Map();
for (const edge of evidence) {
  const rows = byAssertion.get(edge.assertion_id) || [];
  rows.push(edge);
  byAssertion.set(edge.assertion_id, rows);
}
const pythonById = new Map(pythonDerived.map(row => [row.assertion_id, row]));

assert.deepEqual(
  [...pythonById.keys()].sort(),
  assertions.map(row => row.assertion_id).sort(),
  'Python publication assertion set differs from materialized assertion set',
);

const mismatches = [];
for (const assertion of assertions) {
  const rule = rules[assertion.predicate];
  if (!rule) throw new Error(`${assertion.assertion_id}: missing predicate rule ${assertion.predicate}`);
  const [status, reason] = computeStatus(assertion, byAssertion.get(assertion.assertion_id) || [], rule);
  const python = pythonById.get(assertion.assertion_id);
  if (status !== python.computed_status || reason !== python.status_reason) {
    mismatches.push(
      `${assertion.assertion_id}: JS=(${status}, ${JSON.stringify(reason)}) Python=(${python.computed_status}, ${JSON.stringify(python.status_reason)})`,
    );
  }
}
if (mismatches.length) throw new Error(`AUD-10 live status/reason mismatch:\n${mismatches.join('\n')}`);

console.log(`AUD-10 live status+reason parity PASS: ${assertions.length}/${assertions.length} against Python publication output`);
