---
id: sample-airy
title: 一张配图，用 HTML 画出来
digest: 写几行内容，套进骨架，截成图片。字是清楚的，数字是准的，改一个数字只要改一行。
kicker: 白皮 · 头部IP
tags: 配图, HTML, 插图卡
author: 艾元老猫
account: 艾元老猫
card: 记录用 AI 省掉重复劳动的真实做法。
follow: 关注一下，下次实测更多工具。
related: 六个原创主题，各适合写什么::主题实验室导览 | 从 Markdown 到草稿箱，一次走完::发布流程
date: 10·08
cover: none
---

# 一张配图，用 HTML 画出来

![一张配图，用 HTML 画出来](assets/airy-cards/{variant}/wide/cards/cover.jpg)

> 写公众号最费时间的，往往不是文字，是配图。

AI 生图画氛围很好，但一碰到数字和中文就容易出错。截图准确，风格却跟着来源走。我们换了个思路：配图也用排版来做。

## 01　先看结论 ｜ RESULTS

一套骨架，一次出齐。下面是这篇文章的全部配图，左右滑动查看：

:::gallery swipe 同一套配色下的五种骨架，3:4 贴图版
![封面](assets/airy-cards/{variant}/tall/cards/cover.jpg)
![数据](assets/airy-cards/{variant}/tall/cards/stat.jpg)
![对比](assets/airy-cards/{variant}/tall/cards/compare.jpg)
![金句](assets/airy-cards/{variant}/tall/cards/quote.jpg)
![步骤](assets/airy-cards/{variant}/tall/cards/steps.jpg)
:::

## 02　为什么不用生图 ｜ WHY HTML

### CASE 01 · 数字要准

数据卡里的每个数字都是直接排出来的，不存在“画歪了”的问题。改一个数字，只需要改一行。

![一次出图的成本](assets/airy-cards/{variant}/wide/cards/stat.jpg)

### CASE 02 · 三种方式对比

截图适合记录实操，生图适合营造氛围，讲数据、结论和步骤时，卡片更合适。

![三种配图方式](assets/airy-cards/{variant}/wide/cards/compare.jpg)

## 03　怎么做出来 ｜ HOW IT WORKS

![从内容到配图](assets/airy-cards/{variant}/wide/cards/steps.jpg)

给 AI 的指令只有一句：

```prompt 生成配图 · 读系列配色
把这篇文章的三个结论写成 spec.json，用白皮配色各出一张 16:9 卡片。
```

![金句卡](assets/airy-cards/{variant}/wide/cards/quote.jpg)

能用一张卡说清的，就别让读者读三段。

## 最后：你的配图最费时间的是哪一步？

> [!ASK] 找图、做图，还是改图？
