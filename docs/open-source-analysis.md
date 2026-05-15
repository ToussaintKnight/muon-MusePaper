# Open-Source Intelligence System Analysis

## 开源个性化推荐系统调研报告
> Date: 2026-05-14 | Author: Pixie (CTO)

---

## 背景

MUON 正在构建一个面向 Sir（单人用户）的每日情报系统。目标是从百度/微博/B站等平台抓取热搜，通过兴趣匹配过滤出 Sir 会感兴趣的内容，由 LLM 合成摘要后推送到 Telegram。

本文调研了 GitHub 上开源的个性化内容推荐/聚合系统，评估其是否可作为基础或参考。

---

## 1. `1202-corp/personalized-post-platform`

**链接:** https://github.com/1202-corp/personalized-post-platform

**简介:** Telegram bot 从频道抓取贴文 → 向量嵌入 → 个性化推荐给用户。

**技术栈:** Docker Compose / FastAPI + Qdrant（向量数据库） + Aiogram 3 + Telethon + PostgreSQL + Redis

### 架构

```
main-bot (Aiogram 3) ◄──► core-api (FastAPI + ML) ◄──► Qdrant (embeddings)
    │                          │
    ▼ HTTP /cmd/*              ▼ PostgreSQL
user-bot (Telethon scraper)
```

### 评价

| 维度 | 评价 |
|------|------|
| 推荐算法 | 基于向量嵌入的语义搜索（余弦相似度） |
| 个性化 | 每个用户独立的向量偏好 |
| 数据源 | Telegram 频道（Telethon 用户 bot） |
| 推送 | Telegram bot |
| 代码质量 | 俄文注释和文档，代码结构较混乱 |
| 活跃度 | 7 commits, 2025 年，0 stars |

### 局限

1. **太重了：** 7 个容器（Qdrant, Postgres, Redis, PGAdmin, 两个 bot, API），单用户场景不需要
2. **依赖外部 API：** OpenAI 兼容的 embedding API，每次推荐产生网络调用和 token 成本
3. **需要 TG API ID/Hash：** Telethon 用户 bot 需要你的 Telegram 账号凭据，存在安全和封号风险
4. **多用户 SaaS 架构：** 底层是为多用户设计的（Auth, 独立的用户向量），不适合单人场景
5. **俄文：** 所有文档和代码注释均为俄文，维护成本高

### 可借鉴的点

- 使用 Qdrant 作为向量存储的思路（但我们不需要，单用户 50 条数据内存计算即可）
- Tinder-style 反馈界面（👍/👎 滑动选择）
- Aiogram 3 作为 TG bot 框架

---

## 2. `donotdonuts/coffeed-news-the-news-aggregator`

**链接:** https://github.com/donotdonuts/coffeed-news-the-news-aggregator

**简介:** 智能新闻聚合器，每天生成个性化邮件摘要。

**技术栈:** Next.js 14 + FastAPI + Celery + Supabase (pgvector + Auth) + Redis

### 架构

```
RSS / Reddit / Twitter/X / Podcasts → Celery Workers (Ingest: Scrape → Embed → Score)
    → Celery Workers (Synthesize: INRF Ranking → LLM Summary → Email)
    → Celery Workers (Deliver: Resend API)
```

### 推荐算法：INRF

INRF (Insight-Niche-Relevance-Freshness) 公式：
```
score = 0.5 × Insight + 0.3 × Relevance + 0.2 × Niche
```

- **Insight**（洞见度 50%）：文章是否提供了独特的视角或深度分析
- **Relevance**（相关度 30%）：与用户兴趣主题的语义相似度（embedding cosine）
- **Niche**（垂直度 20%）：内容的专业深度 vs 大众广度

### 评价

| 维度 | 评价 |
|------|------|
| 推荐算法 | INRF（结合 embedding + 规则），比简单 cosine 更成熟 |
| 个性化 | 用户选择 topic（AI, Finance, Robotics 等预设主题） |
| 数据源 | RSS / Reddit / Twitter/X / Podcasts |
| 推送 | Email（Resend API） |
| LLM 集成 | DeepSeek → OpenAI → Gemini → Grok fallback chain |
| 代码质量 | 2 commits, Claude（AI）写的，质量尚可 |
| 活跃度 | 2026 年 4 月，0 stars |

### 局限

1. **SaaS 模式：** 需要 Stripe 付费订阅、用户注册登录（Supabase Auth），单人场景多余
2. **多外部依赖：** Supabase（pgvector + Auth）+ OpenAI embedding API + 多路 LLM API + Resend 邮件 API
3. **硬件要求：** 依赖外部向量数据库（pgvector），本地部署需运行整个 Supabase
4. **个性化较弱：** 用户只选预设 topic（"AI"、"Finance"），不是从个体行为学习
5. **邮箱推送：** 用户想要的 Telegram，不是邮件
6. **推荐策略固定：** INRF 权重是 hardcoded，不支持自定义策略规则

### 可借鉴的点

- **INRF 评分公式：** Insight + Relevance + Niche 三维度打分，比单纯 cosine 更丰富
- **LLM 摘要 pipeline：** 多模型 fallback chain 的设计模式
- **Celery 任务队列：** 内容摄取 → 处理 → 推送的异步工作流模式
- **多数据源融合：** 同一个 digest 融合 RSS + 社交 + 播客多个源

---

## 3. Others

额外查看了以下相关项目（均不成熟或无关）：

| 项目 | 理由排除 |
|------|---------|
| `Hemanthkumar04/NewsLens` | 0 stars, 未完成, 仅前端展示 |
| `silverbullet-personal` | 个人知识管理，非推荐系统 |
| `news-please` | 新闻爬虫，无推荐/个性化 |
| `feedly-like` | REST API 包装，无 ML 组件 |

---

## 总结：为什么不直接用现成的

| 对比维度 | 1202-corp | Coffeed News | **MUON 需要的** |
|---------|-----------|-------------|---------------|
| 用户数 | 多用户 | 多用户 + 付费 | **单人** |
| 部署 | Docker Compose × 7 | Supabase × 云服务 | **~200 行 Python** |
| 向量存储 | Qdrant（独立服务） | pgvector（Supabase） | **内存计算，0 依赖** |
| Embedding API | OpenAI（按次付费） | OpenAI（按次付费） | **本地模型，免费** |
| 个性化 | 向量偏好静态度量 | 选 topic（固定） | **从聊天/知识库自动学** |
| 反馈 | Tinder-style 滑动 | 无 | **👍/👃 → 自动调权重** |
| 推送 | Telegram | Email | **Telegram（Hermes 已有）** |
| 文档语言 | 俄文 | 英文 | **中文** |

**核心结论：市面上没有适合单人+学习型+Telegram推送的开源项目。自己做 200 行代码比部署任何现有项目都更快、更轻、更适合。**
