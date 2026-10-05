import { escapeHtml } from './render-shell.mjs';

function requireKey(record, key) {
  if (!Object.hasOwn(record, key)) throw new Error(`external record missing ${key}`);
  return record[key];
}

export function buildExternalRecordsContext(records) {
  const byEntity = new Map();
  for (const record of records) {
    const entityId = requireKey(record, 'entity_id');
    const rows = byEntity.get(entityId) || [];
    rows.push(record);
    byEntity.set(entityId, rows);
  }
  return { byEntity };
}

function card(record) {
  const url = requireKey(record, 'url');
  const system = requireKey(record, 'system');
  const label = requireKey(record, 'label');
  const recordType = requireKey(record, 'record_type');
  const identifier = requireKey(record, 'identifier');
  const note = requireKey(record, 'note');
  return `<li class="external-record"><a href="${escapeHtml(url)}">${escapeHtml(system)} — ${escapeHtml(label)}</a><br><span class="small">${escapeHtml(recordType.replaceAll('_', ' '))} · ID ${escapeHtml(identifier)}</span><br><span class="small">${escapeHtml(note)}</span></li>`;
}

export function renderExternalRecords({ objectId, subjectId = null, subjectName = null, context }) {
  const objectRecords = context.byEntity.get(objectId) || [];
  const authorityRecords = subjectId == null ? [] : (context.byEntity.get(subjectId) || []);
  if (objectRecords.length === 0 && authorityRecords.length === 0) return '';

  let groups = '';
  if (objectRecords.length) {
    groups += `<h3>Monument records</h3><ul class="sources">${objectRecords.map(card).join('')}</ul>\n`;
  }
  if (authorityRecords.length) {
    groups += `<h3>${escapeHtml(subjectName)} authority records</h3><ul class="sources">${authorityRecords.map(card).join('')}</ul>\n`;
  }
  return `<section id="external-records"><h2>External records</h2>\n<p>Links to records for this monument, its subject, and related media in other systems. These records do not change assertion status unless a specific statement is reviewed and added to the evidence record.</p>\n${groups}</section>`;
}
