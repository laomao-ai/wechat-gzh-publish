"""Independent WeChat-safety checker for theme lab output (original implementation).

Usage: python check.py file1.html [file2.html ...]
Exit code 1 if any ERROR.
"""
import re
import sys
from html.parser import HTMLParser

FORBIDDEN_TAGS = {'style', 'script', 'div', 'iframe', 'form', 'input', 'button', 'svg', 'canvas', 'video', 'audio', 'link'}
FORBIDDEN_CSS = [
    (r'position\s*:\s*(fixed|absolute|sticky)', 'position fixed/absolute/sticky'),
    (r'(^|;)\s*float\s*:', 'float'),
    (r'display\s*:\s*grid', 'display:grid'),
    (r'var\(--', 'CSS 变量'),
    (r'white-space\s*:\s*pre(;|$)', 'white-space:pre'),
]
VOID = {'br', 'img', 'hr'}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.warns = [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in FORBIDDEN_TAGS:
            self.errors.append('禁用标签 <%s>' % tag)
        for bad in ('class', 'id'):
            if bad in a:
                self.errors.append('<%s> 带有 %s 属性' % (tag, bad))
        style = a.get('style') or ''
        for pat, label in FORBIDDEN_CSS:
            if re.search(pat, style):
                self.errors.append('<%s> 使用 %s' % (tag, label))
        for size in re.findall(r'font-size\s*:\s*([\d.]+)px', style):
            if float(size) > 24:
                self.errors.append('字号 %spx 超过 24px' % size)
        if tag not in VOID:
            self.stack.append((tag, 'leaf' in a))

    def handle_endtag(self, tag):
        while self.stack:
            t, _ = self.stack.pop()
            if t == tag:
                break

    def handle_data(self, data):
        if not data.strip():
            return
        if not any(is_leaf for _, is_leaf in self.stack):
            self.errors.append('文字未包裹 <span leaf>：%s' % data.strip()[:20])
        if re.search(r'[\u4e00-\u9fff][,.!?;:](?!\d)', data):
            self.warns.append('中文后出现半角标点：%s' % data.strip()[:24])


def check(path):
    text = open(path, encoding='utf-8').read()
    c = Checker()
    c.feed(text)
    return c.errors, c.warns


if __name__ == '__main__':
    bad = 0
    for p in sys.argv[1:]:
        e, w = check(p)
        bad += len(e)
        print('%s  ERROR=%d  WARN=%d' % (p, len(e), len(w)))
        for x in (e + w)[:8]:
            print('   -', x)
    sys.exit(1 if bad else 0)
