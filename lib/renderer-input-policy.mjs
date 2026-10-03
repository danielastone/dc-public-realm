// Machine-readable input policy for the JS object renderer migration.
// Renderer I/O may read only materialized datasets declared here.
// Logical names are the stable contract; paths describe the current build layout.
export const MATERIALIZED_DATASETS = Object.freeze({
  object_overviews: 'build/data/object-overviews.json',
});
