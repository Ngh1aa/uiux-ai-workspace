const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync(path.join(__dirname, '../scripts/capture-example.cjs'), 'utf8');

// Exercise the real runner's failure/exit/report contract without browser downloads.
// These doubles are control-flow evidence, never rendered UI evidence.
async function runGate({ missing = [], axe = true, emptyAxe = false, partial = false, ci = false, pageFailure = false, engines = 'chromium,webkit,firefox' } = {}) {
  const writes = [];
  const process = { argv: ['node', 'capture-example.cjs', '/review', engines, ...(partial ? ['--allow-partial'] : [])], env: ci ? { CI: 'true' } : {}, exitCode: 0 };
  const playwright = Object.fromEntries(['chromium', 'webkit', 'firefox'].map(engine => [engine, {
    async launch() {
      if (missing.includes(engine)) throw new Error(`${engine} unavailable`);
      return {
        async close() {},
        async newPage({ colorScheme }) {
          let search = '';
          const locator = selector => ({
            async click() {}, async waitFor() {}, async fill(value) { search = value; },
            async count() { return search ? 1 : 2; },
            async isVisible() { return selector !== 'form'; },
            async inputValue() { return '0901234567'; },
            async textContent() { return 'CF-0001'; },
          });
          return {
            setDefaultTimeout() {}, on() {}, mouse: { async move() {} },
            async goto() { if (pageFailure) throw new Error('fixture navigation failed'); },
            async evaluate(fn) {
              const code = String(fn);
              if (code.includes('window.axe.run')) return { violations: [], passes: 1, incomplete: [] };
              if (code.includes('scrollWidth')) return false;
              if (code.includes('dataset.theme')) return colorScheme;
              return true;
            },
            getByRole: locator, locator,
            async reload() {}, async addScriptTag() {}, async screenshot() {},
            async addStyleTag() {}, async close() {},
          };
        },
      };
    },
  }]));
  const modules = {
    playwright,
    'node:fs': { readFileSync() { return emptyAxe ? '' : 'axe fixture'; }, mkdirSync() {}, writeFileSync(file, data) { writes.push(JSON.parse(data)); } },
    'node:path': path,
    'node:http': { createServer() { return { listen(port, host, ready) { ready(); }, address() { return { port: 1234 }; }, close() {} }; } },
  };
  const require = name => { if (!(name in modules)) throw new Error(`unexpected module ${name}`); return modules[name]; };
  require.resolve = () => { if (!axe) throw new Error('axe missing'); return '/axe.min.js'; };
  await vm.runInNewContext(source, { require, __dirname: path.join(__dirname, '../scripts'), process, console: { log() {}, error() {} } });
  return { exitCode: process.exitCode, report: writes.at(-1), writes };
}

test('strict review requires the full three-engine matrix', async () => {
  const result = await runGate();
  assert.equal(result.exitCode, 0);
  assert.equal(result.report.status, 'PASS');
  assert.equal(result.report.runs.length, 36);
  assert.equal(result.report.axe, 'RUN');
  assert.equal(result.writes[0].status, 'RUNNING');
});

test('one unavailable engine fails even when two engines work', async () => {
  const result = await runGate({ missing: ['webkit'] });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
  assert.match(result.report.error, /webkit|matrix|engine/i);
});

test('missing axe cannot yield a strict PASS', async () => {
  const result = await runGate({ axe: false });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
  assert.match(result.report.error, /axe/i);
});

test('an empty axe asset cannot silently skip strict accessibility checks', async () => {
  const result = await runGate({ emptyAxe: true });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
});

test('zero engines produces a failure report instead of leaving a stale PASS', async () => {
  const result = await runGate({ missing: ['chromium', 'webkit', 'firefox'] });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
  assert.equal(result.writes[0].status, 'RUNNING');
});

test('a page failure preserves diagnostics and exits nonzero', async () => {
  const result = await runGate({ pageFailure: true });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
  assert.match(result.report.error, /navigation failed/);
});

test('partial local review is explicit and never labelled PASS', async () => {
  const result = await runGate({ missing: ['webkit'], axe: false, partial: true });
  assert.equal(result.exitCode, 0);
  assert.equal(result.report.status, 'PARTIAL');
  assert.equal(result.report.runs.length, 24);
});

test('CI cannot opt out of required engines', async () => {
  const result = await runGate({ missing: ['webkit'], partial: true, ci: true });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
});

test('CI cannot opt out of axe', async () => {
  const result = await runGate({ axe: false, partial: true, ci: true });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
});

test('CI cannot silently request only one engine', async () => {
  const result = await runGate({ engines: 'chromium', ci: true });
  assert.equal(result.exitCode, 1);
  assert.equal(result.report.status, 'FAIL');
  assert.match(result.report.error, /complete.*matrix/);
});

test('an explicit local single-engine review checks its declared matrix', async () => {
  const result = await runGate({ engines: 'chromium' });
  assert.equal(result.exitCode, 0);
  assert.equal(result.report.runs.length, 12);
  assert.equal(result.report.status, 'PASS');
});
