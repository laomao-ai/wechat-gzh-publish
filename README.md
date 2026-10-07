# wechat-gzh-publish

把 Markdown 变成公众号草稿箱里的一篇文章。**本地直连微信官方 API，不上传到任何第三方服务器。**

```
Markdown → 排版（校验 0 WARN）→ 封面 → 直连草稿箱 → 人工点「发表」
```

## 为什么不用现成工具

市面上的公众号排版工具走两条路：

1. 生成 HTML 让你手动 ⌘A⌘C 粘贴
2. 把文章上传到第三方服务器，换取固定出口 IP（这类服务通常按积分或月费收费）

本项目走第三条：**本地直连微信官方 API**。文章不出你的机器。

## 两个别人没有的能力

**幂等更新** —— 改稿不堆重复草稿

云端 Agent 会反复改稿。普通做法每次都 `draft/add`，草稿箱会堆几十篇重复稿。本项目用 `sha1(标题+摘要)` 作 slug 记在本地，命中走 `draft/update`，否则才新建。

> 这个功能看起来可有可无。但如果你经历过「改了十遍稿，草稿箱里堆了十个版本」，就知道它是刚需。。

**出口 IP 双源探测** —— 解决"微信固定出口 IP"这个痛点

微信要求调用接口的 IP 在白名单。**有代理时，境外查询站返回代理节点 IP，而微信在境内流量直连，看到的是你的真实宽带出口**——用错查询源就会加错。

```bash
python3 scripts/wechat_draft.py doctor   # 同时探测境内/境外，明确提示该填哪个
```

> 最可靠：直接看微信报错里的 IP，那是它真实看到的。

## 快速开始

```bash
# 1. 拉取本skill
git clone <this-repo> && cd wechat-gzh-publish

# 2. 微信凭证（AppSecret 交互式输入，不回显）
bash scripts/init_credentials.sh

# 3. IP 白名单
curl -s https://myip.ipip.net   # 境内站才是真出口
# 填进 微信公众平台 → 设置与开发 → 基本配置 → IP 白名单

# 4. 体检
python3 scripts/wechat_draft.py doctor

# 5. 排版 skill
git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git vendor-gzh
```

完整配置见 **[docs/CONFIG.md](docs/CONFIG.md)**。

## 工作流

```
① 选主题   config/brand_voice.json（可自由选，也可自己加）
② 排版     vendor-gzh 组件库 → 校验到 0 WARN
③ 封面     生图 → fit_cover 裁成 900×383
④ 推送     直连草稿箱（同 slug 自动 update）
⑤ 人工点「发表」
```

## 常用命令

```bash
# 排版
python3 vendor-gzh/scripts/component_lint.py vendor-gzh              # 源头关
python3 vendor-gzh/scripts/validate_gzh_html.py article.gzh.html     # 产物关，须 0 WARN
python3 vendor-gzh/scripts/wrap_preview.py article.gzh.html preview/x.html

# 封面
python3 scripts/gen_image.py list                                   # provider 状态
python3 scripts/gen_image.py gen "提示词" --ratio 21:9 -o cover.png
python3 scripts/fit_cover.py cover.png -o cover-900x383.jpg --anchor 0.22
python3 scripts/wechat_draft.py cover cover-900x383.jpg

# 草稿箱
python3 scripts/wechat_draft.py push article.md --title "标题" --digest "摘要"
python3 scripts/wechat_draft.py list --count 10
python3 scripts/wechat_draft.py rm <media_id>
```

## 已知限制

| 限制 | 说明 |
|---|---|
| **「自动发表」做不到** | 2025-07 起微信回收个人主体/未认证账号的 `freepublish` 权限（报 `48001`）。**终点是草稿箱，发表必须人工点。** |
| **动态 IP 需重配** | 家用宽带出口 IP 会变。长期方案是部署到有固定 IP 的机器。 |
| **封面有水印** | AI 生图平台会在右下角打标，`fit_cover.py` 已内置裁掉。 |
| **中文偶发变形** | 图像模型对中文字形把握有限。变形严重时改用无文字封面。 |
| **架构图别交给生图** | 图像模型画架构图文字必然错。用代码生成 SVG/HTML。 |

## 生图 Provider（可选）

**默认不消耗任何 API** —— 宿主 Agent 自带生图能力，直接用它。

需要外部 API 时在 `config/image_providers.json` 配置：

| provider | 端点 | 说明 |
|---|---|---|
| `auto_delegate` | — | 宿主 Agent 自生图（默认，零成本） |
| `gemini` | Google 原生 | 中文文字更好，支持 21:9 |
| `openai` | `/images/generations` | `gpt-image-2` 任意分辨率 + thinking |
| `volcengine` | 火山方舟 | 国内直连无需翻墙 |
| `custom` | 任意 OpenAI 兼容 | **第三方中转**：改 `base_url` 即可 |

```bash
python3 scripts/gen_image.py list
python3 scripts/gen_image.py gen "提示词" --ratio 21:9 --provider gemini
```

## 仓库里有什么

打开这个仓库，你可能想知道"我该看哪个"。按目的找：

| 我想… | 看这个 |
|---|---|
| **装它、用它** | [SKILL.md](SKILL.md) —— Agent 会自动读，你也可以翻 |
| **稿子先过一遍标准** | [references/quality-check.md](references/quality-check.md) —— 质检（标题/结构/内容） |
| **起标题** | [references/title-optimize.md](references/title-optimize.md) —— 标题优化（给候选+打分，不替你拍板） |
| **配凭证和白名单** | [docs/CONFIG.md](docs/CONFIG.md) —— 配置指南，含踩坑排查 |
| **知道有哪些坑** | [docs/BEST-PRACTICE.md](docs/BEST-PRACTICE.md) —— 实战验证过的踩坑记录 |
| **改主题/换风格** | `config/brand_voice.json` —— 主题注册表，可自由增删 |
| **接外部生图 API** | `config/image_providers.example.json` —— 5 种 provider 模板 |

完整目录：

```
wechat-gzh-publish/
│
├── SKILL.md                       ← Agent 使用说明（工作流、命令、坑）
├── README.md                      ← 你正在看的
├── LICENSE                        ← MIT
├── THIRD_PARTY_NOTICES.md         ← 第三方许可说明（gzh-design 是 AGPL）
│
├── docs/
│   ├── CONFIG.md                  ← ★ 配置指南（凭证 / IP 白名单 / 生图选型）
│   └── BEST-PRACTICE.md           ← 踩坑记录（每个坑都是真跑出来的）
│
├── references/
│   ├── quality-check.md           ← 质检框架（标题/结构/内容，排版前先过一遍）
│   └── title-optimize.md          ← 标题优化（通用规律 + 候选生成 + 打分）
│
├── scripts/                       ← 四个脚本，零第三方依赖
│   ├── wechat_draft.py            ← 核心：草稿箱直连 + 幂等更新 + IP 探测
│   ├── gen_image.py               ← 生图 provider 抽象层（5 种可选）
│   ├── fit_cover.py               ← AI 生图 → 微信合规封面 900×383
│   └── init_credentials.sh        ← 交互式填凭证（Secret 不回显）
│
├── config/
│   ├── brand_voice.json           ← 主题注册表（可自由增删，含新增指南）
│   ├── wechat.credentials.example.json   ← 凭证模板
│   └── image_providers.example.json      ← 生图配置模板
│
└── drafts/                        ← 内容方法论（标题/正文诊断的探索稿，当前不启用）
```

**你需要创建的**（`.gitignore` 已排除，不会误提交）：

- `config/wechat.credentials.json` —— 跑 `init_credentials.sh` 自动生成
- `config/image_providers.json` —— 需要接外部生图时才建

**需要另外 clone 的**（不在本仓库内）：

- `vendor-gzh/` —— 排版能力，来自 [gzh-design-skill](https://github.com/isjiamu/gzh-design-skill)（AGPL-3.0）

```bash
git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git vendor-gzh
```

## 三个高频坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 预览好看，粘进后台散架 | 漏 `<span leaf="">` 包裹 | 产物关跑至 **0 WARN** |
| `errcode 47001` | `draft/update` 的 `articles` 用了数组 | 改**对象** + 加 `index: 0` |
| `errcode 40164` | 出口 IP 不在白名单 | **看微信报错里的 IP** |

完整踩坑记录见 [docs/BEST-PRACTICE.md](docs/BEST-PRACTICE.md)。

## License

MIT（见 [LICENSE](LICENSE)）

排版层 `vendor-gzh` 为 [gzh-design-skill](https://github.com/isjiamu/gzh-design-skill)，AGPL-3.0，**独立 clone 使用，未修改**。
第三方许可详情见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
