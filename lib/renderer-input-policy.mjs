// Machine-readable input policy for the JS object renderer migration.
// Renderer I/O may read only inputs declared here, from their actual source layer.
// Logical names are the stable contract; paths describe the current repository/build layout.
export const MATERIALIZED_DATASETS = Object.freeze({
  entities: 'build/data/entities.json',
  assertions: 'build/data/assertions.json',
  assertion_evidence: 'build/data/assertion-evidence.json',
  sources: 'build/data/sources.json',
  research_tasks: 'build/data/research-tasks.json',
  predicate_rules: 'build/data/predicate-rules.json',
  object_overviews: 'build/data/object-overviews.json',
});

export const STATIC_CONFIGURATION = Object.freeze({
  publication_dependency_rules: 'data/publication_dependency_rules.json',
  publication_status_rules: 'data/publication_status_rules.json',
  external_records: 'data/external-records.json',
});

export const REQUIRED_RENDERER_INPUTS = Object.freeze([
  ...Object.keys(MATERIALIZED_DATASETS),
  ...Object.keys(STATIC_CONFIGURATION),
]);

export function pathForRendererInput(logicalName) {
  if (Object.hasOwn(MATERIALIZED_DATASETS, logicalName)) return MATERIALIZED_DATASETS[logicalName];
  if (Object.hasOwn(STATIC_CONFIGURATION, logicalName)) return STATIC_CONFIGURATION[logicalName];
  throw new Error(`undeclared renderer input: ${logicalName}`);
}
