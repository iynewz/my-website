---
date: 2026-03-29
comments: true
tags:
  - 笔记
  - 增长
---

# AI 时代怎么做增长

*写于 2026-03-29*

> 本文档整理自 [AI Odyssey 播客第 74 期](https://www.xiaoyuzhoufm.com/episode/69bac706690ca3160f3bac09)，并补充了相关工具、平台的背景信息。自己听了觉得很有收获，Manus 和我一起合作，整理了一下信息。

> 嘉宾：宗源（X: @jaredliu_bravo）是 YouMind 的增长工程师。近半年，他操盘了 2 次 Product Hunt 打榜（日榜第一、年榜第六），并在近三个月内拿到了全站 50% 以上的流量。YouMind 是一个 AI 学习和创作平台，由前语雀创始人玉伯创立。

## AI 时代的 3 种增长机会

### 1. 魔法型产品

当一个产品首次展示出令人惊叹的能力时（如 Manus 首次展示虚拟计算机的思考过程），用户会自发传播。这种「Magic Moment」带来的口碑效应是最强大的增长引擎，但它依赖于极高的技术门槛和极好的产品体验，不可复制也不可持续。

### 2. 渠道型产品

ChatGPT 等对话式 AI 的推荐、OpenClaw（AI Agent 的"应用商店"）、以及各类 AI Agent Skills 生态。这些渠道的特点是用户在使用 AI 的过程中自然地发现你的产品，而非通过搜索或广告。

### 3. 自动化

这是宗源最核心的增长方法论。借助 AI 工具（特别是 OpenClaw），可以将传统需要大量人力的增长工作自动化。

**案例：自动截流 Nano Banana 2 发布**

宗源虽然不知道 Google 新模型 Nano Banana 2 的具体发布时间，但他提前做了以下准备：

- 用 OpenClaw 在 Vertex AI（Google Cloud 的模型托管平台）上设置了每 30 分钟一次的轮询监控
- 提前准备好了 100 个 Prompt、模型对比页面、测试脚本、各渠道的定制化文案、以及想要联系的 KOL 列表
- 当模型一发布，整套推广物料在几小时内就自动生成并分发完毕

类似的策略也被用在了 Seedance 2.0 上——模型还没发布时，YouMind 已经先建好了落地页，基于「假设」用户可能想体验新模型做一些案例，提前准备好了内容框架，等模型发布后，OpenClaw 自动搜集用户讨论、官方文章，自己总结一篇文章出来，自动发布。

**蹭热点，热点是用户的需求。**

## 社交媒体

### 分发策略

YouMind 在 Twitter 和 Facebook 发力最大。

### 内容运营

素材主要来自 Skills，这样内容是源源不断的。

Skill 的增长逻辑形成了一个完整的飞轮：

1. 用户在 YouMind 中创建 Skill 解决自己的问题
2. 用户在 X / 社交媒体上分享 Skill（获得社交认同）
3. 其他用户看到后来到 YouMind 使用该 Skill（拉新）
4. 新用户在使用过程中创建自己的 Skill（回到第 1 步）

用户自发传播 AI Skill 将成为未来 1-3 年极大的增长变量，类似于「写代码」门槛下放后带来的创作者经济爆发。

## SEO 策略：提升 DR

宗源将 SEO 策略的核心归结为一个指标：**Domain Rating (DR)**。DR 是 Ahrefs 定义的域名权威度评分（0-100），反映了一个网站在搜索引擎眼中的可信度。

他区分了两类关键词：

- **品牌词（Brand Keywords）**：用户直接搜索"YouMind"带来的流量，属于品牌推广的功劳，不属于 SEO
- **信息词（Informational Keywords）**：用户为解决特定痛点而搜索的通用词汇，如"AI image generation prompts"。如果可以从信息词截到用户是最好的

### skywork.ai 案例研究

天工 AI 通过蹭热门模型关键词（如 Sora、Seedance）撰写博客文章，将博客流量做到了整站的 30%。其 SEO 博客的特点是：页面顶部和底部都放置了多个 CTA 按钮，实现从阅读到注册的转化。

天工 AI 的做法是早期先蹭「模型词」来提升 DR。当 DR 提升到一定水平后，再去竞争更广泛的信息词。DR 分数越高（如达到 50 以上），发布的博文越容易在非品牌类的信息词搜索中获取高排名。

### DR 提升手段：外链

外链建设分为三个层级：

**1. 买外链**

- [theresanaiforthat.com](https://theresanaiforthat.com/) —— 几十刀，全球最大的 AI 工具导航站，提交后获得一个反向链接
- 购买 AITDK 作者 blank 的批量提交服务 [submitdirs.com](https://submitdirs.com/) —— 上百个目录，分 3 个月逐步提交，效果不错，可以提升 10 个点的 DR

**2. 自己构建的**

- **资源集合型页面**：YouMind 的 Prompt 集合站（如 youmind.com/nano-banana-pro-prompts）本身就是一个高价值的资源页面。当其他网站引用这些 Prompt 集合时，就会自然产生反向链接。宗源提到，YouMind 的 Prompt 集合站已经带来了数千个外链。
- **GitHub 仓库建设**：这是宗源最推崇的外链策略。当一个 GitHub 仓库突破 200-300 Stars 时，GitHub 会在该仓库的页面上生成一个 Do-follow 外链（指向仓库 README 中的网站链接）。由于 GitHub 的 DR 高达 96-97，这个外链的权重极高。YouMind 通过 YouMind-OpenLab 组织在 GitHub 上维护了 13 个开源仓库，总 Stars 超过 11.8K，为 youmind.com 提供了多个来自 GitHub（DR 96+）的高权重 Do-follow 外链。

## 如何转化？

- **粗暴做法**：在页面上多放几个 CTA 按钮（天工 AI 的做法——页面顶部和底部都有 CTA）
- **精细做法**：One-Tap Login（一键登录），如网页右上角自动弹出的 Google 授权登录。这种方式可以在不增加用户点击成本的情况下，直接提升 3%-8% 的注册转化率

**但！无论 CTA 策略多么精细，如果受众不匹配，一切都是徒劳。** Wordware 的案例证明了这一点（见下文）。

## Product Hunt 打榜

胜负取决于社媒互换票仓网络的规模。如果想拿到结果，必须认识到，**这不是一个纯粹靠产品质量取胜的游戏**。

票源渠道按灰度从灰到白：

1. **印度、东南亚票仓服务**
2. **互换票 / 群**
      - 微信群里有很多打榜群，挨个私聊
      - 在 PH 找当日日榜产品被 feature 的、参与打榜的人。宗源写了一个脚本自动抓 PH 当日日榜里的产品的 members 的社媒
3. **头部 Hunter 进行发布**
      - **Chris Messina** —— 被称为"#1 Product Hunter"，也是 hashtag（#）的发明者。在 PH 上已经 hunt 了超过 2,500 个产品。他基本代表了 PH 官方的审美标准。接受付费咨询（通过 chrismessina.me/hunt-me），如果产品通过他的审核并由他 hunt，100% 可以被 Feature
      - **PH CEO**
      - **Ben Lang** —— 曾任 Notion 社区负责人（Head of Community），在 PH 上 hunt 了超过 360 个产品。目前已加入 Cursor 团队

产品必须被 Feature。如果没有找到合适的 Hunter，产品很可能不会被 Feature，这时候与其硬上，不如把产品下架，重新包装后再 Launch。**在 PH 上，一次失败的 Launch 比没有 Launch 更糟糕。**

## 增长的终极目标：付费订阅飞轮

增长的终极目标不是流量，而是**赚钱**，建立从拉新到付费订阅的飞轮。

### Wordware 案例：700 万 UV 的教训

Wordware（YC S24）是一个 AI Agent 开发平台。2024 年 8 月，他们推出了一个名为 Twitter Personality 的病毒式小工具——用户输入 Twitter 用户名，AI 会生成一份性格分析和吐槽报告。这个工具在 12 天内吸引了超过 810 万用户，产生了 $100K+ 的收入，并帮助 Wordware 在随后拿到了 Spark Capital 领投的 $30M 种子轮。

然而，810 万 UV 中，实际注册 Wordware 平台的用户仅约 27.8 万，注册转化率仅为 3-4%。原因在于**受众错位**——来的人是为了「被 AI 吐槽」的普通用户，而 Wordware 的目标用户是 AI 开发者。

相比之下，YouMind 的提示词集合站（如 youmind.com/nano-banana-pro-prompts）的注册转化率高达 20%，因为来的人本身就是想用 AI 生成图片的创作者——正是 YouMind 的目标用户。