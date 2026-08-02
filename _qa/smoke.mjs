import { chromium } from '/Users/yin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';

const base = 'http://127.0.0.1:4272/?user_name=Alexandria%20Montgomery&outcome=boss';
await fs.mkdir(new URL('./ui/', import.meta.url), { recursive: true });
const browser = await chromium.launch({ headless: true });

for (const [width, height] of [[390, 844], [320, 568]]) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.goto(base, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: '#alteru-guest-banner{display:none!important}' });
  await page.waitForFunction(() => window.__LAST_STRAW?.getState().phase === 'ready');
  const prefix = `${width}x${height}-platform-layout`;
  await page.screenshot({ path: new URL(`./ui/${prefix}-ready.png`, import.meta.url).pathname });
  await page.evaluate(() => window.__LAST_STRAW.dropAt(.18));
  await page.waitForFunction(() => window.__LAST_STRAW?.getState().phase === 'result', null, { timeout: 12000 });
  await page.waitForTimeout(1600);
  await page.screenshot({ path: new URL(`./ui/${prefix}-boss-result-playing.png`, import.meta.url).pathname });
  await page.waitForFunction(() => document.querySelector('#result')?.classList.contains('resolved'), null, { timeout: 12000 });
  await page.waitForTimeout(360);
  await page.screenshot({ path: new URL(`./ui/${prefix}-boss-result-final.png`, import.meta.url).pathname });
  const state = await page.evaluate(() => ({
    game: window.__LAST_STRAW?.getState(),
    body: { sw: document.body.scrollWidth, cw: document.body.clientWidth, sh: document.body.scrollHeight, ch: document.body.clientHeight },
    button: (() => { const r = document.querySelector('#again')?.getBoundingClientRect(); return r && { width: r.width, height: r.height }; })(),
    video: (() => { const v = document.querySelector('#result-video'); return v && { duration: v.duration, width: v.videoWidth, height: v.videoHeight, paused: v.paused }; })(),
  }));
  console.log(JSON.stringify({ width, height, ...state }));
  if (state.body.sw > state.body.cw || state.body.sh > state.body.ch) throw new Error(`overflow ${width}x${height}`);
  if (!state.button || state.button.height < 44) throw new Error(`small result button ${width}x${height}`);
  await page.close();
}

await browser.close();
