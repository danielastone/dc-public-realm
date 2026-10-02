// Pure assertion-status rule. No I/O, no DOM, no publication side effects.
// Behavioral oracle: tests/fixtures/golden-assertion-status.json.

const POSITIVE_ROLES = new Set(['PRIMARY_SUPPORT', 'IMAGE_EVIDENCE', 'CORROBORATION']);
const DIRECT_ROLES = new Set(['PRIMARY_SUPPORT', 'IMAGE_EVIDENCE']);

export function qualifying(rule, evidence) {
  const direct = evidence.filter(e => DIRECT_ROLES.has(e.evidence_role) && e.authority_fit === 'DIRECT');
  switch (rule.standard) {
    case 'CONTEMPORANEOUS_OR_CONSTITUTIVE':
      return direct.some(e => ['CONTEMPORANEOUS_PRIMARY', 'CONSTITUTIVE_REGISTRY_RECORD'].includes(e.proximity));
    case 'CURRENT_ADMINISTRATIVE':
      return direct.some(e => e.proximity === 'CURRENT_ADMINISTRATIVE_RECORD');
    case 'CONSTITUTIVE_REGISTRY':
      return direct.some(e => e.proximity === 'CONSTITUTIVE_REGISTRY_RECORD');
    case 'OBJECT_LINEAGE':
      return direct.some(e => e.proximity === 'CONTEMPORANEOUS_PRIMARY');
    default:
      return false;
  }
}

export function effectiveRoots(edge, bySource, visiting = new Set()) {
  const seen = new Set(visiting);
  const sid = edge.source_id;
  if (seen.has(sid)) return null;
  seen.add(sid);
  const origin = edge.claim_origin;
  const parents = edge.inherits_claim_from_source_ids || [];
  if (origin === 'UNKNOWN') return null;
  if (origin === 'ORIGINAL_TO_SOURCE') return new Set([sid]);
  if (!['INHERITED', 'MIXED'].includes(origin)) return null;
  const roots = origin === 'MIXED' ? new Set([sid]) : new Set();
  for (const parent of parents) {
    const parentEdge = bySource.get(parent);
    if (!parentEdge) {
      roots.add(parent);
      continue;
    }
    const parentRoots = effectiveRoots(parentEdge, bySource, seen);
    if (parentRoots === null) return null;
    for (const root of parentRoots) roots.add(root);
  }
  return roots.size ? roots : null;
}

export function independentlyCorroborated(evidence) {
  const bySource = new Map(evidence.map(e => [e.source_id, e]));
  const direct = evidence.filter(e => DIRECT_ROLES.has(e.evidence_role) && e.authority_fit === 'DIRECT');
  const corroboration = evidence.filter(e => e.evidence_role === 'CORROBORATION' && ['DIRECT', 'SUPPORTING'].includes(e.authority_fit));
  for (const x of direct) {
    const xr = effectiveRoots(x, bySource);
    if (xr === null) continue;
    for (const y of corroboration) {
      const yr = effectiveRoots(y, bySource);
      if (x.source_id === y.source_id || yr === null) continue;
      if ([...xr].every(root => !yr.has(root))) return true;
    }
  }
  return false;
}

export function computeStatus(assertion, evidence, rule) {
  const hasObject = Boolean(assertion.object_entity_id);
  const hasLiteral = Object.prototype.hasOwnProperty.call(assertion, 'literal_value');
  if (!hasObject && !hasLiteral && evidence.some(e => e.evidence_role === 'QUALIFIES')) {
    return ['UNRESOLVED', 'An authoritative source records the value as unresolved.'];
  }
  if (evidence.some(e => POSITIVE_ROLES.has(e.evidence_role)) && evidence.some(e => e.evidence_role === 'CONTRADICTS')) {
    return ['CONTESTED', 'The reviewed sources differ materially on this statement.'];
  }
  if (rule.single_source_can_verify && qualifying(rule, evidence)) {
    return ['VERIFIED', 'A directly authoritative source meets the evidence rule for this statement.'];
  }
  if (independentlyCorroborated(evidence)) {
    return ['VERIFIED', 'Direct support is independently corroborated.'];
  }
  if (evidence.some(e => POSITIVE_ROLES.has(e.evidence_role))) {
    return ['SUPPORTED', 'Credible evidence supports the statement, but the verification threshold is not met.'];
  }
  return !hasObject && !hasLiteral
    ? ['UNRESOLVED', 'No resolved value is established.']
    : ['UNSUPPORTED', 'No adequate positive evidence is recorded.'];
}
