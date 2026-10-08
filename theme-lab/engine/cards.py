"""插图卡：把一页 HTML 卡片截成 JPG，当公众号正文插图 / 题图 / 贴图用。

为什么是截图而不是正文组件：微信正文会洗掉 grid、position、外部字体和 WebGL，
这类"PPT 页面式"的版式只能先渲染成图片再插进去。配色直接读当前系列的 token，
所以插图和正文是同一套视觉。

思路致谢（只借鉴思路，代码、样式、素材均为原创，未复制任何源文件，详见 CREDITS.md）：
- op7418/guizang-ppt-skill（MIT）：先有人工验证过的骨架，AI 只往里填内容
- op7418/guizang-social-card-skill（AGPL-3.0）：公众号头图 + 方图成对出、渲染后实测校验

用法：
  python cards.py spec.json            -> cards/<id>.html，再用 shoot_cards.js 截成 JPG
spec.json:
  {"theme": "airy-cobalt", "ratio": "16:9" | "3:4" | "2.35:1" | "1:1",
   "cards": [{"id": "...", "layout": "cover|stat|compare|quote|steps", ...}]}
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import themes  # noqa: E402
from components import mix  # noqa: E402

E = html.escape
SANS = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans SC',sans-serif"
MONO = "'SF Mono',Menlo,Consolas,monospace"
SIZES = {'16:9': (1280, 720), '3:4': (1080, 1440), '2.35:1': (1410, 600), '1:1': (1080, 1080)}
# 2.35:1 = 公众号头图；1:1 = 转发到聊天/朋友圈时的方图


def palette(theme_variant):
    key, _, var = theme_variant.partition('-')
    T = next(t for t in themes.THEMES if t.key == key)
    accent = next((c for v, _, c in T.variants if v == var), T.variants[0][2])
    bg = T.page_bg if T.page_bg.upper() != '#FFFFFF' else '#F7F7F5'  # 不用纯白
    return {'a': accent, 'ink': T.ink, 'muted': T.muted, 'line': T.line, 'bg': bg,
            'soft': mix(accent, 0.92), 'series': T.name}


def chrome(p, c, n, total, body):
    """统一外框：顶部等宽眉标 + 页码，底部来源行。"""
    return ('<div class="top"><span>%s</span><span>%02d / %02d</span></div>%s'
            '<div class="foot"><span>%s</span><span>%s</span></div>'
            % (E(c.get('kicker', p['series'].upper())), n, total, body,
               E(c.get('source', '')), E(c.get('author', ''))))


def L_cover(p, c):
    hi = ('<div class="h1 a">%s</div>' % E(c['highlight'])) if c.get('highlight') else ''
    return ('<div class="tag">%s</div><div class="h1">%s</div>%s<div class="sub">%s</div>'
            % (E(c.get('tag', '')), E(c['title']).replace('\n', '<br>'), hi, E(c.get('sub', ''))))


def L_stat(p, c):
    cells = ''.join('<div class="cell"><div class="num">%s</div><div class="lbl">%s</div><div class="note">%s</div></div>'
                    % (E(s['value']), E(s['label']), E(s.get('note', ''))) for s in c['stats'])
    return '<div class="h2">%s</div><div class="stats n%d">%s</div>' % (E(c['title']), len(c['stats']), cells)


def L_compare(p, c):
    head = ''.join('<th>%s</th>' % E(h) for h in c['head'])
    hl = c.get('highlight_col', -1)
    rows = ''.join('<tr>%s</tr>' % ''.join('<td class="%s">%s</td>' % ('hl' if j == hl else '', E(str(x)))
                                          for j, x in enumerate(r)) for r in c['rows'])
    return '<div class="h2">%s</div><table><tr>%s</tr>%s</table>' % (E(c['title']), head, rows)


def L_quote(p, c):
    return ('<div class="q">%s</div><div class="cite">— %s</div>'
            % (E(c['text']).replace('\n', '<br>'), E(c.get('cite', ''))))


def L_steps(p, c):
    items = ''.join('<div class="step"><div class="sn">%02d</div><div><div class="st">%s</div><div class="sd">%s</div></div></div>'
                    % (i, E(t), E(d)) for i, (t, d) in enumerate(c['items'], 1))
    return '<div class="h2">%s</div><div class="steps">%s</div>' % (E(c['title']), items)


LAYOUTS = {'cover': L_cover, 'stat': L_stat, 'compare': L_compare, 'quote': L_quote, 'steps': L_steps}


def css(p, w, h):
    # 竖版字要更大：手机信息流里 1 秒决定停不停；扁封面按高度缩，避免字撑破
    s = w / 820 if h > w else (w / 900 if h == w else min(w / 1280, h / 720))
    tall = h >= w  # 方图按竖版排：数据两列、步骤纵排
    return '''
*{margin:0;padding:0;box-sizing:border-box}
body{width:%(w)dpx;height:%(h)dpx;background:%(bg)s;color:%(ink)s;font-family:%(sans)s;
 padding:%(pad)dpx;display:flex;flex-direction:column;overflow:hidden;
 background-image:radial-gradient(%(line)s 1.2px,transparent 1.2px);background-size:%(dot)dpx %(dot)dpx}
.top,.foot{display:flex;justify-content:space-between;font-family:%(mono)s;font-size:%(f1)dpx;
 letter-spacing:2px;color:%(muted)s;text-transform:uppercase}
.top{border-bottom:2px solid %(ink)s;padding-bottom:%(g)dpx}
.foot{border-top:1px solid %(line)s;padding-top:%(g)dpx;margin-top:auto}
main{flex:1;display:flex;flex-direction:column;justify-content:center;padding:%(g2)dpx 0}
.tag{font-family:%(mono)s;font-size:%(f1)dpx;color:%(a)s;letter-spacing:2px;margin-bottom:%(g)dpx;font-weight:700}
.h1{font-size:%(fh1)dpx;line-height:1.15;font-weight:800;letter-spacing:-1px}
.h1.a{color:%(a)s}
.sub{margin-top:%(g2)dpx;font-size:%(fs)dpx;line-height:1.6;color:%(muted)s;max-width:85%%}
.h2{font-size:%(fh2)dpx;font-weight:800;line-height:1.25;margin-bottom:%(g2)dpx}
.stats{display:grid;gap:%(g)dpx;grid-template-columns:repeat(%(cols)s,1fr)}
.stats.n2{--n:2}.stats.n3{--n:3}.stats.n4{--n:4}
.cell{border-top:3px solid %(a)s;padding-top:%(g)dpx}
.num{font-family:%(mono)s;font-size:%(fnum)dpx;font-weight:700;color:%(a)s;line-height:1.1}
.lbl{font-size:%(fs)dpx;font-weight:700;margin-top:6px}
.note{font-size:%(fn)dpx;color:%(muted)s;margin-top:4px;line-height:1.5}
table{width:100%%;border-collapse:collapse;font-size:%(fs)dpx}
th{text-align:left;font-family:%(mono)s;font-size:%(f1)dpx;color:%(muted)s;letter-spacing:1px;
 padding:%(g)dpx 10px;border-bottom:2px solid %(ink)s}
td{padding:%(g)dpx 10px;border-bottom:1px solid %(line)s;font-weight:600}
td.hl{color:%(a)s;font-family:%(mono)s;font-weight:800;background:%(soft)s}
.q{font-size:%(fq)dpx;line-height:1.45;font-weight:800;border-left:6px solid %(a)s;padding-left:%(g2)dpx}
.cite{margin-top:%(g2)dpx;font-size:%(fs)dpx;color:%(muted)s;padding-left:%(g2)dpx}
.steps{display:flex;flex-direction:%(sdir)s;gap:%(g)dpx}
.step{flex:1;display:flex;gap:14px;background:#FFFFFF;border:1px solid %(line)s;border-radius:10px;padding:%(g)dpx}
.sn{font-family:%(mono)s;font-size:%(fh2)dpx;font-weight:800;color:%(a)s;line-height:1}
.st{font-size:%(fs)dpx;font-weight:800;margin-bottom:4px}
.sd{font-size:%(fn)dpx;color:%(muted)s;line-height:1.5}
''' % dict(w=w, h=h, sans=SANS, mono=MONO, pad=int(64 * s), dot=int(24 * s), g=int(16 * s), g2=int(28 * s),
           f1=int(15 * s), fn=int(21 * s), fs=int(22 * s), fh1=int((84 if tall else 72) * s), fh2=int(40 * s),
           fnum=int(64 * s), fq=int((52 if tall else 44) * s), cols='2' if tall else 'var(--n,4)',
           sdir='column' if tall else 'row', **p)


def build(spec_path):
    spec = json.load(open(spec_path, encoding='utf-8'))
    p = palette(spec['theme'])
    w, h = SIZES[spec.get('ratio', '16:9')]
    out_dir = os.path.join(os.path.dirname(os.path.abspath(spec_path)), 'cards')
    os.makedirs(out_dir, exist_ok=True)
    cards = spec['cards']
    files = []
    for n, c in enumerate(cards, 1):
        body = '<main>%s</main>' % LAYOUTS[c['layout']](p, c)
        doc = ('<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>'
               % (css(p, w, h), chrome(p, {**spec.get('defaults', {}), **c}, n, len(cards), body)))
        f = os.path.join(out_dir, '%s.html' % c['id'])
        open(f, 'w', encoding='utf-8').write(doc)
        files.append(f)
    json.dump({'w': w, 'h': h, 'files': files}, open(os.path.join(out_dir, '_manifest.json'), 'w', encoding='utf-8'))
    print('\n'.join(files))


if __name__ == '__main__':
    build(sys.argv[1])
