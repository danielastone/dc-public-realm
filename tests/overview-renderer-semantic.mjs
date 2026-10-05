import fs from 'node:fs';
import assert from 'node:assert/strict';

import { publishedObjects } from '../lib/publication-index.mjs';
import { escapeHtml } from '../lib/render-shell.mjs';
import { renderObjectPage } from '../lib/render-object-page.mjs';
import {
  renderOverview,
  MissingAssertionReferenceError,
  MissingCanonicalAssertionError,
  AssertionSubjectMismatchError,
  LiteralMismatchError,
  NoncanonicalObjectError,
  IncompleteImageRightsError,
  SubjectDateSubjectsDisagreeError,
  SubjectNameMismatchError,
  SubjectDateCardinalityError,
  SubjectDatesMismatchError,
  UnknownRecordTypeError,
  MissingRequiredFieldError,
} from '../lib/render-overview.mjs';
import { OVERVIEW_ERROR_CONDITIONS } from './overview-error-inventory.mjs';

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function clone(value) {
  return structuredClone(value);
}

function countOccurrences(text, needle) {
  return text.split(needle).length - 1;
}

const entitiesPayload = readJson('build/data/entities.json');
const assertionsPayload = readJson('build/data/assertions.json');
const overviewsPayload = readJson('build/data/object-overviews.json');

const entities = entitiesPayload.entities;
const assertions = assertionsPayload.assertions;
const overviews = overviewsPayload.object_overviews;
const overviewsByObject = new Map(overviews.map(row => [row.object_entity_id, row]));

const published = publishedObjects(entitiesPayload);
let reconciledObjects = 0;
for (const object of published) {
  const overview = overviewsByObject.get(object.entity_id);
  assert.ok(overview, `${object.entity_id}: published object must have a materialized overview for the current corpus`);
  const html = renderOverview(overview, assertions, entities);

  const displayedFactCount = Object.keys(overview.assertion_refs ?? {}).length;
  assert.equal(
    countOccurrences(html, 'data-assertion-ids='),
    displayedFactCount,
    `${object.entity_id}: rendered assertion-backed structures must match the materialized assertion_refs fact list`,
  );
  const displayedFields = [
    'object_entity_id',
    'location',
    'location_source_url',
    'event_label',
    'event_date',
    'event_source_url',
    'image_url',
    'image_alt',
    'image_credit',
    'image_rights',
    'image_source_url',
  ];
  if (overview.image_license_url) displayedFields.push('image_license_url');
  if (overview.secondary_event_label) {
    displayedFields.push('secondary_event_label', 'secondary_event_date', 'secondary_event_source_url');
  }
  if (overview.record_type === 'person_memorial') {
    displayedFields.push('subject_name', 'subject_dates', 'subject_bio', 'subject_source_url');
  } else if (overview.record_type === 'historical_object') {
    displayedFields.push('object_context', 'object_context_source_url');
  }

  for (const field of displayedFields) {
    const value = overview[field];
    assert.notEqual(value, undefined, `${object.entity_id}: displayed field ${field} must exist in materialized overview`);
    assert.ok(
      html.includes(escapeHtml(value)),
      `${object.entity_id}: rendered overview must contain materialized field ${field}`,
    );
  }
  reconciledObjects += 1;
}

// Optional-overview behavior: use a real published object, deliberately remove
// its matched overview, and ensure the page still renders without an overview.
const objectWithoutOverview = published[0];
const pageWithoutOverview = renderObjectPage({
  object: objectWithoutOverview,
  overview: undefined,
  assertions: [],
  evidence: [],
  sources: [],
  statusRules: [],
  entities,
  basePath: '/dc-public-realm',
  taskContext: { openTasksByObject: new Map(), derivedById: new Map() },
});
assert.ok(!pageWithoutOverview.includes('class="record-overview"'), 'object without overview must render no overview section');

const validHistorical = {
  overview: {
    object_entity_id: 'OBJ-T',
    record_type: 'historical_object',
    location: 'Test Place',
    location_source_url: 'https://example.test/location',
    event_label: 'Presented',
    event_date: '1928',
    event_source_url: 'https://example.test/event',
    object_context: 'Context.',
    object_context_source_url: 'https://example.test/context',
    image_url: 'https://example.test/image.jpg',
    image_alt: 'Test image',
    image_credit: 'Test credit',
    image_rights: 'Public domain',
    image_source_url: 'https://example.test/image-record',
    assertion_refs: {
      location: ['H-LOC'],
      event_date: ['H-EVENT'],
      object_context: ['H-CONTEXT'],
    },
  },
  assertions: [
    { assertion_id: 'H-LOC', subject_id: 'OBJ-T', literal_value: 'Test Place' },
    { assertion_id: 'H-EVENT', subject_id: 'OBJ-T', literal_value: '1928' },
    { assertion_id: 'H-CONTEXT', subject_id: 'OBJ-T', literal_value: 'Context.' },
  ],
  entities: [
    { entity_id: 'OBJ-T', entity_type: 'PhysicalObject', canonical_name: 'Test Object' },
  ],
};

const validMemorial = {
  overview: {
    object_entity_id: 'OBJ-M',
    record_type: 'person_memorial',
    location: 'Memorial Place',
    location_source_url: 'https://example.test/location',
    event_label: 'Dedicated',
    event_date: '1950',
    event_source_url: 'https://example.test/event',
    subject_name: 'Test Person',
    subject_dates: '1900–1980',
    subject_bio: 'Biography.',
    subject_source_url: 'https://example.test/person',
    image_url: 'https://example.test/image.jpg',
    image_alt: 'Memorial image',
    image_credit: 'Test credit',
    image_rights: 'Public domain',
    image_source_url: 'https://example.test/image-record',
    assertion_refs: {
      location: ['M-LOC'],
      event_date: ['M-EVENT'],
      subject_dates: ['M-BIRTH', 'M-DEATH'],
      subject_bio: ['M-BIO'],
    },
  },
  assertions: [
    { assertion_id: 'M-LOC', subject_id: 'OBJ-M', literal_value: 'Memorial Place' },
    { assertion_id: 'M-EVENT', subject_id: 'OBJ-M', literal_value: '1950' },
    { assertion_id: 'M-BIRTH', subject_id: 'P-1', literal_value: '1900' },
    { assertion_id: 'M-DEATH', subject_id: 'P-1', literal_value: '1980' },
    { assertion_id: 'M-BIO', subject_id: 'P-1', literal_value: 'Biography.' },
  ],
  entities: [
    { entity_id: 'OBJ-M', entity_type: 'PhysicalObject', canonical_name: 'Test Memorial' },
    { entity_id: 'P-1', entity_type: 'Person', canonical_name: 'Test Person' },
  ],
};

// Prove both base fixtures are valid before deriving one-change failures.
renderOverview(validHistorical.overview, validHistorical.assertions, validHistorical.entities);
renderOverview(validMemorial.overview, validMemorial.assertions, validMemorial.entities);

const explicitCases = [
  {
    site: 'refs#1',
    ErrorClass: MissingAssertionReferenceError,
    base: validHistorical,
    mutate(x) { delete x.overview.assertion_refs.location; },
  },
  {
    site: 'refs#2',
    ErrorClass: MissingCanonicalAssertionError,
    base: validHistorical,
    mutate(x) { x.overview.assertion_refs.location = ['MISSING']; },
  },
  {
    site: 'require_subject#1',
    ErrorClass: AssertionSubjectMismatchError,
    base: validHistorical,
    mutate(x) { x.assertions.find(a => a.assertion_id === 'H-CONTEXT').subject_id = 'OTHER'; },
  },
  {
    site: 'fact#1',
    ErrorClass: LiteralMismatchError,
    base: validHistorical,
    mutate(x) { x.overview.location = 'Different Place'; },
  },
  {
    site: 'render_overview#1',
    ErrorClass: NoncanonicalObjectError,
    base: validHistorical,
    mutate(x) { x.entities = []; },
  },
  {
    site: 'render_overview#2',
    ErrorClass: IncompleteImageRightsError,
    base: validHistorical,
    mutate(x) { x.overview.image_url = ''; },
  },
  {
    site: 'render_overview#3',
    ErrorClass: SubjectDateSubjectsDisagreeError,
    base: validMemorial,
    mutate(x) { x.assertions.find(a => a.assertion_id === 'M-DEATH').subject_id = 'P-2'; },
  },
  {
    site: 'render_overview#4',
    ErrorClass: SubjectNameMismatchError,
    base: validMemorial,
    mutate(x) { x.overview.subject_name = 'Wrong Person'; },
  },
  {
    site: 'render_overview#5',
    ErrorClass: SubjectDateCardinalityError,
    base: validMemorial,
    mutate(x) { x.overview.assertion_refs.subject_dates = ['M-BIRTH']; },
  },
  {
    site: 'render_overview#6',
    ErrorClass: SubjectDatesMismatchError,
    base: validMemorial,
    mutate(x) { x.overview.subject_dates = '1900–1981'; },
  },
  {
    site: 'render_overview#7',
    ErrorClass: UnknownRecordTypeError,
    base: validHistorical,
    mutate(x) { x.overview.record_type = 'unknown_type'; },
  },
];

const observedExplicitSites = new Set();
for (const testCase of explicitCases) {
  const fixture = clone(testCase.base);
  testCase.mutate(fixture);
  let caught;
  try {
    renderOverview(fixture.overview, fixture.assertions, fixture.entities);
  } catch (error) {
    caught = error;
  }
  assert.ok(caught instanceof testCase.ErrorClass, `${testCase.site}: wrong error subclass: ${caught?.constructor?.name ?? 'none'}`);
  assert.equal(caught.site, testCase.site, `${testCase.site}: wrong site ID`);
  observedExplicitSites.add(caught.site);
}

const declaredExplicitSites = new Set(OVERVIEW_ERROR_CONDITIONS.map(row => row.site));
const uncoveredExplicitSites = [...declaredExplicitSites].filter(site => !observedExplicitSites.has(site));
assert.deepEqual(uncoveredExplicitSites, [], `explicit overview error coverage incomplete: ${uncoveredExplicitSites.join(', ')}`);

const implicitCases = [
  {
    site: 'implicit:event_label',
    base: validHistorical,
    mutate(x) { delete x.overview.event_label; },
  },
  {
    site: 'implicit:subject_name',
    base: validMemorial,
    mutate(x) { delete x.overview.subject_name; },
  },
  {
    site: 'implicit:literal_value',
    base: validMemorial,
    mutate(x) { x.assertions.find(a => a.assertion_id === 'M-BIRTH').literal_value = null; },
  },
];

const observedImplicitSites = [];
for (const testCase of implicitCases) {
  const fixture = clone(testCase.base);
  testCase.mutate(fixture);
  let caught;
  try {
    renderOverview(fixture.overview, fixture.assertions, fixture.entities);
  } catch (error) {
    caught = error;
  }
  assert.ok(caught instanceof MissingRequiredFieldError, `${testCase.site}: expected MissingRequiredFieldError`);
  assert.equal(caught.site, testCase.site, `${testCase.site}: wrong implicit site ID`);
  observedImplicitSites.push(caught.site);
}

console.log(`overview semantic PASS: ${reconciledObjects} published objects reconciled`);
console.log(`no-overview PASS: ${objectWithoutOverview.entity_id} rendered without record-overview section`);
console.log(`explicit failure coverage: ${observedExplicitSites.size} of ${declaredExplicitSites.size}; uncovered: ${uncoveredExplicitSites.length ? uncoveredExplicitSites.join(', ') : 'none'}`);
console.log(`implicit sites exercised (${observedImplicitSites.length}): ${observedImplicitSites.join(', ')}`);
