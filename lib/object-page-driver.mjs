import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve, relative, isAbsolute, sep } from 'node:path';
import { publishedObjects, pathFor } from './publication-index.mjs';
import { buildEpistemicContext } from './epistemic-context.mjs';
import { buildResearchMissionContext } from './render-tasks.mjs';
import { buildExternalRecordsContext } from './render-external-records.mjs';
import { renderObjectPage } from './render-object-page.mjs';

const BASE_PATH = '/dc-public-realm';
function rows(payload, key) { const value = payload?.[key]; if (!Array.isArray(value)) throw new Error(`${key}: expected array payload`); return value; }
function rules(payload, key) { const value = payload?.[key]; if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${key}: expected object payload`); return value; }

export function normalizeRendererInputs(loaded) {
  return {
    entitiesPayload: loaded.entities,
    entities: rows(loaded.entities, 'entities'), assertions: rows(loaded.assertions, 'assertions'),
    evidence: rows(loaded.assertion_evidence, 'assertion_evidence'), sources: rows(loaded.sources, 'sources'),
    tasks: rows(loaded.research_tasks, 'tasks'), predicateRules: rules(loaded.predicate_rules, 'predicate_rules'),
    overviews: rows(loaded.object_overviews, 'object_overviews'), dependencyRules: rules(loaded.publication_dependency_rules, 'rules'),
    statusRules: rules(loaded.publication_status_rules, 'rules'), externalRecords: rows(loaded.external_records, 'external_records'),
  };
}

export function buildDriverContexts(input) {
  const epistemicContext = buildEpistemicContext(input.evidence, input.sources);
  const taskContext = buildResearchMissionContext(input.tasks, input.assertions, input.evidence, input.predicateRules);
  const externalRecordsContext = buildExternalRecordsContext(input.externalRecords);
  return { epistemicContext, taskContext, externalRecordsContext };
}

export function containedOutputPath(outputRoot, route) {
  if (typeof route !== 'string' || !route || isAbsolute(route)) throw new Error(`unsafe output route: ${String(route)}`);
  const root = resolve(outputRoot); const target = resolve(root, route); const rel = relative(root, target);
  if (!rel || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) throw new Error(`output route escapes root: ${route}`);
  return target;
}
export async function writeContainedOutput(outputRoot, route, html) {
  const target = containedOutputPath(outputRoot, route); await mkdir(dirname(target), { recursive: true }); await writeFile(target, html, 'utf8'); return target;
}

export async function renderPublishedObjectPages(loadedInputs, outputRoot) {
  const input = normalizeRendererInputs(loadedInputs); const contexts = buildDriverContexts(input);
  const overviewByObject = new Map(input.overviews.map(row => [row.object_entity_id, row]));

  // Render the complete publication set before the first write. A render-time
  // failure must not leave a partially updated output tree for route-set checks.
  const rendered = publishedObjects(input.entitiesPayload).map(object => {
    const route = pathFor(object.entity_id, input.entitiesPayload);
    const html = renderObjectPage({ object, overview: overviewByObject.get(object.entity_id) ?? null, assertions: input.assertions, evidence: input.evidence, sources: input.sources, statusRules: input.statusRules, entities: input.entities, basePath: BASE_PATH, epistemicContext: contexts.epistemicContext, dependencyRules: input.dependencyRules, taskContext: contexts.taskContext, externalRecordsContext: contexts.externalRecordsContext });
    return { entityId: object.entity_id, route, html };
  });

  for (const page of rendered) page.path = await writeContainedOutput(outputRoot, page.route, page.html);
  return rendered;
}
