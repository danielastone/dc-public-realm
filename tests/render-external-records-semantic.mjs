import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { buildExternalRecordsContext, renderExternalRecords } from '../lib/render-external-records.mjs';
import { renderOverview, renderOverviewResult, SubjectNameMismatchError } from '../lib/render-overview.mjs';

const load = async (path, key) => JSON.parse(await readFile(path, 'utf8'))[key];
const assertions = await load('build/data/assertions.json', 'assertions');
const entities = await load('build/data/entities.json', 'entities');
const overviews = await load('build/data/object-overviews.json', 'object_overviews');
const records = await load('data/external-records.json', 'external_records');

const artigas = overviews.find(row => row.object_entity_id === 'OBJ-0001');
const overviewResult = renderOverviewResult(artigas, assertions, entities);
assert.equal(overviewResult.html, renderOverview(artigas, assertions, entities));
assert.equal(overviewResult.subjectId, 'AG-0001');
console.log('external records overview PASS: reconciled subject is exposed without changing overview HTML');

const context = buildExternalRecordsContext(records);
const artigasHtml = renderExternalRecords({
  objectId: 'OBJ-0001', subjectId: overviewResult.subjectId, subjectName: artigas.subject_name, context,
});
assert.ok(artigasHtml.startsWith('<section id="external-records"><h2>External records</h2>'));
assert.ok(artigasHtml.includes('<h3>Monument records</h3><ul class="sources">'));
assert.ok(artigasHtml.includes('<h3>José Gervasio Artigas authority records</h3><ul class="sources">'));
assert.equal((artigasHtml.match(/class="external-record"/g) || []).length, records.length);
console.log('external records current-data PASS: object + reconciled authority records preserve the two-group section');

const objectOnly = buildExternalRecordsContext([{ entity_id: 'OBJ-X', url: 'u', system: 's', label: 'l', record_type: 'object_record', identifier: 'i', note: 'n' }]);
const objectOnlyHtml = renderExternalRecords({ objectId: 'OBJ-X', subjectId: 'P-X', subjectName: 'Person X', context: objectOnly });
assert.ok(objectOnlyHtml.includes('<h3>Monument records</h3>'));
assert.ok(!objectOnlyHtml.includes('authority records'));
const authorityOnly = buildExternalRecordsContext([{ entity_id: 'P-X', url: 'u', system: 's', label: 'l', record_type: 'authority_record', identifier: 'i', note: 'n' }]);
const authorityOnlyHtml = renderExternalRecords({ objectId: 'OBJ-X', subjectId: 'P-X', subjectName: 'Person X', context: authorityOnly });
assert.ok(!authorityOnlyHtml.includes('Monument records'));
assert.ok(authorityOnlyHtml.includes('<h3>Person X authority records</h3>'));
assert.equal(renderExternalRecords({ objectId: 'OBJ-X', subjectId: 'P-X', subjectName: 'Person X', context: buildExternalRecordsContext([]) }), '');
console.log('external records extension PASS: object-only, authority-only, and neither are explicit JS extension behavior');

assert.throws(() => buildExternalRecordsContext([{ url: 'u' }]), /external record missing entity_id/);
const selectedMissingField = buildExternalRecordsContext([{ entity_id: 'OBJ-X', url: 'u' }]);
assert.throws(
  () => renderExternalRecords({ objectId: 'OBJ-X', context: selectedMissingField }),
  /external record missing system/,
);
const unselectedMissingField = buildExternalRecordsContext([{ entity_id: 'OTHER', url: 'u' }]);
assert.equal(renderExternalRecords({ objectId: 'OBJ-X', context: unselectedMissingField }), '');
console.log('external records scope PASS: entity_id is eager; card fields are required only for selected records');

const badOverview = { ...artigas, subject_name: 'Wrong person' };
assert.throws(() => renderOverviewResult(badOverview, assertions, entities), SubjectNameMismatchError);
console.log('external records upstream PASS: unresolved person subject aborts in overview reconciliation before 64d rendering');
