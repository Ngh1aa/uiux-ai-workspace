import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { chromium } from '@playwright/test';
import { buildStateUrl, matrixGeometry, matrixTileEvidence, resolveArtifactPath, runStateCoverage, semanticTextIncludes, validateContract } from '../scripts/state-coverage.mjs';

for (const [name, checks, expected] of [
  ['passing checks', [{ viewport: 'desktop', state: 'empty', passed: true }], 'PASS'],
  ['semantic failure', [{ viewport: 'desktop', state: 'empty', semantic_passed: false, passed: false }], 'FAIL'],
  ['runtime failure with passing semantics', [{ viewport: 'desktop', state: 'empty', semantic_passed: true, passed: false }], 'FAIL'],
  ['matching viewport only', [{ viewport: 'mobile', state: 'empty', passed: true }, { viewport: 'desktop', state: 'empty', passed: false }], 'FAIL'],
  ['missing evidence', [{ viewport: 'mobile', state: 'empty', passed: true }], 'UNKNOWN'],
  ['non-boolean evidence', [{ viewport: 'desktop', state: 'empty', passed: 'true' }], 'UNKNOWN']
]) {
  test(`B09 matrix label reflects ${name}`, () => {
    const evidence = matrixTileEvidence(checks, 'desktop', 'empty');
    assert.equal(evidence.status, expected);
    assert.ok(evidence.label.startsWith(expected));
    assert.doesNotMatch(evidence.label, /verified/i);
  });
}

for (const fault of ['launch', 'context', 'page', 'navigation', 'context-close', 'browser-close']) {
  test(`B10 persists failures and attempts cleanup after ${fault} failure`, async t => {
    const { artifacts } = boundaryFixture(t);
    let contextClosed = false, browserClosed = false;
    const page = {
      on() {}, async route() {},
      async goto() { throw new Error('forced-navigation'); },
      url() { return 'http://127.0.0.1:4173/'; }
    };
    const context = {
      async newPage() { if (fault === 'page') throw new Error('forced-page'); return page; },
      async close() { contextClosed = true; if (fault === 'context-close') throw new Error('forced-context-close'); }
    };
    const browser = {
      async newContext() { if (fault === 'context') throw new Error('forced-context'); return context; },
      async close() { browserClosed = true; if (fault === 'browser-close') throw new Error('forced-browser-close'); }
    };
    t.mock.method(chromium, 'launch', async () => {
      if (fault === 'launch') throw new Error('forced-launch');
      return browser;
    });
    const contract = { ...base, frame_selector: null, scope: 'page', entry_route: '/',
      viewports: [{ name: 'desktop', width: 800, height: 600 }],
      states: [{ id: 'normal', scope: 'page', wait_ms: 0, assertions: [] }], matrix: false };
    const { report, reportPath } = await runStateCoverage(contract, { baseUrl: 'http://127.0.0.1:4173', artifactsDir: artifacts });
    assert.equal(report.classification, 'PRODUCT_QA_FAILED');
    assert.deepEqual(JSON.parse(fs.readFileSync(reportPath, 'utf8')), report);
    assert.equal(browserClosed, fault !== 'launch');
    assert.equal(contextClosed, !['launch', 'context'].includes(fault));
    if (['navigation', 'context-close', 'browser-close'].includes(fault)) {
      assert.equal(report.failures.length, 1);
      assert.match(report.failures[0].runtime_error, /forced-navigation/);
    }
    if (fault === 'browser-close') assert.match(report.cleanup_error, /forced-browser-close/);
    if (['launch', 'context', 'page', 'context-close'].includes(fault)) assert.match(report.runtime_error, /forced-/);
  });
}


const base = {
  schema_version: '1.0',
  name: 'Fixture product',
  entry_route: '/fixture/state-lab.html',
  frame_selector: '#fixtureFrame',
  states: [
    { id: 'normal', label: 'Normal', scope: 'iframe', query: { state: 'normal' }, assertions: [] },
    { id: 'empty', label: 'Empty', scope: 'iframe', query: { state: 'empty' }, assertions: [{ type: 'selector', selector: '[data-state-evidence="empty"]' }], focus: '[data-state-evidence="empty"]' },
    { id: 'loading', label: 'Loading', scope: 'iframe', query: { state: 'loading', pin: 1 }, assertions: [{ type: 'text', text: 'Loading evidence' }], focus: '[data-state-evidence="loading"]' },
    { id: 'error', label: 'Error', scope: 'iframe', query: { state: 'error' }, assertions: [{ type: 'attribute', selector: '[data-state-evidence="error"]', attribute: 'role', equals: 'alert' }], focus: '[data-state-evidence="error"]' },
    { id: 'edge', label: 'Edge', scope: 'iframe', query: { state: 'edge' }, assertions: [{ type: 'selector', selector: '[data-state-evidence="edge"]' }], focus: '[data-state-evidence="edge"]' }
  ],
  matrix: { states: ['empty', 'loading', 'error', 'edge'], columns: 2 }
};

test('normalizes a valid state coverage contract', () => {
  const contract = validateContract(base);
  assert.equal(contract.viewports.length, 3);
  assert.deepEqual(contract.matrix.states, ['empty', 'loading', 'error', 'edge']);
  assert.equal(contract.states.find(state => state.id === 'empty').scope, 'iframe');
});

test('requires semantic assertions for non-normal states', () => {
  const broken = structuredClone(base);
  broken.states.find(state => state.id === 'empty').assertions = [];
  assert.throws(() => validateContract(broken), /requires at least one semantic assertion/);
});

test('rejects a matrix that references unknown states', () => {
  const broken = structuredClone(base);
  broken.matrix.states.push('ghost');
  assert.throws(() => validateContract(broken), /unknown state/);
});

test('semantic text matching survives CSS text-transform casing and whitespace', () => {
  assert.equal(
    semanticTextIncludes('DEFAULT → HOVER\n→ PRESSED → DISABLED', 'Default → Hover → Pressed → Disabled'),
    true,
  );
  assert.equal(semanticTextIncludes('SAVED / SHORTLISTED', 'Saved / shortlisted'), true);
});

test('semantic text can opt into case-sensitive matching', () => {
  assert.equal(semanticTextIncludes('SAVED / SHORTLISTED', 'Saved / shortlisted', true), false);
  assert.equal(semanticTextIncludes('Saved / shortlisted', 'Saved / shortlisted', true), true);
});

for (const route of ['//example.org/outside', '///example.org/outside', '/\\example.org/outside', '/\n/example.org/outside', 'https://example.org/outside', '\\\\example.org\\outside', '/bad\u0000route']) {
  test(`B03 rejects a route that is not a bounded origin-relative path: ${JSON.stringify(route)}`, () => {
    assert.throws(() => validateContract({ ...base, entry_route: route }), /entry_route/);
  });
}

for (const output of ['../../outside.png', 'nested/../outside.png', '..\\outside.png', '/outside.png', 'C:\\outside.png', 'C:/outside.png', 'C:outside.png', '\\\\host\\share\\outside.png', '\\\\?\\C:\\outside.png', 'bad\u0000.png', '', '.', 'folder/']) {
  test(`B03 rejects output outside the portable artifact boundary: ${JSON.stringify(output)}`, () => {
    assert.throws(() => validateContract({ ...base, matrix: { ...base.matrix, output } }), /matrix.output/);
  });
}

for (const route of ['/', '/fixture/state-lab.html?view=empty#content', '/trang-ch%E1%BB%A7']) {
  test(`B03 retains a valid same-origin route: ${route}`, () => {
    assert.equal(validateContract({ ...base, entry_route: route }).entry_route, route);
  });
}

for (const output of ['nested/.. /outside.png', 'state-coverage/CON.png', 'state-coverage/nul', 'state-coverage/COM1.png', 'image.png:extra', 'nested./image.png']) {
  test(`B03 rejects ambiguous Windows output: ${output}`, () => {
    assert.throws(() => validateContract({ ...base, matrix: { ...base.matrix, output } }), /matrix.output/);
  });
}

for (const output of [null, 0, {}, []]) {
  test(`B03 rejects a non-string artifact output: ${JSON.stringify(output)}`, () => {
    assert.throws(() => validateContract({ ...base, matrix: { ...base.matrix, output } }), /matrix.output/);
  });
}

test('B03 URL resolution retains target origin and state query', () => {
  const url = new URL(buildStateUrl('http://127.0.0.1:4173/app/', validateContract(base), { query: { state: 'empty', pin: true } }));
  assert.equal(url.origin, 'http://127.0.0.1:4173');
  assert.equal(url.pathname, '/fixture/state-lab.html');
  assert.equal(url.searchParams.get('state'), 'empty');
  assert.equal(url.searchParams.get('pin'), '1');
  assert.throws(() => buildStateUrl('http://127.0.0.1:4173', { entry_route: '//example.org/outside' }, {}), /entry_route/);
});

function boundaryFixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'uiux-state-boundary-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const artifacts = path.join(root, 'artifacts');
  const outside = path.join(root, 'outside');
  fs.mkdirSync(artifacts);
  fs.mkdirSync(outside);
  return { root, artifacts, outside };
}

function linkDirectory(t, target, link) {
  try { fs.symlinkSync(target, link, process.platform === 'win32' ? 'junction' : 'dir'); }
  catch (error) {
    if (['EPERM', 'EACCES', 'ENOSYS'].includes(error.code)) { t.skip(`symlink unavailable: ${error.code}`); return false; }
    throw error;
  }
  return true;
}

test('B03 resolves portable nested output inside artifacts', t => {
  const { artifacts } = boundaryFixture(t);
  assert.equal(resolveArtifactPath(artifacts, 'state-coverage\\matrix.png'), path.join(artifacts, 'state-coverage', 'matrix.png'));
  assert.equal(resolveArtifactPath(artifacts, 'state-coverage/matrix.png'), path.join(artifacts, 'state-coverage', 'matrix.png'));
});

test('B03 rejects a symlinked output directory and a dangling junction', t => {
  const { artifacts, outside } = boundaryFixture(t);
  if (!linkDirectory(t, outside, path.join(artifacts, 'linked'))) return;
  assert.throws(() => resolveArtifactPath(artifacts, 'linked/matrix.png'), /symlink|junction/);
  if (!linkDirectory(t, path.join(outside, 'missing'), path.join(artifacts, 'dangling'))) return;
  assert.throws(() => resolveArtifactPath(artifacts, 'dangling/matrix.png'), /symlink|junction/);
  assert.deepEqual(fs.readdirSync(outside), []);
});

test('B03 rejects a symlinked output file', t => {
  const { artifacts, outside } = boundaryFixture(t);
  const target = path.join(outside, 'owned-fixture.png');
  fs.writeFileSync(target, 'sentinel');
  try { fs.symlinkSync(target, path.join(artifacts, 'matrix.png'), 'file'); }
  catch (error) {
    if (['EPERM', 'EACCES', 'ENOSYS'].includes(error.code)) { t.skip(`file symlink unavailable: ${error.code}`); return; }
    throw error;
  }
  assert.throws(() => resolveArtifactPath(artifacts, 'matrix.png'), /symlink|junction/);
  assert.equal(fs.readFileSync(target, 'utf8'), 'sentinel');
});

test('B03 rechecks the filesystem after preflight', t => {
  const { artifacts, outside } = boundaryFixture(t);
  assert.equal(resolveArtifactPath(artifacts, 'late/matrix.png'), path.join(artifacts, 'late', 'matrix.png'));
  if (!linkDirectory(t, outside, path.join(artifacts, 'late'))) return;
  assert.throws(() => resolveArtifactPath(artifacts, 'late/matrix.png'), /symlink|junction/);
});

test('B03 rejects screenshot/report directory escapes before browser launch', async t => {
  const { artifacts, outside } = boundaryFixture(t);
  if (!linkDirectory(t, outside, path.join(artifacts, 'state-coverage'))) return;
  await assert.rejects(() => runStateCoverage({ ...base, matrix: false }, { artifactsDir: artifacts }), /symlink|junction/);
  assert.deepEqual(fs.readdirSync(outside), []);
});

test('B03 rejects matrix directory escapes before browser launch', async t => {
  const { artifacts, outside } = boundaryFixture(t);
  if (!linkDirectory(t, outside, path.join(artifacts, 'linked'))) return;
  await assert.rejects(() => runStateCoverage({ ...base, matrix: { ...base.matrix, output: 'linked/matrix.png' } }, { artifactsDir: artifacts }), /symlink|junction/);
  assert.deepEqual(fs.readdirSync(outside), []);
});

test('B03 JSON schema route pattern agrees with boundary examples', () => {
  const schema = JSON.parse(fs.readFileSync(new URL('../state-coverage.schema.json', import.meta.url), 'utf8'));
  const pattern = new RegExp(schema.properties.entry_route.pattern);
  for (const route of ['//example.org/outside', '/\\example.org/outside', '/\n/example.org/outside']) assert.equal(pattern.test(route), false);
  for (const route of ['/', '/fixture/state-lab.html?state=empty']) assert.equal(pattern.test(route), true);
});

const matrixBounds = {
  columns: { min: 1, max: 3 },
  tile_width: { min: 240, max: 4096 },
  tile_height: { min: 180, max: 4096 },
  gap: { min: 0, max: 256 },
  padding: { min: 0, max: 256 }
};

for (const [field, bounds] of Object.entries(matrixBounds)) {
  for (const value of [NaN, Infinity, -Infinity, -1, bounds.min + 0.5, bounds.max + 1, Number.MAX_SAFE_INTEGER, '240', true, null, {}]) {
    test(`B11 rejects invalid ${field}: ${String(value)} (${typeof value})`, () => {
      assert.throws(() => validateContract({ ...base, matrix: { ...base.matrix, [field]: value } }), new RegExp(`matrix\\.${field}`));
    });
  }
}

for (const field of ['columns', 'tile_width', 'tile_height']) {
  test(`B11 rejects explicit zero ${field} instead of silently using defaults`, () => {
    assert.throws(() => validateContract({ ...base, matrix: { ...base.matrix, [field]: 0 } }), new RegExp(`matrix\\.${field}`));
  });
}

test('B11 preserves zero gap/padding and valid minimum tile sizes', () => {
  const contract = validateContract({ ...base, matrix: { ...base.matrix, tile_width: 240, tile_height: 180, gap: 0, padding: 0 } });
  assert.equal(contract.matrix.gap, 0);
  assert.equal(contract.matrix.padding, 0);
  assert.equal(contract.matrix.tile_width, 240);
  assert.equal(contract.matrix.tile_height, 180);
});

test('B11 rejects aggregate pixels even when every field is individually valid', () => {
  assert.throws(() => validateContract({ ...base, matrix: { ...base.matrix, tile_width: 2000, tile_height: 2000 } }), /matrix.*pixel/);
});

for (const [name, states, columns, tile_width, tile_height] of [
  ['width', ['empty', 'loading', 'error'], 3, 3000, 180],
  ['height', Array(6).fill('empty'), 1, 240, 1400]
]) {
  test(`B11 rejects excessive canvas ${name} below the pixel ceiling`, () => {
    assert.throws(() => validateContract({ ...base, matrix: { states, columns, tile_width, tile_height } }), /matrix.*dimension/);
  });
}

test('B11 retains omitted defaults and matrix:false', () => {
  const matrix = validateContract({ ...base, matrix: {} }).matrix;
  assert.equal(matrix.tile_width, 720);
  assert.equal(matrix.tile_height, 460);
  assert.equal(matrix.gap, 16);
  assert.equal(matrix.padding, 24);
  assert.equal(validateContract({ ...base, matrix: false }).matrix, null);
});

for (const name of ['fixture/state-coverage.contract.json', 'dogfood/cennext-state-coverage.json']) {
  test(`B11 accepts the existing repository contract: ${name}`, () => {
    const contract = JSON.parse(fs.readFileSync(new URL(`../${name}`, import.meta.url), 'utf8'));
    assert.doesNotThrow(() => validateContract(contract));
  });
}

for (const value of [null, true, 'matrix', []]) {
  test(`B11 rejects a matrix container outside its schema: ${JSON.stringify(value)}`, () => {
    assert.throws(() => validateContract({ ...base, matrix: value }), /matrix must be an object or false/);
  });
}

test('B11 canvas geometry includes borders and keeps minimum-height content inside its tile', () => {
  const matrix = validateContract({ ...base, matrix: { ...base.matrix, tile_width: 240, tile_height: 180, gap: 0, padding: 0 } }).matrix;
  const geometry = matrixGeometry(matrix);
  assert.deepEqual(geometry, { rows: 2, width: 484, height: 438, tileWidth: 242, tileHeight: 182, contentHeight: 132 });
});

test('B11 accepts exactly the pixel ceiling and rejects one extra row', () => {
  const matrix = { states: ['empty'], columns: 1, tile_width: 3998, tile_height: 3924, gap: 0, padding: 0 };
  const geometry = matrixGeometry(validateContract({ ...base, matrix }).matrix);
  assert.equal(geometry.width * geometry.height, 16_000_000);
  assert.throws(() => validateContract({ ...base, matrix: { ...matrix, tile_height: 3925 } }), /matrix.*pixel/);
});

for (const [dimension, matrix, field] of [
  ['width', { states: ['empty', 'loading'], columns: 2, tile_width: 4094, tile_height: 180, gap: 0, padding: 0 }, 'tile_width'],
  ['height', { states: ['empty', 'loading'], columns: 1, tile_width: 240, tile_height: 4057, gap: 0, padding: 0 }, 'tile_height']
]) {
  test(`B11 accepts exactly the ${dimension} ceiling and rejects exceeding it`, () => {
    assert.equal(matrixGeometry(validateContract({ ...base, matrix }).matrix)[dimension], 8192);
    assert.throws(() => validateContract({ ...base, matrix: { ...matrix, [field]: matrix[field] + 1 } }), /matrix.*dimension/);
  });
}

test('B11 JSON schema and runtime agree on numeric field limits', () => {
  const schema = JSON.parse(fs.readFileSync(new URL('../state-coverage.schema.json', import.meta.url), 'utf8'));
  const fields = schema.properties.matrix.oneOf.find(item => item.type === 'object').properties;
  for (const [field, bounds] of Object.entries(matrixBounds)) {
    assert.equal(fields[field].type, 'integer');
    assert.equal(fields[field].minimum, bounds.min);
    assert.equal(fields[field].maximum, bounds.max);
  }
});

for (const [field, bounds] of Object.entries(matrixBounds)) {
  test(`B11 accepts the upper ${field} limit when aggregate geometry is small`, () => {
    const matrix = { states: ['empty'], columns: 1, tile_width: 240, tile_height: 180, gap: 0, padding: 0, [field]: bounds.max };
    assert.equal(validateContract({ ...base, matrix }).matrix[field], bounds.max);
  });
}

for (const matrix of [{ ...base.matrix, tile_width: -10 }, { ...base.matrix, padding: Infinity }, { ...base.matrix, tile_width: 2000, tile_height: 2000 }]) {
  test(`B11 rejects invalid resources before browser/Sharp or artifact creation: ${String(matrix.tile_width)}, ${String(matrix.padding)}`, async t => {
    const { root } = boundaryFixture(t);
    const artifactsDir = path.join(root, 'must-not-exist');
    await assert.rejects(() => runStateCoverage({ ...base, matrix }, { baseUrl: 'http://127.0.0.1:1', artifactsDir }), /State coverage contract error: matrix/);
    assert.equal(fs.existsSync(artifactsDir), false);
  });
}
