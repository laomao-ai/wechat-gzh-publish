"""便签 · 知识手帐. Original theme (replaces 彩签手册 v0.1, kept as LEGACY).

Design intent: a paper notebook page. Dot-grid paper, washi-tape strips,
a rubber stamp, sticky notes, polaroid cards, a to-do list TOC, kaiti
handwriting for headings. Slight tilts (transform) degrade to straight if a
client strips them, so nothing depends on them.
"""
from components import Theme, leaf, blank, mix, KAI, MONO

TAPES = ['#F6C9C0', '#C8E3D4', '#F7E1A1', '#C9D8F2', '#E3D2F0']
PAPER = '#FFFDF7'
INK = '#2D2A26'


def tape(color, width=78, tilt=-2):
    stripe = 'repeating-linear-gradient(45deg,rgba(255,255,255,0.35) 0 4px,rgba(255,255,255,0) 4px 8px)'
    return ('<section style="width:%dpx;height:16px;margin:0 auto -8px;background:%s,%s;background-color:%s;'
            'opacity:0.92;transform:rotate(%sdeg);">%s</section>' % (width, stripe, color, color, tilt, blank()))


class Journal(Theme):
    key = 'journal'
    name = '便签'
    series = '知识手帐'
    fit = '学习笔记、清单盘点、方法论、生活分享'
    principle = '把正文当成一页手帐：点阵纸、和纸胶带、印章和便签负责气氛，正文依旧清楚好读。'
    version = '1.0'
    variants = [('cherry', '樱桃红', '#D9534F'), ('ink', '钢笔蓝', '#3B5BA9'), ('grass', '青草绿', '#4E9A5B')]
    body_color = '#45403A'
    ink = INK
    muted = '#9A9086'
    line = '#E9E1D3'
    radius = 6
    page_bg = PAPER
    head_font = KAI
    code_bg = '#FFFFFF'

    def tp(self, n):
        return TAPES[(n - 1) % len(TAPES)]

    def strong_style(self):
        return 'color:%s;font-weight:700;' % INK

    def mark_style(self):
        return ('color:%s;font-weight:700;background:linear-gradient(to bottom,transparent 50%%,%s 50%%,%s 88%%,transparent 88%%);'
                'padding:0 2px;' % (INK, mix(self.a, 0.72), mix(self.a, 0.72)))

    def code_inline_style(self):
        return ('font-family:%s;font-size:13px;color:%s;background:#FFF3C4;padding:1px 5px;border-radius:3px;margin:0 2px;'
                % (MONO, INK))

    def render(self, meta, blocks):
        body = super().render(meta, blocks)
        dots = 'radial-gradient(%s 1px,transparent 1px)' % '#E6DCCB'
        return body.replace('background:%s;font-family' % PAPER,
                            'background:%s;background-image:%s;background-size:16px 16px;font-family' % (PAPER, dots), 1)

    # -- cover ------------------------------------------------------------
    def cover(self, m):
        tilts = (-3, 2, -1, 3)
        tags = ''.join('<span style="display:inline-block;margin:0 8px 8px 0;padding:3px 10px;background:%s;'
                       'font-size:12px;color:%s;transform:rotate(%sdeg);box-shadow:1px 2px 0 rgba(0,0,0,0.06);">%s</span>'
                       % (self.tp(i + 1), INK, tilts[i % 4], leaf(t)) for i, t in enumerate(self.tags(m)))
        stamp = ('<span style="flex-shrink:0;display:inline-block;width:52px;height:52px;border-radius:50%%;'
                 'border:2px solid %s;color:%s;text-align:center;transform:rotate(-12deg);">'
                 '<span style="display:block;margin-top:9px;font-size:10px;line-height:1.2;font-weight:800;letter-spacing:1px;">%s</span>'
                 '<span style="display:block;font-size:13px;line-height:1.3;font-weight:800;font-family:%s;">%s</span></span>'
                 % (self.a, self.a, leaf('NOTE'), MONO, leaf(m.get('date', '10·08'))))
        return (
            '<section style="margin:10px 0 28px;">%s'
            '<section style="padding:26px 20px 18px;background:#FFFFFF;border:1px solid %s;'
            'box-shadow:3px 4px 0 %s;">'
            '<section style="display:flex;justify-content:space-between;align-items:flex-start;">'
            '<p style="margin:0 0 10px;font-size:12px;color:%s;font-weight:700;letter-spacing:1px;">%s</p>%s</section>'
            '<p style="margin:0 0 12px;font-size:24px;line-height:1.45;color:%s;font-weight:800;font-family:%s;">%s</p>'
            '<p style="margin:0 0 16px;padding:0 0 12px;font-size:14px;line-height:1.8;color:#6E655B;'
            'border-bottom:1px dashed %s;">%s</p>%s'
            '<p style="margin:4px 0 0;font-size:12px;color:%s;font-family:%s;">%s</p></section></section>'
            % (tape(self.tp(1), 96, -3), self.line, '#EFE6D6', self.a, leaf('✎ ' + m.get('kicker', '')), stamp,
               INK, KAI, leaf(m.get('title', '')), self.line, leaf(m.get('digest', '')), tags,
               self.muted, KAI, leaf('—— 记于 ' + m.get('author', '') + ' 的手帐')))

    def lead(self, text):
        return ('<section style="margin:0 14px 30px;padding:16px 18px;background:#FFF1A8;transform:rotate(-1deg);'
                'box-shadow:2px 4px 8px rgba(120,100,20,0.14);">'
                '<p style="margin:0;font-size:16px;line-height:1.85;color:#3D3820;font-family:%s;font-weight:700;">%s</p></section>'
                % (KAI, self.inline(text)))

    def toc(self, sections):
        rows = ''.join(
            '<section style="display:flex;align-items:center;padding:7px 0;border-bottom:1px dashed %s;">'
            '<span style="flex-shrink:0;width:14px;height:14px;margin-right:10px;border:1.5px solid %s;border-radius:3px;">%s</span>'
            '<span style="flex-shrink:0;width:30px;font-size:12px;color:%s;font-family:%s;font-weight:700;">%s</span>'
            '<span style="flex:1;font-size:14px;color:%s;">%s</span></section>'
            % (self.line, '#B9AE9F', blank(), self.a, MONO, leaf(self.sec_label(b, n)), INK, leaf(b['title']))
            for n, b in enumerate(sections, 1))
        return ('<section style="margin:0 0 34px;">%s'
                '<section style="padding:20px 18px 12px;background:#FFFFFF;border:1px solid %s;">'
                '<p style="margin:0 0 6px;font-size:17px;color:%s;font-family:%s;font-weight:800;">%s</p>%s</section></section>'
                % (tape(self.tp(2), 70, 2), self.line, INK, KAI, leaf('今天要读完的 To-do'), rows))

    # -- headings ---------------------------------------------------------
    def h2(self, b, n):
        num = '终' if b.get('final') else (b['num'] or '%02d' % n)
        return ('<section style="margin:46px 0 18px;padding:0 0 8px;border-bottom:2px dotted %s;">'
                '<p style="margin:0;font-size:19px;line-height:1.5;color:%s;font-weight:800;font-family:%s;">'
                '<span style="display:inline-block;margin-right:10px;font-size:24px;color:%s;font-weight:900;'
                'font-family:%s;transform:rotate(-6deg);">%s</span>'
                '<span style="padding:0 6px;background:linear-gradient(to bottom,transparent 55%%,%s 55%%);">%s</span></p></section>'
                % (mix(self.a, 0.55), INK, KAI, self.a, MONO, leaf(num), self.tp(n), leaf(b['title'])))

    def h3(self, b):
        return ('<p style="margin:28px 0 12px;font-size:16px;line-height:1.5;color:%s;font-weight:800;font-family:%s;">'
                '<span style="color:%s;margin-right:6px;">%s</span>%s</p>'
                % (INK, KAI, self.a, leaf('✿'), self.inline(b['text'])))

    # -- emphasis ---------------------------------------------------------
    def keypoint(self, text):
        return ('<section style="margin:8px 0 26px;display:flex;align-items:center;padding:14px 14px 14px 16px;'
                'background:#FFFFFF;border:1.5px dashed %s;">'
                '<p style="flex:1;margin:0;font-size:15px;line-height:1.85;color:%s;font-weight:700;">%s</p>'
                '<span style="flex-shrink:0;margin-left:12px;display:inline-block;width:42px;height:42px;border-radius:50%%;'
                'border:2px solid %s;color:%s;text-align:center;font-size:13px;line-height:38px;font-weight:900;'
                'font-family:%s;transform:rotate(10deg);">%s</span></section>'
                % (mix(self.a, 0.45), INK, self.inline(text), self.a, self.a, KAI, leaf('重点')))

    def quote(self, text, cite=''):
        c = ('<p style="margin:8px 0 0;font-size:12px;color:%s;font-family:%s;">%s</p>'
             % (self.muted, KAI, leaf('—— ' + cite))) if cite else ''
        return ('<section style="margin:26px 8px 30px;">'
                '<section style="padding:16px 18px;background:#FFFFFF;border:1.5px solid %s;border-radius:16px;">'
                '<p style="margin:0;font-size:16px;line-height:1.85;color:%s;font-family:%s;font-weight:700;">%s</p>%s</section>'
                '<section style="width:12px;height:12px;margin:-7px 0 0 28px;background:#FFFFFF;border-right:1.5px solid %s;'
                'border-bottom:1.5px solid %s;transform:rotate(45deg);">%s</section></section>'
                % (INK, INK, KAI, self.inline(text), c, INK, INK, blank()))

    CALLOUT = {
        'tip': ('#3E8E5A', '#E6F4E2', '小贴士'),
        'note': ('#6E655B', '#F4EFE6', '旁注'),
        'warn': ('#C2410C', '#FFE8D9', '小心'),
        'key': (None, None, '记住'),
    }

    def callout(self, b):
        c, bg, label = self.callout_colors(b['kind'])
        bg = '#FFF1A8' if b['kind'] == 'key' else bg
        title = b['title'] or label
        body = ('<p style="margin:6px 0 0;font-size:14px;line-height:1.8;color:%s;">%s</p>'
                % (self.body_color, self.inline(b['text']))) if b['text'] else ''
        return ('<section style="margin:8px 6px 26px;">%s'
                '<section style="padding:16px 16px 14px;background:%s;box-shadow:2px 3px 6px rgba(0,0,0,0.07);">'
                '<p style="margin:0;font-size:15px;color:%s;font-weight:800;font-family:%s;">'
                '<span style="display:inline-block;margin-right:8px;padding:0 6px;border:1.5px solid %s;border-radius:3px;'
                'font-size:11px;line-height:1.6;">%s</span>%s</p>%s</section></section>'
                % (tape(self.tp(3), 56, 3), bg, c, KAI, c, leaf(label), self.inline(title), body))

    def note(self, text):
        return ('<p style="margin:-6px 0 22px;font-size:12px;line-height:1.7;color:%s;font-family:%s;">%s</p>'
                % (self.muted, KAI, self.inline('✎ ' + text)))

    # -- structure --------------------------------------------------------
    def list(self, items, ordered):
        rows = ''.join(
            '<section style="display:flex;align-items:flex-start;margin:0 0 10px;">'
            '<span style="flex-shrink:0;width:22px;height:22px;margin:2px 10px 0 0;border-radius:50%%;background:%s;'
            'text-align:center;font-size:12px;line-height:22px;color:%s;font-weight:800;font-family:%s;">%s</span>'
            '<p style="flex:1;margin:0;font-size:15px;line-height:1.85;color:%s;">%s</p></section>'
            % (self.tp(n), INK, MONO, leaf(str(n) if ordered else '✦'), self.body_color, self.inline(item))
            for n, item in enumerate(items, 1))
        return '<section style="margin:4px 0 22px;">' + rows + '</section>'

    def table(self, head, rows):
        th = ''.join('<td style="padding:9px 10px;font-size:13px;font-weight:800;color:%s;font-family:%s;'
                     'border-bottom:2px solid %s;">%s</td>' % (INK, KAI, self.a, leaf(h)) for h in head)
        body = ''.join('<tr>' + ''.join(
            '<td style="padding:10px;font-size:13px;line-height:1.7;color:%s;border-bottom:1px solid #DCE7F2;%s">%s</td>'
            % (self.body_color, ('font-weight:800;color:%s;white-space:nowrap;' % INK) if c == 0 else '', self.inline(cell))
            for c, cell in enumerate(row)) + '</tr>' for row in rows)
        return ('<section style="margin:8px 0 28px;">%s'
                '<section style="padding:14px 12px 8px;background:#FFFFFF;border:1px solid %s;box-shadow:3px 4px 0 #EFE6D6;">'
                '<table style="width:100%%;border-collapse:collapse;"><tbody><tr>%s</tr>%s</tbody></table></section></section>'
                % (tape(self.tp(4), 80, -2), self.line, th, body))

    def code(self, b):
        grid = ('linear-gradient(#EEF2F7 1px,transparent 1px),linear-gradient(90deg,#EEF2F7 1px,transparent 1px)')
        lines = ''.join(self.code_line(s, '#2D3748', '#9AA5B1') for s in b['lines'])
        return ('<section style="margin:8px 0 26px;">%s'
                '<section style="padding:14px 14px 12px;background:#FFFFFF;background-image:%s;background-size:14px 14px;'
                'border:1px solid #D9E2EC;">'
                '<p style="margin:0 0 8px;font-size:11px;color:%s;font-family:%s;font-weight:800;">%s</p>%s</section></section>'
                % (tape(self.tp(2), 64, 2), grid, self.a, MONO, leaf('✎ ' + (b['lang'] or 'code')), lines))

    def steps(self, b):
        rows, n_all = [], len(b['items'])
        for n, (title, desc) in enumerate(b['items'], 1):
            last = n == n_all
            rows.append(
                '<section style="display:flex;">'
                '<section style="flex-shrink:0;width:30px;margin-right:12px;display:flex;flex-direction:column;align-items:center;">'
                '<span style="display:block;width:26px;height:26px;border-radius:50%%;border:2px solid %s;background:%s;'
                'text-align:center;font-size:13px;line-height:26px;color:%s;font-weight:900;font-family:%s;">%s</span>'
                '<section style="flex:1;width:0;border-left:2px dashed %s;">%s</section></section>'
                '<section style="flex:1;padding:2px 0 %dpx;">'
                '<p style="margin:0;font-size:15px;line-height:1.6;color:%s;font-weight:800;font-family:%s;">%s</p>'
                '<p style="margin:4px 0 0;font-size:14px;line-height:1.8;color:%s;">%s</p></section></section>'
                % (INK, self.tp(n), INK, KAI, leaf(str(n)), 'transparent' if last else '#CFC4B4', blank(),
                   4 if last else 16, INK, KAI, self.inline(title), self.body_color, self.inline(desc)))
        return '<section style="margin:6px 0 24px;">' + ''.join(rows) + '</section>'

    def check(self, b):
        rows = ''.join(
            '<section style="display:flex;align-items:flex-start;padding:8px 2px;border-bottom:1px dashed %s;">'
            '<span style="flex-shrink:0;width:16px;height:16px;margin:4px 10px 0 0;border:1.5px solid %s;border-radius:3px;'
            'text-align:center;font-size:13px;line-height:14px;color:%s;font-weight:900;">%s</span>'
            '<p style="flex:1;margin:0;font-size:14px;line-height:1.8;color:%s;">%s</p></section>'
            % (self.line, INK, self.a, leaf('✓') if done else blank(), self.body_color, self.inline(item))
            for item, done in b['items'])
        return ('<section style="margin:4px 0 24px;padding:6px 14px 8px;background:#FFFFFF;border:1px solid %s;">%s</section>'
                % (self.line, rows))

    def card(self, title, desc, n):
        tilt = (-1.2, 1, -0.6, 1.4)[(n - 1) % 4]
        return ('<section style="margin:0 6px 14px;">%s'
                '<section style="padding:16px 16px 14px;background:#FFFFFF;border:1px solid %s;transform:rotate(%sdeg);'
                'box-shadow:2px 3px 0 #EFE6D6;">'
                '<p style="margin:0 0 4px;font-size:16px;font-weight:800;color:%s;font-family:%s;">%s</p>'
                '<p style="margin:0;font-size:13px;line-height:1.75;color:%s;">%s</p></section></section>'
                % (tape(self.tp(n), 54, -tilt * 2), self.line, tilt, INK, KAI, self.inline(title),
                   self.body_color, self.inline(desc)))

    def figure(self, b):
        if b['src'] and b.get('style') in ('hero', 'bare'):
            return super().figure(b)
        cap = ('<p style="margin:10px 0 0;font-size:13px;text-align:center;color:%s;font-family:%s;">%s</p>'
               % (self.muted, KAI, leaf(b['caption']))) if b['caption'] else ''
        return ('<section style="margin:10px 10px 28px;">%s'
                '<section style="padding:10px 10px 12px;background:#FFFFFF;border:1px solid %s;transform:rotate(-0.8deg);'
                'box-shadow:2px 4px 8px rgba(0,0,0,0.08);">%s%s</section></section>'
                % (tape(self.tp(5), 70, 2), self.line, self.figure_box(b), cap))

    def divider(self):
        return ('<section style="margin:32px 0;display:flex;align-items:center;">'
                '<span style="margin-right:6px;font-size:14px;color:%s;">%s</span>'
                '<section style="flex:1;border-bottom:1.5px dashed #CFC4B4;">%s</section></section>'
                % (self.muted, leaf('✂'), blank()))

    def ending(self, text, m):
        bio = m.get('bio', '')
        bio_p = ('<p style="margin:10px 0 0;font-size:12px;line-height:1.7;color:%s;">%s</p>' % (self.muted, leaf(bio))) if bio else ''
        return ('<section style="margin:42px 4px 10px;">%s'
                '<section style="padding:20px 18px 18px;background:#FFFFFF;border:1px solid %s;box-shadow:3px 4px 0 #EFE6D6;">'
                '<section style="display:flex;justify-content:space-between;align-items:flex-start;margin:0 0 10px;">'
                '<p style="margin:0;font-size:12px;color:%s;font-weight:800;letter-spacing:2px;">%s</p>'
                '<span style="flex-shrink:0;display:inline-block;width:40px;height:46px;border:1.5px dashed %s;'
                'text-align:center;font-size:18px;line-height:44px;">%s</span></section>'
                '<p style="margin:0 0 12px;font-size:17px;line-height:1.75;color:%s;font-weight:800;font-family:%s;">%s</p>'
                '<p style="margin:0;padding-top:10px;border-top:1px dashed %s;font-size:13px;color:%s;font-family:%s;">%s</p>%s'
                '</section></section>'
                % (tape(self.tp(1), 90, -2), self.line, self.a, leaf('POSTCARD · 写给你'), self.a, leaf('💌'),
                   INK, KAI, self.inline(text), self.line, self.muted, KAI,
                   leaf('留言告诉我，下一页手帐写什么。—— ' + m.get('author', '')), bio_p))
