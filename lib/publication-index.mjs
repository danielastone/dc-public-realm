// Pure publication-object discovery and route helpers.
// No I/O: callers pass the parsed entities payload.

export class PublicationIndexError extends Error {}
export class UnknownObjectError extends Error {}
export class NotPublishedError extends Error {}

// Python sorted(str) orders Unicode scalar values by code point. Do not replace
// this with localeCompare/Intl.Collator. Publication entity IDs are required by
// the parity harness to be printable ASCII, where this comparator is identical
// to Python's ordering contract.
function compareEntityId(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

function physicalObjects(payload) {
  if (!payload || !Array.isArray(payload.entities)) {
    throw new PublicationIndexError('invalid entities payload');
  }
  return payload.entities.filter(e => e.entity_type === 'PhysicalObject');
}

function requirePublicationContract(payload) {
  const objects = physicalObjects(payload);
  const missing = objects
    .filter(e => !e.publication || typeof e.publication !== 'object' || Array.isArray(e.publication))
    .map(e => e.entity_id || '<missing entity_id>')
    .sort(compareEntityId);
  if (missing.length) {
    throw new PublicationIndexError(`publication metadata missing for PhysicalObject record(s): ${missing.join(', ')}`);
  }
  return objects;
}

export function publishedObjects(payload) {
  const published = requirePublicationContract(payload)
    .filter(e => e.publication.publish === true)
    .sort((a, b) => compareEntityId(a.entity_id, b.entity_id));
  if (!published.length) {
    throw new PublicationIndexError('publication metadata present but no published objects found');
  }
  return published;
}

export function objectById(entityId, payload) {
  const entity = requirePublicationContract(payload).find(e => e.entity_id === entityId);
  if (!entity) throw new UnknownObjectError(entityId);
  if (entity.publication.publish !== true) throw new NotPublishedError(entityId);
  return entity;
}

export function objectBySlug(slug, payload) {
  const entity = publishedObjects(payload).find(e => e.publication.slug === slug);
  if (!entity) throw new UnknownObjectError(slug);
  return entity;
}

export function slugFor(entityId, payload) {
  return objectById(entityId, payload).publication.slug;
}

export function pathFor(entityId, payload) {
  return `objects/${slugFor(entityId, payload)}/index.html`;
}

export function href(entityId, payload, base = '') {
  return `${base.replace(/\/$/, '')}/objects/${slugFor(entityId, payload)}/`;
}

export function featuredObject(payload) {
  const featured = publishedObjects(payload).filter(e => e.publication.featured === true);
  if (featured.length !== 1) {
    const ids = featured.map(e => e.entity_id).join(', ') || 'none';
    throw new PublicationIndexError(`expected exactly one featured published object; found ${featured.length} (${ids})`);
  }
  return featured[0];
}
