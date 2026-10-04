import assert from 'node:assert/strict';
import { buildEpistemicContext, EpistemicContextError } from '../lib/epistemic-context.mjs';

function validRow(overrides = {}) {
  return {
    assertion_evidence_id: 'AE-X',
    assertion_id: 'A-X',
    source_id: 'SRC-X',
    evidence_role: 'SUPPORTS',
    ...overrides,
  };
}

function validSource(overrides = {}) {
  return { source_id: 'SRC-X', title: 'Source X', ...overrides };
}

function without(row, field) {
  const copy = { ...row };
  delete copy[field];
  return copy;
}

function expectFailure(rows, sources, stage, condition) {
  assert.throws(
    () => buildEpistemicContext(rows, sources),
    error => error instanceof EpistemicContextError
      && error.stage === stage
      && error.condition === condition,
    `expected ${stage}/${condition}`,
  );
}

// assertion_id is checked before validation, even if the evidence ID is absent.
expectFailure(
  [without(without(validRow(), 'assertion_id'), 'assertion_evidence_id')],
  [validSource()],
  'assertion_id',
  'MISSING_ASSERTION_ID',
);
expectFailure([without(validRow(), 'assertion_id')], [validSource()], 'assertion_id', 'MISSING_ASSERTION_ID');

// Present-but-empty assertion_id survives Python's subscript boundary.
const emptyAssertion = validRow({ assertion_evidence_id: 'AE-EMPTY-A', assertion_id: '' });
const emptyAssertionContext = buildEpistemicContext([emptyAssertion], [validSource()]);
assert.deepEqual(emptyAssertionContext.lineageIndex.get('', 'SRC-X'), [emptyAssertion]);

// Validation precedes source_id indexing.
expectFailure(
  [without(without(validRow(), 'assertion_evidence_id'), 'source_id')],
  [validSource()],
  'validation',
  'CONFLICT_VALIDATION_FAILED',
);
expectFailure([without(validRow(), 'source_id')], [validSource()], 'source_id', 'MISSING_SOURCE_ID');

// Empty source_id survives evidence indexing.
const emptySource = validRow({ assertion_evidence_id: 'AE-EMPTY', source_id: '' });
const emptyContext = buildEpistemicContext([emptySource], [validSource()]);
assert.deepEqual(emptyContext.lineageIndex.get('A-X', ''), [emptySource]);

// Nested Maps preserve Python tuple semantics.
const nullSource = validRow({ assertion_evidence_id: 'AE-NULL', source_id: null });
const stringNullSource = validRow({ assertion_evidence_id: 'AE-STRING-NULL', source_id: 'null' });
const collisionContext = buildEpistemicContext([nullSource, stringNullSource], [validSource()]);
assert.deepEqual(collisionContext.lineageIndex.get('A-X', null), [nullSource]);
assert.deepEqual(collisionContext.lineageIndex.get('A-X', 'null'), [stringNullSource]);

// sources.json is read only after evidence validation and indexing. A bad source
// therefore loses to an earlier evidence-validation failure.
const badSource = without(validSource(), 'source_id');
expectFailure([validRow()], [badSource], 'sources', 'MISSING_SOURCE_ID');
expectFailure(
  [without(validRow(), 'assertion_evidence_id')],
  [badSource],
  'validation',
  'CONFLICT_VALIDATION_FAILED',
);

// source_by_id uses dict-comprehension semantics: last duplicate wins.
const firstSource = validSource({ title: 'first' });
const lastSource = validSource({ title: 'last' });
const fullContext = buildEpistemicContext([validRow()], [firstSource, lastSource]);
assert.equal(fullContext.sourceById.get('SRC-X'), lastSource);
assert.deepEqual(fullContext.conflicts.get('A-X') || [], []);

console.log('epistemic context PASS: assertion_id -> validation -> source_id -> index -> sources -> conflicts order');
console.log('epistemic context PASS: empty assertion_id and source_id survive eager key-presence checks');
console.log('epistemic context PASS: null and literal "null" source IDs remain distinct');
console.log('epistemic context PASS: source_by_id is eager and last duplicate wins');
console.log('epistemic context PASS: conflicts reuse canonical conflict index');
