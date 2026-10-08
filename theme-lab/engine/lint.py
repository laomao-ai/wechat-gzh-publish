"""Writing-rhythm lint for Markdown sources (runs before typesetting).

Rules come from common WeChat reading habits:
  - a paragraph longer than ~5 phone lines is hard to read -> suggest a split
    (15px body on a ~343px column holds about 22 CJK chars per line)
  - one article, one emphasis voice: too many ==highlights== dilute each other
  - bold inside a paragraph works when it is rare

Usage: python lint.py file.md [...]     exit code 0 (warnings never block)
"""
import re
import sys
from pathlib import Path

import md

PARA_MAX = 110       # ~5 lines at 15px
MARK_MAX = 2         # per article
BOLD_PER_PARA = 2


def plain(text):
    return re.sub(r'\*\*|==|`', '', text)


def lint(text):
    meta, blocks = md.parse(text)
    warns = []
    marks = 0
    for b in blocks:
        t = b.get('text', '')
        marks += t.count('==') // 2
        if b['t'] == 'p':
            n = len(plain(t))
            if n > PARA_MAX:
                warns.append('段落 %d 字，超过约 5 行（%d 字），建议拆段：%s…' % (n, PARA_MAX, plain(t)[:18]))
            bolds = t.count('**') // 2
            if bolds > BOLD_PER_PARA:
                warns.append('一段里有 %d 处加粗，重点会互相抵消：%s…' % (bolds, plain(t)[:18]))
    if marks > MARK_MAX:
        warns.append('全文 %d 处荧光高亮，建议不超过 %d 处' % (marks, MARK_MAX))
    return warns


def main(paths):
    for p in paths:
        warns = lint(Path(p).read_text(encoding='utf-8'))
        print('%s  写作提示=%d' % (Path(p).name, len(warns)))
        for w in warns:
            print('  WARN', w)


if __name__ == '__main__':
    main(sys.argv[1:])
