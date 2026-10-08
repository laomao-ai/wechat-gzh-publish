---
id: sample-grid
title: 把预览页发布成一个能分享的链接
digest: 用 GitHub Pages 把本地 HTML 变成网址，读者点开就能看。
kicker: 蓝图 · 实操教程
tags: 教程, GitHub Pages, 静态页面
author: 艾元老猫
account: 艾元老猫
card: 记录用 AI 省掉重复劳动的真实做法。
follow: 关注一下，教程类文章会一直更新。
related: 从 Markdown 到草稿箱，一次走完::发布流程 | 六个原创主题，各适合写什么::主题实验室导览
date: 10·08
---

# 把预览页发布成一个能分享的链接

> 本地 HTML 只有你自己能打开。推到 GitHub 仓库，再开启 Pages，就能得到一个公开网址。

## 01　开始前确认

- [x] 页面里引用的图片和文件都是相对路径
- [x] 入口文件叫 `index.html`，放在仓库根目录
- [ ] 已经有一个 GitHub 账号和一个空仓库

> [!WARN] 别用本机绝对路径
> 像 `D:/xxx/a.png` 这样的路径，换一台电脑就打不开。改成 `assets/a.png` 这样的相对路径。

## 02　三步发布

1. **推送代码**：把整个文件夹提交并推到仓库的 main 分支。
2. **开启 Pages**：仓库 Settings → Pages，来源选 main 分支、根目录。
3. **等待部署**：一两分钟后，页面顶部会出现网址。

推送用的命令：

```bash
git add .
git commit -m "publish theme lab"
git push -u origin main
```

## 03　网址长什么样

| 项目 | 格式 |
| --- | --- |
| 仓库 | `github.com/<用户名>/<仓库名>` |
| 网页 | `<用户名>.github.io/<仓库名>` |
| 深链接 | 网页地址后加 #主题-主色 |

**只要路径是相对的，整个文件夹放到哪里都能直接打开。**

*Pages 对公开仓库免费；私有仓库是否可用取决于账号类型。*

## 最后：链接比文件更好分享

一个网址，读者点开就能看，不用下载，也不用解释怎么打开。

> [!ASK] 你打算用 Pages 发布什么？
