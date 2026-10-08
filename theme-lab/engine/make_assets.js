// Generate sample images for the gallery components from our own renders.
// Run after build.py; then run build.py again (images are referenced, not embedded).
// NODE_PATH=<workspace>/node_modules node engine/make_assets.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'assets');
fs.mkdirSync(out, { recursive: true });
const covers = { forest: 'forest-leaf', airy: 'airy-cobalt', clay: 'clay-terracotta', grid: 'grid-cobalt',
  journal: 'journal-cherry', masthead: 'masthead-signal' };
(async () => {
  const b = await require('./browser').launch();
  const p = await b.newPage({ viewport: { width: 390, height: 680 }, deviceScaleFactor: 2 });
  const frag = async (stem) => {
    const html = fs.readFileSync(path.join(root, 'themes', stem + '.fragment.html'), 'utf8');
    const bg = (html.match(/background:(#[0-9A-Fa-f]{6})/) || [0, '#fff'])[1];
    await p.setContent(`<html><body style="margin:0;padding:18px 14px;background:${bg}">${html}</body></html>`);
    await p.waitForTimeout(150);
  };
  for (const [k, stem] of Object.entries(covers)) {
    await frag(stem + '.series');
    await p.screenshot({ path: path.join(out, `cover-${k}.jpg`), type: 'jpeg', quality: 82,
      clip: { x: 0, y: 0, width: 390, height: 680 } });
  }
  // same article in every theme: used where the text claims "one draft, six themes"
  for (const [k, stem] of Object.entries(covers)) {
    await frag(stem);
    await p.screenshot({ path: path.join(out, `same-${k}.jpg`), type: 'jpeg', quality: 82,
      clip: { x: 0, y: 0, width: 390, height: 680 } });
  }
  await frag('forest-leaf.series');
  for (const [i, y] of [[1, 680], [2, 1360]]) {
    await p.screenshot({ path: path.join(out, `long-${i}.jpg`), type: 'jpeg', quality: 82, fullPage: true,
      clip: { x: 0, y, width: 390, height: 680 } });
  }
  const g = await b.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
  await g.goto('file://' + path.join(root, 'index.html') + '#forest-leaf');
  await g.waitForTimeout(1200);
  await g.screenshot({ path: path.join(out, 'gallery.jpg'), type: 'jpeg', quality: 80 });
  console.log(fs.readdirSync(out).join(' '));
  await b.close();
})();
