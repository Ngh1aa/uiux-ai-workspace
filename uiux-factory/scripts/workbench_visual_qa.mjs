import { chromium } from "playwright";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const WEB = path.join(ROOT, "apps", "web");
const OUT = path.resolve(process.argv[2] || path.join(ROOT, "artifacts", "workbench-visual-qa"));
const SKILLS = path.resolve(ROOT, "..", "skills_UIUX");

const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "tablet", width: 1024, height: 900 },
  { name: "mobile", width: 390, height: 844 },
];

const REQUIRED_SKILLS = [
  "visual-design-direction/SKILL.md",
  "brand-distinctiveness-and-visual-signature/SKILL.md",
  "visual-taste-calibration/SKILL.md",
  "interaction-patterns-and-form-ux/SKILL.md",
  "ui-craft-and-visual-qa/SKILL.md",
];

const CONTENT_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
};

function staticServer(root) {
  return http.createServer((req, res) => {
    const url = new URL(req.url || "/", "http://127.0.0.1");
    if (url.pathname.startsWith("/api/")) {
      res.writeHead(503, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "dogfood bridge intentionally unavailable" }));
      return;
    }
    const relative = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname);
    const target = path.resolve(root, "." + relative);
    if (!target.startsWith(path.resolve(root))) {
      res.writeHead(403); res.end("forbidden"); return;
    }
    fs.readFile(target, (error, data) => {
      if (error) { res.writeHead(404); res.end("not found"); return; }
      res.writeHead(200, {
        "Content-Type": CONTENT_TYPES[path.extname(target)] || "application/octet-stream",
        "Cache-Control": "no-store",
      });
      res.end(data);
    });
  });
}

function clamp(value) { return Math.max(0, Math.min(100, Math.round(value))); }
function average(values) { return values.reduce((a, b) => a + b, 0) / Math.max(1, values.length); }

function sourceAudit() {
  const html = fs.readFileSync(path.join(WEB, "index.html"), "utf8");
  const css = fs.readFileSync(path.join(WEB, "styles.css"), "utf8");
  const app = fs.readFileSync(path.join(WEB, "app.js"), "utf8");
  const skills = REQUIRED_SKILLS.map(relative => ({ relative, exists: fs.existsSync(path.join(SKILLS, relative)) }));

  const signatureTokens = ["--ink:", "--paper:", "--accent:", "--font-display:", "--focus:"];
  const oldGenericTells = ["--grad:", "linear-gradient(135deg", ".smart-card", ".panel {", "glassmorphism"];
  const interactionSignals = ["focus-visible", "prefers-reduced-motion", "aria-label", "Auto inspiration", "sandbox=\"allow-scripts\""];

  return {
    skills,
    skillCoverage: skills.filter(item => item.exists).length / REQUIRED_SKILLS.length,
    signatureTokenCoverage: signatureTokens.filter(token => css.includes(token)).length / signatureTokens.length,
    oldGenericTellCount: oldGenericTells.filter(token => css.includes(token) || html.includes(token)).length,
    interactionSignalCoverage: interactionSignals.filter(token => css.includes(token) || html.includes(token) || app.includes(token)).length / interactionSignals.length,
    accentUsageCount: (css.match(/var\(--accent\)/g) || []).length,
    largeRadiusRuleCount: (css.match(/border-radius:\s*(?:2[0-9]|[3-9][0-9])px/g) || []).length,
    iframeSandboxed: html.includes('sandbox="allow-scripts"') && !html.includes("allow-same-origin"),
  };
}

const DOM_AUDIT = `() => {
  const visible = el => {
    const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0.01 && r.width > 0 && r.height > 0;
  };
  const text = el => (el.innerText || el.textContent || '').trim();
  const controls = [...document.querySelectorAll('button,input,select,textarea,[role="button"]')].filter(visible);
  const unlabeled = controls.filter(el => {
    if (el.matches('input[type="radio"],input[type="checkbox"]')) return false;
    const aria = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby');
    const title = el.getAttribute('title');
    const id = el.id;
    const label = id ? document.querySelector('label[for="' + CSS.escape(id) + '"]') : null;
    const wrapped = el.closest('label');
    return !aria && !title && !label && !wrapped && !text(el) && !el.getAttribute('placeholder');
  });
  const small = controls.filter(el => {
    if (el.disabled) return false;
    const r = el.getBoundingClientRect();
    return r.width < 24 || r.height < 24;
  });
  const imgs = [...document.images].filter(visible);
  const missingAlt = imgs.filter(img => !img.hasAttribute('alt'));
  const root = document.documentElement;
  const body = document.body;
  const scrollWidth = Math.max(root.scrollWidth, body ? body.scrollWidth : 0);
  const clientWidth = root.clientWidth;
  const h1s = [...document.querySelectorAll('h1')].filter(visible);
  const main = [...document.querySelectorAll('main')].filter(visible);
  const rect = selector => {
    const el = document.querySelector(selector); if (!el || !visible(el)) return null;
    const r = el.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height};
  };
  return {
    scrollWidth, clientWidth, overflow: Math.max(0, scrollWidth - clientWidth),
    h1Count: h1s.length, mainCount: main.length,
    controlCount: controls.length, unlabeledCount: unlabeled.length,
    smallTargetCount: small.length, missingAltCount: missingAlt.length,
    workspace: rect('.workspace-shell'), rail: rect('.composer-rail'), canvas: rect('.studio-canvas'),
    topbar: rect('.topbar'), intelligence: rect('.intelligence-board'), runStage: rect('.run-stage'),
    bodyBg: getComputedStyle(document.body).backgroundColor,
    bodyColor: getComputedStyle(document.body).color,
    h1FontSize: h1s[0] ? parseFloat(getComputedStyle(h1s[0]).fontSize) : 0,
    h1Family: h1s[0] ? getComputedStyle(h1s[0]).fontFamily : '',
  };
}`;

function scoreViewport(name, metrics) {
  let responsive = 100;
  if (metrics.overflow > 2) responsive -= 45;
  if (!metrics.workspace || !metrics.canvas) responsive -= 20;
  if (name === "mobile") {
    if (metrics.workspace && metrics.workspace.width > 400) responsive -= 25;
    if (metrics.h1FontSize > 42) responsive -= 10;
  }

  let interaction = 100;
  interaction -= Math.min(50, metrics.unlabeledCount * 12);
  interaction -= Math.min(35, metrics.smallTargetCount * 3);
  interaction -= Math.min(30, metrics.missingAltCount * 10);

  let hierarchy = 100;
  if (metrics.h1Count !== 1) hierarchy -= 30;
  if (metrics.mainCount !== 1) hierarchy -= 25;
  if (metrics.h1FontSize < 30) hierarchy -= 18;
  if (!/Iowan|Baskerville|Times/i.test(metrics.h1Family)) hierarchy -= 8;
  if (!metrics.intelligence || !metrics.runStage) hierarchy -= 10;

  return { responsive: clamp(responsive), interaction: clamp(interaction), hierarchy: clamp(hierarchy) };
}

async function run() {
  fs.mkdirSync(OUT, { recursive: true });
  const source = sourceAudit();
  const server = staticServer(WEB);
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  const base = `http://127.0.0.1:${address.port}/`;
  const browser = await chromium.launch({ headless: true });
  const evidence = [];

  try {
    for (const viewport of VIEWPORTS) {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: "reduce" });
      const page = await context.newPage();
      const consoleErrors = [];
      const pageErrors = [];
      page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });
      page.on("pageerror", error => pageErrors.push(String(error)));
      await page.goto(base, { waitUntil: "networkidle", timeout: 30000 });
      await page.waitForTimeout(250);
      const metrics = await page.evaluate(DOM_AUDIT);
      const screenshot = path.join(OUT, `workbench-${viewport.name}.png`);
      await page.screenshot({ path: screenshot, fullPage: true });
      evidence.push({ viewport, metrics, score: scoreViewport(viewport.name, metrics), consoleErrors, pageErrors, screenshot });
      await context.close();
    }
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }

  const runtimeClean = evidence.every(item => item.consoleErrors.length === 0 && item.pageErrors.length === 0);
  const viewportScores = evidence.map(item => item.score);
  const responsive = clamp(average(viewportScores.map(s => s.responsive)));
  const interaction = clamp(average(viewportScores.map(s => s.interaction)));
  const hierarchy = clamp(average(viewportScores.map(s => s.hierarchy)));
  const brand = clamp(70 + source.signatureTokenCoverage * 18 + Math.min(10, source.accentUsageCount) * 1.2 - source.oldGenericTellCount * 8);
  const antiGeneric = clamp(96 - source.oldGenericTellCount * 18 - Math.max(0, source.largeRadiusRuleCount - 2) * 4);
  const skillGrounding = clamp(source.skillCoverage * 100);
  const accessibility = clamp(interaction - (source.iframeSandboxed ? 0 : 20));
  const overall = clamp(average([hierarchy, responsive, interaction, brand, antiGeneric, skillGrounding, accessibility]));

  const issues = [];
  for (const item of evidence) {
    const { name } = item.viewport;
    if (item.metrics.overflow > 2) issues.push({ severity:"P0", category:"responsive", viewport:name, evidence:`horizontal overflow ${item.metrics.overflow}px`, recommendation:"Repair Workbench responsive composition before merge." });
    if (item.pageErrors.length || item.consoleErrors.length) issues.push({ severity:"P0", category:"runtime", viewport:name, evidence:`runtime=${item.pageErrors.length}, console=${item.consoleErrors.length}`, recommendation:"Resolve browser runtime errors." });
    if (item.metrics.unlabeledCount) issues.push({ severity:"P1", category:"interaction", viewport:name, evidence:`${item.metrics.unlabeledCount} unlabeled controls`, recommendation:"Give every visible control an accessible name." });
    if (item.metrics.smallTargetCount > 3) issues.push({ severity:"P1", category:"interaction", viewport:name, evidence:`${item.metrics.smallTargetCount} obvious controls below 24px`, recommendation:"Increase obvious control target size or spacing." });
    if (item.metrics.h1Count !== 1 || item.metrics.mainCount !== 1) issues.push({ severity:"P1", category:"hierarchy", viewport:name, evidence:`h1=${item.metrics.h1Count}, main=${item.metrics.mainCount}`, recommendation:"Restore one clear page H1 and one main landmark." });
  }
  if (source.oldGenericTellCount) issues.push({ severity:"P1", category:"anti-generic", viewport:"all", evidence:`${source.oldGenericTellCount} deprecated generic visual tells found`, recommendation:"Remove old gradient/card-heavy visual language." });
  if (!source.iframeSandboxed) issues.push({ severity:"P0", category:"security", viewport:"all", evidence:"preview iframe sandbox regressed", recommendation:"Restore sandbox=allow-scripts without allow-same-origin." });

  const blocking = issues.some(issue => issue.severity === "P0" || issue.severity === "P1");
  const threshold = 92;
  const status = !blocking && runtimeClean && overall >= threshold ? "passed" : "repair_required";
  const report = {
    schema_version: "1.0.0",
    generated_by: "WorkbenchVisualCritic",
    status,
    threshold,
    score: { overall, hierarchy, responsive, interaction_clarity: interaction, brand_distinctiveness: brand, anti_generic: antiGeneric, skill_grounding: skillGrounding, accessibility_sanity: accessibility },
    skills_used: REQUIRED_SKILLS,
    source_audit: source,
    evidence,
    issues,
    gates: {
      desktop_rendered: evidence.some(item => item.viewport.name === "desktop"),
      tablet_rendered: evidence.some(item => item.viewport.name === "tablet"),
      mobile_rendered: evidence.some(item => item.viewport.name === "mobile"),
      runtime_clean: runtimeClean,
      no_blocking_issues: !blocking,
      craft_threshold_met: overall >= threshold,
      iframe_sandbox_preserved: source.iframeSandboxed,
    },
    notes: [
      "This is a deterministic dogfood Visual Critic grounded in the five requested skills_UIUX policies.",
      "Screenshots are durable workflow artifacts and should be inspected when making subjective craft claims.",
      "Automated accessibility evidence is a smoke gate, not WCAG certification.",
    ],
  };

  fs.writeFileSync(path.join(OUT, "workbench-visual-critic.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ status, threshold, score: report.score, issues }, null, 2));
  if (status !== "passed") process.exitCode = 1;
}

run().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
