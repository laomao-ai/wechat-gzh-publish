#!/usr/bin/env python3
"""把 AI 生成的方形图裁成微信公众号合规封面（900×383, 2.35:1）。

AI 生图默认是 1:1，而微信封面要求 2.35:1，本脚本按比例切出横幅
（锚点偏向文字区）并缩放到 900×383。

⚠️ 关于平台水印：部分生图平台会在角落打「AI 生成」标识。
《人工智能生成合成内容标识办法》第十条明确：不得恶意删除显式标识，
也不得为他人删除标识提供工具。因此本脚本默认**不裁水印**，
只做比例裁切。如确需处理，请自行用 --crop-watermark 并确认合规。

用法：
  python3 fit_cover.py <生图产物.png> [-o out.jpg] [--anchor 0.22]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("缺少 pillow。安装： pip install pillow")


WECHAT_W, WECHAT_H = 900, 383
TARGET_RATIO = WECHAT_W / WECHAT_H# 2.3499


def fit_cover(
    src: Path,
    out: Path,
    anchor: float = 0.22,
    crop_watermark: bool = False,
    watermark_ratio: float = 0.925,
    quality: int = 94,
) -> Path:
    img = Image.open(src).convert("RGB")
    W, H = img.size

    # 1) 裁掉底部平台水印带
    if crop_watermark:
        img = img.crop((0, 0, W, int(H * watermark_ratio)))
        W, H = img.size

    # 2) 按 2.35:1 切出横幅。高度固定，锚点决定垂直位置。
    band_h = int(W / TARGET_RATIO)
    if band_h > H:                      # 图太窄，退化为直接缩放
        band = img.resize((WECHAT_W, WECHAT_H), Image.LANCZOS)
    else:
        top = int(H * anchor)
        top = max(0, min(top, H - band_h))
        band = img.crop((0, top, W, top + band_h))

    band = band.resize((WECHAT_W, WECHAT_H), Image.LANCZOS)

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in (".jpg", ".jpeg"):
        band.save(out, "JPEG", quality=quality)
    else:
        band.save(out, "PNG")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="AI 生图 → 微信合规封面 900×383")
    ap.add_argument("src", help="生图产物路径")
    ap.add_argument("-o", "--out", default="cover-900x383.jpg", help="输出路径")
    ap.add_argument("--anchor", type=float, default=0.22,
                    help="垂直锚点 0~1，越大越靠下（0.22 能保住标题）")
    ap.add_argument("--crop-watermark", action="store_true",
                    help="裁掉底部水印带（默认不裁；注意生成合成内容标识办法第十条）")
    ap.add_argument("--watermark-ratio", type=float, default=0.925,
                    help="水印带起始位置比例，默认裁掉底部 7.5%%")
    ap.add_argument("--quality", type=int, default=94, help="JPEG 质量")
    args = ap.parse_args()

    src = Path(args.src)
    if not src.exists():
        raise SystemExit(f"找不到文件: {src}")

    out = fit_cover(
        src, Path(args.out),
        anchor=args.anchor,
        crop_watermark=args.crop_watermark,
        watermark_ratio=args.watermark_ratio,
        quality=args.quality,
    )
    print(f"✓ 已生成微信合规封面: {out}  ({WECHAT_W}×{WECHAT_H}, 2.35:1)")
    print(f"  下一步: python3 wechat_draft.py cover {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())