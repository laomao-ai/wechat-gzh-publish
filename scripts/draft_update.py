"""在已配好凭证、IP 在白名单的机器上跑：以草稿箱现有内容为底，安全地原地更新一篇草稿。
用法（仓库根目录）：
  python3 scripts/draft_update.py --mid <media_id> --base 上次存的基准.html --content 新正文.html [--cover 封面.jpg --crop235 0_0_1_1 --crop11 0.5744_0_1_1] [--title 新标题]
规则：
 1. 先 draft/get，与 --base 比对；不一致说明有人（通常是作者本人）在后台手改过 → 退出，不覆盖。
 2. 自动把 &#39; 换回 '，否则微信会清空带字体引号的整条 style（标题样式会全丢）。
 3. draft/get 的 thumb_media_id 为空，必须重新传封面拿永久素材 id；不换封面也会把现封面下载重传。
 4. 推完再 draft/get，打印 style 差异，并把结果存成 <content>.after.html 作为下次的 --base。"""
import argparse, json, re, sys, urllib.request
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import wechat_draft as w

ap = argparse.ArgumentParser()
for k in ('--mid', '--base', '--content'): ap.add_argument(k, required=True)
for k in ('--cover', '--crop235', '--crop11', '--title'): ap.add_argument(k)
a = ap.parse_args()
norm = lambda s: re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', s.replace('&#39;', "'")))
t = w.get_token(w.load_creds())
cur = w.api_post('draft/get', t, {'media_id': a.mid})['news_item'][0]
if norm(cur['content']) != norm(Path(a.base).read_text(encoding='utf-8')):
    Path(a.content + '.server_now.html').write_text(cur['content'], encoding='utf-8')
    sys.exit('草稿已被后台改过，已存 .server_now.html。先和作者确认，以最新版为底重改。')
Path(a.content + '.before.json').write_text(json.dumps(cur, ensure_ascii=False), encoding='utf-8')
cover = a.cover
if not cover:
    cover = '/tmp/_cur_cover.jpg'; urllib.request.urlretrieve(cur['thumb_url'], cover)
art = {k: cur[k] for k in ('title', 'author', 'digest', 'content_source_url', 'need_open_comment', 'only_fans_can_comment')}
if a.title: art['title'] = a.title
new = Path(a.content).read_text(encoding='utf-8').replace('&#39;', "'")
art.update(content=new, thumb_media_id=w.upload_thumb(t, Path(cover)))
if a.crop235: art['pic_crop_235_1'] = a.crop235
if a.crop11: art['pic_crop_1_1'] = a.crop11
print(w.api_post('draft/update', t, {'media_id': a.mid, 'index': 0, 'articles': art}))
b = w.api_post('draft/get', t, {'media_id': a.mid})['news_item'][0]
Path(a.content + '.after.html').write_text(b['content'], encoding='utf-8')
st = lambda s: Counter(x.replace('&#39;', "'").replace(' ', '') for x in re.findall(r'style="([^"]*)"', s))
print('style 丢失:', sum((st(new) - st(b['content'])).values()), ' 图片数:', b['content'].count('mmbiz'))
