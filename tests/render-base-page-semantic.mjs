import assert from 'node:assert/strict';
import { renderObjectPage } from '../lib/render-object-page.mjs';

const object = { entity_id: 'OBJ-X', canonical_name: 'Object X', country: 'Testland' };
const entities = [object, { entity_id: 'OBJ-P', canonical_name: 'Predecessor' }];
const assertions = [
  {
    assertion_id: 'A-DIRECT', subject_id: 'OBJ-X', predicate: 'COPY_OF', object_entity_id: 'OBJ-P',
    computed_status: 'SUPPORTED', status_reason: 'Reason one.',
  },
  {
    assertion_id: 'A-LINEAGE', subject_id: 'OBJ-P', predicate: 'CREATOR', literal_value: 'Maker',
    computed_status: 'VERIFIED', status_reason: 'Reason two.',
  },
];
const statusRules = { rules: {
  SUPPORTED: { rule_id: 'STATUS-SUPPORTED-001', public_label: 'Supported' },
  VERIFIED: { rule_id: 'STATUS-VERIFIED-001', public_label: 'Verified' },
} };
const taskContext = { openTasksByObject: new Map(), derivedById: new Map() };
const epistemicContext = { sourceById: new Map(), conflicts: new Map(), lineageIndex: { get() { return undefined; } } };

function render(overrides = {}) {
  return renderObjectPage({
    object, overview: null, assertions, evidence: [], sources: [], statusRules, entities,
    basePath: '/dc-public-realm', epistemicContext, dependencyRules: {}, taskContext,
    ...overrides,
  });
}

const html = render();
assert.ok(html.includes('<header><span class="site-state" aria-label="Site status: alpha">Alpha</span><div class="kicker">Diplomatic Gifts in Washington</div><nav class="primary-nav" aria-label="Primary">'));
assert.ok(html.includes('<div class="kicker" data-object-country="Testland">Testland · catalog record</div><h1 data-object-id="OBJ-X">Object X</h1>'));
assert.ok(html.includes('<article class="assertion" data-assertion-id="A-DIRECT" data-computed-status="SUPPORTED" data-status-rule="STATUS-SUPPORTED-001">'));
assert.ok(html.includes('<div class="kicker">A-DIRECT</div><h3>Copy Of: Predecessor</h3>'));
assert.ok(html.includes('<span class="status-label">Supported</span>'));
assert.ok(html.includes('<a class="status-rule" href="/dc-public-realm/methodology/#rule-STATUS-SUPPORTED-001">Why this status? <span class="rule-id">STATUS-SUPPORTED-001</span></a>'));
assert.ok(html.includes('<details class="evidence" data-evidence-assertion-id="A-DIRECT" data-source-count="0"><summary>Sources · 0</summary></details>'));
assert.ok(html.includes('<h2>Predecessor and lineage</h2><article class="assertion related-assertion" data-related-assertion-id="A-LINEAGE"'));
assert.ok(!html.includes('data-assertion-id="A-LINEAGE"'));
assert.ok(html.indexOf('A-DIRECT') < html.indexOf('Predecessor and lineage'));
assert.ok(html.includes('<h2>Research missions</h2><p class="task-summary" data-open-task-count="0">0 open research missions</p>'));
console.log('base page PASS: final header, record composition, assertion status rule, lineage section, and zero-task section');

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

const noLineage = render({ assertions: [{ ...assertions[0], predicate: 'CREATOR', object_entity_id: undefined, literal_value: 'Maker' }] });
assert.ok(!noLineage.includes('Predecessor and lineage'));
console.log('base page lineage scope PASS: predecessor section follows the frozen predicate set');
