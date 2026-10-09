#!/usr/bin/env python3
"""生图 Provider 抽象层——让排版链路不绑定任何一家生图服务。

设计原则：**优先让宿主 Agent 自己生**，外部 API 只作兜底。
理由：宿主 Agent（WorkBuddy / claude / codex）通常已带生图能力，
走外部 API 多一次网络往返 + 一份密钥 + 一份账单。

## 支持的 provider

| provider | 端点类型 | 备注 |
|---|---|---|
| `auto_delegate` | — | 宿主 Agent 自生图（推荐首选，零成本） |
| `gemini` | Google 原生 / Interactions API | 支持 gemini-3.x-image，21:9 等任意比例 |
| `openai` | `/images/generations` | 支持 gpt-image-2 任意分辨率、thinking |
| `volcengine` | 火山方舟 | 国内直连，无需翻墙 |
| `custom` | 任意 OpenAI 兼容 | 中转服务、自建代理填 base_url 即可 |

## 用法

```bash
python gen_image.py list                              # 看可用 provider
python gen_image.py check                             # 体检
python gen_image.py gen "提示词" -o cover.png --ratio 21:9
python gen_image.py gen "提示词" --provider gemini
```

第三方中转：把 `openai` / `custom` 的 `base_url` 改成中转地址，
只要它兼容 OpenAI 的 `/images/generations` 协议即可。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def _find_config_dir() -> Path:
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent / "config",
        here.parent.parent / "config",
        Path.home() / ".config" / "wechat-gzh-publish",
        Path.home() / ".wechat-gzh-publish",
    ]
    for c in candidates:
        if (c / "image_providers.json").exists() or (c / "image_providers.example.json").exists():
            return c
    for c in candidates:
        if c.is_dir():
            return c
    return here.parent / "config"


CONFIG_DIR = _find_config_dir()
PROVIDERS_FILE = CONFIG_DIR / "image_providers.json"
EXAMPLE_FILE = CONFIG_DIR / "image_providers.example.json"

PROVIDER_ORDER = ["gemini", "openai", "volcengine", "custom"]


def _ctx() -> ssl.SSLContext:
    return ssl.create_default_context()


def load_config() -> dict:
    for f in (PROVIDERS_FILE, EXAMPLE_FILE):
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
    return {}


def enabled_providers(cfg: dict) -> list[str]:
    out = []
    for name in PROVIDER_ORDER:
        p = cfg.get(name)
        if p and p.get("enabled") and p.get("api_key"):
            out.append(name)
    return out


def pick_provider(cfg: dict, want: str | None) -> str:
    """决定用哪个 provider。auto_delegate 优先——零成本且通常质量最好。"""
    ad = cfg.get("auto_delegate", {})
    avail = enabled_providers(cfg)
    if want:
        if want != "auto_delegate" and want not in avail:
            raise SystemExit(f"provider '{want}' 未启用或缺 api_key")
        return want
    if ad.get("enabled", True) and not os.environ.get("FORCE_IMAGE_API"):
        return "auto_delegate"
    if avail:
        return avail[0]
    return "auto_delegate"


# ----------------------------------------------------------------- delegating

def delegate_to_host(prompt: str, ratio: str, out: Path) -> int:
    if out.exists():
        print(f"✓ 已存在，直接复用: {out}")
        return 0
    width, _ = _ratio_to_px(ratio)
    print("┌─ 宿主 Agent 生图模式 " + "─" * 38)
    print("│ 本机 Agent 若自带生图能力（WorkBuddy/claude/codex 通常都有），")
    print("│ 由你直接生成最省事——省一次网络往返、省一份 API Key。")
    print("│")
    print(f"│ 提示词：\n{prompt}")
    print("│")
    print(f"│ 目标文件：{out}")
    print(f"│ 建议比例：{ratio}（约 {width}px 宽）")
    print("│")
    print("└─ 生成后执行：")
    print(f"     python scripts/fit_cover.py {out} -o cover-900x383.jpg --anchor 0.22")
    print(f"     python scripts/wechat_draft.py cover cover-900x383.jpg")
    return 0


# ------------------------------------------------------------------ http core

def _friendly_error(e: urllib.error.HTTPError) -> str:
    """把 API 的原始报错翻译成可执行的下一步。"""
    try:
        detail = e.read().decode("utf-8", "replace")
    except Exception:
        detail = ""
    low = detail.lower()

    if e.code == 429:
        if "quota exceeded" in low or "free_tier" in low:
            return (
                "配额用完了（不是Key 错误，也不是代码问题）。\n"
                "     免费额度按天/按分钟重置，通常等一天即可。\n"
                "     想立刻解决：到 https://aistudio.google.com/apikey 控制台开通付费计划，\n"
                "     或用 --provider openai / volcengine 换一家。"
            )
        return "触发频率限制。稍等几十秒重试，或降低并发。\n     （配额查询：https://ai.dev/rate-limit）"

    if e.code == 400 and "api key" in low:
        return "Key 无效或已撤销。到 https://aistudio.google.com/apikey 重新获取。"

    if e.code == 401:
        return "Key 未通过认证。检查是否复制完整、是否已过期。"

    if e.code == 403:
        return "无权限。可能该模型需要付费计划，或未开通。"

    if e.code == 404:
        return "模型或端点不存在。检查 model 名是否正确（见 config 的注释里有模型清单）。"

    return f"HTTP {e.code}: {detail[:300]}"


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 240) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(_friendly_error(e)) from None


def _b64_to_file(b64: str, out: Path) -> Path:
    if b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    return out


def _download(url: str, out: Path) -> Path:
    with urllib.request.urlopen(url, timeout=120, context=_ctx()) as r:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.read())
    return out


def _ratio_to_px(ratio: str, long_edge: int = 1536) -> tuple[int, int]:
    """比例字符串 → 像素。"""
    try:
        w, h = (int(x) for x in ratio.replace(":", "/").split("/"))
    except Exception:
        return long_edge, long_edge
    if w >= h:
        return long_edge, max(1, int(long_edge * h / w))
    return max(1, int(long_edge * w / h)), long_edge


# ------------------------------------------------------------------- gemini

def gen_gemini(p: dict, prompt: str, ratio: str, out: Path) -> Path:
    """Google Gemini 图像生成。

    优先 Interactions API（官方现役），失败回退 generateContent（legacy，仍支持）。
    gemini-3.x 是推理模型，thinking 不可关闭，按 token 计费。
    """
    model = p.get("model", "gemini-3-pro-image")
    base = p["base_url"].rstrip("/")
    key = p["api_key"]
    size = p.get("image_size", "2K")

    # 路径 A：Interactions API
    # 注意：gemini-nano-banana-2.1 的 supportedGenerationMethods 只有
    # generateContent / countTokens / batchGenerateContent，不含 interactions，
    # 走这个端点会 404/429。所以仅当 api 显式设为 interactions 时才尝试。
    if p.get("api") == "interactions":
        url = f"{base}/v1beta/interactions"
        payload = {
            "model": model,
            "input": prompt,
            "response_format": {"type": "image", "aspect_ratio": ratio, "image_size": size},
        }
        try:
            data = _post_json(url, payload,
                              {"x-goog-api-key": key, "Content-Type": "application/json"})
            out_img = data.get("output_image") or {}
            if out_img.get("data"):
                return _b64_to_file(out_img["data"], out)
            for step in data.get("steps", []):
                for blk in step.get("content", []) or []:
                    if blk.get("type") == "image" and blk.get("data"):
                        return _b64_to_file(blk["data"], out)
            raise RuntimeError(f"Interactions 未找到图片: {json.dumps(data)[:300]}")
        except (RuntimeError, urllib.error.HTTPError) as e:
            if p.get("strict"):
                raise
            print(f"  · Interactions 不可用（{str(e)[:80]}），改用 generateContent", file=sys.stderr)

    # 路径 B：generateContent（gemini-nano-banana-2.1 / 3.x 图像模型的实际端点）
    url = f"{base}/v1beta/models/{model}:generateContent"
    cfg: dict = {"responseModalities": ["TEXT", "IMAGE"]}
    # 比例键名实测：gemini-nano-banana-2.1 只接受蛇形aspect_ratio。
    # 两种键名同时传会报 oneof 冲突（400），所以这里按配置单选，默认蛇形。
    # 老模型（gemini-2.x 文档示例）用驼峰 aspectRatio，若接入报400 就把
    # send_aspect 改成 "camel"。
    style = p.get("send_aspect", "snake")
    if style == "camel":
        cfg["imageConfig"] = {"aspectRatio": ratio}
    else:
        cfg["imageConfig"] = {"aspect_ratio": ratio}
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": cfg}

    data = _post_json(url, payload, {"x-goog-api-key": key, "Content-Type": "application/json"})
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return _b64_to_file(inline["data"], out)
    raise RuntimeError(f"Gemini 未返回图片: {json.dumps(data)[:300]}")


# ------------------------------------------------------------------- openai

def gen_openai(p: dict, prompt: str, ratio: str, out: Path) -> Path:
    """OpenAI images/generations。

    gpt-image-2 起支持任意 WIDTHxHEIGHT（两边须能被 16 整除，比例 1:3~3:1），
    并支持 thinking 参数（对信息图/表格类更准）。
    中转服务只需兼容同一协议，改 base_url 即可。
    """
    url = p["base_url"].rstrip("/") + "/images/generations"
    hdr = {"Content-Type": "application/json", "Authorization": f"Bearer {p['api_key']}"}
    model = p.get("model", "gpt-image-2")

    body: dict = {"model": model, "prompt": prompt, "n": 1}

    w, h = _ratio_to_px(ratio, long_edge=1536)
    w = max(16, (w // 16) * 16)
    h = max(16, (h // 16) * 16)
    if model.startswith("gpt-image-2"):
        body["size"] = f"{w}x{h}"
    elif ratio == "1:1":
        body["size"] = "1024x1024"
    else:
        body["size"] = "1536x1024" if w > h else "1024x1536"

    if p.get("quality"):
        body["quality"] = p["quality"]
    if p.get("thinking"):
        body["thinking"] = p["thinking"]          # gpt-image-2 专属 low/medium/high
    if p.get("output_format"):
        body["output_format"] = p["output_format"]

    data = _post_json(url, body, hdr, timeout=300)
    item = (data.get("data") or [{}])[0]
    if item.get("b64_json"):
        if item.get("revised_prompt"):
            print(f"  · 模型改写了提示词: {item['revised_prompt'][:120]}")
        return _b64_to_file(item["b64_json"], out)
    if item.get("url"):
        return _download(item["url"], out)
    raise RuntimeError(f"OpenAI 未返回图片: {json.dumps(data)[:300]}")


# -------------------------------------------------------------- volcengine

def gen_volcengine(p: dict, prompt: str, ratio: str, out: Path) -> Path:
    """火山引擎方舟（国内直连，无需翻墙）。"""
    url = p["base_url"].rstrip("/") + "/images/generations"
    hdr = {"Content-Type": "application/json", "Authorization": f"Bearer {p['api_key']}"}
    w, h = _ratio_to_px(ratio, long_edge=2048)
    body = {
        "model": p.get("model", "doubao-seedream-4-0-250828"),
        "prompt": prompt,
        "response_format": "b64_json",
        "size": f"{w // 8 * 8}x{h // 8 * 8}",
        "watermark": False,
    }
    if p.get("sequential_image_generation"):
        body["sequential_image_generation"] = p["sequential_image_generation"]
    data = _post_json(url, body, hdr, timeout=300)
    item = (data.get("data") or [{}])[0]
    if item.get("b64_json"):
        return _b64_to_file(item["b64_json"], out)
    if item.get("url"):
        return _download(item["url"], out)
    raise RuntimeError(f"Volcengine 未返回图片: {json.dumps(data)[:300]}")


GENERATORS = {
    "gemini": gen_gemini,
    "openai": gen_openai,
    "volcengine": gen_volcengine,
    "custom": gen_openai,      # custom 复用 OpenAI 协议（中转服务）
}


# ------------------------------------------------------------------ commands

def cmd_list(args) -> int:
    cfg = load_config()
    print("生图 Provider 状态")
    print("-" * 52)
    ad = cfg.get("auto_delegate", {})
    print(f" [{'✓' if ad.get('enabled', True) else ' '}] auto_delegate  宿主 Agent 自生图（推荐首选，零成本）")
    print()
    for name in PROVIDER_ORDER:
        p = cfg.get(name)
        if not p:
            continue
        on = p.get("enabled") and bool(p.get("api_key"))
        tag = "（自定义/中转）" if name == "custom" else ""
        print(f" [{'✓' if on else ' '}] {name:<12}{tag}{p.get('model', '')}")
        if p.get("enabled") and not p.get("api_key"):
            print(f"       ⚠️ 已启用但缺 api_key")
    print()
    src = PROVIDERS_FILE if PROVIDERS_FILE.exists() else EXAMPLE_FILE
    print(f"配置文件: {src}")
    if not PROVIDERS_FILE.exists():
        print(f"  设置: cp {src.name} image_providers.json")
    print(f"\n已配置的外部 API: {enabled_providers(cfg) or '（无，将由宿主 Agent 生图）'}")
    return 0


def cmd_check(args) -> int:
    cfg = load_config()
    print("生图链路体检")
    print("=" * 52)
    print("[1] 配置文件")
    if PROVIDERS_FILE.exists():
        print(f"    ✓ {PROVIDERS_FILE}")
    else:
        print(f"    ℹ️ 未创建正式配置，使用 example（仅 auto_delegate 生效）")
        print(f"    建议: cp {EXAMPLE_FILE.name} image_providers.json")

    print(f"\n[2] 宿主 Agent 能力")
    print(f"    宿主 Agent 若自带生图工具 → 直接让它生成，无需任何 API Key")

    print(f"\n[3] 外部 API")
    avail = enabled_providers(cfg)
    if not avail:
        print("    ℹ️ 未配置外部 API（这没问题，宿主 Agent 能自生）")
    for name in avail:
        p = cfg[name]
        print(f"    · {name} 已配置 model={p.get('model', '')}（未做真实调用，会产生费用）")

    print(f"\n[4] 第三方中转")
    print(f"    custom / openai 的 base_url 可改为任意 OpenAI 兼容中转地址")
    print(f"    协议：POST {{base_url}}/images/generations")
    print(f"    Gemini 中转同理改 base_url（Google 原生协议，需支持 /v1beta/interactions）")
    return 0


def cmd_gen(args) -> int:
    cfg = load_config()
    out = Path(args.out)
    provider = pick_provider(cfg, args.provider)

    if provider == "auto_delegate":
        return delegate_to_host(args.prompt, args.ratio, out)

    p = cfg.get(provider) or {}
    if not p.get("enabled") or not p.get("api_key"):
        raise SystemExit(f"provider '{provider}' 未启用或缺 api_key")

    print(f"· {provider} / {p.get('model')} 生成中（{args.ratio}）…")
    path = GENERATORS[provider](p, args.prompt, args.ratio, out)
    print(f"✓ 已生成: {path}")
    print(f"  下一步: python scripts/fit_cover.py {path} -o cover-900x383.jpg --anchor 0.22")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="生图 Provider 抽象层")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列出 provider 状态").set_defaults(func=cmd_list)
    sub.add_parser("check", help="体检").set_defaults(func=cmd_check)

    p = sub.add_parser("gen", help="生成图片")
    p.add_argument("prompt")
    p.add_argument("-o", "--out", default="cover.png")
    p.add_argument("--ratio", default="1:1", help="宽高比，如 21:9 / 16:9 / 1:1 / 3:4")
    p.add_argument("--provider", default=None,
                   help="auto_delegate / gemini / openai / volcengine / custom")
    p.set_defaults(func=cmd_gen)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
