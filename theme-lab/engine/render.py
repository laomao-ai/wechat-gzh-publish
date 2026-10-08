"""Render one Markdown article with chosen themes -> .gzh.html fragments.

  python engine/render.py <article.md> [series-variant ...] [--out DIR]
  e.g. python engine/render.py drafts/first-article.md forest-leaf airy-cobalt

No theme given = first variant of every series. Output: <out>/<stem>.<key>-<variant>.gzh.html
plus a 390px preview page next to it (<...>.preview.html).
"""
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import md, themes, lint  # noqa: E402

PREVIEW = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title></head>'
           '<body style="margin:0;background:#EDEDED;"><div style="width:390px;margin:0 auto;background:{bg};'
           'min-height:100vh;">{body}</div></body></html>')


def pick(names):
    table = {'%s-%s' % (T.key, v[0]): (T, v) for T in themes.THEMES for v in T.variants}
    if not names:
        return [(T, T.variants[0]) for T in themes.THEMES]
    bad = [n for n in names if n not in table]
    if bad:
        sys.exit('unknown theme %s; choose from: %s' % (bad, ' '.join(table)))
    return [table[n] for n in names]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('md')
    ap.add_argument('themes', nargs='*')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    src = Path(a.md)
    text = src.read_text(encoding='utf-8')
    for w in lint.lint(text):
        print('  lint', w)
    meta, blocks = md.parse(text)
    out = Path(a.out) if a.out else src.parent / 'out'
    out.mkdir(parents=True, exist_ok=True)
    for T, (vkey, vlabel, accent) in pick(a.themes):
        t = T(accent)
        t.variant = vkey
        body = t.render(meta, blocks)
        stem = '%s.%s-%s' % (src.stem, T.key, vkey)
        (out / (stem + '.gzh.html')).write_text(body, encoding='utf-8')
        (out / (stem + '.preview.html')).write_text(
            PREVIEW.format(t=html.escape('%s · %s' % (T.name, vlabel)), bg=t.page_bg, body=body), encoding='utf-8')
        print(out / (stem + '.gzh.html'))


if __name__ == '__main__':
    main()
