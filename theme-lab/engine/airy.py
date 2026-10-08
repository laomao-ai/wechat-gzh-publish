"""白皮 · 头部IP -- original theme (formerly 留白科技).

Design study (principles only, no code copied): AI/tech blogs that look calm
because of rhythm, not decoration -- 15-16px body, ~2x line height, slight
letter-spacing, near-black ink with one grey for annotations, 8-12px image
radius with a whisper of shadow, generous section spacing, and multi-image
layouts (side by side, stitched, swipe) carrying most of the visual weight.
"""
from components import code_label, Theme, leaf, blank, mix, SANS, MONO


def blank_text(t):
    return '—'

INK = '#1F2329'
BODY = '#373C43'
GREY = '#8F959E'
LINE = '#EBEDF0'


class Airy(Theme):
    key = 'airy'
    name = '白皮'
    series = '头部IP'
    fit = 'AI 工具实测、产品速览、头部博主式图文简报'
    principle = '像一份技术白皮书：横滑目录、PART 章节头带英文眉标、CASE / PROMPT 标签；不靠装饰靠节奏，大行距、一种灰做标注，多图承担视觉重量。'
    version = '1.0'
    variants = [('cobalt', '钴蓝', '#1456F0'), ('violet', '电紫', '#6E45E2'), ('graphite', '石墨', '#1F2329')]
    body_color = BODY
    ink = INK
    muted = GREY
    line = LINE
    page_bg = '#FFFFFF'
    radius = 10
    size = 15
    code_bg = '#F6F7F9'
    code_fg = '#1F2329'
    img_shadow = '0 4px 14px rgba(31,35,41,0.08)'
    img_gap = 8

    @property
    def img_radius(self):
        return 10

    # inline ---------------------------------------------------------------
    def strong_style(self):
        return 'color:%s;font-weight:700;' % INK

    def mark_style(self):
        return ('color:%s;font-weight:600;background:linear-gradient(to bottom,transparent 62%%,%s 62%%);padding:0 1px;'
                % (INK, mix(self.a, 0.78)))

    def code_inline_style(self):
        return ('font-family:%s;font-size:13px;color:%s;background:#F2F3F5;padding:2px 6px;border-radius:4px;margin:0 2px;'
                % (MONO, self.a if self.a != INK else '#D83931'))

    # layout ---------------------------------------------------------------
    def cover(self, meta):
        tags = ''.join('<span style="margin-right:12px;font-size:12px;color:%s;">%s</span>' % (self.a, leaf('#' + t))
                       for t in self.tags(meta))
        meta_line = '%s　·　%s　·　约 %d 分钟' % (meta.get('kicker', ''), meta.get('author', ''), self.minutes)
        return ('<section style="margin:8px 0 34px;padding:0 2px;">'
                '<p style="margin:0 0 14px;font-size:12px;letter-spacing:1px;color:%s;">%s</p>'
                '<p style="margin:0 0 14px;font-size:24px;line-height:1.45;color:%s;font-weight:800;letter-spacing:0.5px;">%s</p>'
                '<p style="margin:0 0 16px;font-size:14px;line-height:1.9;color:%s;letter-spacing:0.5px;">%s</p>'
                '<p style="margin:0;padding:0 0 18px;border-bottom:1px solid %s;">%s</p></section>'
                % (GREY, leaf(meta_line), INK, leaf(meta.get('title', '')), GREY, leaf(meta.get('digest', '')),
                   LINE, tags or blank()))

    def lead(self, text):
        return ('<section style="margin:0 0 30px;padding:14px 16px;background:#F7F8FA;border-radius:8px;">'
                '<p style="margin:0;font-size:14px;line-height:1.95;color:%s;letter-spacing:0.5px;">%s</p></section>'
                % (BODY, self.inline(text)))

    def toc(self, sections):
        # 横滑目录卡：N PARTS · CONTENT MAP，每张 = PART 编号 + 标题 + 英文眉标
        parts = [b for b in sections if not b.get('final')]
        cells = ''.join(
            '<section style="flex-shrink:0;width:44%%;margin-right:8px;padding:14px 14px 12px;background:#F7F8FA;'
            'border-radius:10px;box-sizing:border-box;">'
            '<p style="margin:0 0 10px;font-size:11px;letter-spacing:1px;line-height:1.5;color:%s;font-family:%s;font-weight:700;">%s</p>'
            '<p style="margin:0 0 6px;font-size:15px;line-height:1.5;color:%s;font-weight:800;">%s</p>'
            '<p style="margin:0;font-size:10px;letter-spacing:1px;line-height:1.6;color:%s;font-family:%s;">%s</p></section>'
            % (self.a, MONO, leaf('PART ' + self.sec_label(b, n)), INK, leaf(b['title']),
               GREY, MONO, leaf(b.get('kicker') or blank_text(b['title'])))
            for n, b in enumerate(parts, 1))
        return ('<section style="margin:0 0 40px;">'
                '<section style="display:flex;justify-content:space-between;margin:0 0 10px;">'
                '<span style="font-size:11px;letter-spacing:2px;color:%s;font-family:%s;font-weight:700;">%s</span>'
                '<span style="font-size:11px;color:%s;">%s</span></section>'
                '<section style="display:flex;overflow-x:auto;padding:0 0 6px;">%s</section></section>'
                % (INK, MONO, leaf('%d PARTS · CONTENT MAP' % len(parts)), GREY, leaf('左右滑动 →'), cells))

    def h2(self, b, n):
        if b.get('final'):
            return ('<section style="margin:56px 0 22px;">'
                    '<p style="margin:0 0 6px;font-size:11px;letter-spacing:2px;color:%s;font-family:%s;font-weight:700;">%s</p>'
                    '<p style="margin:0;font-size:20px;line-height:1.5;color:%s;font-weight:800;">%s</p></section>'
                    % (GREY, MONO, leaf('OUTLOOK'), INK, leaf(b['title'])))
        # 横排章节头：左「大号编号 + PART」，竖线，右「标题 + 英文眉标」，一行吃掉原来四行的高度
        kicker = ('<p style="margin:4px 0 0;font-size:10px;letter-spacing:2px;line-height:1.5;color:%s;font-family:%s;">%s</p>'
                  % (GREY, MONO, leaf(b['kicker']))) if b.get('kicker') else ''
        return ('<section style="display:flex;align-items:center;margin:52px 0 24px;">'
                '<section style="flex-shrink:0;width:44px;text-align:center;">'
                '<p style="margin:0;font-size:24px;line-height:1.1;color:%s;font-family:%s;font-weight:800;letter-spacing:0;">%s</p>'
                '<p style="margin:3px 0 0;font-size:9px;letter-spacing:2px;line-height:1.3;color:%s;font-family:%s;font-weight:700;">%s</p></section>'
                '<section style="flex-shrink:0;width:1px;height:36px;margin:0 14px 0 12px;background:%s;">%s</section>'
                '<section style="flex:1;min-width:0;">'
                '<p style="margin:0;font-size:18px;line-height:1.45;color:%s;font-weight:800;letter-spacing:0.5px;">%s</p>'
                '%s</section></section>'
                % (self.a, MONO, leaf(self.sec_label(b, n)), GREY, MONO, leaf('PART'),
                   mix(self.a, 0.6), blank(), INK, leaf(b['title']), kicker))

    def h3_labeled(self, b):
        # CASE 01 标签：小号实底标签 + 标题，像白皮书里的案例编号
        return ('<section style="margin:36px 0 14px;">'
                '<p style="margin:0 0 8px;"><span style="font-size:11px;letter-spacing:1px;color:#FFFFFF;background:%s;'
                'padding:2px 8px;border-radius:3px;font-family:%s;font-weight:700;">%s</span></p>'
                '<p style="margin:0;font-size:17px;line-height:1.6;color:%s;font-weight:800;">%s</p></section>'
                % (self.a, MONO, leaf(b['label']), INK, self.inline(b['text'])))

    def prompt(self, b, n):
        head = 'PROMPT %02d' % n + (' · ' + b['title'] if b.get('title') else '')
        body = ''.join('<p style="margin:0 0 6px;font-size:14px;line-height:1.9;color:%s;letter-spacing:0.5px;">%s</p>'
                       % (INK, self.inline(s.strip())) for s in b['lines'] if s.strip())
        return ('<section style="margin:6px 0 28px;border:1px solid %s;border-radius:10px;overflow:hidden;">'
                '<p style="margin:0;padding:9px 14px;font-size:11px;letter-spacing:1px;line-height:1.6;color:%s;'
                'font-family:%s;font-weight:700;background:#F7F8FA;border-bottom:1px solid %s;">%s</p>'
                '<section style="padding:12px 14px 8px;">%s</section></section>'
                % (LINE, self.a, MONO, LINE, leaf(head), body))

    def h3(self, b):
        return ('<p style="margin:34px 0 14px;font-size:16px;line-height:1.6;color:%s;font-weight:700;">'
                '<span style="color:%s;margin-right:6px;">%s</span>%s</p>'
                % (INK, self.a, leaf('/'), self.inline(b['text'])))

    def keypoint(self, text):
        return ('<section style="margin:4px 0 28px;padding:16px 18px;border:1px solid %s;border-radius:10px;">'
                '<p style="margin:0;font-size:15px;line-height:1.9;color:%s;font-weight:700;letter-spacing:0.5px;">%s</p></section>'
                % (LINE, INK, self.inline(text)))

    def quote(self, text, cite=''):
        c = ('<p style="margin:8px 0 0;font-size:12px;color:%s;">%s</p>' % (GREY, leaf('— ' + cite))) if cite else ''
        return ('<section style="margin:28px 0;padding:2px 0 2px 16px;border-left:2px solid %s;">'
                '<p style="margin:0;font-size:15px;line-height:1.95;color:%s;letter-spacing:0.5px;">%s</p>%s</section>'
                % (INK, '#5C6168', self.inline(text), c))

    CALLOUT = {
        'tip': (None, None, '提示'),
        'note': ('#646A73', '#F5F6F7', '说明'),
        'warn': ('#D46B08', '#FFF7E8', '注意'),
        'key': ('#1F2329', '#F5F6F7', '重点'),
    }

    def callout(self, b):
        c, bg, label = self.callout_colors(b['kind'])
        body = ('<p style="margin:6px 0 0;font-size:14px;line-height:1.9;color:%s;">%s</p>'
                % (BODY, self.inline(b['text']))) if b['text'] else ''
        return ('<section style="margin:4px 0 26px;padding:14px 16px;background:%s;border-radius:10px;">'
                '<p style="margin:0;font-size:14px;line-height:1.6;color:%s;font-weight:700;">'
                '<span style="color:%s;margin-right:8px;font-size:12px;">%s</span>%s</p>%s</section>'
                % (bg, INK, c, leaf(label), self.inline(b['title'] or label), body))

    def callout_colors(self, kind):
        c, bg, label = self.CALLOUT.get(kind, self.CALLOUT['note'])
        return (c or self.a), (bg or mix(self.a, 0.94)), label

    def list(self, items, ordered):
        rows = ''.join(
            '<section style="display:flex;margin:0 0 10px;">'
            '<span style="flex-shrink:0;width:22px;font-size:%s;line-height:2;color:%s;font-family:%s;">%s</span>'
            '<p style="flex:1;margin:0;font-size:15px;line-height:2;color:%s;letter-spacing:0.5px;">%s</p></section>'
            % ('12px' if ordered else '15px', self.a, MONO, leaf('%d.' % n if ordered else '·'), BODY, self.inline(it))
            for n, it in enumerate(items, 1))
        return '<section style="margin:0 0 24px;">%s</section>' % rows

    def table(self, head, rows):
        th = ''.join('<td style="padding:10px 12px;font-size:12px;color:%s;font-weight:700;background:#F7F8FA;'
                     'border-bottom:1px solid %s;">%s</td>' % (GREY, LINE, leaf(h)) for h in head)
        body = ''.join('<tr>' + ''.join(
            '<td style="padding:11px 12px;font-size:13px;line-height:1.7;color:%s;border-bottom:1px solid %s;%s">%s</td>'
            % (INK if c == 0 else BODY, LINE, 'font-weight:700;white-space:nowrap;' if c == 0 else '', self.inline(cell))
            for c, cell in enumerate(r)) + '</tr>' for r in rows)
        return ('<section style="margin:4px 0 28px;border:1px solid %s;border-radius:10px;overflow:hidden;">'
                '<table style="width:100%%;border-collapse:collapse;"><tbody><tr>%s</tr>%s</tbody></table></section>'
                % (LINE, th, body))

    def code(self, b):
        lines = ''.join(self.code_line(s, INK, '#8F959E') for s in b['lines'])
        return ('<section style="margin:4px 0 26px;background:#F6F7F9;border:1px solid %s;border-radius:10px;">'
                '<p style="margin:0;padding:8px 14px;font-size:11px;color:%s;font-family:%s;border-bottom:1px solid %s;">%s</p>'
                '<section style="padding:12px 14px 14px;">%s</section></section>'
                % (LINE, GREY, MONO, LINE, leaf(code_label(b)), lines))

    def steps(self, b):
        rows = ''.join(
            '<section style="display:flex;margin:0 0 16px;">'
            '<span style="flex-shrink:0;width:30px;font-size:13px;line-height:1.7;color:%s;font-family:%s;font-weight:700;">%s</span>'
            '<section style="flex:1;">'
            '<p style="margin:0;font-size:15px;line-height:1.7;color:%s;font-weight:700;">%s</p>'
            '<p style="margin:3px 0 0;font-size:14px;line-height:1.9;color:%s;">%s</p></section></section>'
            % (self.a, MONO, leaf('%02d' % n), INK, self.inline(t), GREY, self.inline(d))
            for n, (t, d) in enumerate(b['items'], 1))
        return ('<section style="margin:4px 0 26px;padding:16px 16px 2px;border:1px solid %s;border-radius:10px;">%s</section>'
                % (LINE, rows))

    def check(self, b):
        rows = ''.join(
            '<section style="display:flex;align-items:flex-start;margin:0 0 10px;">'
            '<span style="flex-shrink:0;width:15px;height:15px;margin:6px 10px 0 0;border-radius:4px;%s'
            'text-align:center;font-size:10px;line-height:15px;color:#FFFFFF;">%s</span>'
            '<p style="flex:1;margin:0;font-size:15px;line-height:2;color:%s;">%s</p></section>'
            % (('background:%s;' % self.a) if done else 'border:1.5px solid #C9CDD4;',
               leaf('✓') if done else blank(), BODY if done else GREY, self.inline(it))
            for it, done in b['items'])
        return '<section style="margin:0 0 24px;">%s</section>' % rows

    def cards(self, b):
        items = b['items']
        rows = []
        for k in range(0, len(items), 2):
            pair = items[k:k + 2]
            cells = ''.join(
                '<section style="flex:1;min-width:0;%spadding:14px 14px 12px;background:#F7F8FA;border-radius:10px;">'
                '<p style="margin:0 0 6px;font-size:14px;line-height:1.5;color:%s;font-weight:700;">%s</p>'
                '<p style="margin:0;font-size:13px;line-height:1.8;color:%s;">%s</p></section>'
                % ('margin-right:8px;' if j == 0 and len(pair) == 2 else '', INK, self.inline(t), GREY, self.inline(d))
                for j, (t, d) in enumerate(pair))
            rows.append('<section style="display:flex;margin:0 0 8px;">%s</section>' % cells)
        return '<section style="margin:4px 0 26px;">%s</section>' % ''.join(rows)

    # 图片：不加框，只用一层很淡的阴影托起截图
    fig_border = 'none'
    fig_shadow = '0 2px 12px rgba(15,23,42,0.08)'

    def fig_caption(self, b):
        return ('<p style="margin:10px 0 0;font-size:12px;text-align:center;color:%s;">%s</p>'
                % (GREY, leaf(b['caption']))) if b['caption'] else ''

    def note(self, text):
        return ('<p style="margin:0 0 22px;font-size:12px;line-height:1.9;color:%s;">%s</p>' % (GREY, self.inline(text)))

    def divider(self):
        return ('<section style="margin:40px auto;width:40px;border-top:1px solid #C9CDD4;">%s</section>' % blank())

    def ending(self, text, meta):
        bio = meta.get('bio', '')
        return ('<section style="margin:40px 0 10px;padding:22px 0 0;border-top:1px solid %s;">'
                '<p style="margin:0 0 10px;font-size:16px;line-height:1.8;color:%s;font-weight:700;">%s</p>'
                '<p style="margin:0;font-size:12px;line-height:1.9;color:%s;">%s</p></section>'
                % (LINE, INK, self.inline(text), GREY, leaf(bio or '感谢阅读。')))
