// Publication-context construction for epistemic rendering.
// Mirrors Python's eager build order before any object page is rendered:
// assertion_id across evidence -> conflict validation -> source_id across
// evidence -> lineage index -> source_by_id -> conflicts. No I/O here.

import { conflictIndex, validateConflictRecords } from './derive-epistemics.mjs';

export class EpistemicContextError extends Error {
  constructor(stage, condition, detail = '') {
    super(detail ? `${condition}: ${detail}` : condition);
    this.name = 'EpistemicContextError';
    this.stage = stage;
    this.condition = condition;
  }
}

function requireKey(row, field, stage) {
  // Python row[field] checks presence, not truthiness. Empty string and null
  // therefore survive these eager checks exactly as they do in Python.
  if (!Object.hasOwn(row, field)) {
    throw new EpistemicContextError(stage, `MISSING_${field.toUpperCase()}`);
  }
}

function append(map, key, row) {
  const rows = map.get(key) || [];
  rows.push(row);
  map.set(key, rows);
}

function buildLineageIndex(rows) {
  // Nested Maps preserve Python tuple-key semantics without serializing
  // composite keys, so null, "null", empty strings, and separator-bearing IDs
  // remain distinct.
  const byAssertion = new Map();
  for (const row of rows) {
    const bySource = byAssertion.get(row.assertion_id) || new Map();
    append(bySource, row.source_id, row);
    byAssertion.set(row.assertion_id, bySource);
  }
  return {
    get(assertionId, sourceId) {
      return byAssertion.get(assertionId)?.get(sourceId) || [];
    },
  };
}

export function buildEpistemicContext(rows, sources = []) {
  // build_publication.py constructs by_assertion before build_context().
  const byAssertion = new Map();
  for (const row of rows) {
    requireKey(row, 'assertion_id', 'assertion_id');
    append(byAssertion, row.assertion_id, row);
  }

  // build_context() validates the entire evidence corpus before build_index().
  const validation = validateConflictRecords(rows);
  if (validation.length) {
    throw new EpistemicContextError('validation', 'CONFLICT_VALIDATION_FAILED', JSON.stringify(validation));
  }

  // build_index() then subscripts source_id on every evidence row.
  for (const row of rows) requireKey(row, 'source_id', 'source_id');
  const lineageIndex = buildLineageIndex(rows);

  // Python next builds {s['source_id']: s for s in sources}. Missing keys abort
  // here; duplicate IDs overwrite earlier rows, so Map.set() gives parity.
  const sourceById = new Map();
  for (const source of sources) {
    requireKey(source, 'source_id', 'sources');
    sourceById.set(source.source_id, source);
  }

  // Conflict indexing is the final context component and reuses the proven
  // derivation implementation rather than introducing renderer-local logic.
  const conflicts = conflictIndex(rows);

  return { byAssertion, lineageIndex, sourceById, conflicts };
}
