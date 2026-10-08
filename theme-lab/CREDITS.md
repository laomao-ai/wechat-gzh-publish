# 致谢与原创声明

主题实验室的代码、样式数值、配色、示例文案和插图卡**均为原创**。
下面这些项目和文章给了我们思路，我们只借鉴思路和做法，**没有复制任何源文件、样式表、模板或图片素材**。

## 思路来源

| 来源 | 协议 | 借鉴了什么 | 我们怎么做的 |
|---|---|---|---|
| 归藏（op7418）· [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) | MIT | 先有人工验证过的版式骨架，AI 只往里填内容 | `engine/cards.py` 五种骨架，配色读本项目各系列 token |
| 归藏（op7418）· [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill) | AGPL-3.0 | 公众号头图与方图成对出；渲染后实测越界和字号 | `cards.py` 的 2.35:1 / 1:1 比例，`shoot_cards.js` 的截图前校验，规则自己定 |
| 归藏（op7418）· [guizang-product-video-skill](https://github.com/op7418/guizang-product-video-skill) | AGPL-3.0 | 首帧即成品海报；所有静帧拼一张联系表来审 | 只作为设计原则，没有对应代码 |
| 甲木 · [gzh-design-skill](https://github.com/isjiamu/gzh-design-skill) | AGPL-3.0 | 公众号兼容规则；青林沿用其摸鱼绿的排版参数 | 兼容检查器 `engine/check.py` 自己写；skill 主仓库通过外部 clone 调用其校验脚本，不随仓库分发 |
| 甲木 · 公众号文章《WorkBuddy 想做 AI 时代的 Office》 | — | 横滑目录、PART 章节头、CASE 标签、PROMPT 框的阅读体验 | 白皮系列的对应组件，结构和样式自己实现 |

AGPL 项目的代码我们没有拿来用，所以本项目继续以 MIT 发布。如果你发现哪里和原项目过于相似，欢迎提 issue，我们会改。

感谢归藏师傅和甲木老师把好东西开源出来。
