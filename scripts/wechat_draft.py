#!/usr/bin/env python3
"""微信草稿箱直连推送（零第三方依赖，仅标准库）

直接对话微信官方 API，不经过任何中转服务。

关键设计：
1. access_token 本地文件缓存，提前 5 分钟过期，避免并发刷新互相覆盖
2. 幂等更新：slug 取自 Markdown 的绝对路径（或 front matter 里的 id），
   同一篇文章反复推送只 update 不新建——改标题、改摘要都不会另起一篇
3. 正文图片走 uploadimg 拿微信域名 URL；封面走 material 永久素材拿 media_id
4. IP 白名单由调用方环境保证，本脚本不做代理

用法：
  python wechat_draft.py doctor                    # 体检：配置/网络/权限
  python wechat_draft.py push article.md --title "..." --cover cover.jpg
  python wechat_draft.py list                     # 列出草稿箱最近 10 条
  python wechat_draft.py rm <media_id>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.weixin.qq.com/cgi-bin"
PLATFORM_URL = "https://developers.weixin.qq.com/console/index?tab1=business&tab2=dataStore"
# 首次配置三步，doctor / 缺凭证时原样打印给用户
SETUP_GUIDE = """\
  ① AppID：公众号后台 https://mp.weixin.qq.com
       设置与开发 → 账号设置 → 注册信息，页面底部 wx 开头那串
  ② AppSecret：微信开发者平台（管理员微信扫码登录）
       https://developers.weixin.qq.com/console/index?tab1=business&tab2=dataStore
       顶部「我的业务与服务」→ 下拉选「公众号」→ 输入 ① 的 AppID 绑定
       → 进入公众号基础信息 → 开发密钥，点「重置」，只显示一次，当场存好
  ③ IP 白名单：同一页「API IP 白名单」，填体检 [1] 给出的 IP
       也可以在公众号后台 设置与开发 → 安全中心 → IP 白名单 配置
       （需先设置过开发者密码 AppSecret 才能填白名单）
"""
WHITELIST_WHERE = "开发者平台 公众号基础信息 → API IP 白名单（或公众号后台 设置与开发 → 安全中心 → IP 白名单）"

# 配置目录查找：优先本项目 config/，其次向上查找（skill 独立安装场景），
# 再次回退到~/.config/wechat-gzh-publish/
def _find_config_dir() -> Path:
    """定位配置目录。

    优先找**含凭证文件**的目录，而不是第一个存在的目录。
    原因：开源版的 skill 目录自带 config/（放模板），但真实凭证在
    ~/.config/wechat-gzh-publish/。若只看目录是否存在，会永远命中
    skill 自带的空 config/，导致读不到凭证。
    """
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / "config",# 项目/skill 内标准位置
        here.parent.parent / "config",
        Path.home() / ".config" / "wechat-gzh-publish",
        Path.home() / ".wechat-gzh-publish",
    ]
    # 第一轮：优先选已有凭证的目录
    for c in candidates:
        if (c / "wechat.credentials.json").exists():
            return c
    # 第二轮：没有凭证时用第一个存在的目录（放token/state）
    for c in candidates:
        if c.is_dir():
            return c
    return here.parent / "config"


CONFIG_DIR = _find_config_dir()
TOKEN_CACHE = CONFIG_DIR / "token_cache.json"
CREDS_FILE = CONFIG_DIR / "wechat.credentials.json"
STATE_FILE = CONFIG_DIR / "draft_state.json"


class WeChatError(RuntimeError):
    def __init__(self, code: int, msg: str, hint: str = ""):
        self.code, self.msg, self.hint = code, msg, hint
        super().__init__(f"[{code}] {msg}" + (f"  → {hint}" if hint else ""))


ERROR_HINTS = {
    40001: "AppSecret 错误，或用了 reset 前的旧值",
    40013: "AppID 不正确",
    40164: "出口 IP 不在白名单。把报错里 invalid ip 后面那串填到：开发者平台 公众号基础信息 → API IP 白名单，或公众号后台 设置与开发 → 安全中心 → IP 白名单",
    61004: "出口 IP 不在白名单，同 40164",
    40125: "AppSecret 无效。去开发者平台 公众号基础信息 → 开发密钥 重置后重新配置",
    40243: "AppSecret 已被冻结。去开发者平台 公众号基础信息 → 开发密钥 解冻（约 10 分钟生效）",
    48001: "该账号无此接口权限。个人主体/未认证账号的 freepublish 已被回收（草稿箱接口仍可用）",
    41001: "缺少 access_token",
    45009: "接口调用超限，稍后重试",
}


# ---------------------------------------------------------------- credentials

def load_creds() -> dict:
    if not CREDS_FILE.exists():
        hint = (
            f"缺少配置文件: {CREDS_FILE}\n"
            f"首次配置三步：\n{SETUP_GUIDE}"
            f"拿到后在终端跑（AppSecret 输入不回显，属于正常）：\n"
            f"    python scripts/init_credentials.py\n"
            f"配置指南见 docs/CONFIG.md"
        )
        raise SystemExit(hint)
    return json.loads(CREDS_FILE.read_text(encoding="utf-8"))


def save_creds(c: dict) -> None:
    CREDS_FILE.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(CREDS_FILE, 0o600)
    except OSError:
        pass


# --------------------------------------------------------------------- http

def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def api_get(path: str, token: str, **params) -> dict:
    params["access_token"] = token
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
    return _jsonp(url)


def api_post(path: str, token: str, payload: dict | None = None) -> dict:
    url = f"{BASE}/{path}?access_token={urllib.parse.quote(token)}"
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    return _jsonreq(req)


def api_post_multipart(path: str, token: str, field: str, filepath: Path, extra: dict | None = None) -> dict:
    """微信素材上传走 multipart/form-data，不能用 json。"""
    url = f"{BASE}/{path}?access_token={urllib.parse.quote(token)}"
    boundary = "----WeChatFormBoundary" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    mime = mimetypes.guess_type(filepath.name)[0] or "application/octet-stream"
    parts: list[bytes] = []

    def add_field(k: str, v: str) -> None:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        )

    for k, v in (extra or {}).items():
        add_field(k, v)

    parts.append(
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{field}"; filename="{filepath.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode()
    )
    parts.append(filepath.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        url, data=b"".join(parts), method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    return _jsonreq(req)


def _jsonp(url: str) -> dict:
    return _jsonreq(urllib.request.Request(url, method="GET"))


def _jsonreq(req: urllib.request.Request) -> dict:
    with urllib.request.urlopen(req, timeout=30, context=_ctx()) as resp:
        raw = resp.read().decode("utf-8", "replace")
    data = json.loads(raw)
    if "errcode" in data and data["errcode"] != 0:
        code = data["errcode"]
        raise WeChatError(code, data.get("errmsg", "unknown"),
                          ERROR_HINTS.get(code, ""))
    return data


# --------------------------------------------------------------------- token

def get_token(creds: dict, force: bool = False) -> str:
    """带本地缓存的 access_token 获取，提前 5 分钟视为过期。"""
    if not force and TOKEN_CACHE.exists():
        try:
            c = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
            if c.get("appid") == creds["appid"] and c.get("expires_at", 0) > time.time() + 300:
                return c["token"]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    data = api_get("token", "", grant_type="client_credential",
                   appid=creds["appid"], secret=creds["appsecret"])
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(json.dumps({
        "appid": creds["appid"],
        "token": data["access_token"],
        "expires_at": time.time() + int(data.get("expires_in", 7200)) - 60,
    }), encoding="utf-8")
    try:
        os.chmod(TOKEN_CACHE, 0o600)
    except OSError:
        pass
    return data["access_token"]


# -------------------------------------------------------------------- assets

def upload_content_image(token: str, path: Path) -> str:
    """正文图片 → 微信域名 URL（可直接塞进 HTML的 src）。"""
    data = api_post_multipart("media/uploadimg", token, "media", path)
    return data["url"]


def upload_thumb(token: str, path: Path) -> str:
    """封面 → 永久素材 media_id（草稿接口的 thumb_media_id 必须是永久素材）。"""
    data = api_post_multipart("material/add_material", token, "media", path,
                              extra={"type": "thumb"})
    return data["media_id"]


def rewrite_images(html: str, token: str, image_refs: list[str], base_dir: Path) -> str:
    """把 HTML 里的本地图片引用替换为微信域名 URL。

    gzh-design 的产物用<img src="assets/xxx.png"> 这类相对路径，
    公众号不认，必须先过 uploadimg。
    """
    done: dict[str, str] = {}
    for ref in dict.fromkeys(image_refs):  # 去重：同一张图只上传一次
        p = (base_dir / ref).resolve()
        if not p.exists():
            print(f"  ! 跳过不存在的图片: {ref}", file=sys.stderr)
            continue
        try:
            url = upload_content_image(token, p)
            done[ref] = url
            print(f"  ✓ 正文图已上传 {ref}")
        except WeChatError as e:
            print(f"  ! 正文图上传失败 {ref}: {e}", file=sys.stderr)
    for ref, url in done.items():
        html = html.replace(f'src="{ref}"', f'src="{url}"')
        html = html.replace(f"src='{ref}'", f"src='{url}'")
        html = html.replace(f'src="./{ref}"', f'src="{url}"')
        html = html.replace(f"src='./{ref}'", f"src='{url}'")
    return html


# --------------------------------------------------------------------- draft

def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_state(s: dict) -> None:
    STATE_FILE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_front_matter(md_text: str) -> dict:
    """解析 Markdown 顶部的 YAML front matter（只取 title/digest/id/slug 四个键）。

    只做最小解析，不引入 yaml 依赖。"""
    front: dict[str, str] = {}
    if not md_text.startswith("---"):
        return front
    end = md_text.find("\n---", 3)
    if end == -1:
        return front
    for line in md_text[3:end].splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        if k in ("title", "digest", "id", "slug"):
            front[k] = v.strip().strip('"').strip("'")
    return front


def make_slug(article_path: Path, front: dict) -> str:
    """幂等键：优先 front matter 里的 id/slug，否则用 Markdown 绝对路径。

    改标题、改摘要都不会改变 slug——同一篇文章反复推送只更新、不新建。
    （旧版用 sha1(标题+摘要)，改标题会另起一篇，已废弃。）
    """
    fid = front.get("id") or front.get("slug")
    if fid:
        base = f"id:{fid}"
    else:
        base = f"path:{article_path.resolve()}"
    return hashlib.sha1(base.encode()).hexdigest()[:16]


def upsert_draft(article: dict, slug: str, verbose: bool = True) -> dict:
    """幂等推送：同 slug 已存在则 update，否则 create。

    注意微信两个接口的 articles 结构不同（官方文档 + 社区实测一致）：
      draft/add    → articles: [ {...} ]数组，且需带 thumb_media_id
      draft/update → articles: { ...  } 对象，且必须带 index: 0
    写错会返回 47001 data format error。
    """
    token = article.pop("_token")
    state = _load_state()
    media_id = state.get(slug)

    if media_id:
        try:
            api_post("draft/update", token, {
                "media_id": media_id,
                "index": 0,
                "articles": article,
            })
            if verbose:
                print(f"  ✓ 已更新既有草稿 media_id={media_id}（slug={slug}）")
            return {"action": "updated", "media_id": media_id}
        except WeChatError as e:
            if e.code in (40007, 40001, 47001):
                print(f"  · 草稿 {media_id} 更新失败({e.code})，改为新建", file=sys.stderr)
                media_id = None
            else:
                raise

    data = api_post("draft/add", token, {"articles": [article]})
    state[slug] = data["media_id"]
    _save_state(state)
    if verbose:
        print(f"  ✓ 已新建草稿 media_id={data['media_id']}（slug={slug}）")
    return {"action": "created", "media_id": data["media_id"]}


# ----------------------------------------------------------------- commands

def probe_egress() -> str | None:
    """探测微信真实看到的出口 IP。

    必须同时查境内与境外两个源：若本机开了代理，境外站返回的是代理节点，
    而微信服务器在境内、流量直连，白名单必须填真实宽带出口。
    """
    probes = [
        ("境外(ipify) https://api.ipify.org", "https://api.ipify.org"),
        ("境内(ipip) https://myip.ipip.net", "https://myip.ipip.net"),
    ]
    found: dict[str, str] = {}
    for label, url in probes:
        try:
            with urllib.request.urlopen(url, timeout=8) as r:
                raw = r.read().decode("utf-8", "replace")
            # ipip.net 返回 HTML，取首个 IPv4
            m = re.search(r"\d{1,3}(?:\.\d{1,3}){3}", raw)
            found[label] = (m.group(0) if m else raw).strip()[:60]
        except Exception as e:  # noqa: BLE001
            found[label] = f"探测失败: {e}"

    print("\n[1] 出口 IP 探测（关键）")
    for label, val in found.items():
        print(f"    {label.split()[0]:<12} → {val}")

    domestic = found.get(probes[1][0], "")
    abroad = found.get(probes[0][0], "")
    ip_re = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
    domestic_ok = bool(ip_re.match(domestic or ""))
    abroad_ok = bool(ip_re.match(abroad or ""))
    if domestic_ok and abroad_ok and domestic != abroad:
        print(f"    ⚠️ 两者不同 → 本机可能开着代理。")
        print(f"    微信服务器在境内、流量直连，**白名单应填 {domestic}**")
        print(f"    ({abroad} 是代理节点，填它无效)")
        return domestic
    if domestic_ok:
        print(f"    → 白名单应填 {domestic}")
        return domestic
    if abroad_ok:
        print(f"    → 境内探测失败，暂用境外结果 {abroad}（仅供参考，建议直接看微信报错里的 IP）")
        return abroad
    print(f"    → 两路探测都失败了，直接调一次接口，看微信报错里的 invalid ip")
    return None


def cmd_doctor(args) -> int:
    print("=" * 58)
    print("微信草稿箱链路体检")
    print("=" * 58)

    probe_egress()

    print("\n[2] 配置文件")
    if not CREDS_FILE.exists():
        print(f"    ✗ 缺少 {CREDS_FILE}")
        print("    首次配置三步：")
        print(SETUP_GUIDE, end="")
        print("    拿到后在终端跑：python scripts/init_credentials.py")
        return 1
    creds = load_creds()
    print(f"    ✓ AppID      = {creds['appid']}")
    print(f"    ✓ AppSecret  = {'*' * 8}{creds['appsecret'][-4:]}  (长度 {len(creds['appsecret'])})")

    print("\n[3] access_token")
    try:
        token = get_token(creds, force=True)
        print(f"    ✓ 获取成功 {token[:12]}...({len(token)} 字符)")
    except WeChatError as e:
        print(f"    ✗ {e}")
        if e.code in (40164, 61004):
            # 微信报错里的 invalid ip 就是它真实看到的出口，比任何查询站都准
            m = re.search(r"invalid ip ([0-9.]+)", e.msg)
            ip = m.group(1) if m else "上面 [1] 的 IP"
            print(f"    → 白名单填：{ip}")
            print(f"    位置：{WHITELIST_WHERE}，填完管理员扫码确认")
        return 1

    print("\n[4] 草稿箱接口权限")
    try:
        # draft/count 返回 {"total_count": N}，就是草稿总数
        total = api_post("draft/count", token).get("total_count", "?")
        batch = api_post("draft/batchget", token, {"offset": 0, "count": 3})
        items = batch.get("item", []) or []
        print(f"    ✓ draft/count 与 draft/batchget 均可调用")
        print(f"    ✓ 当前草稿箱共 {total} 篇（下方列出最近 {len(items)} 篇）")
        for it in items:
            news = (it.get("content", {}).get("news_item") or [{}])[0]
            print(f"      · {news.get('title', '(无标题)')}")
    except WeChatError as e:
        print(f"    ✗ {e}")
        return 1

    print("\n[5] 发布接口权限（预期失败，仅作信息展示）")
    try:
        api_post("freepublish/batchget", token, {"offset": 0, "count": 1, "no_content": 1})
        print("    ✓ freepublish 可用 —— 该号可能已完成认证")
    except WeChatError as e:
        print(f"    ℹ️ {e}")

    print("\n" + "=" * 58)
    print("体检结束")
    return 0


def cmd_push(args) -> int:
    src = Path(args.article)
    if not src.exists():
        raise SystemExit(f"找不到文章: {src}")

    # 排版产物推断：优先同名 .gzh.html，其次同名 .html
    #注意 .with_suffix 会把 a.gzh.html 变成 a.gzh.gzh.html，所以要按名字判断
    if args.html:
        html_file = Path(args.html)
    elif src.stem.endswith(".gzh"):
        html_file = src# 已经是排版产物
    else:
        cand1 = src.with_suffix("")
        cand1 = cand1.with_name(cand1.name + ".gzh.html")
        cand2 = src.with_suffix(".html")
        html_file = cand1 if cand1.exists() else cand2

    if not html_file.exists():
        raise SystemExit(
            f"找不到排版产物: {html_file}\n"
            f"请先用 theme-lab/engine/render.py 排版生成 HTML，或用 --html 显式指定"
        )

    creds = load_creds()
    token = get_token(creds)
    html = html_file.read_text(encoding="utf-8")

    # 标题/摘要优先级：命令行参数 > Markdown front matter > 文件名
    front = parse_front_matter(src.read_text(encoding="utf-8")) if src.suffix == ".md" else {}
    title = args.title or front.get("title") or html_file.stem
    digest = args.digest or front.get("digest", "")
    author = creds.get("author", "")

    if args.cover:
        print("· 上传封面…")
        thumb = upload_thumb(token, Path(args.cover))
        print(f"  ✓ 封面 media_id={thumb}")
    elif creds.get("thumb_media_id"):
        thumb = creds["thumb_media_id"]
        print(f"· 复用配置中的封面 media_id={thumb}")
    else:
        raise SystemExit(
            "缺少封面。二选一：\n"
            "  --cover cover.jpg          指定本次封面\n"
            "  在配置文件里填 thumb_media_id 作为默认封面\n"
            "没有现成封面？用插图卡出一张：theme-lab/engine/cards.py（见 SKILL.md「插图卡」）"
        )

    refs: list[str] = []
    for m in re.finditer(r'''<img[^>]+src=["']([^"']+)["']''', html):
        u = m.group(1)
        if not u.startswith(("http://", "https://", "data:")):
            refs.append(u)

    if refs:
        print(f"· 上传 {len(refs)} 张正文图片…")
        html = rewrite_images(html, token, refs, html_file.parent.resolve())

    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": html,
        "content_source_url": args.source_url or "",
        "thumb_media_id": thumb,
        "need_open_comment": 0 if args.no_comment else 1,
        "only_fans_can_comment": 0,
        "_token": token,
    }

    slug = args.slug or make_slug(src, front)
    result = upsert_draft(article, slug)

    print(f"\n✅ 完成：{result['action']}  media_id={result['media_id']}")
    print(f"   去后台草稿箱确认：https://mp.weixin.qq.com  → 草稿箱")
    print(f"   记得在后台点「发表」完成最后一步。")
    return 0


def cmd_cover(args) -> int:
    """上传封面到永久素材库，并把 media_id 写回配置作为默认封面。"""
    path = Path(args.image)
    if not path.exists():
        raise SystemExit(f"找不到图片: {path}")

    creds = load_creds()
    token = get_token(creds)
    print(f"· 上传封面 {path.name} …")
    thumb = upload_thumb(token, path)
    print(f"✓ 封面已上传，media_id={thumb}")

    creds["thumb_media_id"] = thumb
    save_creds(creds)
    print(f"✓ 已写入配置，后续 push 不必再带--cover")
    return 0


def cmd_list(args) -> int:
    creds = load_creds()
    token = get_token(creds)
    data = api_post("draft/batchget", token, {"offset": 0, "count": args.count})
    for it in data.get("item", []):
        info = it.get("content", {}).get("news_item", [{}])[0]
        print(f"{it['media_id']}  {it['update_time']}  {info.get('title', '(无标题)')}")
    return 0



def cmd_rm(args) -> int:
    creds = load_creds()
    token = get_token(creds)
    api_post("draft/delete", token, {"media_id": args.media_id})
    print(f"✓ 已删除草稿 {args.media_id}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="微信草稿箱直连推送")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="链路体检").set_defaults(func=cmd_doctor)

    p = sub.add_parser("push", help="推送/更新草稿")
    p.add_argument("article", help="文章 Markdown 路径（幂等 slug 取自它，改标题不会另起一篇）")
    p.add_argument("--html", help="排版产物 HTML（默认 <article>.gzh.html）")
    p.add_argument("--title", help="不填则读 Markdown front matter 的 title，再没有用文件名")
    p.add_argument("--digest", default="", help="不填则读 front matter 的 digest")
    p.add_argument("--cover", help="封面图路径")
    p.add_argument("--source-url", default="", help="原文链接，读者点「阅读原文」跳转（如 GitHub 地址）")
    p.add_argument("--no-comment", action="store_true", help="关闭留言（默认打开）")
    p.add_argument("--slug", help="幂等键，默认由文章路径（或 front matter 的 id）推导")
    p.set_defaults(func=cmd_push)

    p = sub.add_parser("cover", help="上传封面并设为默认")
    p.add_argument("image", help="封面图片路径")
    p.set_defaults(func=cmd_cover)

    p = sub.add_parser("list", help="列出草稿")
    p.add_argument("--count", type=int, default=10)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("rm", help="删除草稿")
    p.add_argument("media_id")
    p.set_defaults(func=cmd_rm)

    args = ap.parse_args()
    try:
        return args.func(args)
    except WeChatError as e:
        print(f"\n✗ 微信接口错误: {e}", file=sys.stderr)
        return 2
    except SystemExit:
        raise


if __name__ == "__main__":
    sys.exit(main())