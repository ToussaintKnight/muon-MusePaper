# MUON 每日情报系统 — 完整设计

## High-Level → Low-Level 全链路
> Version: 1.0 | Date: 2026-05-14 | Author: Pixie (CTO)

---

## 目录

1. [系统概览](#1-系统概览)
2. [核心数学模型](#2-核心数学模型)
3. [冷启动：交互式兴趣发现](#3-冷启动交互式兴趣发现)
4. [兴趣向量与推荐引擎](#4-兴趣向量与推荐引擎)
5. [预测仪表盘（雷达图）](#5-预测仪表盘雷达图)
6. [每日推送管道](#6-每日推送管道)
7. [反馈学习循环](#7-反馈学习循环)
8. [文件结构与 API](#8-文件结构与-api)
9. [部署与 Cron](#9-部署与-cron)
10. [附录：参数表与默认值](#10-附录参数表与默认值)

---

## 1. 系统概览

### High-Level 架构

```
数据层 ═══▶ 处理层 ═══▶ 推荐层 ═══▶ 推送层
 ┌────┐    ┌──────┐    ┌────────┐    ┌────────┐
 │    │    │      │    │        │    │        │
 │ 热 │    │ 向   │    │ 兴趣   │    │ LLM   │
 │ 搜 │───▶│ 量   │───▶│ 匹配   │───▶│ 摘要  │───▶ Telegram
 │ 爬 │    │ 编   │    │ 排序   │    │ ＋    │
 │ 虫 │    │ 码   │    │        │    │ 推送   │
 │    │    │      │    │        │    │        │
 └────┘    └──────┘    └────────┘    └────────┘
                             ▲
                             │ 反馈
                           ┌─┴──┐
                           │ 👍 │
                           │ 👎 │
                           └────┘
```

### 冷启动流程（独立模块）

```
首次运行或手动触发
  │
  ▼
10 个 General Tags 展示 ──▶ 选 ≥3 个
  │                              │
  │        点击标签 → 展开 10 个子标签
  │                              │
  │        继续点击 → 再展开（递归可扩展）
  │                              ▼
  │                    确认选择 → 生成初始兴趣向量
  │                              │
  └──────────────────────────────▼
                        进入每日推送管道
```

### 三个维度的时间尺度

| 维度 | 频率 | 机制 |
|------|------|------|
| 冷启动（主动选择） | 一次性 / 手动触发 | 树状标签 → 初始向量 |
| 每日推送（被动学习） | 每天 2 次（5:30am/pm） | 推荐 → 展示 → 👍/👎 |
| 权重微调（反馈学习） | 每次 👍/👎 | 向量加权更新 |

---

## 2. 核心数学模型

### 2.1 变量定义

| 符号 | 含义 | 默认值 | 推断方式 |
|------|------|--------|---------|
| `N` | 用户选择的兴趣标签数量 | — | 直接计数 |
| `M` | 每日内容池大小（跨平台） | 150 | Baidu 50 + Weibo 50 + Bilibili 50 |
| `p` | 单个标签平均匹配率 | 0.08 | 经验值（一条热搜命中一个标签的概率） |
| `λ` | 标签有效率 = `p × (1 - overlap)` | 0.068 | `λ = p × (1 - overlap_coeff)` |
| `overlap` | 标签间重叠系数 | 0.15 | 标签相关性衰减因子 |
| `μ` | 相关度增长速率 | 0.10 | embedding 模型经验值 |
| `φ` | 疲劳系数 | 0.05 | 信息增益衰减率 |
| `d` | 嵌入向量维度 | 256 | BAAI/bge-small-zh-v1.5 |
| `k` | 每项每标签评分时间 (ms) | 0.004 | MacBook M 系列实测 |
| `overhead` | 固定计算开销 (ms) | 2.0 | Python 进程启动 |

### 2.2 核心公式

#### 公式 1：覆盖率

```
coverage(N) = 1 - e^{-λN}

λ = p × (1 - overlap)
```

**推导：** 一个标签匹配一条内容的概率为 `p`。N 个独立标签至少有一个匹配的概率是 `1 - (1 - p)^N`。当重叠校正后，近似为指数形式。

```
N=1   → 1 - e^{-0.068} = 6.6%
N=5   → 1 - e^{-0.34}  = 28.8%
N=10  → 1 - e^{-0.68}  = 49.3%
N=15  → 1 - e^{-1.02}  = 63.9%
N=20  → 1 - e^{-1.36}  = 74.3%
N=30  → 1 - e^{-2.04}  = 87.0%
```

#### 公式 2：边际覆盖率增益

```
Δcoverage(N) = coverage(N) - coverage(N-1) = λe^{-λN}
```

第 N 个标签带来的**额外覆盖率**。随 N 指数衰减。

```
N=1  → 6.35%
N=5  → 4.84%
N=10 → 3.44%
N=15 → 2.45%
N=20 → 1.75%
N=30 → 0.88%
```

**规律：** 每条新标签带来的覆盖率增益，大约每 10 个标签减半。

#### 公式 3：相关度

```
relevance(N) = 1 - e^{-μN}

μ = relevance_coeff = 0.10
```

标签越多，每个标签越具体，匹配的内容越相关。

```
N=1   → 1 - e^{-0.10} = 9.5%
N=5   → 1 - e^{-0.50} = 39.3%
N=10  → 1 - e^{-1.00} = 63.2%
N=15  → 1 - e^{-1.50} = 77.7%
N=20  → 1 - e^{-2.00} = 86.5%
N=30  → 1 - e^{-3.00} = 95.0%
```

#### 公式 4：信息增益（每条推荐）

```
IG(N) = coverage(N) × relevance(N) × e^{-φN}

φ = fatigue_coeff = 0.05
```

**三条曲线的乘积。** `coverage` 保证内容够多，`relevance` 保证内容够准，`e^{-φN}` 保证不会因为同一类内容看太多而疲劳。

```
N=1   → 0.066 × 0.095 × 0.951 = 0.006
N=5   → 0.288 × 0.393 × 0.779 = 0.088
N=10  → 0.493 × 0.632 × 0.607 = 0.189
N=15  → 0.639 × 0.777 × 0.472 = 0.235
N=18  → 0.689 × 0.835 × 0.406 = 0.240  ← 峰值
N=20  → 0.743 × 0.865 × 0.368 = 0.236
N=30  → 0.870 × 0.950 × 0.223 = 0.184
```

**最优标签数：** 10-18 个（峰值在 N=18，10-15 是性价比最优区间）

#### 公式 5：内存占用

```
memory(N) = N × d × bytes_per_float

d = 256, bytes_per_float = 4
```

```
memory(10)  = 10 × 256 × 4 = 10,240 bytes = 10.0 KB
memory(30)  = 30 × 256 × 4 = 30,720 bytes = 30.0 KB
memory(100) = 100 × 256 × 4 = 102,400 bytes = 100.0 KB
```

线性增长，始终可忽略。

#### 公式 6：处理时间

```
time(N) = k × N × M + overhead

k = 0.004ms, M = 150, overhead = 2ms
```

```
time(5)  = 0.004 × 5 × 150 + 2 = 5.0ms
time(10) = 0.004 × 10 × 150 + 2 = 8.0ms
time(20) = 0.004 × 20 × 150 + 2 = 14.0ms
time(30) = 0.004 × 30 × 150 + 2 = 20.0ms
```

线性增长，始终 < 30ms。

#### 公式 7：每日推荐条数

```
daily_items(N) = M × coverage(N) = M × (1 - e^{-λN})
```

```
items(5)  = 150 × 0.288 = 43
items(10) = 150 × 0.493 = 74
items(15) = 150 × 0.639 = 95
items(20) = 150 × 0.743 = 111
items(30) = 150 × 0.870 = 130
```

---

## 3. 冷启动：交互式兴趣发现

### 3.1 标签树结构

```
root (10 个一阶标签)
├── AI/ML ─────────┬── 深度学习
│                   ├── LLM
│                   ├── 多模态 ◀── 点击展开 → 10 个子标签
│                   ├── 扩散模型
│                   ├── Agent
│                   ├── RAG
│                   ├── RL
│                   ├── 推理
│                   ├── 训练框架
│                   └── 评估基准
├── 设计工具 ───────┬── ...
├── 创业
├── 学术论文
├── 音乐
├── 游戏
├── 财经
├── 科技新闻
├── 开源
└── AI 艺术
```

### 3.2 节点 JSON 格式

```json
{
  "id": "ai-ml",
  "name": "AI/ML",
  "emoji": "🤖",
  "keywords": ["AI", "machine learning", "deep learning", "neural"],
  "children": [
    {
      "id": "ai-ml-llm",
      "name": "LLM",
      "keywords": ["LLM", "large language model", "GPT", "transformer"],
      "children": [
        {"id": "ai-ml-llm-gpt", "name": "GPT/Azure", "keywords": ["GPT-4", "GPT-4o", "Azure OpenAI"], "children": []},
        {"id": "ai-ml-llm-open", "name": "开源 LLM", "keywords": ["Llama", "Mistral", "Qwen", "DeepSeek"], "children": []},
        {"id": "ai-ml-llm-eval", "name": "评估基准", "keywords": ["MMLU", "GSM8K", "HumanEval", "benchmark"], "children": []}
      ]
    }
  ]
}
```

两层结构约 150 个节点。如果有需求，第三层可扩展到 500+ 节点。

### 3.3 交互流程

```python
class OnboardingFlow:
    """
    冷启动交互逻辑。

    Step 1: show_root_tags() → 用户选 ≥3 个
    Step 2: expand_tag(tag_id) → 展示 10 个子标签
    Step 3: repeat Step 2 或 confirm()
    Step 4: generate_profile(selected_tags)
    """

    def __init__(self, tag_tree: TagTree):
        self.tag_tree = tag_tree
        self.selected = set()   # 已选标签 ID
        self.expanded = set()   # 已展开的父标签 ID

    def show_root_tags(self) -> list[dict]:
        """返回 10 个一阶标签"""
        return [{
            "id": t.id, "name": t.name, "emoji": t.emoji,
            "children_count": len(t.children),
            "selected": t.id in self.selected
        } for t in self.tag_tree.roots]

    def expand_tag(self, tag_id: str) -> list[dict]:
        """展开一个标签的子标签"""
        tag = self.tag_tree.get(tag_id)
        self.expanded.add(tag_id)
        return [{
            "id": c.id, "name": c.name,
            "depth": tag.depth + 1,
            "path": f"{tag.path} → {c.name}",
            "has_children": len(c.children) > 0,
            "selected": c.id in self.selected
        } for c in tag.children]

    def toggle_tag(self, tag_id: str):
        """选择/取消选择标签"""
        if tag_id in self.selected:
            self.selected.remove(tag_id)
        else:
            self.selected.add(tag_id)

    def confirm(self) -> dict:
        """确认选择 → 生成初始兴趣配置"""
        if len(self.selected) < 3:
            return {"error": "至少选择 3 个标签"}

        # 收集所有选中标签的 keywords 和 path
        selected_tags = [self.tag_tree.get(tid) for tid in self.selected]
        return generate_initial_profile(selected_tags)
```

### 3.4 初始兴趣配置生成

```python
def generate_initial_profile(selected_tags: list[TagNode]) -> dict:
    """
    从用户选中的标签生成初始兴趣配置。

    1. 收集所有选中的 keyword
    2. 拼接成一段自然语言描述
    3. 调用 embedding model 编码为初始兴趣向量
    4. 写入 profile.json
    """
    # 收集 keywords
    all_keywords = []
    for tag in selected_tags:
        all_keywords.extend(tag.keywords)

    # 拼接兴趣描述
    profile_text = "; ".join([
        f"{tag.path}: {' '.join(tag.keywords)}"
        for tag in selected_tags
    ])

    # 编码为向量（调用本地 embedding model）
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    base_embedding = model.encode(profile_text).tolist()

    return {
        "version": 1,
        "embedding_model": "BAAI/bge-small-zh-v1.5",
        "base_embedding": base_embedding,
        "selected_tags": [t.id for t in selected_tags],
        "topics": [
            {
                "tag_id": t.id,
                "name": t.name,
                "path": t.path,
                "keywords": t.keywords,
                "weight": 1.0,
                "embedding": model.encode(t.path + ": " + " ".join(t.keywords)).tolist()
            }
            for t in selected_tags
        ],
        "history": [],
        "created_at": timestamp_ms()
    }
```

---

## 4. 兴趣向量与推荐引擎

### 4.1 兴趣配置 (profile.json)

```json
{
  "version": 1,
  "embedding_model": "BAAI/bge-small-zh-v1.5",
  "base_embedding": [0.012, -0.034, ...],
  "selected_tags": ["ai-ml", "ai-ml-llm", "design-tools"],
  "topics": [
    {
      "tag_id": "ai-ml-llm",
      "name": "LLM",
      "path": "AI/ML → LLM",
      "keywords": ["LLM", "GPT", "transformer"],
      "weight": 1.0,
      "embedding": [0.021, -0.015, ...]
    }
  ],
  "history": [],
  "created_at": 1778800000000
}
```

### 4.2 推荐评分算法

```python
def score_item(item_title: str, item_desc: str, profile: dict, model) -> float:
    """
    计算一则内容与用户兴趣的匹配度。

    评分公式：
    score = α × cosine(base_embedding, item_embedding)
          + β × max_i [weight_i × cosine(topic_i, item_embedding)]

    其中 α = 0.3, β = 0.7（base 捕获宏观兴趣，topics 捕获具体兴趣）

    输出: [0, 1] 的浮点数
    """
    # 编码内容
    item_text = f"{item_title}. {item_desc}"
    item_embedding = model.encode(item_text)

    α, β = 0.3, 0.7

    # Base match
    base_score = cosine_similarity(profile["base_embedding"], item_embedding)

    # Topic match (取最高分)
    topic_scores = [
        t["weight"] * cosine_similarity(t["embedding"], item_embedding)
        for t in profile["topics"]
    ]
    max_topic_score = max(topic_scores) if topic_scores else 0

    return α * base_score + β * max_topic_score
```

### 4.3 每日推荐流程

```python
def run_daily_briefing() -> list[dict]:
    """
    每日情报生成管道。

    Step 1: 抓取各平台热搜
    Step 2: 为每条内容评分
    Step 3: 排序取 top N
    Step 4: LLM 写摘要
    Step 5: 推送 Telegram

    输出: 排序后的推荐列表
    """
    # Step 1: 抓取
    from hotlist_scraper import scrape_baidu
    baidu_result = scrape_baidu()

    # (未来) weibo_result = scrape_weibo()
    # (未来) bilibili_result = scrape_bilibili()

    all_items = baidu_result.get("items", [])

    # Step 2: 评分
    model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    profile = load_profile()

    scored_items = []
    for item in all_items:
        score = score_item(item["title"], item.get("description", ""), profile, model)
        scored_items.append({**item, "score": round(score, 4)})

    # Step 3: 排序
    scored_items.sort(key=lambda x: x["score"], reverse=True)

    # Step 4: LLM 摘要（略，调用已有的 DeepSeek Flash）
    summary = synthesize_summary(scored_items[:10])

    # Step 5: 推送
    push_telegram(summary)

    return scored_items
```

---

## 5. 预测仪表盘（雷达图）

### 5.1 数据模型

```javascript
// 浏览器端 JS 版本 of predictor.py
const DEFAULT_PARAMS = {
  dailyPoolSize: 150,    // M
  avgMatchRate: 0.08,    // p
  overlapCoeff: 0.15,    // overlap
  relevanceCoeff: 0.10,  // μ
  fatigueCoeff: 0.05,    // φ
  embeddingDim: 256,      // d
  bytesPerFloat: 4,
  timePerItemPerTagMs: 0.004, // k
  overheadMs: 2.0
};

// coverage: 1 - e^{-λN}
function coverage(N, λ) {
  return 1 - Math.exp(-λ * N);
}

// relevance: 1 - e^{-μN}
function relevance(N, μ) {
  return 1 - Math.exp(-μ * N);
}

// info gain: cov(N) × rel(N) × e^{-φN}
function infoGain(N, λ, μ, φ) {
  return coverage(N, λ) * relevance(N, μ) * Math.exp(-φ * N);
}

// memory: N × d × 4 / 1024 (KB)
function memoryKB(N) {
  return N * DEFAULT_PARAMS.embeddingDim * DEFAULT_PARAMS.bytesPerFloat / 1024;
}

// time: k × N × M + overhead (ms)
function processingTimeMs(N) {
  return DEFAULT_PARAMS.timePerItemPerTagMs * N * DEFAULT_PARAMS.dailyPoolSize + DEFAULT_PARAMS.overheadMs;
}

// daily items: M × coverage(N)
function dailyItems(N) {
  return Math.round(DEFAULT_PARAMS.dailyPoolSize * coverage(N, effectiveLambda()));
}
```

### 5.2 雷达图五维度

| 维度 | 值域 | 计算公式 | 物理意义 |
|------|------|---------|---------|
| 覆盖率 | 0-100% | `1 - e^{-λN}` | 每日内容池中你感兴趣的比例 |
| 信息增益 | 0-1 bits | `cov × rel × e^{-φN}` | 每条推荐的 "新鲜信息密度" |
| 每日推荐 | 0-M 条 | `M × cov(N)` | 实际每天推给你看的条数 |
| 内存 | 0-100 KB | `N × d × 4 / 1024` | 兴趣向量占用的 RAM |
| 处理时间 | 0-50 ms | `k × N × M + overhead` | 推荐计算的延迟 |

### 5.3 用户交互

```
用户 hover 标签 "+多模态" 时：
  N: 10 → 11
  覆盖率: 49.3% → 53.2% (+3.9%)
  信息增益: 0.189 → 0.197 (+0.008 bits)
  每日推荐: 74 → 80 (+6 条)
  内存: 10KB → 11KB (+1KB)
  时间: 8ms → 8.6ms (+0.6ms)

雷达图实时更新，所有公式在浏览器端计算（JS < 1ms）
```

---

## 6. 每日推送管道

### 6.1 时间线

```
05:00 — Cron 触发
05:00-05:02 — 爬虫运行（Baidu 等平台）
05:02-05:03 — Embedding 编码 + 评分（~150 条）
05:03-05:04 — LLM 摘要生成（DeepSeek Flash）
05:04-05:05 — Telegram 推送
```

一次运行总耗时 < 5 分钟。成本：~$0.01（DeepSeek Flash 一次调用）。

### 6.2 推送格式

```
🌅 每日情报 | 2026-05-15 早上
━━━━━━━━━━━━━━━━━━━━━━━━

🔥 你最可能感兴趣的（评分 > 0.6）:
  1. 特朗普访华 — 7.8M 热度 🔺
  2. 中国30万亿元存款第一城诞生 — 7.7M
  3. 刚刚并网发电的金川水电站有多硬核 — 7.6M

📊 同领域关注（评分 0.4-0.6）:
  4. 网警依法打击"湖北人造大米"谣言 — 7.3M
  5. 自助餐加了"饱腹剂"？记者调查 — 7.2M

💡 AI 总结：
  今天科技/政策相关热点占 40%，其中 AI 产业政策尤为密集。
  建议重点关注：XXX（基于你的兴趣趋势分析）

━━━━━━━━━━━━━━━━━━━━━━━━
  👍 有用  |  👎 不感兴趣
```

### 6.3 LLM 摘要 Prompt

```
你是一个每日情报编辑。以下是从百度热搜抓取的 {N} 条内容，
用户的主要兴趣方向是：{兴趣摘要}

请做三件事：
1. 从 {N} 条中选出用户最可能感兴趣的 top 10
2. 为每一条写一句为什么用户会感兴趣（基于其兴趣）
3. 写一段 2-3 句的总体趋势分析

输出格式：
## Top 3 （极高相关）
- [标题]：[为什么会感兴趣]
## 其他关注
- [标题]：[为什么]
## 趋势分析
[2-3 句]
```

---

## 7. 反馈学习循环

### 7.1 👍/👎 反馈处理

```python
def apply_feedback(profile: dict, item_title: str, action: str) -> dict:
    """
    用户反馈 → 更新兴趣权重。

    公式：
    如果 👍: w_i_new = w_i × (1 + δ)   (δ = 0.05)
    如果 👎: w_i_new = w_i × (1 - δ)

    同时更新 matching topic 的 embedding（向 item 方向微调）。
    """
    δ = 0.05

    # 找到匹配度最高的 topic
    item_embedding = model.encode(item_title)
    best_topic = max(profile["topics"],
        key=lambda t: cosine_similarity(t["embedding"], item_embedding))

    # 更新权重
    if action == "like":
        best_topic["weight"] *= (1 + δ)
    elif action == "dislike":
        best_topic["weight"] *= (1 - δ)

    # 裁剪权重范围
    best_topic["weight"] = max(0.1, min(3.0, best_topic["weight"]))

    # 更新 embedding（向 item 靠近/远离）
    η = 0.02  # 学习率
    direction = 1 if action == "like" else -1
    for i in range(len(best_topic["embedding"])):
        best_topic["embedding"][i] += direction * η * (item_embedding[i] - best_topic["embedding"][i])

    # 记录历史
    profile["history"].append({
        "item": item_title,
        "action": action,
        "topic_id": best_topic["tag_id"],
        "timestamp": timestamp_ms()
    })

    # 保存
    save_profile(profile)
    return profile
```

### 7.2 学习速率

```
每次 👍/👎: 权重 ±5%
每天（2 次推送 × 3 次反馈）= 6 次反馈
每周 ≈ 42 次反馈
一个月 ≈ 180 次反馈

权重收敛到稳定值 ≈ 30-45 天（200+ 次反馈后）
```

---

## 8. 文件结构与 API

### 8.1 文件结构

```
/Volumes/Lab/Aether/swarm/
├── intelligence/                   ← 每日情报系统核心
│   ├── __init__.py
│   ├── interest_engine.py         ← 兴趣向量 & 评分 (公式4)
│   ├── daily_briefing.py          ← 每日管道 (6.1)
│   ├── feedback.py                ← 反馈学习 (7.1)
│   ├── predictor.py               ← 数学预测模型 (公式1-7)
│   ├── tag_tree.py                ← 标签树加载 & 交互 (3.3)
│   ├── tag_tree/                  ← 标签树数据 (3.2)
│   │   ├── root.json              ← 10 个一阶标签
│   │   ├── ai-ml.json
│   │   ├── design-tools.json
│   │   └── ...
│   ├── onboarding.py              ← 冷启动流程 (3.4)
│   └── profile.json               ← 运行时兴趣配置 (4.1)
├── dashboard/
│   ├── hierarchy.html             ← 已有层级编辑器
│   └── interests.html             ← 兴趣雷达图 + 标签选择 UI
├── scripts/
│   ├── run_daily_briefing.py      ← cron 入口
│   └── register_intel_cron.sh     ← 注册 5:30am/pm
└── docs/
    └── daily-intelligence-design.md   ← 本文档
```

### 8.2 API 端点（新增到 orchestrator.py）

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/intel/profile` | GET | 获取当前兴趣配置 |
| `/api/intel/tags/root` | GET | 获取 10 个一阶标签 |
| `/api/intel/tags/{tag_id}` | GET | 展开标签的子标签 |
| `/api/intel/onboarding/confirm` | POST | 确认冷启动选择 |
| `/api/intel/predict?N={n}` | GET | 获取 N 个标签的预测数据 |
| `/api/intel/feedback` | POST | 提交 👍/👎 反馈 |
| `/api/intel/recommend` | GET | 获取今日推荐（触发管道）|

---

## 9. 部署与 Cron

### 9.1 注册每日情报 cron

```bash
#!/bin/bash
python3 scripts/register_intel_cron.sh
```

```bash
hermes cron create \
  --name "daily-briefing-am" \
  --schedule "30 5 * * *" \
  --prompt "python3 /Volumes/Lab/Aether/swarm/scripts/run_daily_briefing.py --time=am" \
  --deliver telegram

hermes cron create \
  --name "daily-briefing-pm" \
  --schedule "30 17 * * *" \
  --prompt "python3 /Volumes/Lab/Aether/swarm/scripts/run_daily_briefing.py --time=pm" \
  --deliver telegram
```

### 9.2 一键启动脚本

```bash
# 完整启动序列
python3 -m intelligence.onboarding    # 冷启动初始化（首次）
python3 -m intelligence.daily_briefing # 手动跑一次每日简报（测试）
bash scripts/register_intel_cron.sh   # 注册定时任务
```

---

## 10. 附录：参数表与默认值

### 10.1 完整参数表

| 参数 | 符号 | 默认值 | 调节方式 | 影响 |
|------|------|--------|---------|------|
| 每日内容池大小 | M | 150 | 新增平台 | 线性增加推荐量 |
| 平均匹配率 | p | 0.08 | 经验校准 | 指数影响覆盖率 |
| 标签重叠系数 | overlap | 0.15 | 手动调整 | 0=完全独立，1=完全重复 |
| 相关度增长速率 | μ | 0.10 | 模型选择 | 越大相关度增长越快 |
| 疲劳系数 | φ | 0.05 | 手动调整 | 越大信息增益衰减越快 |
| 嵌入向量维度 | d | 256 | 模型选择 | 128 更快但精度略低 |
| 学习率 | η | 0.02 | 手动调整 | 越大反馈更新越快 |
| 权重调整 | δ | 0.05 | 手动调整 | 越大单次反馈影响越大 |

### 10.2 不同场景的推荐参数

| 场景 | N | M | 覆盖率 | 信息增益 | 推荐理由 |
|------|---|----|--------|---------|---------|
| 初学者 | 5-8 | 150 | 29-42% | 0.09-0.15 | 快速上手，不 overload |
| 标准推荐 | 10-15 | 150 | 49-64% | 0.19-0.24 | 最优性价比 |
| 深度探索 | 15-20 | 150 | 64-74% | 0.24-0.24 | 信息增益峰值后趋于平缓 |
| 全量覆盖 | 20-30 | 150 | 74-87% | 0.24-0.18 | 边际收益递减明显 |

### 10.3 技术约束

| 维度 | 上限 | 原因 |
|------|------|------|
| 标签数 N | ≤ 50 | 超过后处理时间 > 30ms，用户体验劣化 |
| 每日内容池 M | ≤ 500 | Camofox 单次 API 调用超时限制 |
| 向量维度 d | 128-768 | bge-small (256) / bge-base (768) |
| 模型大小 | < 500MB | bge-small ≈ 133MB，bge-base ≈ 440MB |
