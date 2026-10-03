// Machine-readable input policy for the JS object renderer migration.
// Canonical/materialized structured data are permitted by the branch contract.
// Presentation inputs require explicit review and inclusion here.
export const PRESENTATION_DATA_ALLOWLIST = Object.freeze([
  'object-overviews.json',
]);
