// 把 cards.py 生成的 HTML 卡片截成 JPG，并在截图前做渲染后实测校验。
// usage: node shoot_cards.js <cards_dir>
// 校验思路致谢 op7418/guizang-social-card-skill（"渲染后量，而不是凭感觉"），代码原创。
//   ERROR 越界：元素超出画布，或文字在自身盒子里被截断 → 退出码 1
//   WARN  字太小：正文低于画布宽度 1.6%，手机上基本看不清（页眉页脚、等宽小标签是装饰，不查）
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

function audit() {
  const W = innerWidth, H = innerHeight, minFs = W * 0.016, out = [];
  const name = el => el.className ? el.tagName.toLowerCase() + '.' + el.className : el.tagName.toLowerCase();
  for (const el of document.body.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if (r.left < -1 || r.top < -1 || r.right > W + 1 || r.bottom > H + 1)
      out.push(['ERROR', `${name(el)} 超出画布 (${Math.round(r.right)}x${Math.round(r.bottom)} > ${W}x${H})`]);
    if (getComputedStyle(el).overflow !== 'visible' &&
        (el.scrollWidth > el.clientWidth + 2 || el.scrollHeight > el.clientHeight + 2))
      out.push(['ERROR', `${name(el)} 内容被截断`]);
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    const size = parseFloat(getComputedStyle(el).fontSize);
    const deco = el.closest('.top,.foot,.tag,th');
    if (own && !deco && size < minFs) out.push(['WARN', `${name(el)} 字号 ${size}px < ${minFs.toFixed(0)}px`]);
  }
  const b = document.body;
  if (b.scrollHeight > H + 2 || b.scrollWidth > W + 2) out.push(['ERROR', `内容总高 ${b.scrollHeight}px 超出画布 ${H}px`]);
  return out;
}

(async () => {
  const dir = path.resolve(process.argv[2]);
  const m = JSON.parse(fs.readFileSync(path.join(dir, '_manifest.json'), 'utf8'));
  const b = await require('./browser').launch();
  const p = await b.newPage({ viewport: { width: m.w, height: m.h }, deviceScaleFactor: 1 });
  let errors = 0;
  for (const f of m.files) {
    await p.goto('file:///' + f.replace(/\\/g, '/'));
    await p.waitForTimeout(300);
    const issues = await p.evaluate(audit);
    const out = f.replace(/\.html$/, '.jpg');
    await p.screenshot({ path: out, type: 'jpeg', quality: 90 });
    console.log(out);
    for (const [lv, msg] of issues) { console.log(`  ${lv}  ${msg}`); if (lv === 'ERROR') errors++; }
  }
  await b.close();
  if (errors) { console.log(`${errors} 处越界，缩短文案或换比例后重出`); process.exit(1); }
})();
