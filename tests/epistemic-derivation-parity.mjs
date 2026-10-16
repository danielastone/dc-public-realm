import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { deriveEpistemicParity } from '../lib/derive-epistemics.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATA = process.env.KNOWLEDGE_DATA_DIR || 'build/data';
const fixture = JSON.parse(fs.readFileSync(path.join(ROOT, 'tests/fixtures/epistemic-derivation.json'), 'utf8'));
const real = JSON.parse(fs.readFileSync(path.join(ROOT, DATA, 'assertion-evidence.json'), 'utf8')).assertion_evidence;

// Canonicalize object representation only. Arrays are semantic/contractual and
// are deliberately never sorted or otherwise reordered by this comparator.
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  }
  return value;
}

function firstDifference(a, b, at = '$') {
  if (Object.is(a, b)) return null;
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b)) return at;
    if (a.length !== b.length) return `${at}.length`;
    for (let i = 0; i < a.length; i += 1) {
      const diff = firstDifference(a[i], b[i], `${at}[${i}]`);
      if (diff) return diff;
    }
    return null;
  }
  if (a && b && typeof a === 'object' && typeof b === 'object') {
    const ak = Object.keys(a).sort();
    const bk = Object.keys(b).sort();
    if (JSON.stringify(ak) !== JSON.stringify(bk)) return `${at}.[keys]`;
    for (const key of ak) {
      const diff = firstDifference(a[key], b[key], `${at}.${key}`);
      if (diff) return diff;
    }
    return null;
  }
  return at;
}

function walkTrace(node, coverage) {
  if (!node || typeof node !== 'object') return;
  if (node.terminal === null) {
    if (Array.isArray(node.branches) && node.branches.length >= 2) coverage.MULTI_BRANCH += 1;
    for (const branch of node.branches || []) walkTrace(branch, coverage);
  } else if (Object.hasOwn(coverage, node.terminal)) {
    coverage[node.terminal] += 1;
  }
}

function coverageOf(payload) {
  const coverage = {
    ESTABLISHED_ROOT: 0,
    UNRESOLVED_ANCESTRY: 0,
    BROKEN_REFERENCE: 0,
    CYCLE: 0,
    MULTI_BRANCH: 0,
  };
  for (const result of payload.lineage.real) walkTrace(result.trace, coverage);
  for (const testCase of payload.lineage.cases) {
    for (const result of testCase.results) walkTrace(result.trace, coverage);
  }
  return coverage;
}

function requireCoverage(label, payload) {
  const coverage = coverageOf(payload);
  for (const [target, count] of Object.entries(coverage)) {
    if (count === 0) throw new Error(`${label} coverage missing ${target}`);
  }
  return coverage;
}

function assertParity(pythonDump, jsDump, label = 'epistemic derivation') {
  const left = canonical(pythonDump);
  const right = canonical(jsDump);
  const diff = firstDifference(left, right);
  if (diff) throw new Error(`${label} parity failed at ${diff}`);
}

const env = { ...process.env, KNOWLEDGE_DATA_DIR: DATA };
const pythonDump = JSON.parse(execFileSync('python', ['scripts/dump_epistemic_derivation.py'], {
  cwd: ROOT,
  env,
  encoding: 'utf8',
}));
const jsDump = deriveEpistemicParity(real, fixture.cases);

const pythonCoverage = requireCoverage('Python', pythonDump);
const jsCoverage = requireCoverage('JS', jsDump);
assertParity(pythonDump, jsDump);

// Sensitivity proof: mutate one derived leaf on each producer's output. Each
// comparison must fail and must name the path to the changed value.
function proveSensitivity(side, source, other) {
  const changed = structuredClone(source);
  changed.dependency.real[0].state = '__SENSITIVITY_BREAK__';
  let message = '';
  try {
    if (side === 'Python') assertParity(changed, other, `${side} sensitivity`);
    else assertParity(other, changed, `${side} sensitivity`);
  } catch (error) {
    message = String(error.message || error);
  }
  if (!message.includes('$.dependency.real[0].state')) {
    throw new Error(`${side} sensitivity proof did not fail at the changed path: ${message || 'no failure'}`);
  }
}

proveSensitivity('Python', pythonDump, jsDump);
proveSensitivity('JS', jsDump, pythonDump);

const formatCoverage = c => `root=${c.ESTABLISHED_ROOT}, unresolved=${c.UNRESOLVED_ANCESTRY}, broken=${c.BROKEN_REFERENCE}, cycle=${c.CYCLE}, multi-branch=${c.MULTI_BRANCH}`;
console.log('epistemic derivation parity PASS: Python = JS');
console.log(`Python harness coverage: ${formatCoverage(pythonCoverage)}`);
console.log(`JS harness coverage: ${formatCoverage(jsCoverage)}`);
console.log('epistemic parity sensitivity PASS: Python-side and JS-side mutations rejected at $.dependency.real[0].state');
