import { deriveDependencyState, traceRow } from './derive-epistemics.mjs';
import { escapeHtml } from './render-shell.mjs';

const LABELS = Object.freeze({
  ESTABLISHED_ROOT: 'Established claim root',
  UNRESOLVED_ANCESTRY: 'Unresolved ancestry',
  BROKEN_REFERENCE: 'Broken lineage reference',
  CYCLE: 'Lineage cycle detected',
});

export class EpistemicRenderError extends Error {
  constructor(stage, condition, detail = '') {
    super(detail ? `${condition}: ${detail}` : condition);
    this.name = 'EpistemicRenderError';
    this.stage = stage;
    this.condition = condition;
  }
}

function esc(value) {
  // Python html.escape(str(x), quote=True) spells None this way.
  return escapeHtml(value === null ? 'None' : value);
}

function terminalNodes(trace) {
  if (trace?.terminal) return [trace];
  const out = [];
  for (const branch of trace?.branches ?? []) out.push(...terminalNodes(branch));
  return out;
}

export function traceSummary(trace) {
  const labels = [];
  for (const node of terminalNodes(trace)) {
    const label = LABELS[node.terminal];
    if (!labels.includes(label)) labels.push(label);
  }
  return labels.join('; ');
}

function ancestryDetail(row) {
  const origin = row.claim_origin || 'UNKNOWN';
  const dependency = row.dependency_status || 'UNKNOWN';
  const inherited = row.inherits_claim_from_source_ids || [];
  const inheritedText = inherited.length
    ? inherited.join(', ')
    : 'none recorded; this does not establish independence';
  return `<dl class="ancestry-state"><dt>Claim origin</dt><dd data-claim-origin="${esc(origin)}">${esc(origin)}</dd><dt>Dependency status</dt><dd data-canonical-dependency-status="${esc(dependency)}">${esc(dependency)}</dd><dt>Inherited claim from</dt><dd data-inherited-source-count="${inherited.length}">${esc(inheritedText)}</dd></dl>`;
}

function ruleFor(rules, state) {
  const rule = rules instanceof Map ? rules.get(state) : rules?.[state];
  if (!rule) throw new EpistemicRenderError('dependency', 'MISSING_DEPENDENCY_RULE', state);
  return rule;
}

export function renderDependencyBlock(assertionId, rows, rules) {
  if (rows.length < 2) return '';
  const items = rows.map(row => {
    const state = deriveDependencyState(row);
    const rule = ruleFor(rules, state);
    return `<li data-assertion-evidence-id="${esc(row.assertion_evidence_id)}" data-source-id="${esc(row.source_id)}" data-dependency-state="${esc(state)}"><strong>${esc(row.source_id)}</strong>: ${esc(rule.public_label)}. ${esc(rule.explanation)}${ancestryDetail(row)}</li>`;
  }).join('');
  return `<details class="evidence-independence" data-for-assertion-id="${esc(assertionId)}"><summary>Source relationship</summary><p>Corroboration is not automatically independent. Claim origin and dependency status below reproduce the canonical ancestry state; UNKNOWN means the project has not established that part of the lineage.</p><ul>${items}</ul></details>`;
}

function lineageItem(row, context) {
  const source = context.sourceById.get(row.source_id);
  if (!source) {
    throw new EpistemicRenderError(
      'lineage',
      'MISSING_SOURCE_RECORD',
      `${row.assertion_evidence_id}: source ${row.source_id} missing from sources.json`,
    );
  }
  const trace = traceRow(row, context.lineageIndex);
  const parents = row.inherits_claim_from_source_ids || [];
  const parentText = parents.length ? parents.join(', ') : 'none recorded';
  const evidenceNote = row.evidence_note || 'No evidence note recorded.';
  const inheritanceNote = row.inheritance_note || 'No inheritance note recorded.';
  const locator = row.locator || 'no locator recorded';
  const role = row.evidence_role || 'UNSPECIFIED';
  const label = `${source.source_id} — ${source.title || 'Untitled source'}`;
  const sourceHtml = source.url ? `<a href="${esc(source.url)}">${esc(label)}</a>` : esc(label);
  const summary = traceSummary(trace);
  return `<li class="claim-lineage-evidence" data-assertion-evidence-id="${esc(row.assertion_evidence_id)}" data-source-id="${esc(row.source_id)}" data-lineage-terminal="${esc(summary)}"><div><strong>${esc(row.assertion_evidence_id)}</strong> · ${esc(role)}</div><div>Source: ${sourceHtml}</div><div>Locator: ${esc(locator)}</div><div>Evidence note: ${esc(evidenceNote)}</div><div>Direct inherited claim source(s): ${esc(parentText)}</div><div>Lineage terminus: <strong>${esc(summary)}</strong></div><div class="small">Inheritance note: ${esc(inheritanceNote)}</div></li>`;
}

export function renderLineageBlock(assertionId, rows, context) {
  if (!rows.length) return '';
  const items = rows.map(row => lineageItem(row, context)).join('');
  return `<details class="claim-lineage" data-for-assertion-id="${esc(assertionId)}"><summary>Trace this claim</summary><p>Assertion <strong>${esc(assertionId)}</strong>. This trace follows claim ancestry, not merely document provenance. An unresolved terminus means the project has not established the upstream claim root.</p><ol>${items}</ol></details>`;
}

export function renderConflictWarning(assertionId, rows) {
  if (!rows.length) return '';
  const items = rows.map(row =>
    `<li data-conflict-evidence-id="${esc(row.assertion_evidence_id)}" data-source-id="${esc(row.source_id)}"><strong>${esc(row.source_id)}</strong>, ${esc(row.locator)}: ${esc(row.evidence_note)}</li>`
  ).join('');
  return `<aside class="material-conflict" data-conflict-assertion-id="${esc(assertionId)}" role="note"><strong>Conflicting evidence.</strong> The canonical record contains evidence that contradicts this assertion. The displayed value should not be read as uncontested.<ul>${items}</ul></aside>`;
}

export function renderEpistemics(assertionId, rows, dependencyRules, context) {
  return renderConflictWarning(assertionId, context.conflicts.get(assertionId) || [])
    + renderDependencyBlock(assertionId, rows, dependencyRules)
    + renderLineageBlock(assertionId, rows, context);
}
