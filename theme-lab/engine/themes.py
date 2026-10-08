"""Theme catalog for 微信公众号主题实验室. All themes are original.

Components and tokens live in components.py; each theme here overrides only
what gives it character. Retired themes stay in this file (LEGACY) so their
look can be rebuilt or reused later.
"""
from components import Theme, esc, leaf, blank, mix, SANS, SERIF, KAI, MONO


class Clay(Theme):
    """陶土：暖纸底 + 衬线标题 + 居中引语。原则：温暖画布、衬线展示字、克制单色点睛。"""
    key = 'clay'
    name = '陶土'
    series = '故事随笔'
    fit = '品牌故事、个人随笔、观点长文'
    principle = '暖色纸面做画布，衬线字承担情绪，主色只出现在编号与金句。'
    variants = [('terracotta', '陶土橙', '#B8593A'), ('pine', '松针绿', '#3F6B57'), ('indigo', '靛青', '#3E4C7A')]
    page_bg = '#FBF8F3'
    body_color = '#45403A'
    line = '#E8DFD3'

    def cover(self, m):
        return (
            '<section style="margin:0 0 30px;padding:34px 26px 28px;background:#F4EDE2;border-top:3px solid %s;">'
            '<p style="margin:0 0 18px;font-size:11px;letter-spacing:3px;color:%s;font-weight:700;">%s</p>'
            '<p style="margin:0 0 16px;font-size:24px;line-height:1.45;color:#2A2622;font-family:%s;font-weight:700;letter-spacing:0.5px;">%s</p>'
            '<section style="width:36px;height:1px;background:%s;margin:0 0 14px;">%s</section>'
            '<p style="margin:0 0 18px;font-size:14px;line-height:1.85;color:#7A7066;font-family:%s;">%s</p>'
            '<p style="margin:0;font-size:12px;color:#A39888;letter-spacing:1px;">%s</p></section>'
            % (self.a, self.a, leaf(m.get('kicker', '')), SERIF, leaf(m.get('title', '')), self.a, blank(),
               SERIF, leaf(m.get('digest', '')), leaf('文 / ' + m.get('author', '')))
        )

    def lead(self, text):
        return ('<section style="margin:0 8px 28px;padding:6px 0 6px 18px;border-left:2px solid %s;">'
                '<p style="margin:0;font-size:16px;line-height:1.9;color:#5A5148;font-family:%s;">%s</p></section>'
                % (self.a, SERIF, self.inline(text)))

    def toc(self, sections):
        rows = ''.join(
            '<section style="display:flex;padding:9px 0;border-bottom:1px solid %s;">'
            '<span style="width:44px;flex-shrink:0;font-size:13px;color:%s;font-family:%s;font-style:italic;">%s</span>'
            '<span style="flex:1;font-size:14px;color:#45403A;">%s</span></section>'
            % (self.line, self.a, SERIF, leaf(self.sec_label(b, n)), leaf(b['title']))
            for n, b in enumerate(sections, 1))
        return ('<section style="margin:4px 0 34px;padding:18px 20px;background:#FFFFFF;border:1px solid %s;">'
                '<p style="margin:0 0 6px;font-size:11px;letter-spacing:3px;color:#A39888;font-weight:700;">%s</p>%s</section>'
                % (self.line, leaf('本期目录'), rows))

    def h2(self, b, n):
        num = '终' if b.get('final') else (b['num'] or '%02d' % n)
        return ('<section style="margin:42px 0 20px;text-align:center;">'
                '<p style="margin:0 0 6px;font-size:22px;color:%s;font-family:%s;%s">%s</p>'
                '<p style="margin:0 0 12px;font-size:19px;line-height:1.5;color:#2A2622;font-family:%s;font-weight:700;">%s</p>'
                '<section style="width:24px;height:2px;background:%s;margin:0 auto;">%s</section></section>'
                % (self.a, SERIF, '' if b.get('final') else 'font-style:italic;', leaf(num), SERIF, leaf(b['title']), self.a, blank()))

    def strong_style(self):
        return 'color:#2A2622;font-weight:700;background:linear-gradient(to bottom,transparent 62%%,%s 62%%);' % self.soft

    def keypoint(self, text):
        return ('<section style="margin:6px 0 24px;padding:16px 18px;background:%s;">'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:#2A2622;font-weight:700;font-family:%s;">%s</p></section>'
                % (self.faint, SERIF, leaf(text)))

    def quote(self, text, cite=''):
        return ('<section style="margin:30px 10px;padding:20px 0;border-top:1px solid %s;border-bottom:1px solid %s;text-align:center;">'
                '<p style="margin:0;font-size:17px;line-height:1.8;color:%s;font-family:%s;">%s</p></section>'
                % (self.line, self.line, self.a, SERIF, self.inline(text)))

    def ending(self, text, m):
        return ('<section style="margin:36px 0 10px;padding:24px 22px;background:#F4EDE2;text-align:center;">'
                '<p style="margin:0 0 12px;font-size:11px;letter-spacing:3px;color:%s;font-weight:700;">%s</p>'
                '<p style="margin:0 0 14px;font-size:15px;line-height:1.85;color:#2A2622;font-family:%s;">%s</p>'
                '<p style="margin:0;font-size:12px;color:#A39888;">%s</p></section>'
                % (self.a, leaf('留言区见'), SERIF, self.inline(text), leaf('— ' + m.get('author', '') + ' · 感谢读到这里')))


class Grid(Theme):
    """蓝图：直角、发丝线、单一锚点色、等宽标签。原则：工程化设计系统的扁平与秩序。"""
    key = 'grid'
    name = '蓝图'
    series = '实操教程'
    fit = '教程、工具评测、操作指南、产品拆解'
    principle = '零圆角零阴影，一种锚点色贯穿编号与要点，信息靠线和格子分层。'
    variants = [('cobalt', '钴蓝', '#1F5BD8'), ('signal', '信号绿', '#0E8A5F'), ('safety', '安全橙', '#D9541E')]
    body_color = '#33363B'
    line = '#E1E4E8'

    def cover(self, m):
        tags = ''.join('<span style="display:inline-block;margin:0 6px 6px 0;padding:3px 8px;border:1px solid %s;'
                       'font-size:11px;color:%s;font-family:%s;">%s</span>' % (self.a, self.a, MONO, leaf(t))
                       for t in self.tags(m))
        return (
            '<section style="margin:0 0 28px;border:1px solid #1B1D21;">'
            '<section style="background:%s;padding:8px 16px;display:flex;justify-content:space-between;">'
            '<span style="font-size:11px;color:#FFFFFF;font-family:%s;letter-spacing:2px;font-weight:700;">%s</span>'
            '<span style="font-size:11px;color:#FFFFFF;font-family:%s;">%s</span></section>'
            '<section style="padding:24px 18px 20px;">'
            '<p style="margin:0 0 14px;font-size:23px;line-height:1.4;color:#14161A;font-weight:800;">%s</p>'
            '<p style="margin:0 0 16px;font-size:14px;line-height:1.8;color:#5B6068;">%s</p>%s</section></section>'
            % (self.a, MONO, leaf('BLUEPRINT'), MONO, leaf('DOC / v1.0'),
               leaf(m.get('title', '')), leaf(m.get('digest', '')), tags)
        )

    def lead(self, text):
        return ('<section style="margin:0 0 26px;padding:14px 16px;background:%s;border-left:4px solid %s;">'
                '<p style="margin:0 0 6px;font-size:11px;color:%s;font-family:%s;font-weight:700;letter-spacing:1px;">%s</p>'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:#14161A;font-weight:600;">%s</p></section>'
                % (self.faint, self.a, self.a, MONO, leaf('TL;DR'), self.inline(text)))

    def toc(self, sections):
        rows = ''.join(
            '<section style="display:flex;border-top:1px solid %s;">'
            '<span style="width:48px;flex-shrink:0;padding:8px 0;text-align:center;font-size:12px;color:%s;'
            'font-family:%s;font-weight:700;border-right:1px solid %s;">%s</span>'
            '<span style="flex:1;padding:8px 12px;font-size:13px;color:#33363B;">%s</span></section>'
            % (self.line, self.a, MONO, self.line, leaf(self.sec_label(b, n)), leaf(b['title']))
            for n, b in enumerate(sections, 1))
        return ('<section style="margin:0 0 32px;border:1px solid %s;border-top:0;">'
                '<p style="margin:0;padding:8px 12px;font-size:11px;color:#8A9099;font-family:%s;letter-spacing:2px;'
                'border-top:1px solid %s;">%s</p>%s</section>'
                % (self.line, MONO, self.line, leaf('INDEX'), rows))

    def h2(self, b, n):
        num = self.sec_label(b, n)
        return ('<section style="margin:40px 0 18px;display:flex;align-items:stretch;border-bottom:1px solid #1B1D21;">'
                '<span style="flex-shrink:0;padding:6px 10px;background:%s;color:#FFFFFF;font-size:14px;'
                'font-family:%s;font-weight:700;">%s</span>'
                '<p style="flex:1;margin:0;padding:6px 12px;font-size:17px;line-height:1.5;color:#14161A;font-weight:800;">%s</p></section>'
                % (self.a, MONO, leaf(num), leaf(b['title'])))

    def strong_style(self):
        return 'color:%s;font-weight:700;border-bottom:2px solid %s;' % (self.a, self.soft)

    def keypoint(self, text):
        return ('<section style="margin:4px 0 24px;border:1px solid %s;">'
                '<p style="margin:0;padding:6px 12px;background:%s;font-size:11px;color:#FFFFFF;font-family:%s;'
                'font-weight:700;letter-spacing:1px;">%s</p>'
                '<p style="margin:0;padding:12px 14px;font-size:15px;line-height:1.8;color:#14161A;font-weight:700;">%s</p></section>'
                % (self.a, self.a, MONO, leaf('KEY POINT'), leaf(text)))

    def quote(self, text, cite=''):
        return ('<section style="margin:24px 0;padding:14px 16px;background:#F5F6F8;border-left:4px solid #1B1D21;">'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:#14161A;">%s</p></section>' % self.inline(text))

    def note(self, text):
        return ('<section style="margin:-4px 0 22px;display:flex;">'
                '<span style="flex-shrink:0;margin-right:8px;padding:0 6px;height:18px;line-height:18px;background:#1B1D21;'
                'color:#FFFFFF;font-size:10px;font-family:%s;font-weight:700;">%s</span>'
                '<p style="flex:1;margin:0;font-size:12px;line-height:1.6;color:#6B7079;">%s</p></section>'
                % (MONO, leaf('NOTE'), self.inline(text)))

    def list(self, items, ordered):
        rows = ''.join(
            '<section style="display:flex;padding:9px 0;border-bottom:1px dotted %s;">'
            '<span style="flex-shrink:0;width:30px;font-size:12px;line-height:1.9;color:%s;font-family:%s;font-weight:700;">%s</span>'
            '<p style="flex:1;margin:0;font-size:14px;line-height:1.9;color:#33363B;">%s</p></section>'
            % ('#C9CED6', self.a, MONO, leaf(('%02d' % n) if ordered else '■'), self.inline(item))
            for n, item in enumerate(items, 1))
        return '<section style="margin:0 0 22px;border-top:1px solid #1B1D21;">' + rows + '</section>'

    def ending(self, text, m):
        return ('<section style="margin:36px 0 10px;border:1px solid #1B1D21;">'
                '<p style="margin:0;padding:8px 14px;background:#1B1D21;font-size:11px;color:#FFFFFF;font-family:%s;'
                'letter-spacing:2px;font-weight:700;">%s</p>'
                '<p style="margin:0;padding:16px 14px 8px;font-size:15px;line-height:1.8;color:#14161A;font-weight:700;">%s</p>'
                '<p style="margin:0;padding:0 14px 14px;font-size:12px;color:#8A9099;font-family:%s;">%s</p></section>'
                % (MONO, leaf('YOUR TURN'), self.inline(text), MONO, leaf('— ' + m.get('author', '') + ' / END OF DOC')))


TINTS = ['#FDE8D7', '#DCF2E3', '#E7E2F7', '#DCEBFA', '#FBF1C9']


class Tint(Theme):
    """彩签手册：轮换浅色块 + 圆角卡片 + 便签引用。原则：知识工具的柔和色块与好扫读结构。"""
    key = 'tint'
    name = '彩签手册'
    series = '知识系列'
    fit = '知识整理、清单盘点、学习笔记、方法论'
    principle = '每个章节一种浅色签，色块负责分区，正文保持深灰，圆角让密集信息变轻松。'
    variants = [('plum', '梅子紫', '#6A4FC2'), ('coral', '珊瑚红', '#D2513F'), ('ocean', '海湾蓝', '#2369B5')]
    body_color = '#3A3A40'
    line = '#ECEAE6'

    def tint(self, n):
        return TINTS[(n - 1) % len(TINTS)]

    def cover(self, m):
        dots = ''.join('<span style="display:inline-block;width:10px;height:10px;border-radius:50%%;background:%s;'
                       'margin-right:6px;">%s</span>' % (c, blank()) for c in TINTS[:4])
        tags = ''.join('<span style="display:inline-block;margin:0 6px 6px 0;padding:3px 10px;border-radius:999px;'
                       'background:%s;font-size:11px;color:#3A3A40;">%s</span>' % (TINTS[i % 5], leaf(t))
                       for i, t in enumerate(self.tags(m)))
        return (
            '<section style="margin:0 0 26px;padding:24px 22px 20px;background:#FFFBF0;border-radius:18px;'
            'border:1px solid #F1E7C8;">'
            '<section style="margin:0 0 16px;">%s</section>'
            '<p style="margin:0 0 6px;font-size:12px;color:%s;font-weight:700;">%s</p>'
            '<p style="margin:0 0 12px;font-size:22px;line-height:1.45;color:#1F1F24;font-weight:800;">%s</p>'
            '<p style="margin:0 0 14px;font-size:14px;line-height:1.8;color:#66666E;">%s</p>%s</section>'
            % (dots, self.a, leaf(m.get('kicker', '')), leaf(m.get('title', '')), leaf(m.get('digest', '')), tags)
        )

    def lead(self, text):
        return ('<section style="margin:0 6px 26px;padding:16px 18px;background:#FFF6B8;border-radius:4px 4px 14px 4px;'
                'box-shadow:0 3px 10px rgba(120,100,20,0.10);">'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:#3D3820;">%s</p></section>' % self.inline(text))

    def toc(self, sections):
        cards = ''.join(
            '<section style="display:flex;align-items:center;margin:0 0 8px;padding:10px 14px;border-radius:12px;background:%s;">'
            '<span style="flex-shrink:0;width:30px;font-size:13px;font-weight:800;color:#1F1F24;font-family:%s;">%s</span>'
            '<span style="flex:1;font-size:14px;color:#3A3A40;">%s</span></section>'
            % (self.tint(n), MONO, leaf(self.sec_label(b, n)), leaf(b['title']))
            for n, b in enumerate(sections, 1))
        return ('<section style="margin:0 0 30px;"><p style="margin:0 0 10px;font-size:13px;font-weight:800;color:#1F1F24;">'
                '%s</p>%s</section>' % (leaf('📌 这篇会讲'), cards))

    def h2(self, b, n):
        return ('<section style="margin:38px 0 16px;">'
                '<section style="display:inline-block;padding:8px 16px 8px 12px;border-radius:12px;background:%s;">'
                '<span style="display:inline-block;margin-right:8px;padding:0 7px;border-radius:7px;background:#FFFFFF;'
                'font-size:12px;font-weight:800;color:%s;font-family:%s;">%s</span>'
                '<span style="font-size:17px;font-weight:800;color:#1F1F24;">%s</span></section></section>'
                % (self.tint(n), self.a, MONO, leaf(self.sec_label(b, n)), leaf(b['title'])))

    def strong_style(self):
        return 'color:#1F1F24;font-weight:700;background:#FFF1A8;padding:0 2px;border-radius:3px;'

    def keypoint(self, text):
        return ('<section style="margin:4px 0 24px;padding:14px 16px;border-radius:14px;background:%s;border:1px solid %s;">'
                '<p style="margin:0;font-size:15px;line-height:1.8;color:%s;font-weight:700;">%s</p></section>'
                % (self.faint, self.soft, self.a, leaf('✦ ' + text)))

    def quote(self, text, cite=''):
        return ('<section style="margin:26px 4px;padding:16px 18px;border-radius:14px;background:#E7E2F7;">'
                '<p style="margin:0 0 4px;font-size:22px;line-height:1;color:%s;font-family:%s;">%s</p>'
                '<p style="margin:0;font-size:15px;line-height:1.85;color:#2E2A40;">%s</p></section>'
                % (self.a, SERIF, leaf('“'), self.inline(text)))

    def list(self, items, ordered):
        rows = ''.join(
            '<section style="display:flex;margin:0 0 8px;padding:10px 12px;border-radius:12px;background:#F7F6F3;">'
            '<span style="flex-shrink:0;width:22px;height:22px;margin-right:10px;border-radius:7px;background:%s;'
            'text-align:center;font-size:12px;line-height:22px;font-weight:800;color:#1F1F24;">%s</span>'
            '<p style="flex:1;margin:0;font-size:14px;line-height:1.75;color:#3A3A40;">%s</p></section>'
            % (TINTS[(n - 1) % 5], leaf(str(n) if ordered else '✓'), self.inline(item))
            for n, item in enumerate(items, 1))
        return '<section style="margin:4px 0 22px;">' + rows + '</section>'

    def table(self, head, rows):
        cards = ''
        for n, row in enumerate(rows, 1):
            cards += ('<section style="margin:0 0 8px;padding:12px 14px;border-radius:12px;background:%s;">'
                      '<p style="margin:0 0 4px;font-size:14px;font-weight:800;color:#1F1F24;">%s</p>'
                      '<p style="margin:0;font-size:13px;line-height:1.7;color:#4A4A52;">%s</p></section>'
                      % (TINTS[(n - 1) % 5], self.inline(row[0]), self.inline(' · '.join(row[1:]))))
        return '<section style="margin:4px 0 24px;">' + cards + '</section>'

    def ending(self, text, m):
        return ('<section style="margin:36px 0 10px;padding:20px 18px;border-radius:18px;background:#DCEBFA;">'
                '<p style="margin:0 0 8px;font-size:13px;font-weight:800;color:#1F1F24;">%s</p>'
                '<p style="margin:0 0 12px;font-size:15px;line-height:1.8;color:#22303F;">%s</p>'
                '<p style="margin:0;font-size:12px;color:#5B6B7C;">%s</p></section>'
                % (leaf('💬 留个言吧'), self.inline(text), leaf('— ' + m.get('author', '') + '，下篇见')))


class Masthead(Theme):
    """墨刊：粗黑刊头线 + 大号引语 + 黑底章节条。原则：新闻编辑部的强对比与节奏感。"""
    key = 'masthead'
    name = '墨刊'
    series = '头条热点'
    fit = '行业评论、热点解读、周报快讯、强观点'
    principle = '黑白承担九成画面，一种高饱和信号色只做刊头与引语，粗细线制造阅读节奏。'
    variants = [('signal', '信号红', '#E0301E'), ('volt', '电光蓝', '#2346F0'), ('mint', '薄荷绿', '#0A8F6A')]
    body_color = '#2B2B2B'
    line = '#DADADA'

    def cover(self, m):
        tags = ''.join('<span style="display:inline-block;margin:0 6px 6px 0;padding:2px 8px;background:%s;'
                       'font-size:11px;color:#FFFFFF;font-weight:700;">%s</span>'
                       % (self.a if i == 0 else '#111111', leaf(t)) for i, t in enumerate(self.tags(m)))
        return (
            '<section style="margin:0 0 26px;">'
            '<section style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;'
            'border-top:4px solid #111111;border-bottom:1px solid #111111;">'
            '<span style="font-size:11px;font-weight:800;letter-spacing:3px;color:#111111;font-family:%s;">%s</span>'
            '<span style="font-size:11px;color:%s;font-weight:700;font-family:%s;">%s</span></section>'
            '<p style="margin:18px 0 12px;font-size:24px;line-height:1.35;color:#111111;font-weight:900;letter-spacing:-0.5px;">%s</p>'
            '<p style="margin:0 0 14px;font-size:14px;line-height:1.8;color:#555555;">%s</p>%s'
            '<section style="height:1px;background:#111111;margin-top:8px;">%s</section></section>'
            % (MONO, leaf('THE LAB DAILY'), self.a, MONO, leaf('● ' + m.get('kicker', '')),
               leaf(m.get('title', '')), leaf(m.get('digest', '')), tags, blank())
        )

    def lead(self, text):
        return ('<section style="margin:0 0 28px;padding:4px 0 0;">'
                '<p style="margin:0;font-size:24px;line-height:1;color:%s;font-family:%s;font-weight:900;">%s</p>'
                '<p style="margin:0 0 12px;font-size:19px;line-height:1.6;color:#111111;font-weight:800;">%s</p>'
                '<section style="width:56px;height:4px;background:%s;">%s</section></section>'
                % (self.a, SERIF, leaf('“'), self.inline(text), self.a, blank()))

    def toc(self, sections):
        rows = ''.join(
            '<section style="display:flex;padding:7px 0;border-bottom:1px solid %s;">'
            '<span style="width:40px;flex-shrink:0;font-size:12px;font-weight:800;color:%s;font-family:%s;">%s</span>'
            '<span style="flex:1;font-size:14px;color:#111111;font-weight:600;">%s</span></section>'
            % (self.line, self.a, MONO, leaf(self.sec_label(b, n)), leaf(b['title']))
            for n, b in enumerate(sections, 1))
        return ('<section style="margin:0 0 32px;"><p style="margin:0 0 4px;font-size:11px;font-weight:800;'
                'letter-spacing:3px;color:#111111;font-family:%s;">%s</p>'
                '<section style="border-top:2px solid #111111;">%s</section></section>' % (MONO, leaf('IN THIS ISSUE'), rows))

    def h2(self, b, n):
        label = 'FINAL' if b.get('final') else 'PART ' + (b['num'] or '%02d' % n)
        return ('<section style="margin:42px 0 16px;">'
                '<section style="display:flex;align-items:center;margin:0 0 10px;">'
                '<span style="flex-shrink:0;padding:3px 8px;background:#111111;color:#FFFFFF;font-size:11px;'
                'font-weight:800;letter-spacing:2px;font-family:%s;">%s</span>'
                '<section style="flex:1;height:1px;background:#111111;margin-left:8px;">%s</section></section>'
                '<p style="margin:0;font-size:20px;line-height:1.45;color:#111111;font-weight:900;">%s</p></section>'
                % (MONO, leaf(label), blank(), leaf(b['title'])))

    def strong_style(self):
        return 'color:#111111;font-weight:800;border-bottom:3px solid %s;' % self.a

    def keypoint(self, text):
        return ('<section style="margin:6px 0 24px;padding:14px 16px;background:#111111;">'
                '<p style="margin:0;font-size:15px;line-height:1.8;color:#FFFFFF;font-weight:800;">%s</p></section>'
                % leaf(text))

    def quote(self, text, cite=''):
        return ('<section style="margin:30px 0;padding:18px 0;border-top:4px solid #111111;border-bottom:1px solid #111111;">'
                '<p style="margin:0;font-size:18px;line-height:1.65;color:%s;font-weight:900;">%s</p></section>'
                % (self.a, self.inline(text)))

    def table(self, head, rows):
        th = ''.join('<td style="padding:8px 10px;font-size:12px;font-weight:800;color:#111111;'
                     'border-bottom:2px solid #111111;letter-spacing:1px;">%s</td>' % leaf(h) for h in head)
        body = ''.join('<tr>' + ''.join(
            '<td style="padding:10px;font-size:13px;line-height:1.7;color:#2B2B2B;border-bottom:1px solid #DADADA;%s">%s</td>'
            % ('font-weight:800;color:#111111;white-space:nowrap;' if c == 0 else '', self.inline(cell))
            for c, cell in enumerate(row)) + '</tr>' for row in rows)
        return ('<section style="margin:6px 0 24px;border-top:4px solid #111111;"><table style="width:100%%;'
                'border-collapse:collapse;"><tbody><tr>%s</tr>%s</tbody></table></section>' % (th, body))

    def ending(self, text, m):
        return ('<section style="margin:40px 0 10px;border-top:4px solid #111111;padding-top:14px;">'
                '<p style="margin:0 0 8px;font-size:11px;font-weight:800;letter-spacing:3px;color:%s;font-family:%s;">%s</p>'
                '<p style="margin:0 0 12px;font-size:16px;line-height:1.75;color:#111111;font-weight:800;">%s</p>'
                '<p style="margin:0;font-size:12px;color:#777777;font-family:%s;">%s</p></section>'
                % (self.a, MONO, leaf('● 读者来信'), self.inline(text), MONO, leaf('— ' + m.get('author', '') + ' / 编辑部')))




# ---------------------------------------------------------------------------
# Per-theme overrides for newer components (keeps each class's original
# signature intact while giving new components that theme's character).
# ---------------------------------------------------------------------------

def _clay_quote(self, text, cite=''):
    c = ('<p style="margin:10px 0 0;font-size:12px;color:#A39888;letter-spacing:1px;">%s</p>'
         % leaf('—— ' + cite)) if cite else ''
    return ('<section style="margin:30px 10px;padding:20px 0;border-top:1px solid %s;border-bottom:1px solid %s;text-align:center;">'
            '<p style="margin:0;font-size:17px;line-height:1.8;color:%s;font-family:%s;">%s</p>%s</section>'
            % (self.line, self.line, self.a, SERIF, self.inline(text), c))


def _clay_h3(self, b):
    return ('<p style="margin:30px 0 14px;font-size:17px;line-height:1.5;color:#2A2622;font-family:%s;font-weight:700;">'
            '<span style="color:%s;font-style:italic;margin-right:8px;">%s</span>%s</p>'
            % (SERIF, self.a, leaf('§'), self.inline(b['text'])))


def _clay_callout(self, b):
    c, bg, label = self.callout_colors(b['kind'])
    body = ('<p style="margin:8px 0 0;font-size:14px;line-height:1.85;color:#5A5148;font-family:%s;">%s</p>'
            % (SERIF, self.inline(b['text']))) if b['text'] else ''
    return ('<section style="margin:8px 0 24px;padding:14px 18px;background:#FFFFFF;border-top:2px solid %s;'
            'border-bottom:1px solid %s;">'
            '<p style="margin:0;font-size:11px;letter-spacing:3px;color:%s;font-weight:700;">%s</p>'
            '<p style="margin:6px 0 0;font-size:15px;color:#2A2622;font-family:%s;font-weight:700;">%s</p>%s</section>'
            % (c if b['kind'] != 'note' else '#A39888', self.line, c, leaf(label), SERIF,
               self.inline(b['title'] or label), body))


Clay.radius = 2
Clay.ink = '#2A2622'
Clay.muted = '#A39888'
Clay.code_bg = '#2E2924'
Clay.code_fg = '#F1E8DC'
Clay.CALLOUT = dict(Theme.CALLOUT, tip=(None, None, '提示'), warn=('#B0472B', '#FBEFE9', '注意'))
Clay.quote = _clay_quote
Clay.h3 = _clay_h3
Clay.callout = _clay_callout


def _grid_h3(self, b):
    return ('<section style="margin:28px 0 12px;padding:0 0 6px;border-bottom:1px dashed #C9CED6;">'
            '<p style="margin:0;font-size:15px;line-height:1.5;color:#14161A;font-weight:800;">'
            '<span style="color:%s;font-family:%s;margin-right:8px;">%s</span>%s</p></section>'
            % (self.a, MONO, leaf('>'), self.inline(b['text'])))


def _grid_callout(self, b):
    c, bg, label = self.callout_colors(b['kind'])
    tag = {'tip': 'TIP', 'note': 'INFO', 'warn': 'WARNING', 'key': 'KEY'}.get(b['kind'], 'INFO')
    body = ('<p style="margin:6px 0 0;font-size:14px;line-height:1.8;color:#33363B;">%s</p>'
            % self.inline(b['text'])) if b['text'] else ''
    return ('<section style="margin:6px 0 22px;border:1px solid %s;">'
            '<p style="margin:0;padding:5px 12px;background:%s;font-size:11px;color:#FFFFFF;font-family:%s;'
            'font-weight:700;letter-spacing:1px;">%s</p>'
            '<section style="padding:10px 12px 12px;">'
            '<p style="margin:0;font-size:14px;font-weight:800;color:#14161A;">%s</p>%s</section></section>'
            % (c, c, MONO, leaf(tag), self.inline(b['title'] or label), body))


def _grid_quote(self, text, cite=''):
    c = ('<p style="margin:8px 0 0;font-size:11px;color:#8A9099;font-family:%s;">%s</p>'
         % (MONO, leaf('// ' + cite))) if cite else ''
    return ('<section style="margin:24px 0;padding:14px 16px;background:#F5F6F8;border-left:4px solid #1B1D21;">'
            '<p style="margin:0;font-size:15px;line-height:1.85;color:#14161A;">%s</p>%s</section>' % (self.inline(text), c))


Grid.radius = 0
Grid.ink = '#14161A'
Grid.code_bg = '#0D1117'
Grid.CALLOUT = dict(Theme.CALLOUT, tip=(None, None, '提示'), note=('#1B1D21', '#F5F6F8', '说明'))
Grid.h3 = _grid_h3
Grid.callout = _grid_callout
Grid.quote = _grid_quote


def _mast_h3(self, b):
    return ('<p style="margin:28px 0 12px;font-size:16px;line-height:1.5;color:#111111;font-weight:900;">'
            '<span style="display:inline-block;width:9px;height:9px;margin-right:8px;background:%s;">%s</span>%s</p>'
            % (self.a, blank(), self.inline(b['text'])))


def _mast_callout(self, b):
    c, bg, label = self.callout_colors(b['kind'])
    body = ('<p style="margin:6px 0 0;font-size:14px;line-height:1.8;color:#2B2B2B;">%s</p>'
            % self.inline(b['text'])) if b['text'] else ''
    return ('<section style="margin:6px 0 24px;padding:12px 0;border-top:2px solid #111111;border-bottom:1px solid #DADADA;">'
            '<p style="margin:0;font-size:15px;font-weight:900;color:#111111;">'
            '<span style="display:inline-block;margin-right:8px;padding:1px 6px;background:%s;color:#FFFFFF;'
            'font-size:11px;letter-spacing:1px;">%s</span>%s</p>%s</section>'
            % (c, leaf(label), self.inline(b['title'] or label), body))


def _mast_quote(self, text, cite=''):
    c = ('<p style="margin:10px 0 0;font-size:12px;color:#777777;font-weight:700;">%s</p>'
         % leaf('—— ' + cite)) if cite else ''
    return ('<section style="margin:30px 0;padding:18px 0;border-top:4px solid #111111;border-bottom:1px solid #111111;">'
            '<p style="margin:0;font-size:18px;line-height:1.65;color:%s;font-weight:900;">%s</p>%s</section>'
            % (self.a, self.inline(text), c))


Masthead.radius = 0
Masthead.ink = '#111111'
Masthead.code_bg = '#111111'
Masthead.CALLOUT = dict(Theme.CALLOUT, tip=(None, None, '提示'), note=('#111111', '#F4F4F4', '说明'))
Masthead.h3 = _mast_h3
Masthead.callout = _mast_callout
Masthead.quote = _mast_quote


def _square(method):
    """Wrap a default component so round marks become square (Grid / Masthead)."""
    def run(self, b):
        return method(self, b).replace('border-radius:50%', 'border-radius:0').replace('border-radius:4px', 'border-radius:0')
    return run


for _T in (Grid, Masthead):
    _T.steps = _square(Theme.steps)
    _T.check = _square(Theme.check)

from forest import Forest  # noqa: E402
from journal import Journal  # noqa: E402
from airy import Airy  # noqa: E402

# Active catalog shown in the gallery, in recommended order.
THEMES = [Forest, Airy, Clay, Grid, Journal, Masthead]
# Retired but kept: can be re-enabled or mined for parts.
LEGACY = {'tint': Tint}


# ---------------------------------------------------------------------------
# Typesetting per series. Baseline is the common WeChat recipe
# 15px / 1.75 / 1px / 24px after / 16px inset; each series bends it on purpose.
#            size  lh    ls   gap  pad  cover_bleed  body_color
# ---------------------------------------------------------------------------
TYPESET = {
    # 经典通用: the moyu-green recipe the author already publishes with.
    'forest':   (14, 1.9,  0.5, 16, 20, True,  '#374151'),
    # 白皮 · 头部IP: generous air, slightly larger gaps, cover sits flush.
    'airy':     (15, 2.0,  0.8, 28, 16, False, '#373C43'),
    # 社论: magazine long-read, bigger type, wide margins.
    'clay':     (16, 1.9,  0.8, 26, 16, False, '#45403A'),
    # 教程: the baseline recipe as-is; dense but even.
    'grid':     (15, 1.75, 1.0, 24, 16, True,  '#33363B'),
    # 手帐: airy handwriting rhythm on dotted paper.
    'journal':  (15, 2.0,  0.8, 26, 16, False, '#45403A'),
    # 评论: newspaper column, tight leading, narrow margin.
    'masthead': (15, 1.75, 0.3, 20, 12, True,  '#2B2B2B'),
}

for _T in THEMES:
    _spec = TYPESET.get(_T.key)
    if _spec:
        _T.size, _T.lh, _T.ls, _T.gap, _T.pad, _T.cover_bleed, _T.body_color = _spec
