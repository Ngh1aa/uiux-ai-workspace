import { test, expect } from '@playwright/test';
import { inspectRenderedUX, runUXRegression, validateUXContract, qaViewports } from '../scripts/ux-regression.mjs';

const pageHTML = content => `<!doctype html><html><head><style>html{background:#fff;color:#17202b}body{margin:0;padding:20px}button,label{min-height:44px}label{display:flex;justify-content:space-between;padding:10px}.switch{width:44px;height:44px;border-radius:20px}button{background:#18242e;color:#fff;border-radius:16px}</style></head><body>${content}</body></html>`;

test('browser and accessibility share desktop/mobile defaults and reject incomplete viewport matrices', () => {
  expect(qaViewports().map(item => item.name)).toEqual(['desktop', 'mobile']);
  for (const value of [[], [{ name: 'mobile', width: 0, height: 844 }], [{ name: 'x', width: 390, height: 844 }, { name: 'x', width: 1440, height: 1000 }]]) expect(() => qaViewports(JSON.stringify(value))).toThrow();
});

test('catches inherited white text on white without a selector whitelist', async ({ page }) => {
  await page.setContent(pageHTML('<main style="color:white"><h1>Hidden heading</h1><p id="balance">Target €500</p></main>'));
  const broken = await inspectRenderedUX(page);
  expect(broken.failures.some(item => item.target === '#balance' && item.requirement === 'UX-FOREGROUND')).toBe(true);
  await page.locator('main').evaluate(element => element.style.color = '#17202b');
  expect((await inspectRenderedUX(page)).failures).toEqual([]);
});

test('opaque local backplates stop inherited gradient ambiguity and compositing is calculated', async ({ page }) => {
  await page.setContent(pageHTML('<main style="background:linear-gradient(white,black)"><p id="variable">Needs manual inspection</p><p id="plate" style="background:white;color:rgba(0,0,0,.8)">Solid backplate</p><p id="collapse" style="background:rgba(255,255,255,.5);color:white">Invisible</p></main>'));
  const report = await inspectRenderedUX(page);
  expect(report.unknown.some(item => item.target === '#variable')).toBe(true);
  expect(report.unknown.some(item => item.target === '#plate')).toBe(false);
  expect(report.unknown.some(item => item.target === '#collapse')).toBe(true);
  expect(report.inspected_text).toBe(1);
});

test('off-canvas skip links are excluded until focused, while below-fold text is inspected', async ({ page }) => {
  await page.setContent(pageHTML('<a id="skip" href="#below" style="position:fixed;top:-100px;color:white">Skip</a><p id="below" style="margin-top:2000px;color:white">Below fold hidden text</p>'));
  const first = await inspectRenderedUX(page);
  expect(first.failures.some(item => item.target === '#skip')).toBe(false);
  expect(first.failures.some(item => item.target === '#below')).toBe(true);
  await page.evaluate(() => scrollTo(0, 1200));
  expect((await inspectRenderedUX(page)).failures.some(item => item.target === '#skip')).toBe(false);
  await page.locator('#skip').evaluate(element => element.style.top = '10px');
  await page.locator('#skip').focus();
  expect((await inspectRenderedUX(page)).failures.some(item => item.target === '#skip')).toBe(true);
});

test('overflow, broken visible images and reduced motion control reset are detected', async ({ page }) => {
  await page.setContent(pageHTML('<div style="width:3000px">Overflow</div><img src="data:image/png;base64,bad" alt="Broken"><input id="switch" type="checkbox" style="opacity:0"><style>@media(prefers-reduced-motion:reduce){input{opacity:1!important}}</style>'));
  const contract = { schema_version: 1, checks: [{ id: 'HIDDEN-NATIVE', kind: 'style-range', selector: '#switch', property: 'opacity', max: 0 }] };
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const broken = await runUXRegression(page, { route: '/', contract });
  expect(broken.failures.map(item => item.requirement)).toEqual(expect.arrayContaining(['UX-OVERFLOW', 'UX-MEDIA']));
  expect(broken.checks[0].status).toBe('FAIL');
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  expect((await runUXRegression(page, { route: '/', contract })).checks[0].status).toBe('PASS');
});

test('declared geometry catches square reset and wrong row anatomy, without banning square styles', async ({ page }) => {
  await page.setContent(pageHTML('<button id="cta">Continue</button><label id="row">Alerts<span class="switch"></span></label>'));
  const contract = { schema_version: 1, checks: [
    { id: 'CTA', kind: 'style-range', selector: '#cta', property: 'border-top-left-radius', min: 12 },
    { id: 'ALIGN', kind: 'right-aligned', selector: '.switch', within: '#row' },
    { id: 'HIT', kind: 'hit-target', selector: '.switch', min: 44 }
  ] };
  expect((await runUXRegression(page, { route: '/', contract })).status).toBe('PASS');
  await page.addStyleTag({ content: '*{border-radius:0!important}#row{justify-content:flex-start}' });
  expect((await runUXRegression(page, { route: '/', contract })).checks.filter(item => item.status === 'FAIL').map(item => item.id)).toEqual(['CTA', 'ALIGN']);
  expect((await runUXRegression(page, { route: '/' })).status).toBe('PASS');
});

test('obscuring reviewer overlay and missing selectors fail instead of empty PASS', async ({ page }) => {
  await page.setContent(pageHTML('<button id="cta">Continue</button><div id="reviewer" style="position:fixed;inset:0;background:#ddd"></div>'));
  const report = await runUXRegression(page, { route: '/', contract: { schema_version: 1, checks: [
    { id: 'EXPOSED', kind: 'unobscured', selector: '#cta' },
    { id: 'REVIEWER', kind: 'absent-or-hidden', selector: '#reviewer' },
    { id: 'MISSING', kind: 'hit-target', selector: '#does-not-exist' }
  ] } });
  expect(report.checks.map(item => item.status)).toEqual(['FAIL', 'FAIL', 'FAIL']);
  expect(report.visual_review).toBe('UNKNOWN');
});

for (const persistent of [false, true]) {
  test(`keyboard toggle persistence ${persistent ? 'passes and restores' : 'fails for reverted state'}`, async ({ page }) => {
    // First-party local/demo fixture; no remote account settings are touched.
    await page.route('http://ux-fixture.test/**', route => route.fulfill({ contentType: 'text/html', body: pageHTML(`<label for="alerts">Alerts<input id="alerts" type="checkbox"></label><script>const x=document.querySelector('#alerts');${persistent ? "x.checked=localStorage.getItem('alerts')==='true';x.onchange=()=>localStorage.setItem('alerts',x.checked);" : ''}</script>`) }));
    await page.goto('http://ux-fixture.test/settings');
    const result = await runUXRegression(page, { route: '/settings', contract: { schema_version: 1, checks: [{ id: 'PERSIST', kind: 'toggle-persistence', selector: '#alerts' }] } });
    expect(result.checks[0].status).toBe(persistent ? 'PASS' : 'FAIL');
    expect(await page.locator('#alerts').isChecked()).toBe(false);
  });
}

test('rejects unknown checks, duplicate IDs, missing bounds and remote routes', () => {
  for (const check of [
    { id: 'A', kind: 'execute', selector: 'body' },
    { id: 'A', kind: 'style-range', selector: 'body', property: 'background' },
    { id: 'A', kind: 'style-range', selector: 'body', property: 'opacity' },
    { id: 'A', kind: 'hit-target', selector: 'body', route: '//other.example' },
    { id: 'A', kind: 'hit-target', selector: 'body', min: 44, max: 4 },
    { id: 'A', kind: 'hit-target', selector: 'body', pass: true },
    { id: 'UX-FOREGROUND', kind: 'hit-target', selector: 'body' }
  ]) expect(() => validateUXContract({ schema_version: 1, checks: [check] })).toThrow();
  expect(() => validateUXContract({ schema_version: 1, checks: [{ id: 'A', kind: 'hit-target', selector: 'body' }, { id: 'A', kind: 'hit-target', selector: 'body' }] })).toThrow();
});
