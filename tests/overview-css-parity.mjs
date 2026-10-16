import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';

import { OVERVIEW_CSS } from '../lib/render-overview.mjs';
import { renderShell } from '../lib/render-shell.mjs';

const python = spawnSync('python', ['-c', "import sys; sys.path.insert(0, 'scripts'); from overview_renderer import OVERVIEW_CSS; print(OVERVIEW_CSS, end='')"], {
  encoding: 'utf8',
});
if (python.status !== 0) {
  throw new Error(`Python OVERVIEW_CSS import failed: ${python.stderr}`);
}
assert.equal(OVERVIEW_CSS, python.stdout);

const style = `<style>${OVERVIEW_CSS}</style>`;
const withStyle = renderShell({ title: 'X', body: '', basePath: '/dc-public-realm', headContent: style });
assert.ok(withStyle.includes(`<link rel="stylesheet" href="/dc-public-realm/assets/style.css">${style}</head>`));
assert.equal(withStyle.split(style).length - 1, 1);

const withoutStyle = renderShell({ title: 'X', body: '', basePath: '/dc-public-realm' });
assert.ok(!withoutStyle.includes('<style>'));

console.log('overview CSS parity PASS: JS constant equals Python OVERVIEW_CSS and shell inserts optional head content immediately before </head>');
