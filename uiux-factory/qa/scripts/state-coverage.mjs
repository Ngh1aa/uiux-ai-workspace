import { chromium } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import sharp from 'sharp';

const DEFAULT_VIEWPORTS = [
  { name: 'desktop-1440', width: 1440, height: 1000 },
  { name: 'tablet-768', width: 768, height: 1024 },
  { name: 'mobile-390', width: 390, height: 844 }
];

function fail(message) { throw new Error(`State coverage contract error: ${message}`); }

export function validateContract(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) fail('root must be an object');
  const contract = structuredClone(input);
  if (String(contract.schema_version || '') !== '1.0') fail('schema_version must be "1.0"');
  contract.name = String(contract.name || '').trim();
  if (!contract.name) fail('name is required');
  contract.entry_route = String(contract.entry_route || '').trim();
  if (!contract.entry_route.startsWith('/')) fail('entry_route must start with /');

  const viewports = contract.viewports || DEFAULT_VIEWPORTS;
  if (!Array.isArray(viewports) || viewports.length < 1 || viewports.length > 6) fail('viewports must contain 1..6 entries');
  const viewportNames = new Set();
  contract.viewports = viewports.map((item, index) => {
    if (!item || typeof item !== 'object') fail(`viewport[${index}] must be an object`);
    const name = String(item.name || '').trim().toLowerCase();
    const width = Number(item.width);
    const height = Number(item.height);
    if (!/^[a-z0-9][a-z0-9_-]{0,31}$/.test(name)) fail(`invalid viewport name: ${name}`);
    if (viewportNames.has(name)) fail(`duplicate viewport name: ${name}`);
    viewportNames.add(name);
    if (!Number.isInteger(width) || width < 240 || width > 4096) fail(`invalid width for ${name}`);
    if (!Number.isInteger(height) || height < 240 || height > 4096) fail(`invalid height for ${name}`);
    return { name, width, height };
  });

  if (!Array.isArray(contract.states) || contract.states.length < 1 || contract.states.length > 12) fail('states must contain 1..12 entries');
  const stateIds = new Set();
  contract.states = contract.states.map((state, index) => {
    if (!state || typeof state !== 'object') fail(`state[${index}] must be an object`);
    const id = String(state.id || '').trim().toLowerCase();
    if (!/^[a-z0-9][a-z0-9_-]{0,31}$/.test(id)) fail(`invalid state id: ${id}`);
    if (stateIds.has(id)) fail(`duplicate state id: ${id}`);
    stateIds.add(id);
    const label = String(state.label || id).trim();
    const query = state.query && typeof state.query === 'object' && !Array.isArray(state.query) ? state.query : { state: id };
    const scope = String(state.scope || contract.scope || (contract.frame_selector ? 'iframe' : 'page')).toLowerCase();
    if (!['page', 'iframe'].includes(scope)) fail(`state ${id} scope must be page or iframe`);
    const assertions = Array.isArray(state.assertions) ? state.assertions : [];
    if (id !== 'normal' && assertions.length === 0) fail(`state ${id} requires at least one semantic assertion`);
    const normalizedAssertions = assertions.map((assertion, assertionIndex) => {
      if (!assertion || typeof assertion !== 'object') fail(`state ${id} assertion[${assertionIndex}] must be an object`);
      const type = String(assertion.type || '').toLowerCase();
      if (!['selector', 'text', 'attribute'].includes(type)) fail(`state ${id} assertion[${assertionIndex}] has unsupported type ${type}`);
      if (type === 'selector' && !String(assertion.selector || '').trim()) fail(`state ${id} selector assertion requires selector`);
      if (type === 'text' && !String(assertion.text || '').trim()) fail(`state ${id} text assertion requires text`);
      if (type === 'attribute') {
        if (!String(assertion.selector || '').trim()) fail(`state ${id} attribute assertion requires selector`);
        if (!String(assertion.attribute || '').trim()) fail(`state ${id} attribute assertion requires attribute`);
        if (assertion.equals === undefined && assertion.contains === undefined) fail(`state ${id} attribute assertion requires equals or contains`);
      }
      return { ...assertion, type };
    });
    return {
      ...state, id, label, query, scope, assertions: normalizedAssertions,
      wait_ms: Number.isFinite(Number(state.wait_ms)) ? Math.max(0, Math.min(5000, Number(state.wait_ms))) : 350,
      focus: state.focus ? String(state.focus) : null
    };
  });

  const matrix = contract.matrix === false ? null : (contract.matrix || {});
  if (matrix) {
    const matrixStates = Array.isArray(matrix.states) && matrix.states.length ? matrix.states.map(String) : contract.states.filter(state => state.id !== 'normal').slice(0, 4).map(state => state.id);
    if (matrixStates.length < 1 || matrixStates.length > 6) fail('matrix.states must contain 1..6 state ids');
    for (const id of matrixStates) if (!stateIds.has(id)) fail(`matrix references unknown state: ${id}`);
    const columns = Number(matrix.columns || 2);
    if (!Number.isInteger(columns) || columns < 1 || columns > 3) fail('matrix.columns must be 1..3');
    const viewport = String(matrix.viewport || contract.viewports[0].name);
    if (!viewportNames.has(viewport)) fail(`matrix viewport does not exist: ${viewport}`);
    contract.matrix = {
      ...matrix, states: matrixStates, columns, viewport,
      tile_width: Number(matrix.tile_width || 720),
      tile_height: Number(matrix.tile_height || 460),
      gap: Number(matrix.gap || 16),
      padding: Number(matrix.padding || 24),
      output: String(matrix.output || 'state-coverage/state-matrix-2x2.png')
    };
  } else contract.matrix = null;
  contract.frame_selector = contract.frame_selector ? String(contract.frame_selector) : null;
  return contract;
}

function parseArg(name) { const index = process.argv.indexOf(name); return index >= 0 ? process.argv[index + 1] : null; }
function safeName(value) { return String(value).replace(/[^a-z0-9_-]+/gi, '-').replace(/^-|-$/g, '').toLowerCase() || 'state'; }
function buildStateUrl(baseUrl, contract, state) {
  const url = new URL(contract.entry_route, baseUrl);
  for (const [key, rawValue] of Object.entries(state.query || {})) {
    if (rawValue === null || rawValue === undefined || rawValue === false) continue;
    url.searchParams.set(key, rawValue === true ? '1' : String(rawValue));
  }
  return url.toString();
}

async function resolveScope(page, contract, state) {
  if (state.scope === 'page') return { kind: 'page', target: page };
  if (contract.frame_selector) {
    const locator = page.locator(contract.frame_selector).first();
    await locator.waitFor({ state: 'attached', timeout: 5000 });
    const handle = await locator.elementHandle();
    const frame = handle ? await handle.contentFrame() : null;
    if (!frame) throw new Error(`iframe scope not available for selector ${contract.frame_selector}`);
    return { kind: 'iframe', target: frame };
  }
  const baseOrigin = new URL(page.url()).origin;
  const frame = page.frames().find(candidate => candidate !== page.mainFrame() && (() => {
    try { return new URL(candidate.url()).origin === baseOrigin; } catch { return false; }
  })());
  if (!frame) throw new Error('iframe scope requested but no same-origin child frame exists');
  return { kind: 'iframe', target: frame };
}

async function runAssertion(scope, assertion) {
  if (assertion.type === 'selector') {
    const locator = scope.locator(assertion.selector).first();
    const count = await scope.locator(assertion.selector).count();
    const visible = count > 0 ? await locator.isVisible().catch(() => false) : false;
    const passed = count >= Number(assertion.count_at_least || 1) && (assertion.visible === false || visible);
    return { type: 'selector', selector: assertion.selector, count, visible, passed };
  }
  if (assertion.type === 'text') {
    const bodyText = await scope.locator('body').innerText().catch(() => '');
    return { type: 'text', text: assertion.text, passed: bodyText.includes(String(assertion.text)) };
  }
  const locator = scope.locator(assertion.selector).first();
  const count = await scope.locator(assertion.selector).count();
  const actual = count ? await locator.getAttribute(assertion.attribute) : null;
  const passed = assertion.equals !== undefined ? actual === String(assertion.equals) : String(actual || '').includes(String(assertion.contains));
  return { type: 'attribute', selector: assertion.selector, attribute: assertion.attribute, actual, expected: assertion.equals ?? assertion.contains, passed };
}

async function overflowMetrics(target) {
  return target.evaluate(() => ({ width: window.innerWidth, height: window.innerHeight, scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight }));
}
function escapeXml(value) { return String(value).replace(/[<>&'\"]/g, char => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' }[char])); }

async function createMatrix(contract, artifactsDir, matrixTilePaths) {
  if (!contract.matrix) return null;
  const matrix = contract.matrix;
  const rows = Math.ceil(matrix.states.length / matrix.columns);
  const headerHeight = 74;
  const tileHeaderHeight = 48;
  const contentHeight = Math.max(180, matrix.tile_height - tileHeaderHeight);
  const width = matrix.padding * 2 + matrix.columns * matrix.tile_width + (matrix.columns - 1) * matrix.gap;
  const height = matrix.padding * 2 + headerHeight + rows * matrix.tile_height + (rows - 1) * matrix.gap;
  const composites = [];
  const titleSvg = `<svg width="${width}" height="${headerHeight}"><rect width="100%" height="100%" fill="#f3f4f6"/><text x="${matrix.padding}" y="31" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" fill="#15171d">${escapeXml(contract.name)} · Lifecycle state matrix</text><text x="${matrix.padding}" y="53" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#656b76">Rendered by UIUX Factory State Coverage Gate · ${escapeXml(matrix.viewport)}</text></svg>`;
  composites.push({ input: Buffer.from(titleSvg), top: matrix.padding, left: 0 });

  for (let index = 0; index < matrix.states.length; index += 1) {
    const stateId = matrix.states[index];
    const state = contract.states.find(item => item.id === stateId);
    const sourcePath = matrixTilePaths.get(stateId);
    if (!sourcePath || !fs.existsSync(sourcePath)) throw new Error(`matrix tile missing for ${stateId}`);
    const col = index % matrix.columns;
    const row = Math.floor(index / matrix.columns);
    const left = matrix.padding + col * (matrix.tile_width + matrix.gap);
    const top = matrix.padding + headerHeight + row * (matrix.tile_height + matrix.gap);
    const content = await sharp(sourcePath).resize(matrix.tile_width, contentHeight, { fit: 'contain', background: '#ffffff', withoutEnlargement: false }).png().toBuffer();
    const headerSvg = `<svg width="${matrix.tile_width}" height="${tileHeaderHeight}"><rect width="100%" height="100%" fill="#ffffff"/><line x1="0" y1="${tileHeaderHeight - 1}" x2="${matrix.tile_width}" y2="${tileHeaderHeight - 1}" stroke="#d8dbe2"/><text x="14" y="21" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" fill="#15171d">${escapeXml(String(index + 1).padStart(2, '0'))} · ${escapeXml(state.label.toUpperCase())}</text><text x="14" y="37" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="#6b7280">semantic evidence verified</text></svg>`;
    const tile = await sharp({ create: { width: matrix.tile_width, height: matrix.tile_height, channels: 4, background: '#ffffff' } }).composite([{ input: Buffer.from(headerSvg), top: 0, left: 0 }, { input: content, top: tileHeaderHeight, left: 0 }]).extend({ top: 1, bottom: 1, left: 1, right: 1, background: '#d8dbe2' }).png().toBuffer();
    composites.push({ input: tile, top, left });
  }

  const outputPath = path.resolve(artifactsDir, matrix.output);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  await sharp({ create: { width, height, channels: 4, background: '#f3f4f6' } }).composite(composites).png().toFile(outputPath);
  return outputPath;
}

export async function runStateCoverage(rawContract, options = {}) {
  const contract = validateContract(rawContract);
  const baseUrl = options.baseUrl || process.env.QA_BASE_URL || 'http://127.0.0.1:4173';
  const artifactsDir = path.resolve(options.artifactsDir || process.env.QA_ARTIFACTS_DIR || 'artifacts');
  fs.mkdirSync(artifactsDir, { recursive: true });
  const report = { schema_version: '1.0', gate: 'STATE_COVERAGE', name: contract.name, base_url: baseUrl, entry_route: contract.entry_route, generated_at: new Date().toISOString(), checks: [], failures: [], classification: 'PASS' };
  const matrixTilePaths = new Map();
  const browser = await chromium.launch({ headless: true });

  try {
    for (const viewport of contract.viewports) {
      for (const state of contract.states) {
        const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: 'reduce' });
        const page = await context.newPage();
        const consoleErrors = [];
        const pageErrors = [];
        page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
        page.on('pageerror', error => pageErrors.push(String(error)));
        const url = buildStateUrl(baseUrl, contract, state);
        let responseStatus = 0, outer = null, inner = null, assertionResults = [], runtimeError = null, scope = null;
        try {
          const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
          responseStatus = response ? response.status() : 0;
          await page.waitForTimeout(state.wait_ms);
          scope = await resolveScope(page, contract, state);
          outer = await overflowMetrics(page);
          inner = scope.kind === 'iframe' ? await overflowMetrics(scope.target) : outer;
          for (const assertion of state.assertions) assertionResults.push(await runAssertion(scope.target, assertion));
          const dir = path.join(artifactsDir, 'state-coverage', safeName(viewport.name));
          fs.mkdirSync(dir, { recursive: true });
          await page.screenshot({ path: path.join(dir, `${safeName(state.id)}.png`), fullPage: true });
          if (contract.matrix && viewport.name === contract.matrix.viewport && contract.matrix.states.includes(state.id)) {
            const focusSelector = state.focus || state.assertions.find(item => item.type === 'selector')?.selector || 'body';
            const focusLocator = scope.target.locator(focusSelector).first();
            if ((await focusLocator.count()) < 1) throw new Error(`matrix focus selector not found: ${focusSelector}`);
            const tilePath = path.join(artifactsDir, 'state-coverage', 'matrix-tiles', `${safeName(state.id)}.png`);
            fs.mkdirSync(path.dirname(tilePath), { recursive: true });
            await focusLocator.screenshot({ path: tilePath });
            matrixTilePaths.set(state.id, tilePath);
          }
        } catch (error) { runtimeError = String(error?.stack || error); }

        const outerOverflow = outer ? outer.scrollWidth > outer.width + 2 : false;
        const innerOverflow = inner ? inner.scrollWidth > inner.width + 2 : false;
        const semanticPassed = assertionResults.every(item => item.passed);
        const passed = !runtimeError && responseStatus > 0 && responseStatus < 400 && !outerOverflow && !innerOverflow && semanticPassed && consoleErrors.length === 0 && pageErrors.length === 0;
        const check = { viewport: viewport.name, state: state.id, url, response_status: responseStatus, outer, inner, outer_overflow: outerOverflow, inner_overflow: innerOverflow, assertions: assertionResults, semantic_passed: semanticPassed, console_errors: consoleErrors, page_errors: pageErrors, runtime_error: runtimeError, passed };
        report.checks.push(check);
        if (!passed) report.failures.push(check);
        await context.close();
      }
    }
    if (contract.matrix) {
      const matrixPath = await createMatrix(contract, artifactsDir, matrixTilePaths);
      report.matrix = { states: contract.matrix.states, viewport: contract.matrix.viewport, output: path.relative(artifactsDir, matrixPath).replaceAll('\\', '/'), generated: true };
    } else report.matrix = { generated: false };
  } finally { await browser.close(); }

  report.classification = report.failures.length ? 'PRODUCT_QA_FAILED' : 'PASS';
  const reportPath = path.join(artifactsDir, 'state-coverage', 'state-coverage-report.json');
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  return { report, reportPath };
}

async function main() {
  const contractPath = parseArg('--contract') || process.env.QA_STATE_CONTRACT || '';
  if (!contractPath) fail('pass --contract <path> or QA_STATE_CONTRACT');
  const raw = JSON.parse(fs.readFileSync(path.resolve(contractPath), 'utf8'));
  const { report, reportPath } = await runStateCoverage(raw);
  console.log(JSON.stringify({ gate: report.gate, checks: report.checks.length, failures: report.failures.length, classification: report.classification, matrix: report.matrix, report: reportPath }, null, 2));
  if (report.failures.length) { console.error('UIUX_STATE_COVERAGE_FAILED'); process.exit(1); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main().catch(error => { console.error(error?.stack || error); process.exit(1); });
