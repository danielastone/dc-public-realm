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

function without(row, field) {
  const copy = { ...row };
  delete copy[field];
  return copy;
}

function expectFailure(rows, stage, condition) {
  assert.throws(
    () => buildEpistemicContext(rows),
    error => error instanceof EpistemicContextError
      && error.stage === stage
      && error.condition === condition,
    `expected ${stage}/${condition}`,
  );
}

// Whole-corpus assertion_id presence is checked first, even for an unpublished
// row that is also missing its evidence ID. This pins the first precedence edge.
expectFailure(
  [without(without(validRow(), 'assertion_id'), 'assertion_evidence_id')],
  'assertion_id',
  'MISSING_ASSERTION_ID',
);

// Otherwise-valid unpublished rows missing assertion_id also abort eagerly.
expectFailure(
  [without(validRow(), 'assertion_id')],
  'assertion_id',
  'MISSING_ASSERTION_ID',
);

// Validation precedes source_id indexing. A row missing both fields therefore
// fails validation rather than the later source_id presence check.
expectFailure(
  [without(without(validRow(), 'assertion_evidence_id'), 'source_id')],
  'validation',
  'CONFLICT_VALIDATION_FAILED',
);

// Otherwise-valid unpublished rows missing source_id abort only after validation.
expectFailure(
  [without(validRow(), 'source_id')],
  'source_id',
  'MISSING_SOURCE_ID',
);

// Python subscripting tests key presence, not truthiness. An empty source_id is
// legal at this eager boundary and must survive into the index.
const emptySource = validRow({ assertion_evidence_id: 'AE-EMPTY', source_id: '' });
const emptyContext = buildEpistemicContext([emptySource]);
assert.deepEqual(emptyContext.lineageIndex.get('A-X', ''), [emptySource]);

// Nested Maps keep tuple semantics: null and the literal string "null" are
// distinct keys and cannot retrieve one another's rows.
const nullSource = validRow({ assertion_evidence_id: 'AE-NULL', source_id: null });
const stringNullSource = validRow({ assertion_evidence_id: 'AE-STRING-NULL', source_id: 'null' });
const collisionContext = buildEpistemicContext([nullSource, stringNullSource]);
assert.deepEqual(collisionContext.lineageIndex.get('A-X', null), [nullSource]);
assert.deepEqual(collisionContext.lineageIndex.get('A-X', 'null'), [stringNullSource]);

console.log('epistemic context PASS: assertion_id -> validation -> source_id order');
console.log('epistemic context PASS: empty source_id survives indexing');
console.log('epistemic context PASS: null and literal "null" source IDs remain distinct');
