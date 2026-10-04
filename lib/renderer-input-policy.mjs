// Machine-readable input policy for the JS object renderer migration.
// Renderer I/O may read only inputs declared here, from their actual source layer.
// Logical names are the stable contract; paths describe the current repository/build layout.
export const MATERIALIZED_DATASETS = Object.freeze({
  object_overviews: 'build/data/object-overviews.json',
});

export const STATIC_CONFIGURATION = Object.freeze({
  publication_dependency_rules: 'data/publication_dependency_rules.json',
});
