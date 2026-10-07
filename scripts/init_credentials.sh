#!/bin/bash
# 公众号凭证一键配置
#
# 交互式，AppSecret 输入不回显、不经过对话记录、不留 shell history。
#
# 用法（在任何位置都能跑）：
#   bash scripts/init_credentials.sh
set -euo pipefail

# ── 定位配置目录 ────────────────────────────────────────────────
# 脚本位于 <repo>/scripts/，配置写到 <repo>/config/
# 必须用 dirname/.. 回到仓库根，否则会误写到 <repo>/scripts/config/
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="$ROOT_DIR/config"
TARGET="$CONFIG_DIR/wechat.credentials.json"

if [[ -f "$TARGET" ]]; then
  echo "⚠️  已存在：$TARGET"
  echo "    直接编辑它即可；想重新配置就先删掉再跑本脚本。"
  exit 0
fi

echo "=============================================="
echo " 公众号凭证配置"
echo "=============================================="
echo ""

# ── AppID ──────────────────────────────────────────────────────
echo "AppID 在微信公众平台查看："
echo "  设置与开发 → 基本配置 → 开发者ID(AppID)"
echo "  形如 wx1234567890abcdef"
echo ""
read -rp "请粘贴 AppID: " APPID

if [[ -z "${APPID:-}" ]]; then
  echo "✗ AppID 不能为空。"
  exit 1
fi

if [[ ! "$APPID" =~ ^wx[0-9a-fA-F]{16}$ ]]; then
  echo "⚠️  AppID 通常形如 wx + 16 位十六进制字符。"
  echo "    你输入的是：$APPID"
  read -rp "    确认要继续吗？(y/N) " OK
  [[ "${OK:-n}" =~ ^[Yy]$ ]] || exit 1
fi

# ── AppSecret ──────────────────────────────────────────────────
echo ""
echo "AppSecret 在微信公众平台获取："
echo "  设置与开发 → 基本配置 → 开发密钥 → 点「重置」"
echo ""
echo "⚠️  输入时终端不回显（这是正常的，不是卡住了）。粘贴后按回车。"
read -rsp "请粘贴 AppSecret: " APPSECRET
echo ""
echo ""

if [[ ${#APPSECRET} -lt 20 ]]; then
  echo "✗ AppSecret 长度异常（当前 ${#APPSECRET} 位，通常为 32 位）。"
  echo "  请检查是否复制完整。若已丢失，回到后台重新点一次「重置」。"
  exit 1
fi

# ── 作者署名 ────────────────────────────────────────────────────
echo ""
read -rp "作者署名（显示在文章里，可留空）: " AUTHOR
AUTHOR="${AUTHOR:-}"

# ── 写入 ───────────────────────────────────────────────────────
mkdir -p "$CONFIG_DIR"
cat > "$TARGET" <<EOF
{
  "appid": "$APPID",
  "appsecret": "$APPSECRET",
  "author": "$AUTHOR",
  "thumb_media_id": ""
}
EOF

chmod 600 "$TARGET"

echo ""
echo "✓ 已写入：$TARGET"
echo "  文件权限 600，仅当前用户可读。"
echo ""
echo "下一步（体检）："
echo "  python3 $ROOT_DIR/scripts/wechat_draft.py doctor"
echo ""
echo "如果体检第 3 步报 40164（invalid ip），说明出口 IP 不在白名单。"
echo "把报错里那串 IP 加到：公众平台 → 设置与开发 → 基本配置 → IP 白名单"
