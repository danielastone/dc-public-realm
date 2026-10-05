#!/usr/bin/env node
import { loadAllRendererInputs } from '../lib/renderer-input-loader.mjs';
import { renderPublishedObjectPages } from '../lib/object-page-driver.mjs';

if (process.argv.length !== 2) throw new Error('JS object-page driver accepts no arguments');
const inputs = await loadAllRendererInputs();
const rendered = await renderPublishedObjectPages(inputs, 'build/js-site');
console.log(`JS object-page driver: ${rendered.length} published object pages written to build/js-site`);
