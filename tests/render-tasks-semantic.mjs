import fs from 'node:fs';
import assert from 'node:assert/strict';

import { publishedObjects } from '../lib/publication-index.mjs';
import {
  buildResearchMissionContext,
  pred,
  publicStatus,
  quotePlus,
  renderResearchMissions,
  TaskRenderError,
} from '../lib/render-tasks.mjs';

const read = path => JSON.parse(fs.readFileSync(path, 'utf8'));
const entitiesPayload = read('build/data/entities.json');
const tasks = read('build/data/research-tasks.json').tasks;
const assertions = read('build/data/assertions.json').assertions;
const evidence = read('build/data/assertion-evidence.json').assertion_evidence;
const predicateRules = read('build/data/predicate-rules.json').predicate_rules;

const context = buildResearchMissionContext(tasks, assertions, evidence, predicateRules);
const published = publishedObjects(entitiesPayload);
let rendered = 0;
for (const object of published) {
  const html = renderResearchMissions({ objectId: object.entity_id, taskContext: context });
  const count = (context.openTasksByObject.get(object.entity_id) || []).length;
  assert.ok(html.startsWith('<h2>Research missions</h2>'));
  assert.ok(html.includes(`data-open-task-count="${count}"`));
  if (!count) {
    assert.ok(html.includes('There are no open research missions for this catalog record.'));
  } else {
    assert.ok(html.includes(`${count} open research mission${count !== 1 ? 's' : ''}`));
    for (const task of context.openTasksByObject.get(object.entity_id)) {
      assert.ok(html.includes(task.task_id));
      assert.ok(html.includes(task.title));
    }
  }
  rendered += 1;
}

// Task-specific presentation must match Python str.title() behavior for the
// ASCII predicate/status vocabulary, not merely uppercase first characters.
assert.equal(pred('PRIMARY_SOURCE'), 'Primary Source');
assert.equal(pred("foo's_bar"), "Foo'S Bar");
assert.equal(publicStatus('CONTESTED'), 'Sources differ');
assert.equal(publicStatus('CUSTOM_STATUS'), 'Custom_Status');

// #176: Python quote_plus behavior, deliberately not URLSearchParams behavior.
assert.equal(quotePlus("a~b*c'(d) e"), 'a~b%2Ac%27%28d%29+e');

// Scope 1: only OPEN tasks eagerly subscript object_entity_id.
assert.doesNotThrow(() => buildResearchMissionContext(
  [{ status: 'CLOSED' }],
  assertions,
  evidence,
  predicateRules,
));
assert.throws(
  () => buildResearchMissionContext([{ status: 'OPEN' }], assertions, evidence, predicateRules),
  error => error instanceof TaskRenderError && error.stage === 'open-task-index' && error.field === 'object_entity_id',
);

// Caller order: open-task indexing precedes whole-corpus status derivation.
assert.throws(
  () => buildResearchMissionContext(
    [{ status: 'OPEN' }],
    [{ assertion_id: 'A-BAD', predicate: 'MISSING_RULE', literal_value: 'x' }],
    [],
    predicateRules,
  ),
  error => error instanceof TaskRenderError && error.stage === 'open-task-index',
);

// Scope 2: subscripted task fields abort only when the open task belongs to the
// object whose section is rendered. The same bad task on another object is inert.
const badOpen = {
  object_entity_id: 'OBJ-X', status: 'OPEN', task_id: 'TASK-X', title: 'x',
  high_value_result: 'x', repository: 'x', collection: 'x', critical_rule: 'x',
};
const scopedContext = buildResearchMissionContext([badOpen], assertions, evidence, predicateRules);
assert.doesNotThrow(() => renderResearchMissions({ objectId: 'OBJ-Y', taskContext: scopedContext }));
assert.throws(
  () => renderResearchMissions({ objectId: 'OBJ-X', taskContext: scopedContext }),
  error => error instanceof TaskRenderError && error.stage === 'taskblock' && error.field === 'research_gap',
);

// Target fields are subscripted; an unknown assertion ID is a label fallback,
// not an abort.
const targetTask = {
  object_entity_id: 'OBJ-Z', status: 'OPEN', task_id: 'TASK-Z', title: 'z',
  research_gap: 'z', high_value_result: 'z', repository: 'z', collection: 'z', critical_rule: 'z',
  epistemic_targets: [{ assertion_id: 'A-NOT-PRESENT', desired_evidence: 'PRIMARY_SOURCE', desired_effect: 'VERIFY' }],
};
const targetContext = buildResearchMissionContext([targetTask], assertions, evidence, predicateRules);
const targetHtml = renderResearchMissions({ objectId: 'OBJ-Z', taskContext: targetContext });
assert.ok(targetHtml.includes('A-NOT-PRESENT'));
const brokenTarget = structuredClone(targetTask);
delete brokenTarget.epistemic_targets[0].desired_effect;
assert.throws(
  () => renderResearchMissions({
    objectId: 'OBJ-Z',
    taskContext: buildResearchMissionContext([brokenTarget], assertions, evidence, predicateRules),
  }),
  error => error instanceof TaskRenderError && error.stage === 'targetblock' && error.field === 'desired_effect',
);

console.log(`research missions PASS: ${rendered} published-object sections rendered from structured tasks`);
console.log('research missions scope PASS: open-task eager check and rendered-object field aborts match Python scope');
console.log('research missions target PASS: required target fields abort; unknown assertion ID falls back to ID');
console.log('research missions presentation PASS: pred/public_status match Python task labels');
console.log("research missions quote_plus PASS: ~ literal; * ' ( ) escaped; space -> +");
