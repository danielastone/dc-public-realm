import fs from 'node:fs';
import assert from 'node:assert/strict';

import { buildEpistemicContext } from '../lib/epistemic-context.mjs';
import { publishedObjects } from '../lib/publication-index.mjs';
import { escapeHtml } from '../lib/render-shell.mjs';
import { EpistemicRenderError, renderEpistemics } from '../lib/render-epistemics.mjs';

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

const entitiesPayload = readJson('build/data/entities.json');
const assertions = readJson('build/data/assertions.json').assertions;
const evidence = readJson('build/data/assertion-evidence.json').assertion_evidence;
const sources = readJson('build/data/sources.json').sources;
const dependencyRules = readJson('data/publication_dependency_rules.json').rules;

const context = buildEpistemicContext(evidence, sources);
const published = publishedObjects(entitiesPayload);
const publishedIds = new Set(published.map(object => object.entity_id));

let renderedAssertions = 0;
let dependencyBlocks = 0;
let conflictWarnings = 0;

for (const assertion of assertions.filter(row => publishedIds.has(row.subject_id))) {
  const rows = context.byAssertion.get(assertion.assertion_id) || [];
  const html = renderEpistemics(assertion.assertion_id, rows, dependencyRules, context);
  if (!rows.length) {
    assert.equal(html, '', `${assertion.assertion_id}: zero-evidence assertion must render no epistemic block`);
    continue;
  }

  assert.ok(html.includes(`data-for-assertion-id="${escapeHtml(assertion.assertion_id)}"`), `${assertion.assertion_id}: missing assertion marker`);
  assert.ok(html.includes('class="claim-lineage"'), `${assertion.assertion_id}: evidence rows require lineage block`);

  for (const row of rows) {
    assert.ok(
      html.includes(escapeHtml(row.assertion_evidence_id)),
      `${assertion.assertion_id}: rendered epistemics must contain evidence row ${row.assertion_evidence_id}`,
    );
  }

  if (rows.length >= 2) {
    assert.ok(html.includes('class="evidence-independence"'), `${assertion.assertion_id}: multi-row assertion requires dependency block`);
    dependencyBlocks += 1;
  } else {
    assert.ok(!html.includes('class="evidence-independence"'), `${assertion.assertion_id}: single-row assertion must omit dependency block`);
  }

  const conflicts = context.conflicts.get(assertion.assertion_id) || [];
  if (conflicts.length) {
    assert.ok(html.startsWith('<aside class="material-conflict"'), `${assertion.assertion_id}: conflict warning must render first`);
    conflictWarnings += 1;
  }

  renderedAssertions += 1;
}

function row(id, aid, sid, overrides = {}) {
  return {
    assertion_evidence_id: id,
    assertion_id: aid,
    source_id: sid,
    evidence_role: 'SUPPORTS',
    locator: 'record',
    evidence_note: 'note',
    ...overrides,
  };
}

function source(id) {
  return { source_id: id, title: `Source ${id}`, url: `https://example.test/${id}` };
}

function renderPublishedObjectEpistemics(objectId, assertionRows, evidenceRows, sourceRows, rules) {
  const scopedContext = buildEpistemicContext(evidenceRows, sourceRows);
  let html = '';
  for (const assertion of assertionRows.filter(item => item.subject_id === objectId)) {
    const rows = scopedContext.byAssertion.get(assertion.assertion_id) || [];
    html += renderEpistemics(assertion.assertion_id, rows, rules, scopedContext);
  }
  return html;
}

// Renderer failures are publication-scoped. A missing dependency rule on an
// unpublished assertion is inert, but the same two-row assertion aborts when
// rendered. One-row assertions do not consult dependency rules at all.
const missingRuleRows = [
  row('AE-R1', 'A-RULE', 'SRC-R1'),
  row('AE-R2', 'A-RULE', 'SRC-R2'),
];
const noDependencyRules = {
  DEPENDENT: dependencyRules.DEPENDENT,
  INDEPENDENT: dependencyRules.INDEPENDENT,
};
assert.doesNotThrow(() => renderPublishedObjectEpistemics(
  'OBJ-PUBLISHED',
  [{ assertion_id: 'A-RULE', subject_id: 'OBJ-UNPUBLISHED' }],
  missingRuleRows,
  [source('SRC-R1'), source('SRC-R2')],
  noDependencyRules,
));
assert.throws(
  () => renderPublishedObjectEpistemics(
    'OBJ-PUBLISHED',
    [{ assertion_id: 'A-RULE', subject_id: 'OBJ-PUBLISHED' }],
    missingRuleRows,
    [source('SRC-R1'), source('SRC-R2')],
    noDependencyRules,
  ),
  error => error instanceof EpistemicRenderError
    && error.stage === 'dependency'
    && error.condition === 'MISSING_DEPENDENCY_RULE',
);
assert.doesNotThrow(() => {
  const one = [row('AE-ONE', 'A-ONE', 'SRC-ONE')];
  const oneContext = buildEpistemicContext(one, [source('SRC-ONE')]);
  renderEpistemics('A-ONE', one, {}, oneContext);
});

// A source ID present in evidence but absent from sources.json is likewise
// inert on an unpublished assertion and a deliberate lineage failure when the
// assertion is rendered.
const missingSourceRows = [row('AE-MISS', 'A-MISS', 'SRC-MISSING')];
assert.doesNotThrow(() => renderPublishedObjectEpistemics(
  'OBJ-PUBLISHED',
  [{ assertion_id: 'A-MISS', subject_id: 'OBJ-UNPUBLISHED' }],
  missingSourceRows,
  [],
  dependencyRules,
));
assert.throws(
  () => renderPublishedObjectEpistemics(
    'OBJ-PUBLISHED',
    [{ assertion_id: 'A-MISS', subject_id: 'OBJ-PUBLISHED' }],
    missingSourceRows,
    [],
    dependencyRules,
  ),
  error => error instanceof EpistemicRenderError
    && error.stage === 'lineage'
    && error.condition === 'MISSING_SOURCE_RECORD',
);

// Construction order is observable: conflict warning, dependency block, then
// lineage block. Data escaping is checked without making the entire HTML a
// second oracle.
const orderedRows = [
  row('AE-C1', 'A-C', 'SRC-C1', { evidence_role: 'CONTRADICTS', evidence_note: 'A < B', claim_origin: 'UNKNOWN' }),
  row('AE-C2', 'A-C', 'SRC-C2', { claim_origin: 'UNKNOWN' }),
];
const orderedContext = buildEpistemicContext(orderedRows, [source('SRC-C1'), source('SRC-C2')]);
const orderedHtml = renderEpistemics('A-C', orderedRows, dependencyRules, orderedContext);
const conflictAt = orderedHtml.indexOf('class="material-conflict"');
const dependencyAt = orderedHtml.indexOf('class="evidence-independence"');
const lineageAt = orderedHtml.indexOf('class="claim-lineage"');
assert.ok(conflictAt >= 0 && conflictAt < dependencyAt && dependencyAt < lineageAt, 'epistemic block order must be conflict -> dependency -> lineage');
assert.ok(orderedHtml.includes('A &lt; B'), 'conflict evidence text must be escaped');

console.log(`epistemic rendering PASS: ${renderedAssertions} published assertions rendered`);
console.log(`epistemic rendering PASS: ${dependencyBlocks} dependency blocks, ${conflictWarnings} conflict warnings`);
console.log('epistemic rendering scope PASS: unpublished dependency-rule and missing-source defects are inert; published defects abort');
console.log('epistemic rendering order PASS: conflict -> dependency -> lineage');
