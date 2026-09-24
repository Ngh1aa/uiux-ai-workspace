#!/usr/bin/env node

/**
 * Provider/framework-neutral browser sanity guard for ordinary web projects.
 *
 * Requires Playwright in the consuming project/environment:
 *   npm install --no-save playwright
 *
 * Environment:
 *   VISUAL_SANITY_BASE_URL=http://127.0.0.1:4173
 *   VISUAL_SANITY_ROUTES=/,/shop,/cart
 *   VISUAL_SANITY_VIEWPORTS=1363x936,1100x900
 *   VISUAL_SANITY_OUT_DIR=qa-artifacts/elementary-visual-integrity
 *   VISUAL_SANITY_INIT_SCRIPT=./scripts/qa-seed-state.js   (optional)
 *   VISUAL_SANITY_CATASTROPHIC_FLOOR=2.6                  (optional)
 *
 * This is a regression signal, not WCAG-conformance proof and not a substitute
 * for opening/inspecting rendered screenshots.
 */

import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const baseURL = process.env.VISUAL_SANITY_BASE_URL || "http://127.0.0.1:4173";
const outputDir = path.resolve(process.env.VISUAL_SANITY_OUT_DIR || "qa-artifacts/elementary-visual-integrity");
const catastrophicFloor = Number(process.env.VISUAL_SANITY_CATASTROPHIC_FLOOR || 2.6);
const initScript = process.env.VISUAL_SANITY_INIT_SCRIPT || "";

const routes = (process.env.VISUAL_SANITY_ROUTES || "/")
  .split(",")
  .map((value) => value.trim())
  .filter(Boolean);

const viewports = (process.env.VISUAL_SANITY_VIEWPORTS || "1363x936,1100x900")
  .split(",")
  .map((value, index) => {
    const match = value.trim().match(/^(\d+)x(\d+)$/i);
    if (!match) throw new Error(`Invalid VISUAL_SANITY_VIEWPORTS entry: ${value}`);
    return { name: `v${index + 1}-${match[1]}x${match[2]}`, width: Number(match[1]), height: Number(match[2]) };
  });

if (!Number.isFinite(catastrophicFloor) || catastrophicFloor <= 1) {
  throw new Error("VISUAL_SANITY_CATASTROPHIC_FLOOR must be a finite number > 1");
}

await mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const report = {
  generatedAt: new Date().toISOString(),
  baseURL,
  routes,
  viewports,
  catastrophicFloor,
  note: "Regression signal only. Human rendered inspection remains required.",
  states: [],
  blockers: [],
};

const addBlocker = (key, message, detail = null) => report.blockers.push({ key, message, detail });

function slug(value) {
  return value.replace(/^https?:\/\//, "").replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "") || "root";
}

async function freezeMotion(page) {
  await page.addStyleTag({ content: `
    *,*::before,*::after{
      animation-duration:.001ms!important;
      animation-delay:0ms!important;
      transition-duration:.001ms!important;
      transition-delay:0ms!important;
      scroll-behavior:auto!important;
    }
  ` });
}

async function snapshot(locator) {
  return locator.evaluate((el) => {
    const parse = (value) => {
      const match = String(value).match(/rgba?\(([^)]+)\)/i);
      if (!match) return { r: 0, g: 0, b: 0, a: 0 };
      const parts = match[1].split(/[\s,\/]+/).filter(Boolean).map(Number);
      return {
        r: parts[0] || 0,
        g: parts[1] || 0,
        b: parts[2] || 0,
        a: Number.isFinite(parts[3]) ? parts[3] : 1,
      };
    };
    const over = (top, bottom) => {
      const alpha = top.a + bottom.a * (1 - top.a);
      if (alpha <= 0) return { r: 255, g: 255, b: 255, a: 1 };
      return {
        r: (top.r * top.a + bottom.r * bottom.a * (1 - top.a)) / alpha,
        g: (top.g * top.a + bottom.g * bottom.a * (1 - top.a)) / alpha,
        b: (top.b * top.a + bottom.b * bottom.a * (1 - top.a)) / alpha,
        a: alpha,
      };
    };
    const channel = (number) => {
      const value = number / 255;
      return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    };
    const luminance = ({ r, g, b }) => 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
    const contrast = (a, b) => {
      const l1 = luminance(a);
      const l2 = luminance(b);
      return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    };

    const ownText = [...el.childNodes]
      .filter((node) => node.nodeType === Node.TEXT_NODE)
      .map((node) => node.textContent || "")
      .join(" ")
      .replace(/\s+/g, " ")
      .trim();
    const interactive = el.matches('a[href],button,[role="button"],input[type="button"],input[type="submit"]');
    const text = (ownText || (interactive ? (el.innerText || el.textContent || "") : ""))
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 160);

    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    const visible = rect.width > 0 && rect.height > 0 && style.display !== "none" && style.visibility !== "hidden" && Number.parseFloat(style.opacity || "1") > 0.05;

    let cursor = el;
    let background = { r: 255, g: 255, b: 255, a: 0 };
    let variableMediaContext = false;
    while (cursor) {
      const computed = getComputedStyle(cursor);
      if (computed.backgroundImage && computed.backgroundImage !== "none") variableMediaContext = true;
      const localBackground = parse(computed.backgroundColor);
      if (localBackground.a > 0) background = over(background, localBackground);
      if (background.a >= 0.995) break;
      cursor = cursor.parentElement;
    }
    if (background.a < 0.995) background = over(background, { r: 255, g: 255, b: 255, a: 1 });

    if (["absolute", "fixed"].includes(style.position)) {
      const figure = el.closest("figure");
      if (figure?.querySelector("img,video,picture")) variableMediaContext = true;
    }

    const foregroundRaw = parse(style.color);
    const foreground = foregroundRaw.a < 0.995 ? over(foregroundRaw, background) : foregroundRaw;
    const fontSize = Number.parseFloat(style.fontSize) || 16;
    const fontWeight = Number.parseInt(style.fontWeight, 10) || 400;
    const threshold = fontSize >= 24 || (fontSize >= 18.66 && fontWeight >= 700) ? 3 : 4.5;

    return {
      tag: el.tagName,
      className: typeof el.className === "string" ? el.className : "",
      text,
      interactive,
      visible,
      inViewport: rect.right > 0 && rect.bottom > 0 && rect.left < innerWidth && rect.top < innerHeight,
      disabled: !!el.disabled || el.getAttribute("aria-disabled") === "true",
      color: style.color,
      effectiveBackground: `rgb(${Math.round(background.r)}, ${Math.round(background.g)}, ${Math.round(background.b)})`,
      ratio: Number(contrast(foreground, background).toFixed(2)),
      threshold,
      variableMediaContext,
    };
  });
}

async function auditText(page, key, stateEntry) {
  const nodes = page.locator([
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "a[href]", "button", "label", "li", "span",
    "strong", "small", "summary", "legend", "td", "th", "dt", "dd", "[role=button]",
  ].join(","));
  stateEntry.text = { checked: 0, variableMediaSkipped: 0 };

  for (let index = 0; index < await nodes.count(); index += 1) {
    const item = await snapshot(nodes.nth(index));
    if (!item.visible || !item.text) continue;
    stateEntry.text.checked += 1;
    if (item.variableMediaContext) {
      stateEntry.text.variableMediaSkipped += 1;
      continue;
    }
    if (item.ratio < catastrophicFloor) {
      addBlocker(key, `catastrophic visible-text contrast ${item.ratio}:1`, { index, ...item });
    }
  }
}

async function auditInteractive(page, key, stateEntry) {
  const nodes = page.locator('a[href],button,[role="button"],input[type="button"],input[type="submit"]');
  stateEntry.interactive = { checked: 0 };

  for (let index = 0; index < await nodes.count(); index += 1) {
    const node = nodes.nth(index);
    let initial;
    try {
      initial = await snapshot(node);
      if (!initial.visible || !initial.text) continue;
      await node.scrollIntoViewIfNeeded();
      await page.waitForTimeout(10);
      initial = await snapshot(node);
    } catch {
      continue;
    }
    if (!initial.visible || !initial.inViewport) continue;
    stateEntry.interactive.checked += 1;

    const check = (name, item) => {
      if (item.variableMediaContext) return;
      if (item.ratio < item.threshold) {
        addBlocker(key, `interactive ${name} contrast ${item.ratio}:1 below ${item.threshold}:1`, { index, ...item });
      }
    };

    check("default", initial);
    if (initial.disabled) continue;

    try {
      await node.hover({ force: true });
      await page.waitForTimeout(15);
      check("hover", await snapshot(node));
      await node.focus();
      await page.waitForTimeout(15);
      check("focus", await snapshot(node));
    } catch (error) {
      addBlocker(key, `interactive state audit failed: ${initial.text}`, String(error));
    }
  }
}

async function auditCoverMedia(page, key, stateEntry) {
  const nodes = page.locator("main img,main video");
  stateEntry.media = { checked: 0, cover: 0 };

  for (let index = 0; index < await nodes.count(); index += 1) {
    const media = await nodes.nth(index).evaluate((element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      const owner = element.closest("figure,section,article,div");
      return {
        tag: element.tagName,
        src: element.getAttribute("src") || element.querySelector?.("source")?.getAttribute("src") || "",
        objectFit: style.objectFit,
        objectPosition: style.objectPosition,
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        visiblePrimarySize: rect.width >= 240 && rect.height >= 220 && style.display !== "none" && style.visibility !== "hidden",
        cropVerified: element.dataset.cropVerified === "true" || owner?.dataset?.cropVerified === "true",
        focalSubject: element.dataset.focalSubject || owner?.dataset?.focalSubject || "",
      };
    });
    if (!media.visiblePrimarySize) continue;
    stateEntry.media.checked += 1;
    if (media.objectFit !== "cover") continue;
    stateEntry.media.cover += 1;
    if (!media.cropVerified || !media.focalSubject) {
      addBlocker(key, "primary/feature cover media lacks verified crop contract", { index, ...media });
    }
  }
}

for (const viewport of viewports) {
  for (const route of routes) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1,
      colorScheme: "light",
      reducedMotion: "reduce",
    });
    if (initScript) await context.addInitScript({ path: path.resolve(initScript) });
    const page = await context.newPage();
    const consoleErrors = [];
    const pageErrors = [];
    page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
    page.on("pageerror", (error) => pageErrors.push(String(error)));

    const url = new URL(route, baseURL).toString();
    const response = await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
    await page.evaluate(async () => { if (document.fonts?.ready) await document.fonts.ready; });
    await freezeMotion(page);
    await page.waitForTimeout(60);

    const key = `${route}@${viewport.name}`;
    const stateEntry = { key, route, viewport, httpStatus: response?.status() || null, consoleErrors, pageErrors };
    if (!response?.ok()) addBlocker(key, `HTTP ${response?.status() ?? "no response"}`);
    if (consoleErrors.length) addBlocker(key, "console errors", consoleErrors);
    if (pageErrors.length) addBlocker(key, "page errors", pageErrors);

    await auditText(page, key, stateEntry);
    await auditInteractive(page, key, stateEntry);
    await auditCoverMedia(page, key, stateEntry);

    await page.evaluate(() => scrollTo(0, 0));
    await page.screenshot({
      path: path.join(outputDir, `${slug(route)}-${viewport.name}-top.png`),
      fullPage: false,
    });
    report.states.push(stateEntry);
    await context.close();
  }
}

await browser.close();
await writeFile(path.join(outputDir, "report.json"), JSON.stringify(report, null, 2));
console.log(`Elementary visual integrity: ${report.states.length} route/viewport states.`);
console.log(`Blockers: ${report.blockers.length}`);
for (const blocker of report.blockers) console.log(JSON.stringify(blocker));
if (report.blockers.length) process.exit(1);
