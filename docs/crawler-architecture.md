# Muse 爬虫架构 — 验证报告

## 架构概览

```
Muse 双源引擎
│
├── 源 A: Camofox 浏览器 (国际站点) — 5 个 source, 已验证
│   ├── hackernews    → 22 条/8s  ✅
│   ├── github-trending → 12 条/18s ✅
│   ├── producthunt  → 20 条/11s  ✅
│   ├── techcrunch   → 20 条/8s   ✅
│   └── reddit       → 24 条/10s  ✅
│
├── 源 B: NewsNow API (国内站点) — 9 个 source, 已配置
│   ├── weibo         → 30 条/0.5s ✅
│   ├── zhihu         → 20 条/0.6s ✅
│   ├── 36kr          → 20 条/0.5s ✅
│   ├── baidu, bilibili, sspai, v2ex, wallstreetcn, juejin
│
└── 缓存层 (NewsNow 模式)
    ├── interval: 各 source 独立 (3min~1h)
    ├── TTL: 10min 全局
    └── 本地 JSON 缓存 (无需数据库)
```

## 关键发现

### NewsNow 爬虫逻辑借鉴的 3 个核心模式

1. **`defineSource()` 模式** — 每个源是一个自包含的函数，输入 URL 输出 `NewsItem[]`
   - NewsNow 用 `myFetch + cheerio` (HTTP 解析 HTML)
   - 我们用 `Camofox + snapshot parser` (浏览器解析 DOM 无障碍树)
   - **结果相同：统一的 `NewsItem[]` 接口，下游无需关心来源**

2. **缓存策略 (interval + TTL)**
   - `interval`: 各 source 独立刷新间隔
   - `TTL`: 全局 10 分钟缓存失效
   - 缓存优先，后台异步刷新
   - **已验证：在我们的代码中完整实现**

3. **MCP 接口** — NewsNow 自带 MCP Server，任意 AI agent 可以直接查询
   - 未来我们也可以给 Muse 加 MCP 接口

### Camofox 外网爬取能力

| 网站 | 状态 | 速度 | 反爬拦截 | 需要登录 |
|------|------|------|---------|---------|
| Hacker News | ✅ | ~8s | 无 | 否 |
| GitHub Trending | ✅ | ~18s | 无 | 否 |
| Product Hunt | ✅ | ~11s | 无 | 否 |
| TechCrunch | ✅ | ~8s | 无 | 否 |
| Reddit r/all | ✅ | ~10s | 无 | 否 |
| Google | ❌ | - | Cloudflare 拦截 | 否 |
| Twitter/X | ❌ | - | 需要登录 | 是 |

### NewsNow API 接入

- API 地址: `https://newsnow.busiyi.world/api/s?id={source_id}`
- 受 Cloudflare 保护，需要通过 SOCKS5 代理访问
- 返回格式: `{ status, id, updatedTime, items: [{id, title, url, mobileUrl, extra}] }`
- **30 个 source 全量拉取 = ~5 秒 (串行)，实际只拉 9 个 = ~2 秒**

### 文件清单 (已创建)

| 文件 | 作用 | NewsNow 对应 |
|------|------|-------------|
| `muse/types.py` | `NewsItem`, `SourceDef` 数据模型 | `shared/types.ts` |
| `muse/camofox.py` | Camofox REST API 客户端 | — |
| `muse/parsers.py` | 无障碍树解析器 (每 source 一个) | `sources/*.ts` 内的 cheerio 解析 |
| `muse/sources.py` | 5 个外网 source 定义 + 爬取函数 | `getters.ts` |
| `muse/newsnow.py` | NewsNow API 连接器 (9 个国内 source) | `api/s/index.ts` |
| `muse/crawler.py` | 缓存层 (interval + TTL) | `api/s/index.ts` + `database/cache.ts` |
| `muse/engine.py` | 引擎主循环 | — |
| `muse/test.py` | 测试脚本 | — |

## 下一步

如果要继续，下一步可以做：
1. **bge-small-zh embedding 集成** — 编码所有 item title → 兴趣向量余弦排名
2. **注册 cron 任务** — 按 NewsNow 模式调度，每天 2 次推送
3. **加更复杂的 parser** — 比如 `parse_github_trending` 的语言提取可以改进
4. **加更多外网 source** — 比如 Ars Technica, The Verge, Dev.to
