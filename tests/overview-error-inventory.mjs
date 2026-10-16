import fs from 'node:fs';
import assert from 'node:assert/strict';

// Frozen migration inventory of explicit raise sites reachable directly through
// render_overview() and its nested helpers refs(), require_subject(), and fact().
// Site IDs use helper + source-order ordinal. Python is frozen during this
// migration; if the discovered set changes, stop and review the source change.
// This tripwire detects inventory omissions, not incorrect semantic mappings.
export const OVERVIEW_ERROR_CONDITIONS = Object.freeze([
  { site: 'refs#1', condition: 'displayed fact has no assertion reference', fixture: false },
  { site: 'refs#2', condition: 'referenced canonical assertion is missing', fixture: false },
  { site: 'require_subject#1', condition: 'assertion subject mismatch', fixture: false },
  { site: 'fact#1', condition: 'displayed value does not reconcile to canonical assertion', fixture: false },
  { site: 'render_overview#1', condition: 'overview object is not a canonical entity', fixture: false },
  { site: 'render_overview#2', condition: 'incomplete image rights metadata', fixture: false },
  { site: 'render_overview#3', condition: 'subject-date assertion subjects disagree', fixture: false },
  { site: 'render_overview#4', condition: 'subject name does not reconcile to canonical person', fixture: false },
  { site: 'render_overview#5', condition: 'expected birth and death assertions', fixture: false },
  { site: 'render_overview#6', condition: 'subject dates do not reconcile to canonical assertions', fixture: false },
  { site: 'render_overview#7', condition: 'unknown record type', fixture: false },
]);

const PYTHON_SOURCE = 'scripts/overview_renderer.py';
const SCOPED_HELPERS = ['render_overview', 'refs', 'require_subject', 'fact'];

function leadingSpaces(line) {
  return line.length - line.trimStart().length;
}

function functionBlocks(source) {
  // A def's body is every following line indented deeper than the def line;
  // the block ends at the first non-blank line at the same or lesser indent.
  const lines = source.split(/\r?\n/);
  const blocks = new Map();
  for (let i = 0; i < lines.length; i += 1) {
    const match = lines[i].match(/^(\s*)def\s+(render_overview|refs|require_subject|fact)\s*\(/);
    if (!match) continue;
    const indent = match[1].length;
    let end = lines.length;
    for (let j = i + 1; j < lines.length; j += 1) {
      if (lines[j].trim() && leadingSpaces(lines[j]) <= indent) { end = j; break; }
    }
    blocks.set(match[2], { indent, lines: lines.slice(i + 1, end) });
  }
  return blocks;
}

function scanRaiseSites(source) {
  const blocks = functionBlocks(source);
  const discovered = [];
  for (const helper of SCOPED_HELPERS) {
    const block = blocks.get(helper);
    assert.ok(block, `missing scoped Python helper: ${helper}`);
    let ordinal = 0;
    let nestedIndent = null; // indent of a nested def whose body we are skipping
    for (const line of block.lines) {
      // Deliberately simple heuristic: explicit `raise` tokens only. No AST or
      // control-flow analysis. Nested def bodies are excluded from the
      // enclosing block so each raise site is attributed to exactly one helper.
      if (line.trim()) {
        const ind = leadingSpaces(line);
        if (nestedIndent !== null && ind <= nestedIndent) nestedIndent = null;
        if (nestedIndent === null && /^\s*def\s+/.test(line)) { nestedIndent = ind; continue; }
      }
      if (nestedIndent !== null) continue;
      if (/\braise\s+/.test(line)) {
        ordinal += 1;
        discovered.push(`${helper}#${ordinal}`);
      }
    }
  }
  return discovered;
}

const declared = OVERVIEW_ERROR_CONDITIONS.map(({ site }) => site);
const duplicateDeclared = declared.filter((site, index) => declared.indexOf(site) !== index);
assert.deepEqual(duplicateDeclared, [], `duplicate declared site IDs: ${duplicateDeclared.join(', ')}`);

const source = fs.readFileSync(PYTHON_SOURCE, 'utf8');
const discovered = scanRaiseSites(source);

console.log(`scanner site IDs (${discovered.length}): ${discovered.join(', ')}`);
console.log(`declared site IDs (${declared.length}): ${declared.join(', ')}`);
console.log(`duplicate declared IDs: ${duplicateDeclared.length === 0 ? 'none' : duplicateDeclared.join(', ')}`);

assert.deepEqual(new Set(discovered), new Set(declared), 'Python raise-site set differs from frozen overview condition table; stop and inspect, do not renumber');
console.log('exact set comparison: equal');
