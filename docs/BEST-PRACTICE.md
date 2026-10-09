# 公众号排版 + 草稿箱发布 · 最佳实践

> 端到端跑通的实践记录。目标：让云端 Agent 独立完成「排版 → 推草稿箱」，人只点最后一次「发表」。

---

## 一、先认清权限天花板（最重要，先做这一步）

2025 年 7 月起，微信官方回收了以下账号的**发布能力**接口权限：

- 个人主体账号
- 企业主体但未认证的账号
- 不支持认证的账号

被回收的接口（`/cgi-bin/freepublish/*`）：`batchget` / `get` / `submit` / `getarticle` / `delete`
典型报错：`errcode 48001, api unauthorized`

**但草稿箱接口（`/cgi-bin/draft/*`）个人主体账号仍然可用。**

这条决定了整套链路的形态：

| 环节 | 能否自动化 | 说明 |
|---|---|---|
| 排版（Markdown → 内联 HTML） | ✅ 完全自动 | 纯本地，零成本 |
| 上传正文图 → 素材库 | ✅ 完全自动 | `media/uploadimg` |
| 上传封面 → 永久素材 | ✅ 完全自动 | `material/add_material`（type=thumb） |
| 创建/更新草稿 | ✅ 完全自动 | `draft/add`、`draft/update` |
| **点击「发表」** | ❌ **做不到** | 个人主体无freepublish 权限 |

**先验证再动手**：配好凭证后第一件事是跑 `doctor`，确认 `draft/count` 能通。若它返回 48001，说明账号类型不支持，立刻停止开发，不要浪费周期。

---

## 二、整体架构

```
云端 Agent（情报收集 → 知识整理 → 产出 Markdown）
        ↓
排版层  vendor-gzh 组件库（本地）
        ↓  <section> 全内联HTML，无 script/style/div
推送层  scripts/wechat_draft.py（本项目，零第三方依赖）
        ↓  token 缓存 → 封面上传 → 正文图上传 → draft/upsert
公众号草稿箱
        ↓
人工点「发表」
```

---

## 三、排版层：用组件库装配

**默认用内置的 `theme-lab/`**：六个原创系列、一套组件库、公众号兼容检查，随仓库分发，不用额外安装。

**备选 vendor-gzh**：甲木开源的 gzh-design-skill（AGPL-3.0），独立 clone、不随本仓库分发：
`git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git vendor-gzh`

### 微信平台的硬性限制（排版产物必须遵守）

| 禁用 | 替代 |
|---|---|
| `<style>` / `<script>` | 样式全部写`style=""` 内联 |
| `<div>` / `class` / `id` | 一律用 `<section>` |
| `position:fixed/absolute/sticky`、`float` | 正常流布局 |
| `@media` / `@keyframes` | 无（动效用静态图） |
| `display:grid` | `display:flex`（有限支持） |
| 外部字体 / CSS 变量 | 系统字体栈 |
| **裸文本节点** | **每个文字必须 `<span leaf="">…</span>` 包裹** |

**`<span leaf="">` 是最容易踩的坑**。漏了它，微信编辑器会"纠正"并重写样式——排版在浏览器里看着好好的，粘进后台就散架。

### 双关卡校验（务必都跑）

```bash
# 源头关：扫组件库反模式
python scripts/component_lint.py <skill根目录>

# 产物关：扫最终 HTML 合规
python scripts/validate_gzh_html.py article.gzh.html
```

- 源头关查`white-space:pre`（导致大段空白）、正文四周虚线框等 → 须 0 ERROR
- 产物关查禁用标签、`span leaf` 包裹、半角标点 → 须 0 ERROR / 0 WARN

**产物关必须做到 0 WARN 再交付。** warning 数往往就是"粘进后台会掉格式"的数量。

### 图片：公众号不认本地路径

组件库的产物用相对路径 `<img src="assets/x.png">`，公众号**直接丢弃**。必须先过 `media/uploadimg` 换成微信域名 URL 再塞进 `content`。

排版时留`【插入：xxx】` 占位块，等拿到素材再替换——推送脚本会自动做替换。

---

## 四、推送层：直接调微信 API

**为什么不用现成工具**：
- 有的插件本地不调微信，全部转发到自己的云端（文章和图片要上传到第三方服务器，按积分收费）
- 有的工具是 Source Available 非开源，且"固定出口 IP"要另外收费

自己写只有约 300 行（`wechat_draft.py` 仅标准库；裁封面的 `fit_cover.py` 需 pillow），且**Secret 与正文都不出本机**。

### 核心实现要点

**1. access_token 缓存**
微信 token 有效期 7200 秒，但每次调用都刷新会撞限频。本地缓存，**提前 5 分钟视为过期**，避免并发时互相覆盖。缓存文件 `chmod 600`。

**2. 封面 vs 正文图走两个不同接口**
这是最容易搞错的地方：

```python
# 封面 → 永久素材 → media_id（draft 的 thumb_media_id 必须是永久素材）
material/add_material  type=thumb   → media_id

# 正文图 → 微信域名 URL（直接填进 HTML 的 src）
media/uploadimg                   → url
```

用错接口会拿到 url 填进 `thumb_media_id`，报 `40007 invalid media_id`。

**3. 幂等更新（云端 Agent 反复改稿的刚需）**

云端 Agent 会反复生成、改稿。若每次都 `draft/add`，草稿箱会堆几十篇重复稿。

做法：用 **Markdown 绝对路径**（或 front matter 里的 `id`）作 slug 记在本地状态文件里，
命中则走 `draft/update`，否则 `draft/add`。**改标题、改摘要都不会另起一篇。**

```python
slug = hashlib.sha1(f"path:{article_path.resolve()}".encode()).hexdigest()[:16]
if state.get(slug):  draft/update (media_id=...)
else:                 draft/add  → 记入 state
```

**⚠️ 微信两个接口的 `articles` 结构不同，这是最隐蔽的坑：**

| 接口 | `articles` | 额外必填 |
|---|---|---|
| `draft/add` | `[{...}]` **数组** | — |
| `draft/update` | `{...}` **对象** | `index: 0` |

写错会返回 **`errcode 47001 data format error`**，而 `add` 却正常成功——极易误判为"接口不通"。官方文档里 update 的示例确实是对象，社区大量同类提问都是这个原因。

```python
# add
api_post("draft/add", token, {"articles": [article]})
# update —— 注意对象 + index
api_post("draft/update", token, {"media_id": mid, "index": 0, "articles": article})
```

**4. IP 白名单**
微信只认 IPv4。白名单里的 IP 必须是**实际发起请求那台机器的出口 IP**。

⚠️ **若本机开着代理，境内站与境外站看到的 IP 完全不同**：
- 境外查询站（ipify）返回**代理节点 IP**
- 微信服务器在境内、流量直连，看到的是**本地宽带真实出口 IP**

配错会得到 `errcode 40164 invalid ip ... not in whitelist`。**最可靠的办法是直接看微信报错里说的 IP**——那是它真实看到的，比任何第三方查询都准。

本项目 `doctor` 已内置双源探测：同时查境外与境内两个源，不一致时明确提示"白名单应填境内那个"。

**动态 IP 风险**：家用宽带出口 IP 会随重拨变化。有些服务专门卖"固定出口 IP"来解决它——卖的就是这个坑。

**5. 部署位置**
推论：**发布脚本要部署在云端 Agent 所在机器上**，而不是本地。否则云端 Agent 生成的稿子还得手动搬过来，自动化就断了一截。本机跑 doctor 只用于验证。

| 方案 | 稳定性 |
|---|---|
| ⭐⭐⭐ 部署到云端 Agent（有固定 IP） | 长期可用 |
| ⭐⭐ 向运营商申请公网固定 IP | 本机长期可用 |
| ⭐ 本机跑 + IP 变了重配| 临时验证 |


---

## 五、主题锁定：防风格漂移

### 问题的根源

组件库允许"按描述/参考图生成新主题"，主题色由 AI 推导。这很自由，但**自由就是风格漂移的来源**——每篇文章主色都可能不一样，读者感知不到这是一个号。

所以在它之上加了一层约束：**主题必须登记注册，不允许每篇临时生成**。想加新主题，一次性生成、登记、之后固定用。

> 这个思路的代价是牺牲一点自由度，换来的是账号视觉的一致性。对个人号来说值得。

### 采纳的方案：锁主主题 + 收窄选择空间

新建 `config/brand_voice.json`：

```json
{
  "primary": "moyu-green",
  "lock_primary": true,
  "allowed": [{
    "id": "moyu-green",
    "cover_prompt_style": "瑞士国际主义排版风格，大量留白，几何精准克制，无渐变无阴影无纹理，纯白背景，主色 #059669 作为唯一色彩锚点…"
  }]
}
```

**两条铁律**：
1. 主题只能从 `allowed[]` 选，**不允许临时生成新主题**（除非你主动解锁）
2. 封面 prompt 的**风格描述段逐字复用** `cover_prompt_style`，只改标题文字

**关键认知**：稳定性不来自"每次生成得更好"，而来自**收窄选择空间**。换主题是"换预设"，不是"重新描述风格"。

保留主题生成能力 —— 想加新主题时，走一次生成 → 登记进 `brand_voice.json` → 之后固定用。**一次性成本，长期收益**。

### 生图 Provider 可配置

新增 `config/image_providers.json`（从 example 复制），支持：

| provider | 模型 | 说明 |
|---|---|---|
| `auto_delegate` | — | **宿主 Agent 自生图，默认首选** |
| `openai` | `gpt-image-2` | 任意分辨率（两边被 16 整除）+ thinking，中文文字最强 |
| `gemini` | `gemini-nano-banana-2.1` | generateContent 端点，支持 21:9 等比例 |
| `volcengine` | `doubao-seedream-4-0-250828` | 国内直连，无需翻墙 |
| `custom` | 自定义 | 任意 OpenAI 兼容端点 |

```bash
python scripts/gen_image.py list     # 看状态
python scripts/gen_image.py check    # 体检
python scripts/gen_image.py gen "提示词" -o cover.png
```

**云端 Agent 场景**：若该 Agent 无生图能力，把 `auto_delegate` 关掉、配一个外部 provider，整条链路就全自动了。这也是为什么 Provider 必须抽象——不能绑定单一生图服务。

### 不用另接图像 API（默认）

宿主 Agent（WorkBuddy / claude）通常自带生图能力。有些插件自己**没有生图引擎**——它们是调用本机的其他 CLI 去画，再读回文件。

宿主已具备该能力时，走外部 API 这一层是纯开销（多一次进程往返 + 一份 Key + 一份账单）。所以默认配置是「让宿主自己生」。

### 生图后必须处理三件事

AI 生图产物直接推微信会很难看，**缺一不可**：

| 问题 | 处理 |
|---|---|
| 比例是 1:1，微信要 2.35:1 | 裁成 900×383；**锚点取垂直 22% 处** |
| 中文偶发字形变形 | 变形严重时改用纯色/图形封面 |
| 平台「AI 生成」标识 | **默认不裁**——《生成合成内容标识办法》第十条禁恶意删除显式标识；发表时记得勾选 AI 内容声明 |

```bash
python scripts/fit_cover.py 生图产物.png -o cover-900x383.jpg --anchor 0.22
python scripts/wechat_draft.py cover cover-900x383.jpg   # 自动写入配置为默认封面
```

⚠️ **锚点选错会切掉标题**——最容易踩的一步，务必目视检查成品。

### 正文配图

排版时用 `【插入：xxx】` 留占位块，让 Agent 生成配图后替换，再由 `push` 自动过 `media/uploadimg` 换微信域名 URL。公众号不认本地路径。

---

## 六、落地检查清单

- [ ] 公众平台已配 IP 白名单，且是**调用方**出口 IP
- [ ] `config/wechat.credentials.json` 已填（从 example 复制，`chmod 600`，**勿入 git**）
- [ ] `python scripts/wechat_draft.py doctor` → 第4 步 `draft/count` 通过
- [ ] 排版产物 `validate_gzh_html.py` → **0 ERROR 0 WARN**
- [ ] 封面已上传或在配置里填了默认 `thumb_media_id`
- [ ] 预览页浏览器打开，样式正常
- [ ] 推到草稿箱，后台目视复核
- [ ] 人工点「发表」

---

## 七、踩坑记录

| 现象 | 原因 | 处理 |
|---|---|---|
| 浏览器预览好看，粘进后台散架 | 漏 `<span leaf="">`；或用了 `<div>`/`<style>` | 跑产物关校验做到 0 WARN |
| `errcode 40164` | 调用方出口 IP 不在白名单 | **看报错里的 IP**（那是微信真实看到的）；若本机有代理，境内站与境外站看到的不同 |
| `errcode 48001` | 账号类型无该接口权限 | 个人主体已无 freepublish；草稿箱仍可用 |
| `errcode 47001` | 请求体结构错| **`draft/update` 的 `articles` 是对象不是数组，且需 `index:0`** |
| `errcode 40001` | AppSecret 错误，或用了重置前的旧值 | 重置后同步更新配置 |
| `invalid media_id` | 封面误用了 uploadimg 的 url | 封面必须 `material/add_material`（永久素材） |
| 正文图片不显示 | 仍是本地相对路径 | 先 `media/uploadimg` 换 URL，且必须是微信域名 URL |
| 草稿箱堆满重复稿 | 每次都 `draft/add` | 实现 slug 幂等，走 update |
| 正文字体比预览小 / 样式被重写 | 同 `<p>` 内混了多个 `font-size` | 拆成多个 `<p>`，每个只一个字号 |

---

## 八、项目结构

```
wechat-gzh-publish/
├── scripts/
│   ├── wechat_draft.py             # 直连微信推送（零第三方依赖）
│   ├── fit_cover.py                # AI 生图 → 微信合规封面 900×383
│   ├── gen_image.py                # 生图 Provider 抽象层
│   └── init_credentials.py         # 凭证配置（跨平台，Secret 不回显）
├── config/
│   ├── wechat.credentials.json     # AppID/AppSecret（gitignore, 600）
│   ├── brand_voice.json            # 主题注册表（锁定主主题，防漂移）
│   ├── image_providers.json        # 生图 provider 配置（gitignore）
│   ├── image_providers.example.json
│   ├── token_cache.json            # access_token 缓存（自动生成）
│   └── draft_state.json            # slug → media_id 幂等映射
├── docs/
│   ├── CONFIG.md                   # 配置指南（凭证 / IP 白名单 / 生图选型）
│   └── BEST-PRACTICE.md            # 本文件
├── references/
│   ├── quality-check.md            # 质检框架
│   └── title-optimize.md           # 标题优化
└── vendor-gzh/                     # 排版组件库（clone 获得，不入库）
```

## 命令速查

```bash
PY=python

# 凭证与诊断
$PY scripts/init_credentials.py          # 凭证配置（Secret 不回显）
$PY scripts/wechat_draft.py doctor       # 链路体检（含双源 IP 探测）

# 生图
$PY scripts/gen_image.py list            # provider 状态
$PY scripts/gen_image.py gen "提示词" -o cover.png
$PY scripts/fit_cover.py cover.png -o cover-900x383.jpg --anchor 0.22

# 排版
$PY vendor-gzh/scripts/component_lint.py vendor-gzh              # 源头关
$PY vendor-gzh/scripts/validate_gzh_html.py article.gzh.html    # 产物关（须0 WARN）
$PY vendor-gzh/scripts/wrap_preview.py article.gzh.html preview/x.html

# 草稿箱
$PY scripts/wechat_draft.py cover cover-900x383.jpg    # 上传封面并设为默认
$PY scripts/wechat_draft.py push article.md --title "标题" --digest "摘要"
$PY scripts/wechat_draft.py list --count 10
$PY scripts/wechat_draft.py rm <media_id>
```

## 已知限制

- **自动发表做不到**：个人主体/未认证账号无 `freepublish` 权限（`48001`），永久限制。
- **家宽 IP 动态**：本机跑需IP 变了重配白名单；长期方案是部署到有固定 IP 的云端 Agent。
- **生图有标识**：AI 生图平台会在角落打「AI 生成」标识，`fit_cover.py` 默认不裁（法规要求）；发表时记得勾选 AI 内容声明。
- **中文偶发变形**：图像模型对中文字形把握不稳，关键封面建议人工过一眼。


```bash
PY=python
$PY scripts/wechat_draft.py doctor                    # 体检
$PY scripts/wechat_draft.py list                      # 列草稿
$PY scripts/wechat_draft.py push article.md \
    --title "标题" --digest "摘要" --cover cover.jpg   # 推送（改标题不会另起一篇）
$PY scripts/wechat_draft.py rm <media_id>             # 删草稿

$PY vendor-gzh/scripts/validate_gzh_html.py article.gzh.html   # 产物关（须 0 WARN）
$PY vendor-gzh/scripts/wrap_preview.py article.gzh.html preview/x.html
```