// 渲染 README 头图：node engine/shoot_hero.js -> ../docs/images/hero.jpg
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await require('./browser').launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 715 }, deviceScaleFactor: 1.5 });
  await p.goto('file:///' + path.join(__dirname, 'readme_hero.html').replace(/\\/g, '/'));
  await p.waitForTimeout(500);
  const out = path.join(__dirname, '..', '..', 'docs', 'images', 'hero.jpg');
  await p.screenshot({ path: out, type: 'jpeg', quality: 85 });
  console.log(out);
  await b.close();
})();
