import assert from 'node:assert/strict';
import { buildEpistemicContext } from '../lib/epistemic-context.mjs';
import { renderObjectPage } from '../lib/render-object-page.mjs';
import { buildResearchMissionContext } from '../lib/render-tasks.mjs';

const object = { entity_id: 'OBJ-X', canonical_name: 'Object X', country: 'Testland' };
const entities = [object, { entity_id: 'OBJ-P', canonical_name: 'Predecessor' }];
const assertions = [
  {
    assertion_id: 'A-DIRECT', subject_id: 'OBJ-X', predicate: 'COPY_OF', object_entity_id: 'OBJ-P',
  },
  {
    assertion_id: 'A-LINEAGE', subject_id: 'OBJ-P', predicate: 'CREATOR', literal_value: 'Maker',
  },
];
const evidence = [
  {
    assertion_evidence_id: 'AE-DIRECT', assertion_id: 'A-DIRECT', source_id: 'SRC-DIRECT',
    evidence_role: 'PRIMARY_SUPPORT', authority_fit: 'SUPPORTING', proximity: 'LATER_SECONDARY',
    claim_origin: 'ORIGINAL_TO_SOURCE', locator: 'record',
  },
  {
    assertion_evidence_id: 'AE-LINEAGE', assertion_id: 'A-LINEAGE', source_id: 'SRC-LINEAGE',
    evidence_role: 'PRIMARY_SUPPORT', authority_fit: 'DIRECT', proximity: 'CONTEMPORANEOUS_PRIMARY',
    claim_origin: 'ORIGINAL_TO_SOURCE', locator: 'record',
  },
];
const sources = [
  { source_id: 'SRC-DIRECT', title: 'Direct source', url: 'https://example.test/direct' },
  { source_id: 'SRC-LINEAGE', title: 'Lineage source', url: 'https://example.test/lineage' },
];
const predicateRules = {
  COPY_OF: { standard: 'OBJECT_LINEAGE', single_source_can_verify: false },
  CREATOR: { standard: 'CONTEMPORANEOUS_OR_CONSTITUTIVE', single_source_can_verify: true },
};
const statusRules = { rules: {
  SUPPORTED: { rule_id: 'STATUS-SUPPORTED-001', public_label: 'Supported' },
  VERIFIED: { rule_id: 'STATUS-VERIFIED-001', public_label: 'Verified' },
} };
const dependencyRules = {};
const taskContext = buildResearchMissionContext([], assertions, evidence, predicateRules);
const epistemicContext = buildEpistemicContext(evidence, sources);

function render(overrides = {}) {
  return renderObjectPage({
    object, overview: null, assertions, evidence, sources, statusRules, entities,
    basePath: '/dc-public-realm', epistemicContext, dependencyRules, taskContext,
    ...overrides,
  });
}

const html = render();
assert.ok(html.includes('<header><span class="site-state" aria-label="Site status: alpha">Alpha</span><div class="kicker">Diplomatic Gifts in Washington</div><nav class="primary-nav" aria-label="Primary">'));
assert.ok(html.includes('<div class="kicker" data-object-country="Testland">Testland · catalog record</div><h1 data-object-id="OBJ-X">Object X</h1>'));
assert.ok(html.includes('<article class="assertion" data-assertion-id="A-DIRECT" data-computed-status="SUPPORTED" data-status-rule="STATUS-SUPPORTED-001">'));
assert.ok(html.includes('<div class="kicker">A-DIRECT</div><h3>Copy Of: Predecessor</h3>'));
assert.ok(html.includes('<span class="status-label">Supported</span>'));
assert.ok(html.includes('<span class="status-reason">Credible evidence supports the statement, but the verification threshold is not met.</span>'));
assert.ok(html.includes('<a class="status-rule" href="/dc-public-realm/methodology/#rule-STATUS-SUPPORTED-001">Why this status? <span class="rule-id">STATUS-SUPPORTED-001</span></a>'));
assert.ok(html.includes('<details class="evidence" data-evidence-assertion-id="A-DIRECT" data-source-count="1"><summary>Sources · 1</summary>'));
assert.ok(html.includes('<h2>Predecessor and lineage</h2><article class="assertion related-assertion" data-related-assertion-id="A-LINEAGE"'));
assert.ok(html.includes('<span class="status-reason">A directly authoritative source meets the evidence rule for this statement.</span>'));
assert.ok(!html.includes('data-assertion-id="A-LINEAGE"'));
assert.ok(!html.includes('undefined'));
assert.ok(html.indexOf('A-DIRECT') < html.indexOf('Predecessor and lineage'));
assert.ok(html.includes('<h2>Research missions</h2><p class="task-summary" data-open-task-count="0">0 open research missions</p>'));
console.log('base page PASS: final header, derived status reasons, assertion status rule, lineage section, and zero-task section');

assert.throws(
  () => render({ statusRules: { rules: { VERIFIED: statusRules.rules.VERIFIED } } }),
  /A-DIRECT: no publication status rule for SUPPORTED/,
);
assert.throws(
  () => render({ statusRules: { rules: { SUPPORTED: statusRules.rules.SUPPORTED } } }),
  /A-LINEAGE: no publication status rule for VERIFIED/,
);
console.log('base page status-rule scope PASS: direct and related assertions both abort on missing rule');

assert.throws(
  () => render({ object: { entity_id: 'OBJ-X', canonical_name: 'Object X', country: '' } }),
  /OBJ-X: canonical entity has no country/,
);
console.log('base page country PASS: missing canonical country aborts before composition');

const noLineageAssertions = [{
  assertion_id: 'A-DIRECT', subject_id: 'OBJ-X', predicate: 'CREATOR', literal_value: 'Maker',
}];
const noLineageEvidence = [evidence[0]];
const noLineageTaskContext = buildResearchMissionContext([], noLineageAssertions, noLineageEvidence, predicateRules);
const noLineageEpistemicContext = buildEpistemicContext(noLineageEvidence, [sources[0]]);
const noLineage = render({
  assertions: noLineageAssertions,
  evidence: noLineageEvidence,
  sources: [sources[0]],
  taskContext: noLineageTaskContext,
  epistemicContext: noLineageEpistemicContext,
});
assert.ok(!noLineage.includes('Predecessor and lineage'));
console.log('base page lineage scope PASS: predecessor section follows the frozen predicate set');
