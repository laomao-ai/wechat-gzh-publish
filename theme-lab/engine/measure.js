// Measure computed typography of each theme's article fragment at 390px width.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const keys = process.argv.slice(2);

(async () => {
  const b = await require('./browser').launch();
  const p = await b.newPage({ viewport: { width: 390, height: 800 } });
  const out = [];
  for (const k of keys) {
    const html = fs.readFileSync(path.join(root, 'themes', k + '.fragment.html'), 'utf8');
    await p.setContent('<body style="margin:0">' + html + '</body>');
    const r = await p.evaluate(() => {
      const root = document.body.firstElementChild;
      const R = root.getBoundingClientRect();
      const ps = [...root.querySelectorAll('p')].filter(e => {
        const t = e.innerText.trim();
        return t.length > 40 && !e.closest('table');
      });
      // body paragraph = most common font-size among long paragraphs
      const cnt = {};
      ps.forEach(e => { const fs = getComputedStyle(e).fontSize; cnt[fs] = (cnt[fs] || 0) + 1; });
      const bodyFs = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0][0];
      const bp = ps.find(e => getComputedStyle(e).fontSize === bodyFs);
      const s = getComputedStyle(bp);
      const br = bp.getBoundingClientRect();
      const lh = parseFloat(s.lineHeight) / parseFloat(s.fontSize);
      // sizes of the largest text (title) and section headings
      const sizes = [...root.querySelectorAll('p,span')].map(e => parseFloat(getComputedStyle(e).fontSize));
      return {
        family: s.fontFamily.split(',')[0].replace(/"/g, ''),
        size: s.fontSize, lh: lh.toFixed(2), ls: s.letterSpacing, color: s.color,
        weight: s.fontWeight, margin: s.marginBottom,
        padL: Math.round(br.left - R.left), padR: Math.round(R.right - br.right),
        max: Math.max(...sizes) + 'px', align: s.textAlign,
      };
    });
    out.push([k, r]);
  }
  console.log(JSON.stringify(out, null, 1));
  await b.close();
})();
