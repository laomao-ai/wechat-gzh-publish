#!/usr/bin/env python3
"""公众号凭证配置（Windows / macOS / Linux 通用）。

AppSecret 用 getpass 输入，不回显、不进 shell history，也不需要贴进对话。

用法：
  python scripts/init_credentials.py

在哪拿：跑 `python scripts/wechat_draft.py doctor`，缺凭证时会打印完整三步
（AppID 在公众号后台，AppSecret 和 IP 白名单在微信开发者平台）。
"""
from __future__ import annotations

import getpass
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "config" / "wechat.credentials.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wechat_draft import SETUP_GUIDE  # noqa: E402  三步说明只维护一份


def main() -> int:
    if TARGET.exists():
        print(f"已存在：{TARGET}")
        print("直接编辑它即可；想重新配置就先删掉再跑一次。")
        return 0

    print("公众号凭证配置")
    print("先按这三步拿到 AppID 和 AppSecret：")
    print(SETUP_GUIDE)

    appid = input("AppID（wx 开头）: ").strip()
    if not appid:
        print("AppID 不能为空。")
        return 1
    if not re.fullmatch(r"wx[0-9a-fA-F]{16}", appid):
        if input(f"AppID 通常是 wx + 16 位十六进制，你填的是 {appid}，继续吗？(y/N) ").strip().lower() != "y":
            return 1

    print("\nAppSecret：见上面第 ② 步，点「重置」后只显示一次。")
    print("输入时屏幕不回显，粘贴后直接回车。")
    secret = getpass.getpass("AppSecret: ").strip()
    if len(secret) < 20:
        print(f"AppSecret 长度异常（{len(secret)} 位，通常 32 位），请检查是否复制完整。")
        return 1

    author = input("\n作者署名（显示在文章里，可留空）: ").strip()

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps({"appid": appid, "appsecret": secret, "author": author, "thumb_media_id": ""},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    try:
        os.chmod(TARGET, 0o600)
    except OSError:
        pass

    print(f"\n已写入：{TARGET}")
    print("下一步跑体检，它会告诉你 IP 白名单该填哪个：")
    print(f"  {Path(sys.executable).name} scripts/wechat_draft.py doctor")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n已取消。")
        sys.exit(1)
