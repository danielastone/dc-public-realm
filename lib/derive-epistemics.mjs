// Clean-room JS implementation of the frozen epistemic derivation contract.
// Source rules: EPI-002 dependency state, EPI-004 lineage, EPI-005 conflicts.
// No file reads and no renderer/presentation policy live here.

export const ESTABLISHED_ROOT = 'ESTABLISHED_ROOT';
export const UNRESOLVED_ANCESTRY = 'UNRESOLVED_ANCESTRY';
export const BROKEN_REFERENCE = 'BROKEN_REFERENCE';
export const CYCLE = 'CYCLE';

const CONTRADICTS = 'CONTRADICTS';
const ROOT_ORIGINS = new Set(['ORIGINAL_TO_SOURCE', 'INDEPENDENT_CLAIM_ROOT']);

function codePointCompare(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

export function deriveDependencyState(record) {
  const inherited = record.inherits_claim_from_source_ids || [];
  const status = record.dependency_status ?? 'UNKNOWN';
  const origin = record.claim_origin ?? 'UNKNOWN';
  if (status === 'DEPENDENT' || inherited.length) return 'DEPENDENT';
  if (status === 'INDEPENDENT' && ROOT_ORIGINS.has(origin)) return 'INDEPENDENT';
  return 'INDEPENDENCE_NOT_ESTABLISHED';
}

function lineageIndex(rows) {
  const index = new Map();
  for (const row of rows) {
    const key = JSON.stringify([row.assertion_id, row.source_id]);
    const candidates = index.get(key) || [];
    candidates.push(row); // input order is contractual
    index.set(key, candidates);
  }
  return index;
}

function isRoot(row) {
  return row.dependency_status === 'INDEPENDENT'
    && ROOT_ORIGINS.has(row.claim_origin)
    && !(row.inherits_claim_from_source_ids || []).length;
}

function traceRow(row, index, stack = []) {
  const key = [row.assertion_id, row.source_id];
  if (stack.some(node => node[0] === key[0] && node[1] === key[1])) {
    return { terminal: CYCLE, path: [...stack, key] };
  }

  const parents = row.inherits_claim_from_source_ids || [];
  if (parents.length) {
    const branches = [];
    const nextStack = [...stack, key];
    for (const parentSourceId of parents) {
      const candidates = index.get(JSON.stringify([row.assertion_id, parentSourceId])) || [];
      if (!candidates.length) {
        branches.push({
          terminal: BROKEN_REFERENCE,
          path: [...nextStack, [row.assertion_id, parentSourceId]],
          missing_source_id: parentSourceId,
        });
        continue;
      }
      for (const parent of candidates) branches.push(traceRow(parent, index, nextStack));
    }
    return { terminal: null, node: key, branches };
  }

  if (isRoot(row)) return { terminal: ESTABLISHED_ROOT, path: [...stack, key] };
  return {
    terminal: UNRESOLVED_ANCESTRY,
    path: [...stack, key],
    claim_origin: row.claim_origin || 'UNKNOWN',
    dependency_status: row.dependency_status || 'UNKNOWN',
  };
}

export function traceAll(rows) {
  const index = lineageIndex(rows);
  const traces = new Map();
  for (const row of rows) traces.set(row.assertion_evidence_id, traceRow(row, index));
  return traces;
}

export function validateConflictRecords(rows) {
  const conditions = [];
  const seen = new Set();
  for (const row of rows) {
    const evidenceId = row.assertion_evidence_id;
    if (!evidenceId) {
      conditions.push({ evidence_id: null, condition: 'MISSING_ASSERTION_EVIDENCE_ID' });
      continue;
    }
    if (seen.has(evidenceId)) {
      conditions.push({ evidence_id: evidenceId, condition: 'DUPLICATE_ASSERTION_EVIDENCE_ID' });
    }
    seen.add(evidenceId);
    if (row.evidence_role !== CONTRADICTS) continue;
    for (const field of ['assertion_id', 'source_id', 'locator', 'evidence_note']) {
      if (!row[field]) conditions.push({ evidence_id: evidenceId, condition: 'INCOMPLETE_CONTRADICTS', field });
    }
  }
  return conditions;
}

export function conflictIndex(rows) {
  const index = new Map();
  for (const row of rows) {
    if (row.evidence_role !== CONTRADICTS) continue;
    const values = index.get(row.assertion_id) || [];
    values.push(row); // evidence-input order is contractual
    index.set(row.assertion_id, values);
  }
  return index;
}

function dependencyResults(rows) {
  return rows
    .map(row => ({ evidence_id: row.assertion_evidence_id, state: deriveDependencyState(row) }))
    .sort((a, b) => codePointCompare(a.evidence_id, b.evidence_id));
}

function lineageResults(rows) {
  const traces = traceAll(rows);
  return [...traces.keys()]
    .sort(codePointCompare)
    .map(evidenceId => ({ evidence_id: evidenceId, trace: traces.get(evidenceId) }));
}

function sortedConflictObject(index) {
  return Object.fromEntries([...index.keys()].sort(codePointCompare).map(key => [key, index.get(key)]));
}

function conflictBlock(rows, validationOnly) {
  const validation = validateConflictRecords(rows);
  if (validationOnly) return { validation_only: true, validation };
  return { validation_only: false, index: sortedConflictObject(conflictIndex(rows)), validation };
}

/** Produce the logical document frozen in docs/audits/epistemic-derivation-parity.md. */
export function deriveEpistemicParity(realRows, cases) {
  const realValidation = validateConflictRecords(realRows);
  const realIndex = realValidation.length ? new Map() : conflictIndex(realRows);
  const dependencyCases = [];
  const lineageCases = [];
  const conflictCases = [];

  for (const testCase of [...cases].sort((a, b) => codePointCompare(a.case_id, b.case_id))) {
    const validationOnly = testCase.validation_only === true;
    if (testCase.kind === 'conflict') {
      conflictCases.push({ case_id: testCase.case_id, ...conflictBlock(testCase.rows, validationOnly) });
    } else if (validationOnly) {
      throw new Error(`validation_only case ${testCase.case_id} has kind ${testCase.kind}`);
    } else if (testCase.kind === 'dependency') {
      dependencyCases.push({ case_id: testCase.case_id, results: dependencyResults(testCase.rows) });
    } else if (testCase.kind === 'lineage') {
      const ids = testCase.rows.map(row => row.assertion_evidence_id);
      if (ids.some(id => !id) || new Set(ids).size !== ids.length) {
        throw new Error(`lineage case ${testCase.case_id} needs present, unique evidence IDs`);
      }
      lineageCases.push({ case_id: testCase.case_id, results: lineageResults(testCase.rows) });
    } else {
      throw new Error(`unknown case kind ${JSON.stringify(testCase.kind)}`);
    }
  }

  return {
    dependency: { real: dependencyResults(realRows), cases: dependencyCases },
    lineage: { real: lineageResults(realRows), cases: lineageCases },
    conflicts: {
      real: { index: sortedConflictObject(realIndex), validation: realValidation },
      cases: conflictCases,
    },
  };
}
