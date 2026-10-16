import assert from 'node:assert/strict';
import { buildEpistemicContext } from '../lib/epistemic-context.mjs';
import { BROKEN_REFERENCE, ESTABLISHED_ROOT, traceRow } from '../lib/derive-epistemics.mjs';

const parent = {
  assertion_evidence_id: 'AE-PARENT',
  assertion_id: 'A-X',
  source_id: '',
  evidence_role: 'SUPPORTS',
  dependency_status: 'INDEPENDENT',
  claim_origin: 'ORIGINAL_TO_SOURCE',
};
const child = {
  assertion_evidence_id: 'AE-CHILD',
  assertion_id: 'A-X',
  source_id: 'SRC-CHILD',
  evidence_role: 'SUPPORTS',
  inherits_claim_from_source_ids: [''],
};

const context = buildEpistemicContext([parent, child], []);
const trace = traceRow(child, context.lineageIndex);

assert.equal(trace.terminal, null);
assert.equal(trace.branches.length, 1);
assert.equal(trace.branches[0].terminal, ESTABLISHED_ROOT);
assert.notEqual(trace.branches[0].terminal, BROKEN_REFERENCE);
assert.deepEqual(trace.branches[0].path, [
  ['A-X', 'SRC-CHILD'],
  ['A-X', ''],
]);

console.log('epistemic trace-row PASS: shared context index resolves inherited empty source ID');
