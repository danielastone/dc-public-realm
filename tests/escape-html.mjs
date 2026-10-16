import assert from 'node:assert/strict';
import { escapeHtml } from '../lib/render-shell.mjs';

// Python reference: html.escape(value, quote=True)
const input = `& < > " '`;
const expected = '&amp; &lt; &gt; &quot; &#x27;';
assert.equal(escapeHtml(input), expected);
console.log('escapeHtml: matches Python html.escape(..., quote=True) for & < > " \'');
