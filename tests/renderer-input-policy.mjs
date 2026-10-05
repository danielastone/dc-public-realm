import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
import { MATERIALIZED_DATASETS, STATIC_CONFIGURATION } from '../lib/renderer-input-policy.mjs';

const categories = [
  ['materialized dataset', MATERIALIZED_DATASETS, 7],
  ['static configuration', STATIC_CONFIGURATION, 3],
];
const contract = [
  await readFile('docs/audits/js-object-renderer-parity.md', 'utf8'),
  await readFile('docs/audits/js-object-driver-contract.md', 'utf8'),
].join('\n');

for (const [categoryName, policy, expectedCount] of categories) {
  const entries = Object.entries(policy);
  assert.equal(entries.length, expectedCount, `renderer input policy must declare exactly ${expectedCount} ${categoryName} entries`);

  for (const [logicalName, path] of entries) {
    assert.ok(contract.includes(`\`${logicalName}\``), `branch contract must document logical ${categoryName} ${logicalName}`);
    const info = await stat(path);
    assert.ok(info.isFile(), `${logicalName}: ${path} must be a regular file`);
    assert.ok(info.size > 0, `${logicalName}: ${path} must be non-empty`);
    if (path.endsWith('.json')) {
      const parsed = JSON.parse(await readFile(path, 'utf8'));
      const recordCount = Array.isArray(parsed) ? parsed.length : parsed && typeof parsed === 'object' ? Object.keys(parsed).length : 0;
      assert.ok(recordCount > 0, `${logicalName}: ${path} must contain at least one JSON record`);
    }
  }
  console.log(`renderer input policy: ${entries.length} ${categoryName} entries checked`);
}
