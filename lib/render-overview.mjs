import { escapeHtml } from './render-shell.mjs';

export class OverviewReconciliationError extends Error {
  constructor(site, message) {
    super(message);
    this.name = new.target.name;
    this.site = site;
  }
}

export class MissingAssertionReferenceError extends OverviewReconciliationError {}
export class MissingCanonicalAssertionError extends OverviewReconciliationError {}
export class AssertionSubjectMismatchError extends OverviewReconciliationError {}
export class LiteralMismatchError extends OverviewReconciliationError {}
export class NoncanonicalObjectError extends OverviewReconciliationError {}
export class IncompleteImageRightsError extends OverviewReconciliationError {}
export class SubjectDateSubjectsDisagreeError extends OverviewReconciliationError {}
export class SubjectNameMismatchError extends OverviewReconciliationError {}
export class SubjectDateCardinalityError extends OverviewReconciliationError {}
export class SubjectDatesMismatchError extends OverviewReconciliationError {}
export class UnknownRecordTypeError extends OverviewReconciliationError {}
export class MissingRequiredFieldError extends OverviewReconciliationError {}

function assertionMap(assertions) {
  if (assertions instanceof Map) return assertions;
  return new Map(assertions.map(row => [row.assertion_id, row]));
}

function entityMap(entities) {
  if (entities instanceof Map) return entities;
  return new Map(entities.map(row => [row.entity_id, row]));
}

function requiredField(record, field) {
  if (!Object.prototype.hasOwnProperty.call(record, field)) {
    throw new MissingRequiredFieldError(`implicit:${field}`, `missing required field ${field}`);
  }
  return record[field];
}

/**
 * Pure JS counterpart of scripts/overview_renderer.py:render_overview().
 * Reconciliation remains at the renderer boundary even though materialization
 * validates upstream data. Explicit typed errors carry the frozen Python
 * raise-site IDs from tests/overview-error-inventory.mjs; implicit Python
 * KeyError/TypeError aborts use "implicit:<field>" site IDs.
 */
export function renderOverview(overview, assertions, entities) {
  const byAssertion = assertionMap(assertions);
  const byEntity = entityMap(entities);
  const oid = requiredField(overview, 'object_entity_id');

  function refs(field) {
    const raw = overview.assertion_refs?.[field];
    const ids = Array.isArray(raw) ? raw : (raw ? [raw] : []);
    if (ids.length === 0) {
      throw new MissingAssertionReferenceError('refs#1', `${oid}.${field}: displayed fact has no assertion reference`);
    }
    const missing = ids.filter(id => !byAssertion.has(id));
    if (missing.length) {
      throw new MissingCanonicalAssertionError('refs#2', `${oid}.${field}: missing canonical assertions ${missing.join(', ')}`);
    }
    return ids;
  }

  function requireSubject(field, subject) {
    const ids = refs(field);
    if (ids.some(id => byAssertion.get(id)?.subject_id !== subject)) {
      throw new AssertionSubjectMismatchError('require_subject#1', `${oid}.${field}: assertion subject mismatch`);
    }
    return ids;
  }

  const attr = ids => escapeHtml(ids.join(','));

  function fact(field, label, value, url) {
    const ids = requireSubject(field, oid);
    if (ids.length !== 1 || byAssertion.get(ids[0])?.literal_value !== value) {
      throw new LiteralMismatchError('fact#1', `${oid}.${field}: displayed value does not reconcile to canonical assertion`);
    }
    return `<div data-assertion-ids="${attr(ids)}"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)} <a class="overview-source" href="${escapeHtml(url)}" aria-label="Source for ${escapeHtml(label)}">Source</a></dd></div>`;
  }

  if (!byEntity.has(oid)) {
    throw new NoncanonicalObjectError('render_overview#1', `${oid}: overview object is not a canonical entity`);
  }
  if (!['image_url', 'image_alt', 'image_credit', 'image_rights', 'image_source_url'].every(key => overview[key])) {
    throw new IncompleteImageRightsError('render_overview#2', `${oid}: incomplete image rights metadata`);
  }

  let rights = escapeHtml(overview.image_rights);
  if (overview.image_license_url) rights = `<a href="${escapeHtml(overview.image_license_url)}">${rights}</a>`;
  const figure = `<figure class="record-photo"><img src="${escapeHtml(overview.image_url)}" alt="${escapeHtml(overview.image_alt)}" loading="eager"><figcaption>${escapeHtml(overview.image_credit)} · ${rights} · <a href="${escapeHtml(overview.image_source_url)}">Image record</a></figcaption></figure>`;

  const location = requiredField(overview, 'location');
  const locationSourceUrl = requiredField(overview, 'location_source_url');
  let facts = fact('location', 'Location', location, locationSourceUrl);

  const eventLabel = requiredField(overview, 'event_label');
  const eventDate = requiredField(overview, 'event_date');
  const eventSourceUrl = requiredField(overview, 'event_source_url');
  facts += fact('event_date', eventLabel, eventDate, eventSourceUrl);

  if (overview.secondary_event_label) {
    const secondaryEventDate = requiredField(overview, 'secondary_event_date');
    const secondaryEventSourceUrl = requiredField(overview, 'secondary_event_source_url');
    facts += fact('secondary_event_date', overview.secondary_event_label, secondaryEventDate, secondaryEventSourceUrl);
  }

  const recordType = requiredField(overview, 'record_type');
  let intro;
  if (recordType === 'person_memorial') {
    const dateIds = refs('subject_dates');
    const subjects = new Set(dateIds.map(id => byAssertion.get(id)?.subject_id));
    if (subjects.size !== 1) {
      throw new SubjectDateSubjectsDisagreeError('render_overview#3', `${oid}.subject_dates: assertion subjects disagree`);
    }
    const sid = subjects.values().next().value;
    const person = byEntity.get(sid);
    const subjectName = requiredField(overview, 'subject_name');
    if (!person || person.entity_type !== 'Person' || person.canonical_name !== subjectName) {
      throw new SubjectNameMismatchError('render_overview#4', `${oid}.subject_name: does not reconcile to canonical person`);
    }
    if (dateIds.length !== 2) {
      throw new SubjectDateCardinalityError('render_overview#5', `${oid}.subject_dates: expected birth and death assertions`);
    }
    const dateValues = dateIds.map(id => {
      const assertion = byAssertion.get(id);
      const value = Object.prototype.hasOwnProperty.call(assertion, 'literal_value') ? assertion.literal_value : '';
      if (typeof value !== 'string') {
        throw new MissingRequiredFieldError('implicit:literal_value', `${id}: literal_value cannot participate in Python string join`);
      }
      return value;
    });
    const dates = dateValues.join('–');
    const subjectDates = requiredField(overview, 'subject_dates');
    if (dates !== subjectDates) {
      throw new SubjectDatesMismatchError('render_overview#6', `${oid}.subject_dates: does not reconcile to canonical assertions`);
    }
    const bioIds = requireSubject('subject_bio', sid);
    const subjectBio = requiredField(overview, 'subject_bio');
    const subjectSourceUrl = requiredField(overview, 'subject_source_url');
    facts += `<div data-assertion-ids="${attr(dateIds)}"><dt>Subject</dt><dd><strong>${escapeHtml(person.canonical_name)}</strong> (${escapeHtml(dates)})</dd></div>`;
    intro = `<section class="record-introduction" data-assertion-ids="${attr(bioIds)}" aria-labelledby="record-introduction-heading"><h2 id="record-introduction-heading">About the memorial</h2><p>${escapeHtml(subjectBio)} <a class="overview-source" href="${escapeHtml(subjectSourceUrl)}">Source</a></p></section>`;
  } else if (recordType === 'historical_object') {
    const ids = requireSubject('object_context', oid);
    const objectContext = requiredField(overview, 'object_context');
    const objectContextSourceUrl = requiredField(overview, 'object_context_source_url');
    intro = `<section class="record-introduction" data-assertion-ids="${attr(ids)}" aria-labelledby="record-introduction-heading"><h2 id="record-introduction-heading">About the object</h2><p>${escapeHtml(objectContext)} <a class="overview-source" href="${escapeHtml(objectContextSourceUrl)}">Source</a></p></section>`;
  } else {
    throw new UnknownRecordTypeError('render_overview#7', `${oid}: unknown record_type ${recordType}`);
  }

  return `<section class="record-overview" data-object-entity-id="${escapeHtml(oid)}" aria-label="Object overview">${figure}<div class="record-facts"><dl>${facts}</dl>${intro}</div></section>`;
}
