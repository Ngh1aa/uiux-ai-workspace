import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

async function main() {
  const configPath = process.argv[2];
  if (!configPath) {
    throw new Error("usage: node integrations/playwright/capture.mjs <config.json>");
  }

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    throw new Error("Playwright is optional. Install with: npm install -D playwright");
  }

  const config = JSON.parse(await fs.readFile(configPath, "utf8"));
  const outputDir = path.resolve(config.outputDir || ".uiux-evidence");
  await fs.mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const manifest = { schema_version: 1, base_url: config.baseUrl, captures: [] };

  try {
    for (const viewport of config.viewports || []) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
      });
      const page = await context.newPage();

      for (const route of config.routes || []) {
        const consoleErrors = [];
        const failedRequests = [];
        page.removeAllListeners("console");
        page.removeAllListeners("requestfailed");
        page.on("console", (msg) => {
          if (msg.type() === "error") consoleErrors.push(msg.text());
        });
        page.on("requestfailed", (request) => {
          failedRequests.push({
            url: request.url(),
            error: request.failure()?.errorText || "unknown",
          });
        });

        const slug = `${route.name}-${viewport.name}`;
        const url = new URL(route.path, config.baseUrl).toString();
        const response = await page.goto(url, { waitUntil: "networkidle" });
        const htmlPath = path.join(outputDir, `${slug}.html`);
        const screenshotPath = path.join(outputDir, `${slug}.png`);
        const logPath = path.join(outputDir, `${slug}.json`);

        await fs.writeFile(htmlPath, await page.content(), "utf8");
        await page.screenshot({ path: screenshotPath, fullPage: true });
        await fs.writeFile(
          logPath,
          JSON.stringify(
            {
              url,
              status: response?.status() ?? null,
              console_errors: consoleErrors,
              failed_requests: failedRequests,
            },
            null,
            2,
          ),
          "utf8",
        );

        manifest.captures.push({
          route: route.name,
          viewport: viewport.name,
          url,
          html: htmlPath,
          screenshot: screenshotPath,
          runtime_log: logPath,
        });
      }

      await context.close();
    }
  } finally {
    await browser.close();
  }

  await fs.writeFile(
    path.join(outputDir, "manifest.json"),
    JSON.stringify(manifest, null, 2),
    "utf8",
  );
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
