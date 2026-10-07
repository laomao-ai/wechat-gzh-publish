---
name: wechat-gzh-publish
description: 公众号发布前的四步工作流——质检（标题/结构/内容）→ 排版（校验零警告）→ 配图（封面生图+裁切）→ 推送草稿箱（幂等更新）。当用户说「发公众号」「推草稿箱」「公众号排版」「帮我看看这稿行不行」「起个标题」「同步到草稿箱」，或需要把 Markdown 变成公众号文章并送进后台草稿箱时使用。覆盖内容质检、标题优化、多主题排版、微信平台合规校验、封面上传、正文图上传、幂等草稿更新、出口 IP 探测。
agent_created: true
---

# 公众号发布四步：质检 → 排版 → 配图 → 推送

把一篇稿子变成公众号草稿箱里的一篇文章。**质检是把关，排版交给脚本，推送直连微信官方 API。**

---

## 权限天花板（先看，不然后面白干）

**「自动发表」在接口层面做不到。**

2025 年 7 月起微信回收了个人主体 / 未认证企业账号的 `/cgi-bin/freepublish/*` 权限，报 `errcode 48001`。这是平台策略，不是配置问题。

但 `/cgi-bin/draft/*` **草稿箱接口个人主体仍可用**。

**所以终点是草稿箱，不是发布。最后一步必须人工点「发表」。**

---

## 安装（三步，Agent 照着跑）

```bash
# 1. 本 skill：clone 到你的 Agent 的 skills 目录
git clone https://github.com/laomao-ai/wechat-gzh-publish.git
#   Claude Code → ~/.claude/skills/wechat-gzh-publish
#   Codex      → ~/.codex/skills/wechat-gzh-publish
#   Cursor     → 项目 .cursor/skills/ 或 ~/.cursor/skills/
#   其他 Agent → 问它"你的 skills 目录在哪"，放到对应位置

# 2. 排版依赖（AGPL-3.0，独立 clone，不随本仓库分发）
git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git \
  <skill目录>/wechat-gzh-publish/vendor-gzh

# 3. Python 依赖（wechat_draft.py 仅标准库；裁封面需要 Pillow）
pip install pillow
```

Windows 注意：`bash xxx.sh` 请用 Git Bash 或 WSL 跑；`python3` 常常叫 `python`，命令里自行替换。

---

## 这个 skill 解决什么

市面上公众号排版工具普遍走两条路：生成 HTML 让你手动 ⌘A⌘C 粘贴，或者把文章上传到第三方服务器换取固定出口 IP。

本 skill 走另一条：**本地直连微信官方 API**。

### 两个我自己最需要的能力

**1. 幂等更新（改稿不堆重复稿）**

云端 Agent 会反复改稿。普通做法每次都 `draft/add`，草稿箱会堆几十篇重复稿。

本 skill 的 slug 取自 **Markdown 的绝对路径**（或 front matter 里的 `id`），记在本地；
命中走 `draft/update`，否则才新建。**改标题、改摘要都不会另起一篇。**

```python
slug = make_slug(article_path, front)  # sha1(path 或 id)[:16]
if state.get(slug):  draft/update       # 同一篇只更新
else:                 draft/add         # → 记入 state
```

**2. 出口 IP 双源探测**

微信要求调用接口的 IP 在白名单。本 skill 同时探测境内/境外两个源并对比：

```bash
python3 scripts/wechat_draft.py doctor
```

为什么需要对比：**有代理时，境外查询站返回的是代理节点 IP，而微信服务器在境内、流量直连，看到的是你的真实宽带出口。**

用境外站测 IP 会加错——这是我自己踩过的坑。脚本会明确提示该填哪个。

> 最可靠的办法：**直接看微信报错里的 IP** —— 那是它真实看到的，比任何第三方查询都准。

---

## 工作流

```
① 质检 → 标题 + 结构 + 内容（references/quality-check.md）→ 用户确认
② 排版 → 选主题 + 装配 → 校验到 0 WARN
③ 配图 → 封面生图 + fit_cover 裁成 900×383
④ 推送 → 直连草稿箱（同 slug 自动 update）
⑤ 人工点「发表」
```

**质检是入口，不是可选项。** 用户拿来一篇稿子，先过一遍标准，确认后再动手排版。

---

## 步骤 1：质检

完整框架见 `references/quality-check.md`。查三块：

### 标题（三条红线）
1. **有没有关键词** —— 没有行业词，读者搜不到、平台不识别
2. **长度 14～24 字** —— 超 28 字会被折叠
3. **事实是否成立** —— 标题承诺的，正文必须兑现（最重要）

完整方法见 `references/title-optimize.md`（含六类结构、打分维度、淘汰清单）。

### 结构
- 核心主张是否只有一个
- 开头能不能让读者认出自己（前 3 段说清"给谁看、他遇到什么问题"）
- 有没有"结论无推导"

### 内容
- **标题承诺是否兑现**（最容易崩的一环）
- 有没有 AI 味（过度总结 / 空洞排比 / 预设读者 / 空动词 / 完美收尾）
- 段落是否过长（超 3 行考虑拆）

### 输出格式

```markdown
## 质检结果

### 标题
- ⚠️ 问题：{具体问题}
- 改法：{具体建议}

### 结构
- ⚠️ 问题：... / 改法：...

### 内容
- ⚠️ 问题：... / 改法：...

### 通过项
- ✅ {哪些没问题}
```

**只报有问题的，通过项列一行即可。用户确认后再进排版。**

**诊断，不代写。** 给判断和方向，不替用户改稿。

**用户说"直接排"时可跳过** —— 但要提示一次"跳过质检，只负责排版，内容问题不兜底"。

---

## 步骤 2：排版（选主题 + 校验到 0 WARN）

### 先选主题

读 `config/brand_voice.json`。

**这个配置是可改的，不是硬编码：**

| 字段 | 作用 |
|---|---|
| `primary` | 默认主题，想换改这里 |
| `lock_primary: false` | 允许自由选择 allowed[] 任意主题 |
| `lock_primary: true` | 锁定只用 primary，适合账号风格已定型 |
| `allowed[]` | 主题清单，可自由增删 |

**默认是 `false`** —— 别人的账号不该被我锁死主题。

### 想加自己的主题

一次性生成、登记、之后固定用（不要每篇临时生成，那是风格漂移的根源）：

```bash
# 1. 用主题生成器出区块库（需先 clone vendor-gzh）
# 2. 转为标准主题库 vendor-gzh/references/theme-{标识}.md
# 3. 在 brand_voice.json 的 allowed[] 追加一行
# 4. 校验
python3 vendor-gzh/scripts/component_lint.py vendor-gzh
```

配置里有完整的 `新增主题指南`。要点：样式全内联、文字 `<span leaf="">` 包裹、封面风格段写进 `cover_prompt_style`。

### 再装配并校验


```bash
# 首次：拉取排版 skill
git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git vendor-gzh

# 源头关：扫组件库
python3 vendor-gzh/scripts/component_lint.py vendor-gzh

# 产物关：扫最终 HTML，须 0 WARN
python3 vendor-gzh/scripts/validate_gzh_html.py article.gzh.html

# 生成带复制按钮的预览页
python3 vendor-gzh/scripts/wrap_preview.py article.gzh.html preview/x.html
```

**产物必须 0 ERROR 0 WARN 才交付。warning 数就是「粘进后台会掉样式的处数」。**

### 微信平台硬性限制
| 禁用 | 用 |
|---|---|
| `<style>` `<script>` | 全内联 `style=""` |
| `<div>` `class` `id` | `<section>` |
| `position:fixed/absolute`、`float` | 正常流 |
| `@media` `@keyframes` | 无 |
| `display:grid` | `display:flex`（有限） |
| 外部字体 / CSS 变量 | 系统字体栈 |
| **裸文本节点** | `<span leaf="">文字</span>` |

**每个文字节点都要 `<span leaf="">` 包裹**，漏了微信会"纠正"并重写样式。

同 `<p>` 内不要混多个 `font-size`，拆成多个 `<p>`。

### 常见 WARNING 与修法
| warning | 修法 |
|---|---|
| 中文文本未被 `<span leaf>` 包裹 | **写脚本批量补**，别手改 |
| 四周虚线框 | 正文强调改用左竖条；虚线框仅用于居中素材占位 |

---

## 步骤 3：配图

```bash
python3 scripts/gen_image.py list                              # 看可用 provider
python3 scripts/gen_image.py gen "提示词" --ratio 21:9 -o cover.png
python3 scripts/fit_cover.py cover.png -o cover-900x383.jpg --anchor 0.22
python3 scripts/wechat_draft.py cover cover-900x383.jpg       # 上传并设为默认
```

**三件必做后处理**：

| 问题 | 处理 |
|---|---|
| 生图比例不对 | **优先按目标比例生成**（`--ratio 21:9`），比事后裁切省事；否则 `fit_cover.py` 按 2.35:1 裁 |
| 中文文字变形 | **严重时改用无文字封面**，别死磕 |
| 平台「AI 生成」标识 | **默认不裁**——《生成合成内容标识办法》第十条禁恶意删除显式标识；发表时记得勾选 AI 内容声明 |

⚠️ **锚点选错会切掉标题**，务必目视检查成品。

### 生图 Provider 配置

`gen_image.py` 支持 5 种 provider，按需在 `config/image_providers.json` 配置：

| provider | 端点 | 说明 |
|---|---|---|
| **`auto_delegate`** | — | **默认首选**：宿主 Agent 自生图，零成本 |
| `gemini` | Google 原生 / Interactions API | gemini-3.x 系列，**中文文字明显更好**，支持 21:9 |
| `openai` | `/images/generations` | gpt-image-2 支持任意分辨率 + `thinking`，**精确文字/信息图最强** |
| `volcengine` | 火山方舟 | 国内直连无需翻墙 |
| `custom` | 任意 OpenAI 兼容 | **第三方中转**：改 `base_url` 即可 |

```bash
# 首次配置
cp config/image_providers.example.json config/image_providers.json
# 然后填入 api_key

# 强制走外部 API（跳过宿主自生图）
python3 scripts/gen_image.py gen "提示词" --provider gemini --ratio 21:9
```

**API Key 怎么存**：写进 `config/image_providers.json`（已 gitignore），`chmod 600`。**不要在对话里粘贴明文密钥。**

### 模型选择速查

| 需求 | 推荐 |
|---|---|
| 纯氛围图、无文字 | 宿主自生 / `volcengine` 便宜够用 |
| 封面（中文文字为主） | `gemini-3-pro-image` 或 `gpt-image-2` |
| 信息图 / 表格 / 数字 | `gpt-image-2` + `thinking: medium` |
| 中文文字准确度优先 | `gemini-3-pro-image`（Nano Banana Pro） |

**Gemini 注意**：是推理模型，thinking 默认开启不可关闭，按 token 计费。`image_size` 必须大写 `K`（`2K` 而非 `2k`）。

### 配图分路（重要）

| 图类型 | 生成方式 | 理由 |
|---|---|---|
| **架构图 / 流程图 / 数据图表** | **代码生成 SVG/HTML** | 文字必须准确，生图必然出错 |
| 封面 | AI 生图 + 后处理 | 有设计感、文字为主 |
| 正文氛围图 | AI 生图 | 无文字、看构图 |

**最常见的错误是把架构图丢给 AI 生图。** 图像模型画架构图文字必然错，而架构图价值全在文字准确。


---

## 步骤 4：推送草稿箱

```bash
python3 scripts/wechat_draft.py push article.md \
  --title "标题" --digest "摘要" --source-url "https://github.com/xxx"
```

- `--title`/`--digest` 不填时，读 Markdown 顶部 front matter 的 `title`/`digest`
- `--source-url` 填原文链接，读者点「阅读原文」跳转（公众号正文外链点不了，这是最顺手的入口）
- 留言默认打开；`--no-comment` 可关闭
- 同一篇文章反复推自动走 `draft/update`，草稿箱不会堆重复稿

其他命令：

```bash
python3 scripts/wechat_draft.py list --count 10     # 列草稿
python3 scripts/wechat_draft.py rm <media_id>      # 删草稿
```

---

## 首次配置

**完整配置指南见 `docs/CONFIG.md`**（含 AppSecret 申请、IP 白名单排查、生图 Provider 选型）。

三步起：

```bash
# 1. 微信凭证（AppSecret 交互式输入，不回显，自动 chmod 600）
bash scripts/init_credentials.sh

# 2. IP 白名单 —— 必须用境内站查，境外站返回的是代理节点 IP
curl -s https://myip.ipip.net
# 填进：微信公众平台 → 设置与开发 → 基本配置 → IP 白名单

# 3. 体检（验证 1+2 都对了）
python3 scripts/wechat_draft.py doctor
```

**Secret 不要在对话里粘贴**——对话会留档。

**不确定自己的 IP 对不对？直接跑一次请求，看微信报错里说的 IP**——那是它真实看到的，比任何查询都准：

```
errcode 40164, invalid ip 203.0.113.45 ... not in whitelist
                    ^^^^^^^^^^^^^^^^ 填这个
```

---

## 高频坑速查

| 现象 | 原因 | 处理 |
|---|---|---|
| 预览好看，粘进后台散架 | 漏 `<span leaf>` | 产物关跑至 0 WARN |
| `40164` | 出口 IP 不在白名单 | **看报错里的 IP** |
| `47001` | update 的 articles 用了数组 | 改对象 + `index:0` |
| `48001` | 账号无该接口权限 | 草稿箱仍可用 |
| `40001` | Secret 错或用了重置前的值 | 重置后更新配置 |
| `invalid media_id` | 封面误用 uploadimg 的 url | 封面必须走 `material/add_material` |
| 正文图不显示 | 还是本地相对路径 | 先 `media/uploadimg` |
| 封面标题被切掉 | 裁切锚点不对 | `--anchor 0.22` |

### 微信两接口的 articles 结构不同（最隐蔽的坑）
```python
api_post("draft/add", token, {"articles": [article]})     # 数组
api_post("draft/update", token, {"media_id": mid,
                                  "index": 0,               # 必填
                                  "articles": article})     # 对象，不是数组
```

---

## 部署要点

**推送脚本要跑在调用方所在的机器上。** IP 白名单只认实际发起请求那台机器的出口 IP。

家用宽带出口 IP 会随重拨变化——这就是为什么有些工具要收"固定出口 IP"的费用。

| 方案 | 稳定性 |
|---|---|
| 部署到有固定 IP 的机器 | ⭐⭐⭐ |
| 向运营商申请公网固定 IP | ⭐⭐ |
| 本机跑 + IP 变了重配 | ⭐ 临时验证 |

---

## 路线图

### 已实现

- **质检** —— 见 `references/quality-check.md`
  查标题（三条红线）、结构（主张/开头/推导）、内容（承诺兑现/AI 味/段落）。
  输出问题清单和改法，**用户确认后再进排版**。

- **标题优化** —— 见 `references/title-optimize.md`
  输入文章内容，输出「1 首选 + 3～5 备选 + 关键词 + 首选理由」。
  含六类结构、打分维度、情绪钩子、淘汰清单。**给候选和理由，不替用户拍板。**

### 规划中

- **选题装配**：从已有知识库交叉定位"该写什么"
- 多平台分发（飞书、知乎等）
- 排版效果回归用例（`eval-cases.md`）

> 设计原则：能复用成熟方案的就不重写。自己实现的每一部分，都要能说清它解决了什么别人没解决的问题。

**用户本轮的明确要求高于本 skill 任何默认规则。**

---

## 深入

- `references/quality-check.md` — 质检框架（标题/结构/内容）
- `references/title-optimize.md` — 标题方法（规律 + 结构 + 打分）
- `docs/CONFIG.md` — ★ 配置指南（微信凭证 / IP 白名单 / 生图 Provider / 主题）
- `docs/BEST-PRACTICE.md` — 踩坑记录与实战验证（IP 探测、幂等设计、微信接口细节）
- `config/brand_voice.json` — 主题注册表（可自由增删，含新增指南）
