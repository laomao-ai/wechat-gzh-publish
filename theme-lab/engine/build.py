"""Build 微信公众号主题实验室: fragments + preview pages + gallery index.

python engine/build.py   (run from anywhere)
"""
import html
import json
from pathlib import Path

import components
import lint
import md
import themes

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'themes'
OUT.mkdir(exist_ok=True)

PREVIEW = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{margin:0;background:{bg}}}#bar{{position:sticky;top:0;z-index:9;display:flex;justify-content:space-between;
align-items:center;gap:8px;padding:8px 12px;background:rgba(255,255,255,.92);border-bottom:1px solid #e5e5e5;
font:12px -apple-system,'PingFang SC',sans-serif;color:#555}}#bar button{{border:0;border-radius:6px;padding:7px 12px;
background:#111;color:#fff;font-size:12px;cursor:pointer}}#wrap{{padding:16px 12px 40px}}
#toast{{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#111;color:#fff;padding:8px 14px;
border-radius:8px;font:13px sans-serif;opacity:0;transition:.3s}}</style></head><body>
<div id="bar"><span>{title}</span><button onclick="copyIt()">复制到公众号</button></div>
<div id="wrap"><div id="content">{body}</div></div><div id="toast">已复制，去公众号编辑器粘贴</div>
<script>
function toast(t){{var x=document.getElementById('toast');x.textContent=t;x.style.opacity=1;setTimeout(function(){{x.style.opacity=0}},1800)}}
function copyIt(){{var n=document.getElementById('content');var r=document.createRange();r.selectNodeContents(n);
var s=window.getSelection();s.removeAllRanges();s.addRange(r);var ok=false;try{{ok=document.execCommand('copy')}}catch(e){{}}
s.removeAllRanges();toast(ok?'已复制，去公众号编辑器粘贴':'复制失败，请手动全选复制')}}
</script></body></html>'''


# 'series' is per theme (samples/<key>.md); the other two are shared by all themes.
DOCS = [('series', '本系列样例', None), ('article', '主题介绍', 'sample-article.md'), ('showcase', '组件展厅', 'showcase.md')]


def used_components(blocks):
    """Map block types (+ inline marks) to component keys from the registry."""
    keys = {'cover'}
    for b in blocks:
        t = b['t']
        keys.add({'h2': 'h2', 'key': 'key'}.get(t, t))
        if t == 'h2':
            keys.add('toc')
        text = b.get('text', '') + ''.join(
            x if isinstance(x, str) else ''.join(y for y in x if isinstance(y, str)) for x in b.get('items', []))
        if '**' in text:
            keys.add('strong')
        if '==' in text:
            keys.add('mark')
        if '`' in text:
            keys.add('code_inline')
    return [c[1] for c in components.COMPONENTS if c[0] in keys]


def build():
    # themes/ is generated and overwritten in place.
    # Files of retired themes are reported, not deleted automatically.
    def load(fname):
        text = (ROOT / fname).read_text(encoding='utf-8')
        for w in lint.lint(text):
            print('  lint', fname, w)
        meta, blocks = md.parse(text)
        keys = used_components(blocks)
        if meta.get('related') or meta.get('account'):
            keys.append(dict((c[0], c[1]) for c in components.COMPONENTS)['outro'])
        return meta, blocks, keys

    shared = {}
    for dkey, dlabel, fname in DOCS:
        if fname:
            shared[dkey] = load(fname)
    catalog = []
    for T in themes.THEMES:
        sample = 'samples/%s.md' % T.key
        own = load(sample)
        entry = {'key': T.key, 'name': T.name, 'series': T.series, 'fit': T.fit, 'version': T.version,
                 'principle': T.principle, 'variants': [], 'sample': sample, 'sample_title': own[0].get('title', ''),
                 'used': own[2],
                 'typeset': '正文 %dpx · 行高 %s · 字距 %spx · 段后 %dpx · 两侧 %dpx' % (T.size, T.lh, T.ls, T.gap, T.pad)}
        for vkey, vlabel, accent in T.variants:
            stem = '%s-%s' % (T.key, vkey)
            files = {}
            for dkey, dlabel, fname in DOCS:
                meta, blocks, _ = own if dkey == 'series' else shared[dkey]
                t = T(accent)
                t.variant = vkey
                t.asset_prefix = '../'
                body = t.render(meta, blocks)
                name = stem if dkey == 'article' else stem + '.' + dkey
                (OUT / (name + '.fragment.html')).write_text(body, encoding='utf-8')
                (OUT / (name + '.html')).write_text(
                    PREVIEW.format(title=html.escape('%s · %s · %s' % (T.name, vlabel, dlabel)),
                                   bg=t.page_bg, body=body), encoding='utf-8')
                files[dkey] = 'themes/%s.html' % name
            entry['variants'].append({'key': vkey, 'label': vlabel, 'accent': accent, 'files': files})
        catalog.append(entry)
    docs = [{'key': k, 'label': l, 'md': f, 'used': shared[k][2] if f else []} for k, l, f in DOCS]
    hist_path = ROOT / 'archive' / 'index.json'
    history = json.loads(hist_path.read_text(encoding='utf-8')) if hist_path.exists() else []
    data = {
        'catalog': catalog,
        'docs': docs,
        'components': [{'name': c[1], 'syntax': c[2], 'use': c[3]} for c in components.COMPONENTS],
        'history': history,
    }
    gallery = (ROOT / 'engine' / 'gallery.template.html').read_text(encoding='utf-8')
    gallery = gallery.replace('/*DATA*/', json.dumps(data, ensure_ascii=False))
    (ROOT / 'index.html').write_text(gallery, encoding='utf-8')
    live = {Path(v['files'][k]).name for c in catalog for v in c['variants'] for k in v['files']}
    live |= {n.replace('.html', '.fragment.html') for n in live}
    stale = sorted(p.name for p in OUT.glob('*.html') if p.name not in live)
    if stale:
        print('stale files in themes/ (safe to remove):', stale)
    print('themes:', len(catalog), 'variants:', sum(len(c['variants']) for c in catalog),
          'docs:', [d['key'] for d in docs])


if __name__ == '__main__':
    build()
