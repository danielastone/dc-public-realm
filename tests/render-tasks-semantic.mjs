import fs from 'node:fs';
import assert from 'node:assert/strict';

import { buildOpenTasksByObject, quotePlus, renderResearchMissions, TaskRenderError } from '../lib/render-tasks.mjs';

const read = path => JSON.parse(fs.readFileSync(path, 'utf8'));
const tasks = read('build/data/research-tasks.json').tasks;
const assertions = read('build/data/assertions.json').assertions;
const evidence = read('build/data/assertion-evidence.json').assertion_evidence;
const predicateRules = Object.fromEntries(read('build/data/predicate-rules.json').predicate_rules.map(rule => [rule.predicate, rule]));

const open = buildOpenTasksByObject(tasks);
const objectIds = ['OBJ-0001', 'OBJ-0002', 'OBJ-0003'];
let rendered = 0;
for (const objectId of objectIds) {
  const html = renderResearchMissions({ objectId, openTasksByObject: open, assertions, evidence, predicateRules });
  const count = (open.get(objectId) || []).length;
  assert.ok(html.startsWith('<h2>Research missions</h2>'));
  assert.ok(html.includes(`data-open-task-count="${count}"`));
  if (!count) {
    assert.ok(html.includes('There are no open research missions for this catalog record.'));
  } else {
    assert.ok(html.includes(`${count} open research mission${count !== 1 ? 's' : ''}`));
    for (const task of open.get(objectId)) {
      assert.ok(html.includes(task.task_id));
      assert.ok(html.includes(task.title));
    }
  }
  rendered += 1;
}

// #176: Python quote_plus behavior, deliberately not URLSearchParams behavior.
assert.equal(quotePlus("a~b*c'(d) e"), 'a~b%2Ac%27%28d%29+e');

// Scope 1: only OPEN tasks eagerly subscript object_entity_id.
assert.doesNotThrow(() => buildOpenTasksByObject([{ status: 'CLOSED' }]));
assert.throws(
  () => buildOpenTasksByObject([{ status: 'OPEN' }]),
  error => error instanceof TaskRenderError && error.stage === 'open-task-index' && error.field === 'object_entity_id',
);

// Scope 2: subscripted task fields abort only when the open task belongs to the
// object whose section is rendered. The same bad task on another object is inert.
const badOpen = {
  object_entity_id: 'OBJ-X', status: 'OPEN', task_id: 'TASK-X', title: 'x',
  high_value_result: 'x', repository: 'x', collection: 'x', critical_rule: 'x',
};
const scoped = buildOpenTasksByObject([badOpen]);
assert.doesNotThrow(() => renderResearchMissions({ objectId: 'OBJ-Y', openTasksByObject: scoped, assertions, evidence, predicateRules }));
assert.throws(
  () => renderResearchMissions({ objectId: 'OBJ-X', openTasksByObject: scoped, assertions, evidence, predicateRules }),
  error => error instanceof TaskRenderError && error.stage === 'taskblock' && error.field === 'research_gap',
);

// Target fields are subscripted; an unknown assertion ID is a label fallback,
// not an abort.
const targetTask = {
  object_entity_id: 'OBJ-Z', status: 'OPEN', task_id: 'TASK-Z', title: 'z',
  research_gap: 'z', high_value_result: 'z', repository: 'z', collection: 'z', critical_rule: 'z',
  epistemic_targets: [{ assertion_id: 'A-NOT-PRESENT', desired_evidence: 'PRIMARY_SOURCE', desired_effect: 'VERIFY' }],
};
const targetIndex = buildOpenTasksByObject([targetTask]);
const targetHtml = renderResearchMissions({ objectId: 'OBJ-Z', openTasksByObject: targetIndex, assertions, evidence, predicateRules });
assert.ok(targetHtml.includes('A-NOT-PRESENT'));
const brokenTarget = structuredClone(targetTask);
delete brokenTarget.epistemic_targets[0].desired_effect;
assert.throws(
  () => renderResearchMissions({ objectId: 'OBJ-Z', openTasksByObject: buildOpenTasksByObject([brokenTarget]), assertions, evidence, predicateRules }),
  error => error instanceof TaskRenderError && error.stage === 'targetblock' && error.field === 'desired_effect',
);

console.log(`research missions PASS: ${rendered} object sections rendered from structured tasks`);
console.log('research missions scope PASS: open-task eager check and rendered-object field aborts match Python scope');
console.log('research missions target PASS: required target fields abort; unknown assertion ID falls back to ID');
console.log("research missions quote_plus PASS: ~ literal; * ' ( ) escaped; space -> +");
