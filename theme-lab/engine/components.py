"""Shared component library for 微信公众号主题实验室 (original implementation).

Every theme subclasses Theme. Tokens (colors, radius, fonts) drive the default
look of every component; a theme overrides only the components that carry its
character. New components are added here once and every theme gets a default,
so older themes never lose features when the library grows.

WeChat rules: inline style only; <section>/<p>/<span>/<strong>/<table>/<img>;
every text node inside <span leaf="">; font-size <= 24px; no class/id/div.
"""
import html
import re

SANS = "-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif"
SERIF = "Georgia,'Songti SC','STSong','SimSun',serif"
KAI = "'Kaiti SC','STKaiti','KaiTi','Songti SC',serif"
# Menlo first: best hit rate on iOS WeChat.
def code_label(b):
    """Fence label: explicit lang, else LINK for a lone URL, else code."""
    if b['lang']:
        return b['lang']
    ls = [x for x in b['lines'] if x.strip()]
    return 'link' if len(ls) == 1 and ls[0].strip().startswith('http') else 'code'


MONO = "Menlo,Consolas,'SF Mono',Monaco,monospace"

# Pictographic emoji render as black boxes in some WeChat clients; swap for
# geometric marks that every font has. Dingbats like ✓ ✦ ✎ are safe and kept.
EMOJI_MAP = {'🌱': '✦', '🌿': '✦', '👀': '▸', '👍': '✓', '💡': '✦', '📎': '▸',
             '💬': '▸', '📌': '▎', '💌': '✉', '⚠': '!'}
EMOJI_RE = re.compile('[\U0001F300-\U0001FAFF]\ufe0f?')
STYLE_RE = re.compile(r'style="([^"]*)"')


def wechat_safe(h):
    """Last pass before output, fixes found on a real phone:
    1. monospace runs inherit the body letter-spacing and come out as
       'n o t  i n  l i s t' -> force letter-spacing:0 on them;
    2. emoji -> geometric marks (EMOJI_MAP; unknown ones are dropped)."""
    def fix(m):
        s = m.group(1)
        if 'monospace' in s and 'letter-spacing:0;' not in s:
            s = re.sub(r'letter-spacing:[^;]*;?', '', s).rstrip(';') + ';letter-spacing:0;'
        return 'style="%s"' % s
    h = STYLE_RE.sub(fix, h)
    for k, v in EMOJI_MAP.items():
        h = h.replace(k + '\ufe0f', v).replace(k, v)
    return EMOJI_RE.sub('', h)


def _lum(h):
    h = h.lstrip('#')
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def text_safe(hex_color, target=4.6):
    """Same hue, darkened until small text on white reaches WCAG ~4.5:1.
    Blocks and lines keep the bright accent; only `color:` uses this."""
    c = hex_color
    for k in range(1, 20):
        if 1.05 / (_lum(c) + 0.05) >= target:
            return c
        c = mix(hex_color, 0.04 * k, (0, 0, 0))
    return c


def esc(s):
    return html.escape(s, quote=False)


def leaf(s):
    return '<span leaf="">' + esc(s) + '</span>'


def blank():
    return '<span leaf=""><br></span>'


def mix(hex_color, ratio, to=(255, 255, 255)):
    """Blend toward white (or `to`). ratio=0.9 -> 90% target."""
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(c + (t - c) * ratio) for c, t in zip((r, g, b), to))
    return '#%02X%02X%02X' % (r, g, b)


def read_minutes(blocks):
    n = 0
    for b in blocks:
        for k in ('text', 'title'):
            n += len(b.get(k, '') or '')
        for x in b.get('items', []):
            n += len(x) if isinstance(x, str) else sum(len(y) for y in x if isinstance(y, str))
    return max(1, round(n / 400))


# name, markdown, what it is for -- shown in the gallery 组件清单
COMPONENTS = [
    ('cover', '封面卡', 'front matter: title / digest / kicker / tags', '文章开头的身份卡'),
    ('lead', '导语', '章节前第一个 > 引用', '一句话说清这篇讲什么'),
    ('toc', '目录导航', '自动（按 ## 生成）', '长文先给读者一张路线图'),
    ('h2', '章节标题', '## 01　标题', '大段落切分'),
    ('h3', '小节标题', '### 小标题', '章节内部再分一层'),
    ('p', '正文段落', '普通段落', '阅读主体'),
    ('strong', '加粗强调', '**文字**', '句内重点'),
    ('mark', '荧光高亮', '==文字==', '全文最想让人记住的半句话'),
    ('code_inline', '行内代码', '`文字`', '命令、文件名、参数'),
    ('key', '划重点', '**整段加粗**', '一节的结论'),
    ('quote', '引语', '> 句子 / > —— 出处', '金句或他人观点'),
    ('callout', '提示卡', '> [!TIP] 标题（TIP/NOTE/WARN/KEY）', '提醒、注意、补充说明'),
    ('list', '列表', '- 项目 / 1. 项目', '并列信息'),
    ('steps', '步骤条', '1. **步骤**：说明', '按顺序操作的教程'),
    ('check', '清单', '- [x] 事项', '检查项、待办'),
    ('cards', '卡片组', ':::cards  - **标题**：说明  :::', '并列方案、功能点'),
    ('table', '表格', '| 表 | 格 |', '多维对照'),
    ('code', '代码块', '```lang ... ```', '可复制的命令或配置'),
    ('figure', '图片 / 占位', '![图注](src)，src 留空 = 待补素材', '截图、配图；先占位后补图'),
    ('gallery', '多图排版', ':::gallery row|stack|swipe|scroll|frame 说明 … :::', '并排对比、长图拼接、左右/上下滑动、窗口边框'),
    ('note', '注释', '*整段*（渲染为灰色小字，不用斜体）', '小字补充、免责声明'),
    ('divider', '分隔符', '***', '话题转场'),
    ('outro', '往期 + 作者名片', 'front matter: related / account / card / follow', '文末固定区，配置一次每篇自动带上'),
    ('ending', '结尾互动', '> [!ASK] 问题', '把话头交给读者'),
]


class Theme:
    key = ''
    name = ''
    series = ''
    fit = ''
    principle = ''
    version = '1.0'
    variants = []  # [(variant_key, label, accent_hex)]

    # tokens -------------------------------------------------------------
    body_color = '#3F3F46'
    ink = '#1F2328'
    muted = '#8A8F98'
    body_font = SANS
    head_font = SANS
    mono = MONO
    line = '#E5E7EB'
    page_bg = '#FFFFFF'
    radius = 8
    code_bg = '#1E2227'
    code_fg = '#E6E6E6'
    size = 15

    # typesetting tokens: every series sets its own rhythm (see TYPESET.md)
    lh = 1.75          # body line-height
    ls = 1.0           # body letter-spacing, px
    gap = 24           # space after a paragraph, px
    pad = 16           # left/right inset of the article body, px
    cover_bleed = False  # True: cover spans edge to edge, body is inset

    def __init__(self, accent):
        self.a = accent
        self.soft = mix(accent, 0.84)
        self.faint = mix(accent, 0.93)
        self.deep = mix(accent, 0.35, (0, 0, 0))

    # inline -------------------------------------------------------------
    def strong_style(self):
        return 'color:%s;font-weight:700;' % self.a

    def mark_style(self):
        return 'color:%s;font-weight:700;background:linear-gradient(to bottom,transparent 55%%,#FFE58A 55%%);padding:0 2px;' % self.ink

    def code_inline_style(self):
        return ('font-family:%s;font-size:13px;color:%s;background:%s;padding:1px 5px;border-radius:4px;margin:0 2px;'
                % (self.mono, self.deep, self.faint))

    # == and ** may nest (==**x**== / **==x==**): match the outer one first,
    # then parse the captured text again so no raw marker leaks into the page.
    INLINE_RE = re.compile(r'(==(?:(?!==).)+==|\*\*(?:(?!\*\*).)+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))')

    def inline(self, text):
        out = []
        for part in self.INLINE_RE.split(text):
            if not part:
                continue
            if part.startswith('**'):
                out.append('<strong style="%s">%s</strong>' % (self.strong_style(), self.inline(part[2:-2])))
            elif part.startswith('=='):
                out.append('<span style="%s">%s</span>' % (self.mark_style(), self.inline(part[2:-2])))
            elif part.startswith('`'):
                out.append('<span style="%s">%s</span>' % (self.code_inline_style(), leaf(part[1:-1])))
            elif part.startswith('['):
                label = re.match(r'\[([^\]]+)\]', part).group(1)
                out.append('<span style="color:%s;border-bottom:1px solid %s;">%s</span>' % (self.a, self.soft, leaf(label)))
            else:
                out.append(leaf(part))
        return ''.join(out)

    # assembly -----------------------------------------------------------
    def render(self, meta, blocks):
        self.meta = meta
        self.minutes = read_minutes(blocks)
        sections = [b for b in blocks if b['t'] == 'h2']
        self.total = len([b for b in sections if not b.get('final')])
        out, toc_done, count, prompts = [], False, 0, 0
        for b in blocks:
            t = b['t']
            if t == 'h2':
                if not toc_done:
                    out.append(self.toc(sections))
                    toc_done = True
                count += 1
                out.append(self.h2(b, count))
            elif t == 'key':
                out.append(self.keypoint(b['text']))
            elif t == 'list':
                out.append(self.list(b['items'], b['ordered']))
            elif t == 'table':
                out.append(self.table(b['head'], b['rows']))
            elif t == 'ending':
                out.append(self.ending(b['text'], meta))
            elif t == 'quote':
                out.append(self.quote(b['text'], b.get('cite', '')))
            elif t == 'divider':
                out.append(self.divider())
            elif t == 'h3' and b.get('label'):
                out.append(self.h3_labeled(b))
            elif t == 'code' and b['lang'].lower() in ('prompt', '提示词'):
                prompts += 1
                out.append(self.prompt(b, prompts))
            else:
                out.append(getattr(self, t)(b) if t in ('h3', 'code', 'callout', 'steps', 'check', 'cards', 'figure', 'gallery')
                           else getattr(self, t)(b['text']))
        out.append(self.outro(meta))
        body = self.retype(''.join(out))
        # front matter `cover: none` -> the hero image is the cover, skip the text card
        cover = '' if meta.get('cover', '').strip().lower() == 'none' else self.cover(meta)
        pad = 'padding:0 %dpx;' % self.pad
        if self.cover_bleed:
            inner = cover + '<section style="%s">%s</section>' % (pad, body)
        else:
            inner = '<section style="%s">%s</section>' % (pad, cover + body)
        html_out = ('<section style="max-width:677px;margin:0 auto;padding:0;background:%s;font-family:%s;'
                    'color:%s;line-height:%s;letter-spacing:%spx;">%s</section>'
                    % (self.page_bg, self.body_font, self.body_color, self.lh, self.ls, inner))
        ta = text_safe(self.a)
        if ta != self.a:   # (?<![-\w]) -> plain `color:` only, not background-color/border-color
            html_out = re.sub(r'(?<![-\w])color:%s' % re.escape(self.a), 'color:' + ta, html_out, flags=re.I)
        return wechat_safe(html_out)

    BODY_RE = re.compile(r'font-size:15px;line-height:(1\.[789]\d?|2(?:\.0)?);')

    def retype(self, html):
        """Bring every body-sized run (paragraphs, list items, callout text,
        step text ...) onto this series' size and line-height, so the whole
        article reads with one rhythm. Headings use other sizes and are left alone."""
        return self.BODY_RE.sub('font-size:%dpx;line-height:%s;' % (self.size, self.lh), html)

    # outro: author card + related posts, configured once in front matter ---
    def related(self, meta):
        items = []
        for raw in meta.get('related', '').split('|'):
            raw = raw.strip()
            if raw:
                title, _, note = raw.partition('::')
                items.append((title.strip(), note.strip()))
        return items

    def outro(self, meta):
        rel, account = self.related(meta), meta.get('account', '')
        if not rel and not account:
            return ''
        r = max(self.radius, 0)
        parts = []
        if rel:
            rows = ''.join(
                '<section style="display:flex;align-items:flex-start;padding:10px 0;border-top:1px dashed %s;">'
                '<span style="flex-shrink:0;margin-right:10px;font-size:12px;line-height:1.7;color:%s;font-family:%s;font-weight:700;">%s</span>'
                '<section style="flex:1;"><p style="margin:0;font-size:14px;line-height:1.7;color:%s;font-weight:700;">%s</p>%s</section></section>'
                % (self.line, self.a, self.mono, leaf('%02d' % (i + 1)), self.ink, leaf(t),
                   ('<p style="margin:2px 0 0;font-size:12px;line-height:1.7;color:%s;">%s</p>' % (self.muted, leaf(n))) if n else '')
                for i, (t, n) in enumerate(rel))
            parts.append('<section style="margin:0 0 18px;">'
                         '<p style="margin:0 0 4px;font-size:12px;letter-spacing:2px;color:%s;font-weight:700;">%s</p>%s</section>'
                         % (self.muted, leaf('往期 · 接着读'), rows))
        if account:
            initial = account[:1]
            follow = meta.get('follow', '')
            parts.append(
                '<section style="display:flex;align-items:center;padding:14px;background:%s;border-radius:%dpx;">'
                '<section style="flex-shrink:0;width:44px;height:44px;margin-right:12px;border-radius:%dpx;background:%s;'
                'text-align:center;"><p style="margin:0;font-size:20px;line-height:44px;color:#FFFFFF;font-weight:800;">%s</p></section>'
                '<section style="flex:1;"><p style="margin:0;font-size:15px;line-height:1.5;color:%s;font-weight:800;">%s</p>'
                '<p style="margin:3px 0 0;font-size:12px;line-height:1.7;color:%s;">%s</p>%s</section></section>'
                % (self.faint, r, 22 if r >= 6 else 0, self.a, leaf(initial), self.ink, leaf(account),
                   self.muted, leaf(meta.get('card', meta.get('bio', ''))),
                   ('<p style="margin:6px 0 0;font-size:12px;line-height:1.6;color:%s;font-weight:700;">%s</p>'
                    % (self.a, leaf(follow))) if follow else ''))
        return '<section style="margin:34px 0 10px;">%s</section>' % ''.join(parts)

    def tags(self, meta):
        return [t.strip() for t in meta.get('tags', '').split(',') if t.strip()]

    def sec_label(self, b, n):
        return 'END' if b.get('final') else (b['num'] or '%02d' % n)

    # block defaults (token driven) --------------------------------------
    def p(self, text):
        return ('<p style="margin:0 0 %dpx;font-size:%dpx;line-height:%s;color:%s;letter-spacing:%spx;'
                'text-align:justify;">%s</p>' % (self.gap, self.size, self.lh, self.body_color, self.ls, self.inline(text)))

    def note(self, text):
        return ('<p style="margin:-6px 0 20px;font-size:12px;line-height:1.7;color:#9CA3AF;">%s</p>'
                % self.inline('注：' + text))

    def h3(self, b):
        return ('<section style="margin:28px 0 14px;display:flex;align-items:center;">'
                '<span style="flex-shrink:0;width:4px;height:16px;margin-right:9px;background:%s;border-radius:2px;">%s</span>'
                '<p style="margin:0;font-size:16px;line-height:1.5;color:%s;font-weight:700;font-family:%s;">%s</p></section>'
                % (self.a, blank(), self.ink, self.head_font, self.inline(b['text'])))

    # ### CASE 01 · 标题  -> small mono label above a normal h3
    def h3_labeled(self, b):
        return ('<p style="margin:30px 0 0;font-size:11px;letter-spacing:2px;line-height:1.6;color:%s;'
                'font-family:%s;font-weight:700;">%s</p>%s'
                % (self.a, self.mono, leaf(b['label']), self.h3(b)))

    # ```prompt 标题 -> prose box (prompts are read, not run: no monospace, wraps naturally)
    def prompt(self, b, n):
        head = 'PROMPT %02d' % n + ('　·　' + b['title'] if b.get('title') else '')
        body = ''.join('<p style="margin:0 0 6px;font-size:14px;line-height:1.85;color:%s;">%s</p>'
                       % (self.ink, self.inline(s.strip())) for s in b['lines'] if s.strip())
        return ('<section style="margin:6px 0 24px;padding:12px 16px 8px;background:%s;border-left:3px solid %s;'
                'border-radius:0 %dpx %dpx 0;">'
                '<p style="margin:0 0 8px;font-size:11px;letter-spacing:1px;line-height:1.6;color:%s;font-family:%s;font-weight:700;">%s</p>'
                '%s</section>'
                % (mix(self.a, 0.95), self.a, self.radius, self.radius, self.a, self.mono, leaf(head), body))

    def keypoint(self, text):
        return ('<section style="margin:6px 0 24px;padding:14px 16px;background:%s;border-radius:%dpx;">'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:%s;font-weight:700;">%s</p></section>'
                % (self.faint, self.radius, self.ink, self.inline(text)))

    def quote(self, text, cite=''):
        c = ('<p style="margin:8px 0 0;font-size:12px;color:%s;">%s</p>' % (self.muted, leaf('—— ' + cite))) if cite else ''
        return ('<section style="margin:24px 0;padding:14px 16px;border-left:3px solid %s;background:%s;">'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:%s;">%s</p>%s</section>'
                % (self.a, self.faint, self.ink, self.inline(text), c))

    def lead(self, text):
        return self.quote(text)

    def list(self, items, ordered):
        rows = []
        for n, item in enumerate(items, 1):
            mark = ('%02d' % n) if ordered else '—'
            rows.append(
                '<section style="display:flex;margin:0 0 10px;">'
                '<span style="flex-shrink:0;width:28px;font-size:13px;line-height:1.9;color:%s;font-weight:700;font-family:%s;">%s</span>'
                '<p style="flex:1;margin:0;font-size:15px;line-height:1.9;color:%s;">%s</p></section>'
                % (self.a, self.mono, leaf(mark), self.body_color, self.inline(item)))
        return '<section style="margin:4px 0 22px;">' + ''.join(rows) + '</section>'

    def table(self, head, rows):
        th = ''.join('<td style="padding:10px 12px;font-size:13px;font-weight:700;color:#fff;background:%s;'
                     'border:1px solid %s;">%s</td>' % (self.a, self.a, leaf(h)) for h in head)
        body = ''
        for n, row in enumerate(rows):
            bg = self.faint if n % 2 else '#FFFFFF'
            body += '<tr>' + ''.join(
                '<td style="padding:10px 12px;font-size:13px;line-height:1.7;color:%s;background:%s;border:1px solid %s;%s">%s</td>'
                % (self.body_color, bg, self.line, 'font-weight:700;white-space:nowrap;' if c == 0 else '', self.inline(cell))
                for c, cell in enumerate(row)) + '</tr>'
        return ('<section style="margin:6px 0 24px;"><table style="width:100%%;border-collapse:collapse;">'
                '<tbody><tr>%s</tr>%s</tbody></table></section>' % (th, body))

    CALLOUT = {
        'tip': ('#0F8A5F', '#EAF6F0', '提示'),
        'note': ('#5B6472', '#F3F4F6', '说明'),
        'warn': ('#C2620A', '#FFF4E5', '注意'),
        'key': (None, None, '重点'),
    }

    def callout_colors(self, kind):
        c, bg, label = self.CALLOUT.get(kind, self.CALLOUT['note'])
        return (c or self.a), (bg or self.faint), label

    def callout(self, b):
        c, bg, label = self.callout_colors(b['kind'])
        title = b['title'] or label
        body = ('<p style="margin:6px 0 0;font-size:14px;line-height:1.8;color:%s;">%s</p>'
                % (self.body_color, self.inline(b['text']))) if b['text'] else ''
        return ('<section style="margin:6px 0 22px;padding:12px 14px;background:%s;border-radius:%dpx;border-left:3px solid %s;">'
                '<p style="margin:0;font-size:14px;font-weight:700;color:%s;">%s</p>%s</section>'
                % (bg, self.radius, c, c, self.inline(title), body))

    def code_line(self, s, fg, comment):
        """One code line -> <p>. Spaces kept with nbsp (WeChat drops white-space:pre)."""
        if not s.strip():
            return '<p style="margin:0;line-height:1.7;">%s</p>' % blank()
        indent = len(s) - len(s.lstrip(' '))
        txt = '\u00a0' * indent + s.lstrip(' ').replace('  ', '\u00a0\u00a0')
        is_c = s.lstrip().startswith(('#', '//'))
        return ('<p style="margin:0;font-size:12.5px;line-height:1.7;font-family:%s;color:%s;word-break:break-all;">%s</p>'
                % (self.mono, comment if is_c else fg, leaf(txt)))

    def code(self, b):
        lines = ''.join(self.code_line(s, self.code_fg, '#8B949E') for s in b['lines'])
        lang = leaf(code_label(b))
        return ('<section style="margin:8px 0 24px;background:%s;border-radius:%dpx;overflow:hidden;">'
                '<p style="margin:0;padding:8px 14px;font-size:11px;color:#9AA0A6;font-family:%s;'
                'border-bottom:1px solid rgba(255,255,255,0.08);">%s</p>'
                '<section style="padding:12px 14px 14px;">%s</section></section>'
                % (self.code_bg, self.radius, self.mono, lang, lines))

    def steps(self, b):
        rows, n_all = [], len(b['items'])
        for n, (title, desc) in enumerate(b['items'], 1):
            last = n == n_all
            rows.append(
                '<section style="display:flex;">'
                '<section style="flex-shrink:0;width:26px;margin-right:12px;display:flex;flex-direction:column;align-items:center;">'
                '<span style="display:block;width:24px;height:24px;border-radius:50%%;background:%s;color:#FFFFFF;'
                'text-align:center;font-size:12px;line-height:24px;font-weight:700;font-family:%s;">%s</span>'
                '<section style="flex:1;width:2px;min-height:12px;background:%s;">%s</section></section>'
                '<section style="flex:1;padding:1px 0 %dpx;">'
                '<p style="margin:0;font-size:15px;line-height:1.6;color:%s;font-weight:700;">%s</p>'
                '<p style="margin:4px 0 0;font-size:14px;line-height:1.8;color:%s;">%s</p></section></section>'
                % (self.a, self.mono, leaf(str(n)), 'transparent' if last else self.soft, blank(),
                   4 if last else 16, self.ink, self.inline(title), self.body_color, self.inline(desc)))
        return '<section style="margin:6px 0 24px;">' + ''.join(rows) + '</section>'

    def check(self, b):
        rows = ''.join(
            '<section style="display:flex;align-items:flex-start;margin:0 0 8px;padding:9px 12px;background:%s;border-radius:%dpx;">'
            '<span style="flex-shrink:0;width:16px;height:16px;margin:3px 10px 0 0;border-radius:4px;%s'
            'text-align:center;font-size:11px;line-height:16px;color:#FFFFFF;font-weight:700;">%s</span>'
            '<p style="flex:1;margin:0;font-size:14px;line-height:1.75;color:%s;">%s</p></section>'
            % (self.faint if done else '#F6F7F8', self.radius,
               ('background:%s;' % self.a) if done else 'border:1.5px solid #C4C8CE;background:#FFFFFF;',
               leaf('✓') if done else blank(), self.body_color, self.inline(item))
            for item, done in b['items'])
        return '<section style="margin:4px 0 22px;">' + rows + '</section>'

    def card(self, title, desc, n):
        return ('<section style="margin:0 0 10px;padding:14px 16px;background:#FFFFFF;border:1px solid %s;border-radius:%dpx;">'
                '<p style="margin:0 0 4px;font-size:15px;font-weight:700;color:%s;">%s</p>'
                '<p style="margin:0;font-size:13px;line-height:1.75;color:%s;">%s</p></section>'
                % (self.line, self.radius, self.ink, self.inline(title), self.body_color, self.inline(desc)))

    def cards(self, b):
        return ('<section style="margin:6px 0 24px;">'
                + ''.join(self.card(t, d, n) for n, (t, d) in enumerate(b['items'], 1)) + '</section>')

    # Image rules carried over from the first published article (v0.6):
    # - corners are clipped by a wrapper (radius + overflow:hidden + line-height:0), not by <img>
    #   alone: the editor may rewrite <img> styles, and line-height:0 kills the gap under images
    # - screenshots get a 1px hairline so white UI does not melt into a white page
    # - the first image before any ## is a hero: full width, no frame padding
    # Themes tune it with: fig_pad (frame padding), fig_shadow, fig_border, fig_style
    fig_pad = 0
    fig_shadow = 'none'
    fig_border = None      # None -> 1px solid self.line

    def clip(self, inner, radius=None, extra=''):
        r = max(self.radius - 4, 0) if radius is None else radius
        return ('<section style="margin:0;border-radius:%dpx;overflow:hidden;line-height:0;%s">%s</section>'
                % (r, extra, inner))

    def figure_box(self, b):
        if b['src']:
            im = ('<img src="%s" style="display:block;width:100%%;height:auto;margin:0 auto;">'
                  % self.img_src(b['src']))
            return self.clip(im)
        return ('<section style="padding:34px 12px;text-align:center;background:%s;border:1.5px dashed %s;border-radius:%dpx;">'
                '<p style="margin:0;font-size:13px;color:%s;font-weight:700;">%s</p>'
                '<p style="margin:4px 0 0;font-size:11px;color:%s;">%s</p></section>'
                % (self.faint, self.soft, max(self.radius - 4, 0), self.a, leaf('待补素材'), self.muted,
                   leaf('发布前替换为真实图片')))

    def fig_caption(self, b):
        return ('<p style="margin:8px 0 0;font-size:12px;line-height:1.6;text-align:center;color:%s;">%s</p>'
                % (self.muted, leaf(b['caption']))) if b['caption'] else ''

    def figure(self, b):
        cap = self.fig_caption(b)
        if not b['src']:
            return '<section style="margin:8px 0 24px;">%s%s</section>' % (self.figure_box(b), cap)
        style = b.get('style') or 'frame'
        im = ('<img src="%s" style="display:block;width:100%%;height:auto;margin:0 auto;">' % self.img_src(b['src']))
        border = self.fig_border if self.fig_border is not None else '1px solid %s' % self.line
        if style == 'hero':
            # 题图：通栏、无边框，只保留圆角
            return '<section style="margin:4px 0 26px;">%s%s</section>' % (self.clip(im, self.img_radius), cap)
        if style == 'bare':
            return '<section style="margin:8px 0 24px;">%s%s</section>' % (self.clip(im, self.img_radius), cap)
        if self.fig_pad:
            # 双层相框：外层白卡（边框+淡阴影+留边），内层再圆角裁切
            outer = self.img_radius + self.fig_pad
            box = ('<section style="padding:%dpx;background:#FFFFFF;border-radius:%dpx;border:%s;box-shadow:%s;">%s</section>'
                   % (self.fig_pad, outer, border, self.fig_shadow, self.clip(im, self.img_radius)))
        else:
            box = self.clip(im, self.img_radius, 'border:%s;box-shadow:%s;' % (border, self.fig_shadow))
        return '<section style="margin:8px 0 26px;">%s%s</section>' % (box, cap)

    # multi-image ------------------------------------------------------------
    # Tokens a theme may override: img_radius, img_shadow, img_gap, img_border
    asset_prefix = ''      # build.py sets '../' so assets/ resolves from themes/
    img_shadow = 'none'
    img_border = 'none'
    img_gap = 8

    @property
    def img_radius(self):
        return max(self.radius - 2, 0)

    variant = ''       # set by build/render; lets image paths use {variant}

    def img_src(self, src):
        src = (src or '').replace('{variant}', self.variant)
        if src and not re.match(r'^(https?:|data:|/|\.\./)', src):
            src = self.asset_prefix + src
        return html.escape(src)

    def img(self, src, extra='', radius=None):
        r = self.img_radius if radius is None else radius
        if not src or src.lower() == 'todo':
            return ('<section style="padding:40px 8px;text-align:center;background:%s;border-radius:%dpx;%s">'
                    '<p style="margin:0;font-size:12px;color:%s;">%s</p></section>'
                    % (self.faint, r, extra, self.muted, leaf('待补图片')))
        im = '<img src="%s" style="display:block;width:100%%;height:auto;margin:0 auto;">' % self.img_src(src)
        if r == 0 and 'box-shadow:none' in extra:
            return im
        # corners/border/shadow live on the clip wrapper, same as figure()
        return self.clip(im, r, 'box-shadow:%s;border:%s;%s' % (self.img_shadow, self.img_border,
                                                               extra.replace('border-radius:0;', '')))

    def gallery_caption(self, text):
        if not text:
            return ''
        return ('<p style="margin:10px 0 0;font-size:12px;line-height:1.6;text-align:center;color:%s;">%s</p>'
                % (self.muted, self.inline(text)))

    def gallery_frame(self, inner):
        dots = ''.join('<span style="display:inline-block;width:7px;height:7px;margin-right:5px;border-radius:50%%;'
                       'background:%s;">%s</span>' % (c, blank()) for c in ('#E5E6EB', '#E5E6EB', '#E5E6EB'))
        return ('<section style="padding:0 6px 6px;background:#F2F3F5;border:1px solid #E5E6EB;border-radius:%dpx;">'
                '<section style="padding:8px 4px 7px;line-height:7px;">%s</section>%s</section>'
                % (self.img_radius + 4, dots, inner))

    def gallery(self, b):
        items, mode, gap = b['items'], b['mode'], self.img_gap
        n = len(items)
        if mode == 'stack':
            # 纵向拼接：多张图无缝叠成一张长图，只有外框带圆角
            body = ''.join(self.img(s, 'border-radius:0;box-shadow:none;border:none;', 0) for _, s in items)
            body = ('<section style="border-radius:%dpx;overflow:hidden;box-shadow:%s;border:%s;line-height:0;">%s</section>'
                    % (self.img_radius, self.img_shadow, self.img_border, body))
        elif mode == 'swipe':
            # 左右滑动：每张约 72% 宽，露出下一张提示可以滑
            cells = ''.join('<section style="flex-shrink:0;width:72%%;margin-right:%dpx;">%s%s</section>'
                            % (gap if k < n - 1 else 0, self.img(s),
                               ('<p style="margin:6px 0 0;font-size:11px;color:%s;">%s</p>' % (self.muted, leaf(c))) if c else '')
                            for k, (c, s) in enumerate(items))
            body = ('<section style="display:flex;overflow-x:auto;padding:2px 2px 8px;">%s</section>'
                    '<p style="margin:2px 0 0;font-size:11px;text-align:right;color:%s;">%s</p>'
                    % (cells, self.muted, leaf('左右滑动查看 %d 张 →' % n)))
        elif mode == 'scroll':
            # 上下滑动：固定高度的长图窗口
            inner = ''.join(self.img(s, 'border-radius:0;box-shadow:none;border:none;', 0) for _, s in items)
            body = ('<section style="height:420px;overflow-y:auto;border-radius:%dpx;border:1px solid %s;line-height:0;">%s</section>'
                    '<p style="margin:6px 0 0;font-size:11px;text-align:right;color:%s;">%s</p>'
                    % (self.img_radius, self.line, inner, self.muted, leaf('在框内上下滑动 ↕')))
        else:
            per = 2 if (mode == 'frame' and n > 1) or n == 4 or n > 3 else max(n, 1)
            rows = [items[k:k + per] for k in range(0, n, per)]
            out = []
            for r in rows:
                cells = []
                for k, (c, s) in enumerate(r):
                    im = self.img(s)
                    if mode == 'frame':
                        im = self.gallery_frame(self.img(s, 'box-shadow:none;border:none;'))
                    cells.append('<section style="flex:1;min-width:0;%s">%s</section>'
                                 % ('margin-right:%dpx;' % gap if k < len(r) - 1 else '', im))
                if len(r) < per:
                    cells.append('<section style="flex:%d;">%s</section>' % (per - len(r), blank()))
                out.append('<section style="display:flex;align-items:flex-start;margin:0 0 %dpx;">%s</section>'
                           % (gap, ''.join(cells)))
            body = ''.join(out)
            if n == 1 and mode == 'frame':
                body = self.gallery_frame(self.img(items[0][1], 'box-shadow:none;border:none;'))
        return '<section style="margin:10px 0 26px;">%s%s</section>' % (body, self.gallery_caption(b['caption']))

    def divider(self):
        return ('<section style="margin:30px 0;text-align:center;">'
                '<span style="font-size:14px;letter-spacing:10px;color:%s;">%s</span></section>' % (self.soft, leaf('• • •')))
