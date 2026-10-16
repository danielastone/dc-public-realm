import { readFile } from 'node:fs/promises';
import { REQUIRED_RENDERER_INPUTS, pathForRendererInput } from './renderer-input-policy.mjs';

export function assertCompleteRendererInputContract(names = REQUIRED_RENDERER_INPUTS) {
  const expected = new Set(REQUIRED_RENDERER_INPUTS);
  const actual = new Set(names);
  if (actual.size !== expected.size || [...expected].some(name => !actual.has(name))) {
    throw new Error(`renderer input set must be exactly: ${REQUIRED_RENDERER_INPUTS.join(', ')}`);
  }
  // Resolve every logical name before the first read. This makes an incomplete or
  // undeclared contract fail before any renderer input is loaded.
  return names.map(name => [name, pathForRendererInput(name)]);
}

export async function loadRendererInput(logicalName) {
  const path = pathForRendererInput(logicalName);
  return JSON.parse(await readFile(path, 'utf8'));
}

export async function loadAllRendererInputs() {
  const resolved = assertCompleteRendererInputContract();
  const loaded = {};
  // Deliberately sequential: provenance and failure order stay deterministic.
  for (const [logicalName, path] of resolved) {
    loaded[logicalName] = JSON.parse(await readFile(path, 'utf8'));
  }
  return loaded;
}
