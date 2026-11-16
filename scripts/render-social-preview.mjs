// Renders docs/assets/social-preview.svg to docs/assets/social-preview.png (1280x640)
// with a local Chromium via Playwright. Nothing leaves the machine.
// Usage: NODE_PATH="$(npm root -g)" node scripts/render-social-preview.mjs
// (needs Playwright installed globally or in the current project).
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import path from "node:path";

const { chromium } = createRequire(import.meta.url)("playwright");

const here = path.dirname(fileURLToPath(import.meta.url));
const assets = path.resolve(here, "../docs/assets");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 1 });
await page.goto("file://" + path.join(assets, "social-preview.svg"));
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: path.join(assets, "social-preview.png") });
await browser.close();
