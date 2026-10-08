// Screenshot each theme preview at phone width for visual review.
// NODE_PATH=<workspace>/node_modules node engine/shoot.js
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '..');
const files = process.argv.slice(2).length ? process.argv.slice(2)
  : ['clay-terracotta', 'grid-cobalt', 'tint-plum', 'masthead-signal'];
(async () => {
  const browser = await require('./browser').launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 900 }, deviceScaleFactor: 1 });
  for (const f of files) {
    await page.goto('file://' + path.join(root, 'themes', f + '.html'));
    await page.screenshot({ path: path.join(root, 'shots', f + '.png'), fullPage: true });
    // also slice into 1100px segments for close review
    const h = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0, i = 0; y < h; y += 1100, i++) {
      await page.screenshot({ path: path.join(root, 'shots', `${f}-${i}.png`), fullPage: true,
        clip: { x: 0, y, width: 390, height: Math.min(1100, h - y) } });
    }
    console.log('shot', f);
  }
  await browser.close();
})();
