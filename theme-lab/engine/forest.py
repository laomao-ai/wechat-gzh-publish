"""青林 · 经典系列. Original theme: a full component set on a forest-green palette.

Design intent: white page, one living green, soft-tinted surfaces, round but
not bubbly (radius 10). Signature pieces: trail-map TOC, number tile section
heads, "题眼" lead capsule, timeline steps, forest code window, leaf dividers,
three-pill closing card. Everything here is drawn from scratch.
"""
from components import Theme, leaf, blank, mix, MONO


class Forest(Theme):
    key = 'forest'
    name = '青林'
    series = '经典通用'
    fit = '综合长文、产品发布、开源介绍、经验复盘'
    principle = '白底一抹活绿：浅绿面承担分区，深绿只落在编号、重点和行动处；组件多但同一套圆角与间距。'
    version = '1.0'
    variants = [('leaf', '叶绿', '#12945F'), ('pine', '松墨', '#2E6B4F'), ('lake', '湖青', '#0E8C8C')]
    body_color = '#33413A'
    ink = '#18241E'
    muted = '#8C9A92'
    line = '#E2ECE6'
    radius = 10
    code_bg = '#14231C'
    code_fg = '#DDEBE3'

    def __init__(self, accent):
        super().__init__(accent)
        self.mint = mix(accent, 0.90)
        self.mist = mix(accent, 0.955)

    def strong_style(self):
        return 'color:%s;font-weight:700;' % self.a

    def mark_style(self):
        return ('color:%s;font-weight:700;background:linear-gradient(to bottom,transparent 58%%,#FFE27A 58%%);'
                'padding:0 2px;' % self.ink)

    # -- cover ------------------------------------------------------------
    def cover(self, m):
        tags = ''.join('<span style="display:inline-block;margin:0 6px 6px 0;padding:3px 10px;border-radius:999px;'
                       'background:%s;font-size:11px;color:%s;font-weight:600;">%s</span>'
                       % (self.mint, self.deep, leaf('# ' + t)) for t in self.tags(m))
        return (
            '<section style="margin:4px 0 26px;border-radius:14px;overflow:hidden;border:1px solid %s;'
            'box-shadow:0 6px 20px rgba(20,60,40,0.06);">'
            '<section style="padding:22px 20px 18px;background:linear-gradient(160deg,%s 0%%,#FFFFFF 70%%);">'
            '<p style="margin:0 0 14px;"><span style="display:inline-block;padding:3px 10px;border-radius:999px;'
            'background:%s;font-size:11px;color:#FFFFFF;font-weight:700;letter-spacing:1px;">%s</span></p>'
            '<p style="margin:0 0 12px;font-size:23px;line-height:1.42;color:%s;font-weight:800;letter-spacing:0.3px;">%s</p>'
            '<section style="width:40px;height:4px;border-radius:2px;margin:0 0 14px;'
            'background:linear-gradient(90deg,%s,%s);">%s</section>'
            '<p style="margin:0 0 14px;font-size:14px;line-height:1.8;color:#5D6B63;">%s</p>%s</section>'
            '<section style="display:flex;justify-content:space-between;padding:10px 20px;background:%s;">'
            '<span style="font-size:12px;color:%s;font-weight:700;">%s</span>'
            '<span style="font-size:12px;color:%s;">%s</span></section></section>'
            % (self.line, self.mist, self.a, leaf(m.get('kicker', '')), self.ink, leaf(m.get('title', '')),
               self.a, self.soft, blank(), leaf(m.get('digest', '')), tags,
               self.a, '#FFFFFF', leaf('文 / ' + m.get('author', '')),
               mix(self.a, 0.75), leaf('阅读约 %d 分钟' % self.minutes)))

    def lead(self, text):
        return ('<section style="margin:0 0 26px;padding:18px 20px;text-align:center;background:%s;border-radius:%dpx;">'
                '<p style="margin:0 0 8px;font-size:11px;letter-spacing:4px;color:%s;font-weight:700;">%s</p>'
                '<p style="margin:0;font-size:16px;line-height:1.8;color:%s;font-weight:700;">%s</p></section>'
                % (self.mist, self.radius, self.a, leaf('— 题眼 —'), self.ink, self.inline(text)))

    # -- navigation -------------------------------------------------------
    def toc(self, sections):
        rows, n_all = [], len(sections)
        for n, b in enumerate(sections, 1):
            last = n == n_all
            label = '终章' if b.get('final') else 'PART ' + self.sec_label(b, n)
            rows.append(
                '<section style="display:flex;">'
                '<section style="flex-shrink:0;width:14px;margin-right:12px;display:flex;flex-direction:column;align-items:center;">'
                '<span style="display:block;width:10px;height:10px;margin-top:5px;border-radius:50%%;'
                'background:%s;border:2px solid %s;">%s</span>'
                '<section style="flex:1;width:2px;background:%s;">%s</section></section>'
                '<section style="flex:1;padding:0 0 %dpx;">'
                '<p style="margin:0;font-size:10px;letter-spacing:1px;color:%s;font-weight:700;font-family:%s;">%s</p>'
                '<p style="margin:1px 0 0;font-size:14px;line-height:1.6;color:%s;font-weight:600;">%s</p></section></section>'
                % ('#FFFFFF' if b.get('final') else self.a, self.a, blank(),
                   'transparent' if last else self.soft, blank(), 0 if last else 12,
                   self.muted, MONO, leaf(label), self.ink, leaf(b['title'])))
        return ('<section style="margin:4px 0 32px;padding:16px 18px 14px;border-radius:%dpx;background:%s;border:1px solid %s;">'
                '<section style="display:flex;justify-content:space-between;margin:0 0 12px;">'
                '<span style="font-size:13px;color:%s;font-weight:800;">%s</span>'
                '<span style="font-size:12px;color:%s;">%s</span></section>%s</section>'
                % (self.radius, '#FFFFFF', self.line, self.ink, leaf('🌿 本文路线'), self.muted,
                   leaf('共 %d 站' % n_all), ''.join(rows)))

    # -- headings ---------------------------------------------------------
    def h2(self, b, n):
        final = b.get('final')
        num = '//' if final else (b['num'] or '%02d' % n)
        sub = 'LAST STOP' if final else 'SECTION %s / %02d' % (num, self.total)
        return ('<section style="margin:44px 0 18px;">'
                '<section style="display:flex;align-items:center;">'
                '<span style="flex-shrink:0;width:44px;height:44px;margin-right:12px;border-radius:12px;background:%s;'
                'color:#FFFFFF;text-align:center;font-size:19px;line-height:44px;font-weight:800;font-family:%s;'
                'box-shadow:0 4px 10px %s;">%s</span>'
                '<section style="flex:1;">'
                '<p style="margin:0;font-size:10px;letter-spacing:2px;color:%s;font-weight:700;font-family:%s;">%s</p>'
                '<p style="margin:2px 0 0;font-size:18px;line-height:1.45;color:%s;font-weight:800;">%s</p></section></section>'
                '<section style="margin:12px 0 0;height:2px;border-radius:1px;'
                'background:linear-gradient(90deg,%s 0%%,%s 30%%,rgba(255,255,255,0) 100%%);">%s</section></section>'
                % (self.a, MONO, mix(self.a, 0.7), leaf(num), self.a, MONO, leaf(sub),
                   self.ink, leaf(b['title']), self.a, self.soft, blank()))

    def h3(self, b):
        return ('<section style="margin:28px 0 14px;">'
                # block-level, not inline-block: WeChat rewrites inline-block and the
                # background then only covers the first line of a wrapped heading.
                '<p style="margin:0;padding:6px 14px 6px 10px;border-radius:0 8px 8px 0;'
                'background:linear-gradient(90deg,%s,%s);border-left:3px solid %s;'
                'font-size:15px;line-height:1.5;color:%s;font-weight:800;">%s</p></section>'
                % (self.mint, self.mist, self.a, self.deep, self.inline(b['text'])))

    # -- emphasis ---------------------------------------------------------
    def keypoint(self, text):
        return ('<section style="margin:8px 0 26px;padding:16px 18px 16px;border-radius:%dpx;background:%s;'
                'border:1px solid %s;">'
                '<p style="margin:0 0 6px;"><span style="display:inline-block;padding:1px 8px;border-radius:4px;'
                'background:%s;font-size:11px;color:#FFFFFF;font-weight:700;letter-spacing:1px;">%s</span></p>'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:%s;font-weight:700;">%s</p></section>'
                % (self.radius, self.mist, self.mint, self.a, leaf('划重点'), self.ink, self.inline(text)))

    def quote(self, text, cite=''):
        c = ('<p style="margin:10px 0 0;font-size:12px;color:%s;">%s</p>' % (self.muted, leaf('—— ' + cite))) if cite else ''
        return ('<section style="margin:26px 0;padding:14px 18px 16px;border-radius:%dpx;background:#FAFBFA;'
                'border:1px solid %s;">'
                '<p style="margin:0;font-size:24px;line-height:1;color:%s;font-weight:900;font-family:Georgia,serif;">%s</p>'
                '<p style="margin:2px 0 0;font-size:15px;line-height:1.85;color:%s;font-weight:600;">%s</p>%s</section>'
                % (self.radius, self.line, self.soft, leaf('“'), self.ink, self.inline(text), c))

    CALLOUT = {
        'tip': (None, None, '💡 小贴士'),
        'note': ('#66756D', '#F4F6F5', '📎 补充'),
        'warn': ('#C46A0C', '#FFF6E8', '⚠️ 注意'),
        'key': (None, None, '🌱 关键'),
    }

    def callout(self, b):
        c, bg, label = self.callout_colors(b['kind'])
        bg = self.mist if b['kind'] in ('tip', 'key') else bg
        title = ('<p style="margin:4px 0 0;font-size:15px;line-height:1.6;color:%s;font-weight:800;">%s</p>'
                 % (self.ink, self.inline(b['title']))) if b['title'] else ''
        body = ('<p style="margin:6px 0 0;font-size:14px;line-height:1.8;color:%s;">%s</p>'
                % (self.body_color, self.inline(b['text']))) if b['text'] else ''
        return ('<section style="margin:8px 0 24px;padding:12px 16px 14px;border-radius:%dpx;background:%s;'
                'border:1px dashed %s;">'
                '<p style="margin:0;font-size:12px;color:%s;font-weight:800;letter-spacing:1px;">%s</p>%s%s</section>'
                % (self.radius, bg, mix(c, 0.55), c, leaf(label), title, body))

    def note(self, text):
        return ('<p style="margin:-6px 0 22px;padding:0 0 0 10px;border-left:2px solid %s;font-size:12px;'
                'line-height:1.7;color:%s;">%s</p>' % (self.line, self.muted, self.inline(text)))

    # -- structure --------------------------------------------------------
    def list(self, items, ordered):
        rows = ''.join(
            '<section style="display:flex;align-items:flex-start;margin:0 0 8px;padding:9px 14px;border-radius:%dpx;background:%s;">'
            '<span style="flex-shrink:0;margin-right:10px;font-size:13px;line-height:1.75;color:%s;font-weight:800;font-family:%s;">%s</span>'
            '<p style="flex:1;margin:0;font-size:14px;line-height:1.75;color:%s;">%s</p></section>'
            % (self.radius - 2, self.mist, self.a, MONO, leaf(('%02d' % n) if ordered else '●'),
               self.body_color, self.inline(item))
            for n, item in enumerate(items, 1))
        return '<section style="margin:4px 0 22px;">' + rows + '</section>'

    def table(self, head, rows):
        th = ''.join('<td style="padding:10px 12px;font-size:12px;font-weight:800;color:%s;background:%s;'
                     'border-bottom:1px solid %s;letter-spacing:0.5px;">%s</td>'
                     % (self.deep, self.mint, self.soft, leaf(h)) for h in head)
        body = ''
        for r, row in enumerate(rows):
            last = r == len(rows) - 1
            body += '<tr>' + ''.join(
                '<td style="padding:11px 12px;font-size:13px;line-height:1.7;color:%s;background:#FFFFFF;%s%s">%s</td>'
                % (self.body_color, '' if last else 'border-bottom:1px solid %s;' % self.line,
                   ('font-weight:800;color:%s;white-space:nowrap;' % self.a) if c == 0 else '', self.inline(cell))
                for c, cell in enumerate(row)) + '</tr>'
        return ('<section style="margin:8px 0 26px;border-radius:%dpx;overflow:hidden;border:1px solid %s;">'
                '<table style="width:100%%;border-collapse:collapse;"><tbody><tr>%s</tr>%s</tbody></table></section>'
                % (self.radius, self.soft, th, body))

    def code(self, b):
        dots = ''.join('<span style="display:inline-block;width:8px;height:8px;margin-right:5px;border-radius:50%%;'
                       'background:%s;">%s</span>' % (c, blank()) for c in ('#E8705F', '#E6B44C', self.a))
        lines = ''.join(self.code_line(s, self.code_fg, '#7F9A8C') for s in b['lines'])
        return ('<section style="margin:8px 0 24px;border-radius:%dpx;overflow:hidden;background:%s;'
                'box-shadow:0 6px 16px rgba(10,40,25,0.16);">'
                '<section style="display:flex;justify-content:space-between;align-items:center;padding:9px 14px;'
                'background:rgba(255,255,255,0.05);">'
                '<span style="line-height:8px;">%s</span>'
                '<span style="font-size:10px;color:%s;font-family:%s;letter-spacing:1px;">%s</span></section>'
                '<section style="padding:12px 16px 14px;">%s</section></section>'
                % (self.radius, self.code_bg, dots, mix(self.a, 0.45), MONO, leaf((b['lang'] or 'text').upper()), lines))

    def code_inline_style(self):
        return ('font-family:%s;font-size:13px;color:%s;background:%s;padding:1px 6px;border-radius:5px;margin:0 2px;'
                % (MONO, self.deep, self.mint))

    def check(self, b):
        rows = ''.join(
            '<section style="display:flex;align-items:flex-start;margin:0 0 8px;padding:10px 14px;border-radius:%dpx;'
            'background:%s;border:1px solid %s;">'
            '<span style="flex-shrink:0;width:18px;height:18px;margin:2px 10px 0 0;border-radius:6px;%s'
            'text-align:center;font-size:12px;line-height:18px;color:#FFFFFF;font-weight:800;">%s</span>'
            '<p style="flex:1;margin:0;font-size:14px;line-height:1.75;color:%s;%s">%s</p></section>'
            % (self.radius - 2, self.mist if done else '#FFFFFF', self.mint if done else self.line,
               ('background:%s;' % self.a) if done else 'border:1.5px solid #BFCBC4;background:#FFFFFF;',
               leaf('✓') if done else blank(), self.body_color, 'font-weight:600;' if done else '',
               self.inline(item))
            for item, done in b['items'])
        return '<section style="margin:4px 0 22px;">' + rows + '</section>'

    def card(self, title, desc, n):
        return ('<section style="margin:0 0 10px;padding:14px 16px;border-radius:%dpx;background:#FFFFFF;'
                'border:1px solid %s;border-top:3px solid %s;">'
                '<p style="margin:0 0 4px;font-size:10px;letter-spacing:1px;color:%s;font-family:%s;font-weight:700;">%s</p>'
                '<p style="margin:0 0 4px;font-size:15px;font-weight:800;color:%s;">%s</p>'
                '<p style="margin:0;font-size:13px;line-height:1.75;color:%s;">%s</p></section>'
                % (self.radius, self.line, self.a if n == 1 else self.soft, self.muted, MONO, leaf('NO.%02d' % n),
                   self.ink, self.inline(title), self.body_color, self.inline(desc)))

    # 图片：沿用第一篇的双层圆角相框（外白卡留 6px + 淡阴影，内层圆角裁切）
    fig_pad = 6
    fig_shadow = '0 4px 14px rgba(20,60,40,0.06)'

    def fig_caption(self, b):
        return ('<p style="margin:10px 0 0;font-size:12px;text-align:center;color:%s;">%s</p>'
                % (self.muted, leaf('▲ ' + b['caption']))) if b['caption'] else ''

    def divider(self):
        return ('<section style="margin:32px 0;display:flex;align-items:center;">'
                '<section style="flex:1;height:1px;background:%s;">%s</section>'
                '<span style="margin:0 12px;font-size:12px;color:%s;letter-spacing:6px;">%s</span>'
                '<section style="flex:1;height:1px;background:%s;">%s</section></section>'
                % (self.line, blank(), self.soft, leaf('✦ ✦ ✦'), self.line, blank()))

    # -- closing ----------------------------------------------------------
    def ending(self, text, m):
        pills = ''.join('<span style="display:inline-block;margin:0 4px;padding:6px 14px;border-radius:999px;'
                        'background:%s;font-size:12px;color:%s;font-weight:700;%s">%s</span>'
                        % (self.a if i == 2 else '#FFFFFF', '#FFFFFF' if i == 2 else self.deep,
                           '' if i == 2 else 'border:1px solid %s;' % self.soft, leaf(t))
                        for i, t in enumerate(('👍 点赞', '👀 在看', '↗ 转发')))
        bio = m.get('bio', '')
        bio_p = ('<p style="margin:14px 0 0;font-size:12px;line-height:1.7;color:%s;">%s</p>'
                 % (self.muted, leaf(bio))) if bio else ''
        return ('<section style="margin:40px 0 10px;padding:22px 20px 20px;border-radius:14px;text-align:center;'
                'background:linear-gradient(180deg,%s 0%%,#FFFFFF 100%%);border:1px solid %s;">'
                '<p style="margin:0 0 10px;font-size:11px;letter-spacing:3px;color:%s;font-weight:800;">%s</p>'
                '<p style="margin:0 0 16px;font-size:16px;line-height:1.75;color:%s;font-weight:800;">%s</p>'
                '<section style="margin:0 0 4px;">%s</section>%s</section>'
                % (self.mist, self.line, self.a, leaf('— 留言区见 —'), self.ink, self.inline(text), pills, bio_p))
