import { escapeHtml, renderShell } from './render-shell.mjs';

const DIRECT_ROLES = new Set(['PRIMARY_SUPPORT', 'IMAGE_EVIDENCE']);

function titleCase(value) {
  return String(value).replaceAll('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function publicStatus(status) {
  return ({ VERIFIED: 'Verified', SUPPORTED: 'Supported', CONTESTED: 'Sources differ', UNRESOLVED: 'Unresolved', UNSUPPORTED: 'Not established' })[status] ?? titleCase(status);
}

function evidenceBlock(edge, sourceById) {
  const source = sourceById.get(edge.source_id);
  if (!source) throw new Error(`Missing source ${edge.source_id}`);
  const role = ({ PRIMARY_SUPPORT: 'Main source', CORROBORATION: 'Additional source', QUALIFIES: 'Qualification', CONTRADICTS: 'Differing record', IMAGE_EVIDENCE: 'Image evidence' })[edge.evidence_role] ?? titleCase(edge.evidence_role);
  const parents = edge.inherits_claim_from_source_ids ?? [];
  let lineage;
  if (edge.claim_origin === 'ORIGINAL') lineage = 'Source history: this source presents the claim directly.';
  else if (edge.claim_origin === 'INHERITED') lineage = parents.length ? `Source history: inherits this claim from ${parents.join(', ')}.` : 'Source history: inherited; upstream source not yet identified.';
  else if (edge.claim_origin === 'MIXED') lineage = 'Source history: mixed origin; upstream source not yet identified.';
  else lineage = 'Source history: not yet established.';
  return `<div class="source-row"><div class="source-role">${escapeHtml(role)}</div><a href="${escapeHtml(source.url)}">${escapeHtml(source.title)}</a><div class="meta">${escapeHtml(edge.locator ?? 'Record')}</div><div class="meta source-lineage">${escapeHtml(lineage)}</div></div>`;
}

function assertionBlock(assertion, evidence, sourceById, statusRules, entityById) {
  const rows = evidence.filter(row => row.assertion_id === assertion.assertion_id);
  const sourceCount = new Set(rows.map(row => row.source_id)).size;
  const statusRule = statusRules.get(assertion.computed_status);
  if (!statusRule) throw new Error(`${assertion.assertion_id}: no publication status rule for ${assertion.computed_status}`);
  const value = assertion.object_entity_id ? (entityById.get(assertion.object_entity_id)?.canonical_name ?? assertion.object_entity_id) : (assertion.literal_value ?? 'Unresolved');
  const evidenceHtml = rows.map(row => evidenceBlock(row, sourceById)).join('');
  return `<article class="assertion ${escapeHtml(assertion.computed_status)}" data-assertion-id="${escapeHtml(assertion.assertion_id)}" data-computed-status="${escapeHtml(assertion.computed_status)}" data-status-rule="${escapeHtml(statusRule.rule_id)}"><div class="kicker">${escapeHtml(titleCase(assertion.predicate))}</div><h3>${escapeHtml(value)}</h3><div class="status"><span class="status-label">${escapeHtml(publicStatus(assertion.computed_status))}</span><span class="status-reason">${escapeHtml(assertion.status_reason)}</span></div><details class="evidence"><summary>${sourceCount} source${sourceCount === 1 ? '' : 's'}</summary>${evidenceHtml}</details></article>`;
}

export function renderObjectPage({ object, assertions, evidence, sources, statusRules, entities, basePath, overviewHtml = '', epistemicsByAssertion = new Map(), taskHtml = '' }) {
  const sourceById = new Map(sources.map(row => [row.source_id, row]));
  const entityById = new Map(entities.map(row => [row.entity_id, row]));
  const statusRuleByStatus = new Map(statusRules.map(row => [row.status, row]));
  const related = assertions.filter(row => row.subject_id === object.entity_id);
  const assertionHtml = related.map(row => {
    const base = assertionBlock(row, evidence, sourceById, statusRuleByStatus, entityById);
    const extra = epistemicsByAssertion.get(row.assertion_id) ?? '';
    return extra ? base.replace('</article>', `${extra}</article>`) : base;
  }).join('');
  const body = `<div class="kicker">${escapeHtml(object.country)}</div><h1>${escapeHtml(object.canonical_name)}</h1>${overviewHtml}${assertionHtml}${taskHtml}`;
  return renderShell({ title: object.canonical_name, body, basePath });
}

// Exported only for contract tests: the renderer must stay data-driven.
export const rendererContract = Object.freeze({ directRoles: [...DIRECT_ROLES] });
