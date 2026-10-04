import { escapeHtml } from './render-shell.mjs';
import { computeStatus } from './status.mjs';

const BASE = '/dc-public-realm';
const REPO = 'https://github.com/danielastone/dc-public-realm';

export class TaskRenderError extends Error {
  constructor(stage, condition, field, detail = '') {
    super(`task renderer ${stage}: ${condition}${field ? ` ${field}` : ''}${detail ? ` (${detail})` : ''}`);
    this.name = 'TaskRenderError';
    this.stage = stage;
    this.condition = condition;
    this.field = field;
  }
}

function requireKey(row, field, stage) {
  if (!Object.hasOwn(row, field)) throw new TaskRenderError(stage, 'MISSING_REQUIRED_FIELD', field);
  return row[field];
}

export function pred(value) {
  return String(value).replaceAll('_', ' ').replace(/\b\w/g, char => char.toUpperCase());
}

export function publicStatus(status) {
  return ({
    VERIFIED: 'Verified',
    SUPPORTED: 'Supported',
    CONTESTED: 'Sources differ',
    UNRESOLVED: 'Unresolved',
    UNSUPPORTED: 'Not established',
  })[status] ?? pred(status);
}

// Python urllib.parse.quote_plus semantics used by urlencode here: unreserved
// ASCII including ~ stays literal, space becomes +, and * ' ( ) are escaped.
export function quotePlus(value) {
  const bytes = new TextEncoder().encode(String(value));
  let out = '';
  for (const byte of bytes) {
    const unreserved = (byte >= 0x41 && byte <= 0x5a)
      || (byte >= 0x61 && byte <= 0x7a)
      || (byte >= 0x30 && byte <= 0x39)
      || byte === 0x5f || byte === 0x2e || byte === 0x2d || byte === 0x7e;
    if (unreserved) out += String.fromCharCode(byte);
    else if (byte === 0x20) out += '+';
    else out += `%${byte.toString(16).toUpperCase().padStart(2, '0')}`;
  }
  return out;
}

function taskUrl(task) {
  const taskId = requireKey(task, 'task_id', 'taskurl');
  const title = requireKey(task, 'title', 'taskurl');
  const repository = requireKey(task, 'repository', 'taskurl');
  const collection = requireKey(task, 'collection', 'taskurl');
  const body = `Task: ${taskId}\nTask URL: https://danielastone.github.io/dc-public-realm/tasks/${String(taskId).toLowerCase()}/\n\nRepository: ${repository}\nCollection: ${collection}\n\nFindings:\n\nCitations:\n\nFiles/images/links:\n`;
  return `${REPO}/issues/new?title=${quotePlus(`${taskId} - ${title}`)}&body=${quotePlus(body)}`;
}

function deriveAssertions(assertions, evidence, predicateRules) {
  const byAssertion = new Map();
  for (const row of evidence) {
    const rows = byAssertion.get(row.assertion_id) || [];
    rows.push(row);
    byAssertion.set(row.assertion_id, rows);
  }
  return assertions.map(assertion => {
    const rule = predicateRules[assertion.predicate];
    if (!rule) throw new TaskRenderError('status', 'MISSING_PREDICATE_RULE', 'predicate', assertion.predicate);
    const [computedStatus] = computeStatus(assertion, byAssertion.get(assertion.assertion_id) || [], rule);
    return { ...assertion, computed_status: computedStatus };
  });
}

function targetLabel(target, derivedById) {
  if (target.assertion_id) {
    const assertion = derivedById.get(target.assertion_id);
    return assertion
      ? `${target.assertion_id} · ${pred(assertion.predicate)} · ${publicStatus(assertion.computed_status)}`
      : target.assertion_id;
  }
  return `Potential new proposition: ${target.proposition ?? ''}`;
}

function targetBlock(target, derivedById) {
  const desiredEvidence = requireKey(target, 'desired_evidence', 'targetblock');
  const desiredEffect = requireKey(target, 'desired_effect', 'targetblock');
  return `<li><strong>${escapeHtml(targetLabel(target, derivedById))}</strong><br><span class="meta">Requested evidence: ${escapeHtml(pred(desiredEvidence))}. Possible effect after review: ${escapeHtml(pred(desiredEffect))}.</span></li>`;
}

function taskBlock(task, derivedById) {
  const taskId = requireKey(task, 'task_id', 'taskblock');
  const title = requireKey(task, 'title', 'taskblock');
  const researchGap = requireKey(task, 'research_gap', 'taskblock');
  const highValueResult = requireKey(task, 'high_value_result', 'taskblock');
  const repository = requireKey(task, 'repository', 'taskblock');
  const collection = requireKey(task, 'collection', 'taskblock');
  const criticalRule = requireKey(task, 'critical_rule', 'taskblock');
  const status = requireKey(task, 'status', 'taskblock');
  const targets = (task.epistemic_targets ?? []).map(target => targetBlock(target, derivedById)).join('');
  const slug = escapeHtml(String(taskId).toLowerCase());
  return `<article class="task"><div class="kicker">Research mission · ${escapeHtml(status)}</div><h3><a href="${BASE}/tasks/${slug}/">${escapeHtml(title)}</a></h3><p>${escapeHtml(researchGap)}</p><p><strong>Requested result:</strong> ${escapeHtml(highValueResult)}</p><details><summary>Research details</summary><h4>Record affected</h4><ul>${targets}</ul><p class="meta"><strong>Repository:</strong> ${escapeHtml(repository)}<br><strong>Collection:</strong> ${escapeHtml(collection)}</p><p class="meta"><strong>Evidence requirement:</strong> ${escapeHtml(criticalRule)}</p></details><a class="button" href="${BASE}/tasks/${slug}/">Mission details</a><a class="button" href="${escapeHtml(taskUrl(task))}">Submit a finding</a></article>`;
}

export function buildOpenTasksByObject(tasks) {
  const byObject = new Map();
  for (const task of tasks) {
    if (task.status !== 'OPEN') continue;
    const objectId = requireKey(task, 'object_entity_id', 'open-task-index');
    const rows = byObject.get(objectId) || [];
    rows.push(task);
    byObject.set(objectId, rows);
  }
  return byObject;
}

export function renderResearchMissions({ objectId, openTasksByObject, assertions, evidence, predicateRules }) {
  const tasks = openTasksByObject.get(objectId) || [];
  if (!tasks.length) return '<h2>Research missions</h2><p class="task-summary" data-open-task-count="0">0 open research missions</p><p>There are no open research missions for this catalog record.</p>';
  const derived = deriveAssertions(assertions, evidence, predicateRules);
  const derivedById = new Map(derived.map(row => [row.assertion_id, row]));
  const count = tasks.length;
  return `<h2>Research missions</h2><p class="task-summary" data-open-task-count="${count}">${count} open research mission${count !== 1 ? 's' : ''}</p><p>These missions identify records that could clarify or qualify this catalog record.</p>${tasks.map(task => taskBlock(task, derivedById)).join('')}`;
}
