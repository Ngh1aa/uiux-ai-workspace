import { chromium } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const DEFAULT_VIEWPORTS = [
  { name: 'desktop-1440', width: 1440, height: 1000 },
  { name: 'tablet-768', width: 768, height: 1024 },
  { name: 'mobile-390', width: 390, height: 844 }
];

const MATRIX_FIELDS = {
  columns: { min: 1, max: 3, default: 2 },
  tile_width: { min: 240, max: 4096, default: 720 },
  tile_height: { min: 180, max: 4096, default: 460 },
  gap: { min: 0, max: 256, default: 16 },
  padding: { min: 0, max: 256, default: 24 }
};
const MATRIX_MAX_DIMENSION = 8192;
const MATRIX_MAX_PIXELS = 16_000_000;
const MATRIX_HEADER_HEIGHT = 74;
const TILE_HEADER_HEIGHT = 48;

function fail(message) { throw new Error(`State coverage contract error: ${message}`); }

function matrixNumber(matrix, field) {
  const bounds = MATRIX_FIELDS[field];
  const value = matrix[field] === undefined ? bounds.default : matrix[field];
  if (!Number.isInteger(value) || value < bounds.min || value > bounds.max) {
    fail(`matrix.${field} must be an integer in ${bounds.min}..${bounds.max}`);
  }
  return value;
}

export function matrixGeometry(matrix) {
  const rows = Math.ceil(matrix.states.length / matrix.columns);
  // Sharp adds a one-pixel border on every side of each tile.
  const tileWidth = matrix.tile_width + 2;
  const tileHeight = matrix.tile_height + 2;
  const width = matrix.padding * 2 + matrix.columns * tileWidth + (matrix.columns - 1) * matrix.gap;
  const height = matrix.padding * 2 + MATRIX_HEADER_HEIGHT + rows * tileHeight + (rows - 1) * matrix.gap;
  if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height) || width > MATRIX_MAX_DIMENSION || height > MATRIX_MAX_DIMENSION) {
    fail(`matrix canvas dimensions must not exceed ${MATRIX_MAX_DIMENSION}px`);
  }
  if (width * height > MATRIX_MAX_PIXELS) fail(`matrix canvas exceeds ${MATRIX_MAX_PIXELS} pixels`);
  return { rows, width, height, tileWidth, tileHeight, contentHeight: matrix.tile_height - TILE_HEADER_HEIGHT };
}

function validateEntryRoute(route) {
  if (!route.startsWith('/') || route.startsWith('//') || /[\\\u0000-\u0020\u007f]/.test(route)) {
    fail('entry_route must be an origin-relative path without backslashes or control characters');
  }
  const base = new URL('https://state-coverage.invalid/');
  if (new URL(route, base).origin !== base.origin) fail('entry_route must preserve the target origin');
}

function normalizeArtifactOutput(value) {
  if (typeof value !== 'string') fail('matrix.output must be a relative artifact file path string');
  const output = String(value).trim();
  if (!output || /[\u0000-\u001f\u007f:]/.test(output) || path.posix.isAbsolute(output) || path.win32.isAbsolute(output)) {
    fail('matrix.output must be a relative artifact file path');
  }
  const parts = output.split(/[\\/]/);
  if (parts.some(part => part === '..' || /[. ]$/.test(part) || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(part)) || !parts.at(-1)) {
    fail('matrix.output must not contain traversal, device names or ambiguous Windows path segments');
  }
  return output.replaceAll('\\', '/');
}

export function resolveArtifactPath(artifactsDir, relativeOutput) {
  const output = normalizeArtifactOutput(relativeOutput);
  const root = path.resolve(artifactsDir);
  const realRoot = fs.realpathSync(root);
  const target = path.resolve(root, output);
  const relative = path.relative(root, target);
  if (!relative || relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    fail('artifact output escapes artifactsDir');
  }
  let current = root;
  for (const part of relative.split(path.sep)) {
    current = path.join(current, part);
    const stat = fs.lstatSync(current, { throwIfNoEntry: false });
    if (!stat) break;
    if (stat.isSymbolicLink()) fail('artifact output must not traverse a symlink or junction');
    const realRelative = path.relative(realRoot, fs.realpathSync(current));
    if (realRelative === '..' || realRelative.startsWith(`..${path.sep}`) || path.isAbsolute(realRelative)) {
      fail('artifact output escapes the real artifactsDir');
    }
  }
  return target;
}

export function validateContract(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) fail('root must be an object');
  const contract = structuredClone(input);
  if (String(contract.schema_version || '') !== '1.0') fail('schema_version must be "1.0"');
  contract.name = String(contract.name || '').trim();
  if (!contract.name) fail('name is required');
  contract.entry_route = String(contract.entry_route || '').trim();
  validateEntryRoute(contract.entry_route);

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

  if (contract.matrix !== undefined && contract.matrix !== false && (!contract.matrix || typeof contract.matrix !== 'object' || Array.isArray(contract.matrix))) {
    fail('matrix must be an object or false');
  }
  const matrix = contract.matrix === false ? null : (contract.matrix || {});
  if (matrix) {
    const matrixStates = Array.isArray(matrix.states) && matrix.states.length ? matrix.states.map(String) : contract.states.filter(state => state.id !== 'normal').slice(0, 4).map(state => state.id);
    if (matrixStates.length < 1 || matrixStates.length > 6) fail('matrix.states must contain 1..6 state ids');
    for (const id of matrixStates) if (!stateIds.has(id)) fail(`matrix references unknown state: ${id}`);
    const columns = matrixNumber(matrix, 'columns');
    const viewport = String(matrix.viewport || contract.viewports[0].name);
    if (!viewportNames.has(viewport)) fail(`matrix viewport does not exist: ${viewport}`);
    contract.matrix = {
      ...matrix, states: matrixStates, columns, viewport,
      tile_width: matrixNumber(matrix, 'tile_width'),
      tile_height: matrixNumber(matrix, 'tile_height'),
      gap: matrixNumber(matrix, 'gap'),
      padding: matrixNumber(matrix, 'padding'),
      output: normalizeArtifactOutput(matrix.output === undefined ? 'state-coverage/state-matrix-2x2.png' : matrix.output)
    };
    matrixGeometry(contract.matrix);
  } else contract.matrix = null;
  contract.frame_selector = contract.frame_selector ? String(contract.frame_selector) : null;
  return contract;
}

function parseArg(name) { const index = process.argv.indexOf(name); return index >= 0 ? process.argv[index + 1] : null; }
function safeName(value) { return String(value).replace(/[^a-z0-9_-]+/gi, '-').replace(/^-|-$/g, '').toLowerCase() || 'state'; }
export function buildStateUrl(baseUrl, contract, state) {
  validateEntryRoute(contract.entry_route);
  const base = new URL(baseUrl);
  if (!['http:', 'https:'].includes(base.protocol)) fail('baseUrl must use HTTP or HTTPS');
  const url = new URL(contract.entry_route, baseUrl);
  if (url.origin !== base.origin) fail('entry_route must preserve the target origin');
  for (const [key, rawValue] of Object.entries(state.query || {})) {
    if (rawValue === null || rawValue === undefined || rawValue === false) continue;
    url.searchParams.set(key, rawValue === true ? '1' : String(rawValue));
  }
  return url.toString();
}

export async function navigateWithinOrigin(page, initialUrl) {
  const origin = new URL(initialUrl).origin;
  let redirectUrl = null;
  let navigating = true;
  let navigationError = null;
  await page.route('**/*', async route => {
    const request = route.request();
    if (!request.isNavigationRequest() || request.frame() !== page.mainFrame()) return route.continue();
    if (new URL(request.url()).origin !== origin) return route.abort('blockedbyclient');
    // Playwright does not route subsequent HTTP redirects, so fetch exactly one response.
    let response;
    try { response = await route.fetch({ maxRedirects: 0, timeout: 15000 }); }
    catch (error) { navigationError = error; return route.abort('failed'); }
    const location = response.headers().location;
    if ([301, 302, 303, 307, 308].includes(response.status()) && location) {
      let destination;
      try { destination = new URL(location, request.url()); }
      catch (error) { navigationError = error; return route.abort('failed'); }
      if (destination.origin !== origin || !navigating) return route.abort('blockedbyclient');
      redirectUrl = destination.href;
      // Navigate explicitly to retain the final URL and relative asset base without an unchecked redirect chain.
      return route.fulfill({ status: 200, contentType: 'text/html', body: '' });
    }
    return route.fulfill({ response });
  });
  try {
    let url = initialUrl;
    for (let redirects = 0; redirects <= 20; redirects += 1) {
      redirectUrl = null;
      let response;
      try { response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 }); }
      catch (error) { throw navigationError || error; }
      if (!redirectUrl) return response;
      url = redirectUrl;
    }
    throw new Error('State coverage navigation exceeded 20 same-origin redirects');
  } finally { navigating = false; }
}

async function resolveScope(page, contract, state) {
  if (state.scope === 'page') return { kind: 'page', target: page };
  if (contract.frame_selector) {
    const locator = page.locator(contract.frame_selector).first();
    await locator.waitFor({ state: 'attached', timeout: 5000 });
    const handle = await locator.elementHandle();
    const frame = handle ? await handle.contentFrame() : null;
    if (!frame) throw new Error(`iframe scope not available for selector ${contract.frame_selector}`);
    if (new URL(frame.url()).origin !== new URL(page.url()).origin) throw new Error('iframe scope must preserve the target origin');
    return { kind: 'iframe', target: frame };
  }
  const baseOrigin = new URL(page.url()).origin;
  const frame = page.frames().find(candidate => candidate !== page.mainFrame() && (() => {
    try { return new URL(candidate.url()).origin === baseOrigin; } catch { return false; }
  })());
  if (!frame) throw new Error('iframe scope requested but no same-origin child frame exists');
  return { kind: 'iframe', target: frame };
}

function normalizeSemanticText(value, caseSensitive = false) {
  const normalized = String(value ?? '').replace(/\s+/g, ' ').trim();
  return caseSensitive ? normalized : normalized.toLocaleLowerCase();
}

export function semanticTextIncludes(actual, expected, caseSensitive = false) {
  return normalizeSemanticText(actual, caseSensitive).includes(normalizeSemanticText(expected, caseSensitive));
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
    const selector = String(assertion.selector || 'body');
    const locator = scope.locator(selector).first();
    const count = await scope.locator(selector).count();
    const visible = count > 0 ? await locator.isVisible().catch(() => false) : false;
    const actual = count > 0 ? await locator.innerText().catch(() => '') : '';
    const caseSensitive = assertion.case_sensitive === true;
    const passed = count > 0 && (assertion.visible === false || visible) && semanticTextIncludes(actual, assertion.text, caseSensitive);
    return { type: 'text', selector, text: assertion.text, case_sensitive: caseSensitive, count, visible, passed };
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

export function matrixTileEvidence(checks, viewport, stateId) {
  const check = checks.find(item => item.viewport === viewport && item.state === stateId);
  if (check?.passed === true) return { status: 'PASS', label: 'PASS · QA checks passed', color: '#146c43' };
  if (check?.passed === false) return { status: 'FAIL', label: 'FAIL · QA checks failed', color: '#b52b3e' };
  return { status: 'UNKNOWN', label: 'UNKNOWN · QA evidence unavailable', color: '#6b7280' };
}

async function createMatrix(contract, artifactsDir, matrixTilePaths, checks) {
  if (!contract.matrix) return null;
  const matrix = contract.matrix;
  const { width, height, tileWidth, tileHeight, contentHeight } = matrixGeometry(matrix);
  const { default: sharp } = await import('sharp');
  const headerHeight = MATRIX_HEADER_HEIGHT;
  const tileHeaderHeight = TILE_HEADER_HEIGHT;
  const composites = [];
  const titleSvg = `<svg width="${width}" height="${headerHeight}"><rect width="100%" height="100%" fill="#f3f4f6"/><text x="${matrix.padding}" y="31" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" fill="#15171d">${escapeXml(contract.name)} · Lifecycle state matrix</text><text x="${matrix.padding}" y="53" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#656b76">Rendered by UIUX Factory State Coverage Gate · ${escapeXml(matrix.viewport)}</text></svg>`;
  composites.push({ input: Buffer.from(titleSvg), top: matrix.padding, left: 0 });

  for (let index = 0; index < matrix.states.length; index += 1) {
    const stateId = matrix.states[index];
    const state = contract.states.find(item => item.id === stateId);
    const evidence = matrixTileEvidence(checks, matrix.viewport, stateId);
    const storedPath = matrixTilePaths.get(stateId);
    const sourcePath = storedPath ? resolveArtifactPath(artifactsDir, path.relative(artifactsDir, storedPath)) : null;
    if (!sourcePath || !fs.existsSync(sourcePath)) throw new Error(`matrix tile missing for ${stateId}`);
    const col = index % matrix.columns;
    const row = Math.floor(index / matrix.columns);
    const left = matrix.padding + col * (tileWidth + matrix.gap);
    const top = matrix.padding + headerHeight + row * (tileHeight + matrix.gap);
    const content = await sharp(sourcePath).resize(matrix.tile_width, contentHeight, { fit: 'contain', background: '#ffffff', withoutEnlargement: false }).png().toBuffer();
    const headerSvg = `<svg width="${matrix.tile_width}" height="${tileHeaderHeight}"><rect width="100%" height="100%" fill="#ffffff"/><line x1="0" y1="${tileHeaderHeight - 1}" x2="${matrix.tile_width}" y2="${tileHeaderHeight - 1}" stroke="#d8dbe2"/><text x="14" y="21" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" fill="#15171d">${escapeXml(String(index + 1).padStart(2, '0'))} · ${escapeXml(state.label.toUpperCase())}</text><text x="14" y="37" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="${evidence.color}">${escapeXml(evidence.label)}</text></svg>`;
    const tile = await sharp({ create: { width: matrix.tile_width, height: matrix.tile_height, channels: 4, background: '#ffffff' } }).composite([{ input: Buffer.from(headerSvg), top: 0, left: 0 }, { input: content, top: tileHeaderHeight, left: 0 }]).extend({ top: 1, bottom: 1, left: 1, right: 1, background: '#d8dbe2' }).png().toBuffer();
    composites.push({ input: tile, top, left });
  }

  const outputPath = resolveArtifactPath(artifactsDir, matrix.output);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  await sharp({ create: { width, height, channels: 4, background: '#f3f4f6' } }).composite(composites).png().toFile(resolveArtifactPath(artifactsDir, matrix.output));
  return outputPath;
}

export async function runStateCoverage(rawContract, options = {}) {
  const contract = validateContract(rawContract);
  const baseUrl = options.baseUrl || process.env.QA_BASE_URL || 'http://127.0.0.1:4173';
  const artifactsDir = path.resolve(options.artifactsDir || process.env.QA_ARTIFACTS_DIR || 'artifacts');
  for (const state of contract.states) buildStateUrl(baseUrl, contract, state);
  fs.mkdirSync(artifactsDir, { recursive: true });
  const reportOutput = 'state-coverage/state-coverage-report.json';
  const screenshotOutput = (viewport, state) => `state-coverage/${safeName(viewport.name)}/${safeName(state.id)}.png`;
  const tileOutput = state => `state-coverage/matrix-tiles/${safeName(state.id)}.png`;
  // Reject existing filesystem escapes before starting browser observations.
  resolveArtifactPath(artifactsDir, reportOutput);
  if (contract.matrix) resolveArtifactPath(artifactsDir, contract.matrix.output);
  for (const viewport of contract.viewports) {
    for (const state of contract.states) {
      resolveArtifactPath(artifactsDir, screenshotOutput(viewport, state));
      if (contract.matrix && viewport.name === contract.matrix.viewport && contract.matrix.states.includes(state.id)) {
        resolveArtifactPath(artifactsDir, tileOutput(state));
      }
    }
  }
  const report = { schema_version: '1.0', gate: 'STATE_COVERAGE', name: contract.name, base_url: baseUrl, entry_route: contract.entry_route, generated_at: new Date().toISOString(), checks: [], failures: [], classification: 'UNKNOWN', matrix: { generated: false } };
  const persistReport = () => {
    const failed = report.failures.length || report.runtime_error || report.cleanup_error || report.matrix.error;
    const complete = report.checks.length === contract.viewports.length * contract.states.length && (!contract.matrix || report.matrix.generated);
    report.classification = failed ? 'PRODUCT_QA_FAILED' : complete ? 'PASS' : 'UNKNOWN';
    const reportPath = resolveArtifactPath(artifactsDir, reportOutput);
    fs.mkdirSync(path.dirname(reportPath), { recursive: true });
    fs.writeFileSync(resolveArtifactPath(artifactsDir, reportOutput), JSON.stringify(report, null, 2));
    return reportPath;
  };
  const matrixTilePaths = new Map();
  let browser = null;
  persistReport();

  try {
    browser = await chromium.launch({ headless: true });
    for (const viewport of contract.viewports) {
      for (const state of contract.states) {
        const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: 'reduce', serviceWorkers: 'block' });
        try {
          const page = await context.newPage();
          const consoleErrors = [];
          const pageErrors = [];
          page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
          page.on('pageerror', error => pageErrors.push(String(error)));
          const url = buildStateUrl(baseUrl, contract, state);
          let responseStatus = 0, outer = null, inner = null, assertionResults = [], runtimeError = null, scope = null;
          try {
            const response = await navigateWithinOrigin(page, url);
            responseStatus = response ? response.status() : 0;
            await page.waitForTimeout(state.wait_ms);
            if (new URL(page.url()).origin !== new URL(baseUrl).origin) throw new Error('page scope must preserve the target origin');
            scope = await resolveScope(page, contract, state);
            outer = await overflowMetrics(page);
            inner = scope.kind === 'iframe' ? await overflowMetrics(scope.target) : outer;
            for (const assertion of state.assertions) assertionResults.push(await runAssertion(scope.target, assertion));
            const screenshotPath = resolveArtifactPath(artifactsDir, screenshotOutput(viewport, state));
            fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
            await page.screenshot({ path: resolveArtifactPath(artifactsDir, screenshotOutput(viewport, state)), fullPage: true });
            if (contract.matrix && viewport.name === contract.matrix.viewport && contract.matrix.states.includes(state.id)) {
              const focusSelector = state.focus || state.assertions.find(item => item.type === 'selector')?.selector || 'body';
              const focusLocator = scope.target.locator(focusSelector).first();
              if ((await focusLocator.count()) < 1) throw new Error(`matrix focus selector not found: ${focusSelector}`);
              const tilePath = resolveArtifactPath(artifactsDir, tileOutput(state));
              fs.mkdirSync(path.dirname(tilePath), { recursive: true });
              await focusLocator.screenshot({ path: resolveArtifactPath(artifactsDir, tileOutput(state)) });
              matrixTilePaths.set(state.id, tilePath);
            }
          } catch (error) { runtimeError = String(error?.stack || error); }

          const outerOverflow = outer ? outer.scrollWidth > outer.width + 2 : false;
          const innerOverflow = inner ? inner.scrollWidth > inner.width + 2 : false;
          const semanticPassed = assertionResults.every(item => item.passed);
          const passed = !runtimeError && responseStatus > 0 && responseStatus < 400 && !outerOverflow && !innerOverflow && semanticPassed && consoleErrors.length === 0 && pageErrors.length === 0;
          const check = { viewport: viewport.name, state: state.id, url, final_url: page.url(), response_status: responseStatus, outer, inner, outer_overflow: outerOverflow, inner_overflow: innerOverflow, assertions: assertionResults, semantic_passed: semanticPassed, console_errors: consoleErrors, page_errors: pageErrors, runtime_error: runtimeError, passed };
          report.checks.push(check);
          if (!passed) report.failures.push(check);
        } finally { await context.close(); }
      }
    }
  } catch (error) { report.runtime_error = String(error?.stack || error); }
  finally {
    if (browser) {
      try { await browser.close(); }
      catch (error) { report.cleanup_error = String(error?.stack || error); }
    }
    // Retain browser/check failures before any image reads, allocations or writes.
    persistReport();
  }

  if (contract.matrix) {
    report.matrix = { states: contract.matrix.states, viewport: contract.matrix.viewport, output: contract.matrix.output, generated: false,
      tiles: contract.matrix.states.map(state => ({ state, ...matrixTileEvidence(report.checks, contract.matrix.viewport, state) })) };
    if (report.runtime_error) report.matrix.skipped_reason = 'Browser phase failed; see runtime_error';
    else {
      try {
        await createMatrix(contract, artifactsDir, matrixTilePaths, report.checks);
        report.matrix.generated = true;
      } catch (error) { report.matrix.error = String(error?.stack || error); }
    }
  }
  const reportPath = persistReport();
  return { report, reportPath };
}

async function main() {
  const contractPath = parseArg('--contract') || process.env.QA_STATE_CONTRACT || '';
  if (!contractPath) fail('pass --contract <path> or QA_STATE_CONTRACT');
  const raw = JSON.parse(fs.readFileSync(path.resolve(contractPath), 'utf8'));
  const { report, reportPath } = await runStateCoverage(raw);
  console.log(JSON.stringify({ gate: report.gate, checks: report.checks.length, failures: report.failures.length, classification: report.classification, runtime_error: report.runtime_error, cleanup_error: report.cleanup_error, matrix: report.matrix, report: reportPath }, null, 2));
  if (report.classification !== 'PASS') { console.error('UIUX_STATE_COVERAGE_FAILED'); process.exit(1); }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main().catch(error => { console.error(error?.stack || error); process.exit(1); });
