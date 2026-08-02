import { chromium } from '/Users/yin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';

const browser = await chromium.launch({ headless: true });
const out = new URL('./ui/', import.meta.url);
await fs.mkdir(out, { recursive: true });

for (const fate of ['reply', 'coffee']) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await page.addInitScript(() => localStorage.setItem('game_locale', 'en'));
  await page.goto(`http://127.0.0.1:4272/?user_name=Alexandria%20Montgomery&outcome=${fate}`, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: '#alteru-guest-banner{display:none!important}' });
  await page.waitForFunction(() => window.__LAST_STRAW?.getState().phase === 'ready');
  await page.evaluate(value => window.__LAST_STRAW.forceOutcome(value), fate);
  await page.waitForFunction(() => window.__LAST_STRAW?.getState().phase === 'result');
  await page.waitForTimeout(1700);
  await page.screenshot({ path: new URL(`390x844-platform-layout-${fate}-playing.png`, out).pathname });
  await page.waitForFunction(() => document.querySelector('#result')?.classList.contains('resolved'), null, { timeout: 12000 });
  await page.waitForTimeout(360);
  await page.screenshot({ path: new URL(`390x844-platform-layout-${fate}-final.png`, out).pathname });
  const metrics = await page.evaluate(() => {
    const video = document.querySelector('#result-video');
    return { state: window.__LAST_STRAW.getState(), duration: video.duration, video: [video.videoWidth, video.videoHeight], overflow: document.documentElement.scrollWidth > innerWidth || document.documentElement.scrollHeight > innerHeight };
  });
  console.log(JSON.stringify({ fate, ...metrics }));
  if (metrics.duration < 9.9 || metrics.duration > 10.2 || metrics.overflow) throw new Error(`bad ${fate} result`);
  await page.close();
}

const external = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
await external.goto('http://127.0.0.1:4272/', { waitUntil: 'networkidle' });
await external.waitForFunction(() => window.__LAST_STRAW?.getState().phase === 'ready');
await external.screenshot({ path: new URL('390x844-external-guest-ready.png', out).pathname });
const guest = await external.evaluate(() => {
  const banner = document.querySelector('#alteru-guest-banner');
  return { exists: Boolean(banner), height: banner?.getBoundingClientRect().height ?? 0, phase: window.__LAST_STRAW.getState().phase };
});
console.log(JSON.stringify({ externalGuest: guest }));
await browser.close();
