"""Markdown -> block list parser for the theme lab (original implementation).

Block syntax (each maps to one component in components.py):
  ## 01　标题            h2  章节
  ### 小标题             h3  小节
  > 引用 / > —— 出处      quote（首个出现在章节前的引用 = lead 导语）
  > [!TIP] 标题 / 正文    callout  tip|note|warn|key
  **整段加粗**           key  划重点
  *整段斜体*             note 注释
  - 列表 / 1. 列表        list
  1. **步骤**：说明       steps（有序列表且每项以粗体开头）
  - [x] 事项             check 清单
  | 表 | 格 |            table
  ```lang 代码 ```        code
  ![图注](src)           figure（src 留空或 todo = 待补素材占位）
  ![图注](src "hero")    hero 通栏题图 / bare 无边框 / frame 相框（默认）；首个 ## 前的图自动 hero
  :::cards ... :::       cards（每行 - **标题**：说明）
  :::gallery 模式 说明    gallery 多图（模式 row 并排 / stack 拼接 / swipe 左右滑 /
    ![图注](src) ...      scroll 上下滑 / frame 带窗口边框；每行一张图）
  :::
  ***                    divider
  末段问号结尾            ending
Inline: **粗体**  ==高亮==  `代码`
"""
import re

GALLERY_MODES = ('row', 'stack', 'swipe', 'scroll', 'frame')


def parse_front(text):
    meta = {}
    if text.startswith('---'):
        _, head, body = text.split('---', 2)
        for line in head.strip().splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        text = body
    return meta, text.strip()


def split_section(title):
    """'01　好看的排版' -> ('01', '好看的排版'); '最后：xx' -> ('', '最后：xx')."""
    m = re.match(r'^(\d{1,2})[\s　]+(.+)$', title)
    if m:
        return m.group(1), m.group(2).strip()
    return '', title.strip()


def split_title(item):
    """'**标题**：说明' -> ('标题', '说明'); otherwise ('', item)."""
    m = re.match(r'^\*\*([^*]+)\*\*[：:]?\s*(.*)$', item)
    return (m.group(1), m.group(2)) if m else ('', item)


LIST_RE = re.compile(r'^(- |\d+\. )')
CALLOUT_RE = re.compile(r'^\[!(TIP|NOTE|WARN|KEY|ASK)\]\s*(.*)$', re.I)


def parse(text):
    meta, body = parse_front(text)
    lines = body.splitlines()
    blocks, i = [], 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line or line == '---':
            i += 1
            continue
        if line.startswith('```'):
            lang, _, ctitle = line[3:].strip().partition(' ')
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i].rstrip())
                i += 1
            blocks.append({'t': 'code', 'lang': lang, 'title': ctitle.strip(), 'lines': code})
            i += 1
            continue
        if line.startswith(':::cards'):
            items = []
            i += 1
            while i < len(lines) and lines[i].strip() != ':::':
                s = lines[i].strip()
                if s.startswith('- '):
                    items.append(split_title(s[2:]))
                i += 1
            blocks.append({'t': 'cards', 'items': items})
            i += 1
            continue
        if line.startswith(':::gallery'):
            # :::gallery <row|stack|swipe|scroll|frame> [图组说明]
            head = line[len(':::gallery'):].strip().split(None, 1)
            mode = head[0] if head and head[0] in GALLERY_MODES else 'row'
            caption = head[1] if len(head) > 1 else (head[0] if head and head[0] not in GALLERY_MODES else '')
            items = []
            i += 1
            while i < len(lines) and lines[i].strip() != ':::':
                im = re.fullmatch(r'!\[([^\]]*)\]\(([^)]*)\)', lines[i].strip())
                if im:
                    items.append((im.group(1), im.group(2).strip()))
                i += 1
            blocks.append({'t': 'gallery', 'mode': mode, 'caption': caption, 'items': items})
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append({'t': 'table', 'head': rows[0], 'rows': rows[1:]})
            continue
        if line.startswith('>'):
            quote = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            m = CALLOUT_RE.match(quote[0])
            if m and m.group(1).upper() == 'ASK':
                # 显式结尾互动：> [!ASK] 问题（不再靠“最后一段是问号”去猜）
                blocks.append({'t': 'ending', 'text': ' '.join(x for x in [m.group(2)] + quote[1:] if x)})
            elif m:
                blocks.append({'t': 'callout', 'kind': m.group(1).lower(), 'title': m.group(2),
                               'text': ' '.join(q for q in quote[1:] if q)})
            else:
                cite = ''
                if len(quote) > 1 and re.match(r'^(——|—|--)', quote[-1]):
                    cite = re.sub(r'^(——|—|--)\s*', '', quote.pop())
                blocks.append({'t': 'quote', 'text': ' '.join(q for q in quote if q), 'cite': cite})
            continue
        if LIST_RE.match(line):
            ordered = bool(re.match(r'^\d+\. ', line))
            items, checks = [], []
            while i < len(lines) and LIST_RE.match(lines[i].strip()):
                item = LIST_RE.sub('', lines[i].strip())
                cm = re.match(r'^\[([ xX])\]\s*', item)
                checks.append(cm.group(1).lower() == 'x' if cm else None)
                items.append(item[cm.end():] if cm else item)
                i += 1
            if all(c is not None for c in checks):
                blocks.append({'t': 'check', 'items': list(zip(items, checks))})
            elif ordered and all(split_title(x)[0] for x in items):
                blocks.append({'t': 'steps', 'items': [split_title(x) for x in items]})
            else:
                blocks.append({'t': 'list', 'ordered': ordered, 'items': items})
            continue
        fm = re.fullmatch(r'!\[([^\]]*)\]\(([^)]*)\)', line)
        if line.startswith('# '):
            meta.setdefault('title', line[2:].strip())
        elif line.startswith('### '):
            hm = re.match(r'^([A-Z][A-Z ]{1,10}\d{1,2})\s*[·・]\s*(.+)$', line[4:].strip())
            blocks.append({'t': 'h3', 'text': hm.group(2) if hm else line[4:].strip(),
                           'label': hm.group(1) if hm else ''})
        elif line.startswith('## '):
            parts = re.split(r'\s+[｜|]\s+', line[3:].strip(), 1)
            num, title = split_section(parts[0])
            blocks.append({'t': 'h2', 'num': num, 'title': title, 'kicker': parts[1].strip() if len(parts) > 1 else ''})
        elif line in ('***', '* * *'):
            blocks.append({'t': 'divider'})
        elif fm:
            src, style = fm.group(2).strip(), ''
            sm = re.match(r'^(\S+)\s+"(hero|bare|frame)"$', src)
            if sm:
                src, style = sm.group(1), sm.group(2)
            if not style and not any(x['t'] == 'h2' for x in blocks):
                style = 'hero'      # 首个 ## 之前的图 = 题图
            blocks.append({'t': 'figure', 'caption': fm.group(1), 'style': style,
                           'src': '' if src.lower() in ('', 'todo') else src})
        elif re.fullmatch(r'\*\*[^*]+\*\*', line):
            blocks.append({'t': 'key', 'text': line[2:-2]})
        elif re.fullmatch(r'\*[^*]+\*', line):
            blocks.append({'t': 'note', 'text': line[1:-1]})
        else:
            blocks.append({'t': 'p', 'text': line})
        i += 1
    # First quote before any h2 = lead
    for b in blocks:
        if b['t'] == 'h2':
            break
        if b['t'] == 'quote':
            b['t'] = 'lead'
            break
    for b in blocks:
        if b['t'] == 'h2' and not b['num']:
            b['final'] = True
    return meta, blocks
