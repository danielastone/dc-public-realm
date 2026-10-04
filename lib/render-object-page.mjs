import { escapeHtml, renderShell } from './render-shell.mjs';
import { renderOverviewResult } from './render-overview.mjs';
import { renderConflictWarning, renderDependencyBlock, renderLineageBlock } from './render-epistemics.mjs';
import { pred, renderResearchMissions } from './render-tasks.mjs';
import { renderExternalRecords } from './render-external-records.mjs';

const DIRECT_ROLES = new Set(['PRIMARY_SUPPORT', 'IMAGE_EVIDENCE']);
const LINEAGE_PREDICATES = new Set(['RECAST_OF', 'COPY_OF', 'DERIVED_FROM_MATERIAL', 'RELIEF_DERIVED_FROM']);

function statusRuleFor(statusRules, status) {
  const rules = statusRules?.rules ?? statusRules;
  return rules instanceof Map ? rules.get(status) : rules?.[status];
}

function assertionValue(assertion, entityById) {
  if (assertion.object_entity_id) {
    return entityById.get(assertion.object_entity_id)?.canonical_name ?? assertion.object_entity_id;
  }
  return Object.hasOwn(assertion, 'literal_value') ? assertion.literal_value : 'Unresolved';
}

function evidenceBlock(edge, sourceById) {
  const source = sourceById.get(edge.source_id);
  if (!source) throw new Error(`Missing source ${edge.source_id}`);
  const role = ({
    PRIMARY_SUPPORT: 'Main source',
    CORROBORATION: 'Additional source',
    QUALIFIES: 'Qualification',
    CONTRADICTS: 'Differing record',
    IMAGE_EVIDENCE: 'Image evidence',
  })[edge.evidence_role] ?? pred(edge.evidence_role);
  const origin = edge.claim_origin ?? 'UNKNOWN';
  const parents = edge.inherits_claim_from_source_ids ?? [];
  let lineage;
  if (origin === 'ORIGINAL_TO_SOURCE') lineage = 'Source history: recorded as originating in this source.';
  else if (origin === 'INHERITED' && parents.length) lineage = `Source history: inherited from ${parents.join(', ')}.`;
  else if (origin === 'MIXED' && parents.length) lineage = `Source history: mixed; includes material inherited from ${parents.join(', ')}.`;
  else if (origin === 'MIXED') lineage = 'Source history: mixed origin; upstream source not yet identified.';
  else lineage = 'Source history: not yet established.';
  return `<div class="source-row"><div class="source-role">${escapeHtml(role)}</div><a href="${escapeHtml(source.url)}">${escapeHtml(source.title)}</a><div class="meta">${escapeHtml(edge.locator ?? 'Record')}</div><div class="meta source-lineage">${escapeHtml(lineage)}</div></div>`;
}

function assertionBlock({ assertion, evidenceRows, sourceById, statusRules, entityById, epistemicContext, dependencyRules, related = false, basePath }) {
  const statusRule = statusRuleFor(statusRules, assertion.computed_status);
  if (!statusRule) throw new Error(`${assertion.assertion_id}: no publication status rule for ${assertion.computed_status}`);
  const sourceCount = new Set(evidenceRows.map(row => row.source_id)).size;
  const idAttribute = related ? 'data-related-assertion-id' : 'data-assertion-id';
  const relatedClass = related ? ' related-assertion' : '';
  const conflictHtml = related ? '' : renderConflictWarning(assertion.assertion_id, epistemicContext.conflicts.get(assertion.assertion_id) || []);
  const epistemicTail = related ? '' : renderDependencyBlock(assertion.assertion_id, evidenceRows, dependencyRules)
    + renderLineageBlock(assertion.assertion_id, evidenceRows, epistemicContext);
  const evidenceHtml = evidenceRows.map(row => evidenceBlock(row, sourceById)).join('');
  const value = assertionValue(assertion, entityById);
  return `<article class="assertion${relatedClass}" ${idAttribute}="${escapeHtml(assertion.assertion_id)}" data-computed-status="${escapeHtml(assertion.computed_status)}" data-status-rule="${escapeHtml(statusRule.rule_id)}">${conflictHtml}<div class="kicker">${escapeHtml(assertion.assertion_id)}</div><h3>${escapeHtml(pred(assertion.predicate))}: ${escapeHtml(value)}</h3><div class="canonical-status status ${escapeHtml(assertion.computed_status)}"><span class="status-label">${escapeHtml(statusRule.public_label)}</span><span class="status-reason">${escapeHtml(assertion.status_reason)}</span><a class="status-rule" href="${escapeHtml(basePath)}/methodology/#rule-${escapeHtml(statusRule.rule_id)}">Why this status? <span class="rule-id">${escapeHtml(statusRule.rule_id)}</span></a></div><details class="evidence" data-evidence-assertion-id="${escapeHtml(assertion.assertion_id)}" data-source-count="${sourceCount}"><summary>Sources · ${sourceCount}</summary>${evidenceHtml}</details>${epistemicTail}</article>`;
}

export function renderObjectPage({ object, overview, assertions, evidence, sources, statusRules, entities, basePath, epistemicContext, dependencyRules, taskContext, externalRecordsContext = null }) {
  if (!object.country) throw new Error(`${object.entity_id}: canonical entity has no country`);
  const sourceById = epistemicContext?.sourceById ?? new Map(sources.map(row => [row.source_id, row]));
  const entityById = new Map(entities.map(row => [row.entity_id, row]));
  const byAssertion = new Map();
  for (const row of evidence) {
    const rows = byAssertion.get(row.assertion_id) || [];
    rows.push(row);
    byAssertion.set(row.assertion_id, rows);
  }

  const renderedAssertions = assertions.map(row => {
    const derived = taskContext?.derivedById?.get(row.assertion_id);
    return derived
      ? { ...row, computed_status: derived.computed_status, status_reason: derived.status_reason }
      : row;
  });
  const directAssertions = renderedAssertions.filter(row => row.subject_id === object.entity_id);
  const predecessorIds = new Set(directAssertions
    .filter(row => LINEAGE_PREDICATES.has(row.predicate))
    .map(row => row.object_entity_id));
  const lineageAssertions = renderedAssertions.filter(row => predecessorIds.has(row.subject_id));

  const overviewResult = overview ? renderOverviewResult(overview, assertions, entities) : { html: '', subjectId: null };
  const directHtml = directAssertions.map(assertion => assertionBlock({
    assertion,
    evidenceRows: byAssertion.get(assertion.assertion_id) || [],
    sourceById,
    statusRules,
    entityById,
    epistemicContext,
    dependencyRules,
    related: false,
    basePath,
  })).join('');
  const lineageHtml = lineageAssertions.length
    ? `<h2>Predecessor and lineage</h2>${lineageAssertions.map(assertion => assertionBlock({
      assertion,
      evidenceRows: byAssertion.get(assertion.assertion_id) || [],
      sourceById,
      statusRules,
      entityById,
      epistemicContext,
      dependencyRules,
      related: true,
      basePath,
    })).join('')}`
    : '';
  const taskSection = renderResearchMissions({ objectId: object.entity_id, taskContext });
  const subjectName = overviewResult.subjectId == null ? null : entityById.get(overviewResult.subjectId)?.canonical_name;
  const externalRecordsHtml = externalRecordsContext
    ? renderExternalRecords({ objectId: object.entity_id, subjectId: overviewResult.subjectId, subjectName, context: externalRecordsContext })
    : '';
  const body = `<div class="kicker" data-object-country="${escapeHtml(object.country)}">${escapeHtml(object.country)} · catalog record</div><h1 data-object-id="${escapeHtml(object.entity_id)}">${escapeHtml(object.canonical_name)}</h1>${overviewResult.html}<p class="lede">Current research record with each statement presented together with its status and supporting sources.</p><p><a href="${escapeHtml(basePath)}/data/">Canonical data</a></p><h2>Record</h2>${directHtml}${lineageHtml}${taskSection}${externalRecordsHtml}`;
  return renderShell({ title: object.canonical_name, body, basePath });
}

// Exported only for contract tests: the renderer must stay data-driven.
export const rendererContract = Object.freeze({ directRoles: [...DIRECT_ROLES] });
