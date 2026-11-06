"""纸墨（版心草图 v1 视觉）：纸白底、墨色宋体标题、一枚朱砂印、1px 细线、无投影、圆角 2。"""
from components import Theme, leaf, blank, mix, SANS, SERIF, MONO
from themes import Clay  # 版心在陶土上派生

INK = '#1A1917'; G6 = '#746E65'; G3 = '#D6D1C6'; G1 = '#EFECE5'; PAPER = '#F7F5F0'; MOSS = '#3D5A44'


class Banxin(Clay):
    key = 'banxin'
    name = '纸墨'
    series = '版心'
    fit = '产品发布、长文、观点'
    principle = '纸白做底，墨色宋体立骨架，朱砂只盖在要紧处，像一枚亲手按下的印。'
    variants = [('zhusha', '朱砂', '#BA3E2A'), ('moss', '苔绿', MOSS)]
    page_bg = PAPER
    body_color = '#3A3733'
    line = G3
    radius = 2
    ink = INK
    muted = G6
    code_bg = '#1F1E1B'
    code_fg = '#ECE8DF'
    body_font = SANS
    size, lh, ls, gap, pad, cover_bleed = 15, 1.9, 0.5, 22, 18, False

    def seal(self, text, size=34):
        return ('<span style="display:inline-block;width:%dpx;height:%dpx;line-height:%dpx;background:%s;color:%s;'
                'text-align:center;font-size:%dpx;font-family:%s;font-weight:700;border-radius:2px;letter-spacing:0;">%s</span>'
                % (size, size, size, self.a, PAPER, int(size * 0.42), SERIF, leaf(text)))

    def cover(self, m):
        return (
            '<section style="margin:0 0 30px;padding:30px 4px 22px;border-top:1px solid %s;border-bottom:1px solid %s;">'
            '<section style="display:flex;justify-content:space-between;align-items:center;margin:0 0 22px;">'
            '<span style="font-size:11px;letter-spacing:3px;color:%s;font-family:%s;">%s</span>%s</section>'
            '<p style="margin:0 0 16px;font-size:24px;line-height:1.5;color:%s;font-family:%s;font-weight:700;">%s</p>'
            '<p style="margin:0 0 18px;font-size:14px;line-height:1.9;color:%s;">%s</p>'
            '<p style="margin:0;font-size:12px;color:%s;letter-spacing:1px;">%s</p></section>'
            % (INK, G3, G6, MONO, leaf(m.get('kicker', '')), self.seal('首发' if '首发' in m.get('kicker', '') else '版心'),
               INK, SERIF, leaf(m.get('title', '')), G6, leaf(m.get('digest', '')), G6, leaf('文 / ' + m.get('author', ''))))

    def lead(self, text):
        return ('<section style="margin:0 0 28px;padding:0 0 0 16px;border-left:2px solid %s;">'
                '<p style="margin:0;font-size:16px;line-height:1.95;color:%s;font-family:%s;">%s</p></section>'
                % (self.a, INK, SERIF, self.inline(text)))

    def toc_classic(self, sections):
        rows = ''.join(
            '<section style="display:flex;padding:10px 0;border-bottom:1px solid %s;">'
            '<span style="width:40px;flex-shrink:0;font-size:12px;color:%s;font-family:%s;">%s</span>'
            '<span style="flex:1;font-size:14px;color:%s;">%s</span></section>'
            % (G3, self.a, MONO, leaf('%02d' % n), INK, leaf(b['title']))
            for n, b in enumerate(sections, 1))
        return ('<section style="margin:0 0 34px;border-top:1px solid %s;">'
                '<p style="margin:12px 0 2px;font-size:11px;letter-spacing:3px;color:%s;">%s</p>%s</section>'
                % (INK, G6, leaf('目录'), rows))

    def toc(self, sections):
        """版心不出目录：章节编号本身就是导航。"""
        return ''

    def h2(self, b, n):
        """大号朱砂编号 + 宋体标题 + 短红线。"""
        num = '终' if b.get('final') else (b['num'] or '%02d' % n)
        return ('<section style="margin:48px 0 22px;">'
                '<p style="margin:0;font-size:40px;line-height:1;color:%s;font-family:Georgia,%s;font-weight:700;letter-spacing:1px;">%s</p>'
                '<p style="margin:10px 0 0;font-size:21px;line-height:1.5;color:%s;font-family:%s;font-weight:700;">%s</p>'
                '<section style="margin:14px 0 0;width:36px;height:3px;background:%s;">%s</section></section>'
                % (self.a, SERIF, leaf(num), INK, SERIF, leaf(b['title']), self.a, blank()))

    def h2_classic(self, b, n):
        num = '终' if b.get('final') else (b['num'] or '%02d' % n)
        return ('<section style="margin:44px 0 20px;">'
                '<section style="display:flex;align-items:center;margin:0 0 12px;">'
                '<span style="font-size:13px;color:%s;font-family:%s;margin-right:10px;">%s</span>'
                '<section style="flex:1;height:1px;background:%s;">%s</section></section>'
                '<p style="margin:0;font-size:20px;line-height:1.5;color:%s;font-family:%s;font-weight:700;">%s</p></section>'
                % (self.a, MONO, leaf(num), G3, blank(), INK, SERIF, leaf(b['title'])))

    def strong_style(self):
        return 'color:%s;font-weight:700;border-bottom:1px solid %s;padding-bottom:1px;' % (INK, self.a)

    def keypoint(self, text):
        return ('<section style="margin:6px 0 24px;padding:14px 16px;background:#FFFFFF;border:1px solid %s;border-left:2px solid %s;border-radius:2px;">'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:%s;font-weight:700;font-family:%s;">%s</p></section>'
                % (G3, self.a, INK, SERIF, leaf(text)))

    def ending(self, text, m):
        return ('<section style="margin:40px 0 10px;padding:22px 0 0;border-top:1px solid %s;text-align:center;">'
                '<section style="margin:0 0 14px;">%s</section>'
                '<p style="margin:0 0 12px;font-size:15px;line-height:1.9;color:%s;font-family:%s;">%s</p>'
                '<p style="margin:0;font-size:12px;color:%s;">%s</p></section>'
                % (INK, self.seal('留言', 30), INK, SERIF, self.inline(text), G6, leaf('— ' + m.get('author', '') + '，下篇见')))


def _h3(self, b):
    return ('<p style="margin:28px 0 12px;font-size:16px;line-height:1.6;color:%s;font-family:%s;font-weight:700;">'
            '<span style="display:inline-block;width:6px;height:6px;margin:0 9px 3px 0;background:%s;">%s</span>%s</p>'
            % (INK, SERIF, self.a, blank(), self.inline(b['text'])))


def _quote(self, text, cite=''):
    c = ('<p style="margin:10px 0 0;font-size:12px;color:%s;">%s</p>' % (G6, leaf('—— ' + cite))) if cite else ''
    return ('<section style="margin:28px 0;padding:18px 4px;border-top:1px solid %s;border-bottom:1px solid %s;">'
            '<p style="margin:0;font-size:16px;line-height:1.9;color:%s;font-family:%s;">%s</p>%s</section>'
            % (INK, G3, INK, SERIF, self.inline(text), c))


Banxin.h3 = _h3
Banxin.quote = _quote
