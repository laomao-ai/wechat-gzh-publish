# 依赖说明

本项目的代码（`scripts/` 与文档）采用 [MIT 协议](LICENSE)。

它依赖一个**外部的排版组件库**，需要单独获取，不随本仓库分发。

---

## 排版组件库（clone 获得）

| 项 | 值 |
|---|---|
| 仓库 | https://github.com/isjiamu/gzh-design-skill |
| 协议 | AGPL-3.0 |
| 用途 | 提供公众号排版的组件库（多套主题）+ 两个校验脚本 |
| 获取 | `git clone --depth 1 https://github.com/isjiamu/gzh-design-skill.git vendor-gzh` |

**本项目如何使用它**

- 通过命令行调用其校验脚本（`component_lint.py` / `validate_gzh_html.py`）
- 读取其 Markdown 组件库文件，按组件装配 HTML
- **未修改其任何源代码**

**如果要再分发**

`vendor-gzh/` 是独立的第三方项目，以其仓库中的 LICENSE 为准。本项目的 MIT 协议不覆盖它。

另外，`config/brand_voice.json` 中默认主题 `moyu-green` 的样式描述片段衍生自该组件库，
已在该 JSON 文件内标注 `source: gzh-design-skill (AGPL-3.0)`。该片段随本仓库分发，
使用时请注意其来源标注。

---

## 平台接口

本项目调用微信官方公开接口（[developers.weixin.qq.com](https://developers.weixin.qq.com/doc/)）：

| 接口 | 用途 |
|---|---|
| `GET /cgi-bin/token` | 获取调用凭证 |
| `POST /cgi-bin/material/add_material` | 上传封面 |
| `POST /cgi-bin/media/uploadimg` | 上传正文图 |
| `POST /cgi-bin/draft/add` · `update` · `batchget` · `count` · `delete` | 草稿管理 |

**平台限制**：自 2025 年 7 月起，个人主体 / 未认证企业账号的 `freepublish/*` 接口已被回收。本项目因此**只到草稿箱为止**，「发表」由人工完成。

---

## 生图服务

本项目**不内置任何图像模型**，也不附带模型权重。

`scripts/gen_image.py` 只提供接口适配层，实际调用需要你自己申请并配置第三方服务的 API Key：

| 服务 | 获取地址 |
|---|---|
| Google AI Studio（Gemini 图像模型） | https://aistudio.google.com/apikey |
| OpenAI | https://platform.openai.com/api-keys |
| 火山引擎方舟 | 火山引擎控制台 |

各服务的使用条款与费用由其提供方承担。

**默认不调用任何外部服务** —— 如果宿主 Agent 自带生图能力，这一层完全不需要配置。
