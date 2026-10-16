#!/usr/bin/env node
import { rm } from 'node:fs/promises';
import { loadAllRendererInputs } from '../lib/renderer-input-loader.mjs';
import { renderPublishedObjectPages } from '../lib/object-page-driver.mjs';

if (process.argv.length !== 2) throw new Error('JS object-page driver accepts no arguments');
const inputs = await loadAllRendererInputs();
const outputRoot = 'build/js-site';
await rm(outputRoot, { recursive: true, force: true });
const rendered = await renderPublishedObjectPages(inputs, outputRoot);
console.log(`JS object-page driver: ${rendered.length} published object pages written to build/js-site`);
