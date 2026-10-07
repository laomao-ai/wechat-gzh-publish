# 配置指南

三类配置，三条独立的路。**互不依赖**，可以只配其中一部分。

| 配置 | 必需吗 | 用途 |
|---|---|---|
| [微信凭证](#一微信凭证) | ✅ 必需 | 推草稿箱 |
| [IP 白名单](#二ip-白名单) | ✅ 必需（除非你的机器已在白名单） | 微信接口调用 |
| [生图 Provider](#三生图-provider完全可选) | ⭕ 可选 | 封面生成 |

---

## 一、微信凭证

### 1.1 拿 AppID 与 AppSecret

登录[微信公众平台](https://mp.weixin.qq.com) → **设置与开发 → 基本配置（开发密钥管理）**

| 字段 | 说明 |
|---|---|
| AppID（开发者ID） | 页面上直接可见，形如 `wx1234567890abcdef` |
| AppSecret（AppSecret） | 点「重置」才显示，**只显示一次**，务必当场保存 |

> ⚠️ **点「重置」会立刻作废旧密钥**。如果别处正在用会中断。

### 1.2 写入配置文件

```bash
bash scripts/init_credentials.sh
```

脚本会交互式询问（**Secret 输入不回显**，这是正常的，不是卡住了），写入 `config/wechat.credentials.json` 并自动 `chmod 600`。

**不要把 AppSecret 明文贴在对话里或提交到 git。** 本 skill 的 `.gitignore` 已排除所有凭证文件。

### 1.3 手动配置（不想用脚本的话）

```bash
cp config/wechat.credentials.example.json config/wechat.credentials.json
# 填 appid / appsecret / author
chmod 600 config/wechat.credentials.json
```

### 1.4 账号权限限制（必读）

**2025 年 7 月起，微信回收了个人主体 / 未认证企业账号的发布能力接口。**

| 能力 | 个人/未认证 | 说明 |
|---|---|---|
| `draft/*` 草稿箱 | ✅ **可用** | 建草稿、改草稿、读草稿 |
| `media/*` 素材管理 | ✅ 可用 | 上传封面、正文图 |
| `freepublish/*` 发布 | ❌ **已被回收** | 报错 `48001 api unauthorized` |

**所以本skill 的终点是草稿箱，最后「发表」必须人工点。** 这是平台策略，不是配置问题，换工具也没用。

---

## 二、IP 白名单

### 2.1 为什么必须配

微信要求调用接口的**来源 IP** 在白名单里。不配会报：

```
errcode 40164, invalid ip 223.64.75.45, ipv6 ::ffff:223.64.75.45, not in whitelist
```

### 2.2 在哪配

微信公众平台 → **设置与开发 → 基本配置 → IP 白名单**

### 2.3 ⚠️ 怎么找你的真实出口 IP（这里最容易踩坑）

**如果你的机器开着代理，境内站和境外站看到的 IP 不一样。**

| 你访问的站| 它返回什么 |
|---|---|
| 境外站（`api.ipify.org`） | **代理节点的 IP** |
| 境内站（`myip.ipip.net`） | **你的真实宽带出口 IP** |

**微信服务器在境内、流量直连，所以只有境内站看到的那个 IP 才有用。**

```bash
# 境内站 —— 这个才是你要填的
curl -s https://myip.ipip.net
```

### 2.4 最可靠的办法：直接看微信报错

如果你不确定自己填对了没，**随便调一次接口，让微信告诉你它看到的 IP**：

```
errcode 40164, invalid ip 223.64.75.45 ... not in whitelist
                    ^^^^^^^^^^^^^^^^ 微信真实看到的
```

**报错里这个 IP 才是它真实看到的，比任何第三方查询都准。** 把它填进白名单就行。

### 2.5 动态 IP 的问题

家用宽带出口 IP 会随重拨变化。

| 部署方式 | 稳定性 |
|---|---|
| 部署到有固定 IP 的云服务器 | ⭐⭐⭐ |
| 向运营商申请公网固定 IP | ⭐⭐ |
| 本机跑 + IP 变了重配白名单 | ⭐仅适合验证 |

> 有些工具会卖「固定出口 IP」服务来解决这个问题——它们卖的就是这个坑。
> 成本参考：云托管的固定 IP 是额外收费项（约 49 元/月），而一台轻量应用服务器的固定 IP 是默认赠送的。

### 2.6 体检

```bash
python3 scripts/wechat_draft.py doctor
```

第 1 步会同时探测境内/境外两个源并对比，明确提示该填哪个。

---

## 三、生图 Provider（完全可选）

### 3.1 决策树

```
你的 Agent 自带生图能力吗？
├─ 是 → 什么都不用配，用 auto_delegate（默认）✅ 零成本
└─ 否 → 选一家外部 API ↓
        ├─ 要中文文字准确→ gemini / openai
        ├─ 要国内直连、不想翻墙 → volcengine
        └─ 要用第三方中转 → custom
```

### 3.2 配置

```bash
cp config/image_providers.example.json config/image_providers.json
chmod 600 config/image_providers.json
# 编辑填入 api_key
```

### 3.3 支持的 Provider

#### `auto_delegate`（默认，零成本）

不调任何 API。脚本会输出提示词，**由宿主 Agent 自己生成**。

如果你在 WorkBuddy / Claude Code / Codex 里用这个 skill，**Agent 本身就带生图能力**——这层是纯开销（多一次网络往返 + 一份密钥 + 一份账单）。

#### `gemini`（Google AI Studio）

| 项 | 值 |
|---|---|
| 申请 Key | https://aistudio.google.com/apikey |
| 默认模型 | `gemini-nano-banana-2.1` |
| 端点 | `{base_url}/v1beta/models/{model}:generateContent` |
| 鉴权 | header `x-goog-api-key` |
| 支持比例 | 21:9 16:9 9:16 1:1 3:4 4:3 2:3 3:2 4:1 1:4 5:4 4:5 1:8 8:1 |

**实测坑（已写进配置注释）：**
1. `gemini-nano-banana-2.1` **不支持 interactions 端点**，只有 `generateContent`
2. 比例键名只认蛇形 `aspect_ratio`；传驼峰或两者同传会报 `oneof` 冲突
3. **429 多半是免费额度用完**（`quota exceeded`），不是 Key 错误

价格：1K $0.0336 / 2K $0.0504 / 4K $0.0756。前代 `gemini-3.1-flash-image` 已公告 10 月 29 日关停。

#### `openai`

| 项 | 值 |
|---|---|
| 申请 Key | https://platform.openai.com/api-keys |
| 默认模型 | `gpt-image-2` |
| 端点 | `{base_url}/images/generations` |
| 前置条件 | **需在控制台完成 Organization Verification** |

`gpt-image-2` 支持**任意分辨率**（两边能被 16 整除，比例 1:3~3:1），并支持 `thinking` 参数（对信息图/表格类更准）。中文文字渲染目前最强。

#### `volcengine`（火山方舟，国内直连）

| 项 | 值 |
|---|---|
| base_url | `https://ark.cn-beijing.volces.com/api/v3` |
| 默认模型 | `doubao-seedream-4-0-250828` |

无需翻墙，性价比高。

#### `custom`（第三方中转 / 自建代理）

**填兼容 OpenAI `/images/generations` 协议的 `base_url` 即可。**

Gemini 中转需兼容 Google 原生协议（`{base}/v1beta/models/{model}:generateContent`）。

### 3.4 其他图像服务商

想用 Qwen（通义万相）、Midjourney、Stable Diffusion 等非上述格式的？

**两种做法：**

1. **让 Agent 自己生**（推荐）——如果你的 Agent 集成了这些能力，`auto_delegate` 模式下直接告诉它用哪个即可
2. **包一层适配**——在 `scripts/gen_image.py` 的 `GENERATORS` 字典里加一个函数，复用 `_post_json` / `_b64_to_file` / `_download` 三个工具函数

### 3.5 用法

```bash
python3 scripts/gen_image.py list                 # 看当前可用
python3 scripts/gen_image.py check                # 体检
python3 scripts/gen_image.py gen "提示词" --ratio 21:9          # 默认 auto_delegate
python3 scripts/gen_image.py gen "提示词" --provider gemini    # 强制走外部
```

比例直接按目标来，比事后裁切省事：**公众号头图用 `21:9`**。

---

## 四、主题配置（可选）

`config/brand_voice.json` 决定排版主题。

| 字段 | 作用 |
|---|---|
| `primary` | 默认主题，想换改这里 |
| `lock_primary: false` | 允许自由选择 `allowed[]` 任意主题 |
| `lock_primary: true` | 锁定只用 `primary`，适合账号风格已定型 |
| `allowed[]` | 主题清单，可自由增删 |

**默认 `false`** —— 你的账号不该被别人的偏好锁死。

### 加自己的主题

一次性生成、登记、之后固定用（**不要每篇临时生成，那是风格漂移的根源**）：

```bash
# 1. 用主题生成器出区块库
git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git vendor-gzh
# 2. 转为标准主题库 vendor-gzh/references/theme-{标识}.md
# 3. 在 config/brand_voice.json 的 allowed[] 追加一行
# 4. 校验
python3 vendor-gzh/scripts/component_lint.py vendor-gzh
```

要点：样式全内联、文字 `<span leaf="">` 包裹、封面风格段写进 `cover_prompt_style`。

---

## 五、完整初始化清单

```bash
# 1. 微信凭证
bash scripts/init_credentials.sh

# 2. IP 白名单（用境内站查 IP，或直接跑 doctor 看微信报什么）
curl -s https://myip.ipip.net
# → 填进公众平台 → 设置与开发 → 基本配置 → IP 白名单

# 3. 体检（验证 1+2 都对了）
python3 scripts/wechat_draft.py doctor
# 期望：[3] access_token ✓  [4] draft/count ✓

# 4. 拉取排版 skill
git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git vendor-gzh

# 5. 生图（可选，默认用 Agent 自带能力）
python3 scripts/gen_image.py list
```

---

## 安全约定

| 文件 | 权限 | 是否入 git |
|---|---|---|
| `config/wechat.credentials.json` | 600 | ❌ 已在 .gitignore |
| `config/image_providers.json` | 600 | ❌ 已在 .gitignore |
| `config/token_cache.json` | 600 | ❌ 自动生成 |
| `config/draft_state.json` | 600 | ❌ 自动生成 |
| `config/*.example.json` | 644 | ✅ 可入（不含真实密钥） |
| `config/brand_voice.json` | 644 | ✅ 可入（你的主题偏好） |

**密钥一律不提交。** example 文件是模板，只放占位符。
