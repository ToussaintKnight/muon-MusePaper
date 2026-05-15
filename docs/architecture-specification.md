# MUON 每日情报系统 — 分层架构规格说明书

## Layer-by-Layer Specification
> Version: 1.0 | Date: 2026-05-14 | Author: Pixie (CTO)

---

## 目录

- [L0: 实体定义与数据结构](#l0-实体定义与数据结构)
- [L1: 数据采集层](#l1-数据采集层)
- [L2: 向量编码层](#l2-向量编码层)
- [L3: 兴趣匹配层](#l3-兴趣匹配层)
- [L4: 预测仪表盘层](#l4-预测仪表盘层)
- [L5: 冷启动交互层](#l5-冷启动交互层)
- [L6: 反馈学习层](#l6-反馈学习层)
- [L7: LLM 摘要层](#l7-llm-摘要层)
- [L8: 推送层](#l8-推送层)
- [L9: 调度层 (Cron)](#l9-调度层-cron)
- [附录: 完整数据流追踪](#附录-完整数据流追踪)

---

## L0: 实体定义与数据结构

### L0.1 兴趣配置 schema (`profile.json`)

```typescript
interface Profile {
  version: 1;
  embedding_model: "BAAI/bge-small-zh-v1.5";
  base_embedding: Float32Array(256);  // aggregated interest vector

  selected_tags: TagID[];             // flat list of all selected tag IDs
  topics: Topic[];                    // per-tag configurations

  history: FeedbackEvent[];           // feedback log (append-only)

  created_at: Unix_ms;
  last_updated: Unix_ms;
}

interface Topic {
  tag_id: TagID;                      // e.g. "ai-ml-llm"
  name: string;                       // "LLM"
  path: string;                       // "AI/ML → LLM"
  keywords: string[];                 // ["LLM", "GPT", "transformer"]
  weight: float;                      // [0.1, 3.0], default 1.0
  embedding: Float32Array(256);       // topic-specific embedding
}

interface FeedbackEvent {
  item_title: string;
  action: "like" | "dislike";
  topic_id: TagID;
  score_before: float;
  score_after: float;
  timestamp: Unix_ms;
}
```

### L0.2 标签树节点 schema (`tag_tree/*.json`)

```typescript
interface TagNode {
  id: TagID;                          // unique identifier, e.g. "ai-ml"
  name: string;                       // display name, e.g. "AI/ML"
  emoji?: string;                     // 🤖
  keywords: string[];                 // search keywords for matching
  children: TagNode[];                // recursive subtree (depth ≤ 3)
}

// Root file: tag_tree/root.json
//   ├── children: TagNode[10]         (10 first-level tags)
// Child file: tag_tree/ai-ml.json
//   └── children: TagNode[~8]         (8 sub-tags of AI/ML)
```

### L0.3 内容项 schema (`hotlist_scraper.py` output)

```typescript
interface ContentItem {
  rank: number;
  title: string;
  heat_score: number;
  description: string;
  platform: "baidu" | "weibo" | "bilibili";
  url?: string;
  embedding?: Float32Array(256);      // <-- filled by L2
  score?: float;                       // <-- filled by L3
}
```

### L0.4 推荐结果 schema

```typescript
interface Recommendation {
  timestamp: Unix_ms;
  items: ScoredItem[];
  metadata: {
    n_tags: number;                   // N at time of run
    pool_size: number;                // M
    coverage_pct: float;
    avg_score: float;
    top1_score: float;
    total_time_ms: float;
  };
}

interface ScoredItem extends ContentItem {
  score: float;                        // [0, 1]
  matched_topics: MatchedTopic[];      // which topics contributed
}

interface MatchedTopic {
  topic_id: TagID;
  topic_name: string;
  cosine: float;                      // raw cosine similarity
  weighted_contribution: float;       // weight × cosine
}
```

### L0.5 预测模型输出 schema

```typescript
interface RadarDataPoint {
  N: number;
  coverage_pct: float;
  avg_relevance: float;
  info_gain_bits: float;
  daily_items: number;
  memory_kb: float;
  processing_time_ms: float;
  marginal_gain_pct: float;
}
```

---

## L1: 数据采集层

### 职责

从各中文平台爬取当日热搜/热榜内容，产出原始 `ContentItem[]`。

### 文件

| 文件 | 职责 | 输出 |
|------|------|------|
| `hotlist_scraper.py` | 百度热搜爬虫（Camofox API） | `ContentItem[50]` |
| `scrapers/weibo.py`（未来） | 微博热搜爬虫 | `ContentItem[50]` |
| `scrapers/bilibili.py`（未来） | B站热搜爬虫 | `ContentItem[50]` |

### 函数签名

```python
def scrape_baidu() -> dict:
    """
    Returns: {
        "success": bool,
        "platform": "baidu",
        "timestamp": ISO_string,
        "count": int,
        "items": [{
            "rank": int,
            "title": str,
            "heat_score": int,
            "description": str,
            "platform": "baidu"
        }]
    }
    """
```

### 数据流

```
Camofox Browser (port 9377)
  → POST /tabs {url, userId, sessionKey}
  → POST /tabs/{tabId}/scroll
  → GET  /tabs/{tabId}/snapshot?full=true
  → DELETE /tabs/{tabId}
  → Parse accessibility tree → extract items
```

**Camofox API 调用次数：** 4 次/平台/轮次（create tab, scroll, snapshot, close tab）
**单次耗时：** ~3 秒/平台

### 错误处理

| 错误 | 行为 |
|------|------|
| Camofox 无响应（超时 20s） | 跳过该平台，日志记录 |
| Snapshot 返回空 | 重试 1 次，仍空则跳过 |
| 解析到 0 条数据 | 返回空 items 数组 |

---

## L2: 向量编码层

### 职责

将原始文本内容编码为 256 维 embedding 向量。

### 文件

`intelligence/interest_engine.py`

### 模型

| 属性 | 值 |
|------|-----|
| 模型 | `BAAI/bge-small-zh-v1.5` |
| 维度 | 256 |
| 本地大小 | ~133 MB |
| 推理设备 | CPU (M-series Neural Engine) |
| 单条编码时间 | ~5ms |
| 首次加载 | 下载模型（~30s, 一次性） |

### 函数签名

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# Module-level singleton (load once)
_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (singleton pattern)."""
    global _model
    if _model is None:
        _model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    return _model

def encode_text(text: str) -> np.ndarray:
    """
    Encode a single text string to a 256-dim vector.
    Returns: Float32Array(256)
    """
    return get_model().encode(text)

def encode_items(items: list[ContentItem]) -> list[ContentItem]:
    """
    Batch encode all items. Mutates items in-place, adding .embedding.
    Returns: same list with embeddings filled.
    """
    model = get_model()
    texts = [f"{i['title']}. {i.get('description', '')}" for i in items]
    embeddings = model.encode(texts, show_progress_bar=False)
    for i, emb in zip(items, embeddings):
        i['embedding'] = emb.tolist()
    return items
```

### 数据流

```
hotlist_scraper output (50 items, raw text)
  → encode_items()
  → 50 items with .embedding filled
  → Pass to L3
```

### 错误处理

| 条件 | 行为 |
|------|------|
| 模型文件未下载 | 首次运行时自动下载（~30s） |
| 模型加载失败 | fallback 到关键词匹配（Level 1） |
| 内存不足（< 500MB 空闲） | 打印警告，继续使用 CPU 慢速路径 |

---

## L3: 兴趣匹配层

### 职责

将编码后的内容与用户兴趣配置对比，计算每条内容的匹配度评分。

### 文件

`intelligence/interest_engine.py`（同上文件，不同函数）

### 评分公式

```
score(item) = α · cos(base_embedding, item_embedding) 
            + (1-α) · max_i [ weight_i · cos(topic_i, item_embedding) ]

where α = 0.3 (base vs topics blend ratio)
      weight_i ∈ [0.1, 3.0]
```

### 函数签名

```python
def score_item(item: ContentItem, profile: Profile) -> ScoredItem:
    """
    Score a single content item against the user's interest profile.
    
    Returns: ScoredItem with score and matched_topics filled.
    """
    item_emb = np.array(item['embedding'])
    base_score = cosine_similarity(profile['base_embedding'], item_emb)
    
    topic_scores = []
    for topic in profile['topics']:
        t_emb = np.array(topic['embedding'])
        cos_sim = cosine_similarity(t_emb, item_emb)
        weighted = topic['weight'] * cos_sim
        topic_scores.append({
            'topic_id': topic['tag_id'],
            'topic_name': topic['name'],
            'cosine': round(float(cos_sim), 4),
            'weighted_contribution': round(float(weighted), 4)
        })
    
    max_topic = max(topic_scores, key=lambda x: x['weighted_contribution'])
    final_score = 0.3 * base_score + 0.7 * max_topic['weighted_contribution']
    
    return {
        **item,
        'score': round(float(final_score), 4),
        'matched_topics': sorted(topic_scores, key=lambda x: -x['weighted_contribution'])[:3]
    }

def rank_items(items: list[ContentItem], profile: Profile) -> list[ScoredItem]:
    """
    Score and rank all items by descending score.
    Returns: sorted ScoredItem list.
    """
    scored = [score_item(item, profile) for item in items]
    scored.sort(key=lambda x: -x['score'])
    return scored
```

### 排序后处理

```python
def filter_recommendations(scored: list[ScoredItem], 
                           min_score: float = 0.15,
                           max_items: int = 20) -> list[ScoredItem]:
    """
    Apply quality filters:
    1. Remove items below min_score
    2. Diversity: no more than 3 items from the same matched topic
    3. Cap at max_items
    """
```

### 数据流

```
profile.json (interest profile)
  │
  ▼
L2 output: 50 encoded items
  │
  ▼
score_item() × 50  ──→  each item gets score + matched_topics
  │
  ▼
rank_items()        ──→  sorted by score descending
  │
  ▼
filter_recommendations()  ──→  top 20 items
  │
  ▼
Pass to L7 (LLM summary)
```

### 时间复杂度

```
O(N × M) = O(10 × 150) = 1,500 cosine similarity ops
Each cosine: 256 dims = 256 FLOPs
Total: ~384K FLOPs
Estimated wall time (MacBook M2): < 5ms
```

---

## L4: 预测仪表盘层

### 职责

给定标签数 N，预测 5 个维度的数值，用于实时雷达图展示。

### 文件

`intelligence/predictor.py`

### 数学模型

| 维度 | 公式 | 变量定义 |
|------|------|---------|
| 覆盖率 | `C(N) = 1 - e^{-λN}` | `λ = p(1-α)`, `p=0.08`, `α=0.15` |
| 边际增益 | `ΔC(N) = λe^{-λN}` | 同上 |
| 相关度 | `R(N) = 1 - e^{-μN}` | `μ = 0.10` |
| 信息增益 | `G(N) = C(N) · R(N) · e^{-φN}` | `φ = 0.05` |
| 每日推荐数 | `I(N) = M · C(N)` | `M = 150` |
| 内存 | `M_mem(N) = N · d · 4` bytes | `d = 256` |
| 处理时间 | `T(N) = k · N · M + t₀` | `k=0.004ms`, `t₀=2.0ms` |

### 函数签名

```python
def radar_data(N: int, params?: Params) -> RadarDataPoint:
    """
    Pure function: given N, return all 5 dimensions.
    No state, no I/O, no randomness.
    Can be called 1000x/sec in a browser.
    """

def radar_series(max_N: int = 30, params?: Params) -> list[RadarDataPoint]:
    """N=1..max_N, for line charts."""

def suggest_optimal_N(params?: Params) -> dict:
    """
    Returns:
      info_gain_peak_N: int       (where G(N) is maximized)
      sweet_spot_N: int           (where marginal gain > threshold)
      coverage_60_N: int          (minimum N for 60% coverage)
      recommendation: string
    """
```

### 浏览器端 JS 版本

```javascript
// dashboard/interests.html — 嵌入式 JS 副本
const PREDICTOR = {
  coverage(N) { return 1 - Math.exp(-0.068 * N); },
  relevance(N) { return 1 - Math.exp(-0.10 * N); },
  infoGain(N) { return this.coverage(N) * this.relevance(N) * Math.exp(-0.05 * N); },
  memoryKB(N) { return N * 256 * 4 / 1024; },
  timeMs(N) { return 0.004 * N * 150 + 2.0; },
  dailyItems(N) { return Math.round(150 * this.coverage(N)); },
  marginal(N) { return 0.068 * Math.exp(-0.068 * N) * 100; },

  radarData(N) {
    return {
      coverage_pct: +(this.coverage(N) * 100).toFixed(1),
      info_gain_bits: +this.infoGain(N).toFixed(3),
      daily_items: this.dailyItems(N),
      memory_kb: +this.memoryKB(N).toFixed(1),
      processing_time_ms: +this.timeMs(N).toFixed(1),
      marginal_gain_pct: +this.marginal(N).toFixed(2),
    };
  }
};
```

### API 端点

```
GET /api/intel/predict?N=15
→ { "coverage_pct": 63.9, "info_gain_bits": 0.235, ... }
```

---

## L5: 冷启动交互层

### 职责

新用户的兴趣发现流程：从 10 个通用标签开始，逐层展开，选择兴趣。

### 状态机

```
IDLE ──→ ONBOARDING_STEP1 (显示 10 个根标签)
                │
                ├── select ≥3 tags ──→ ONBOARDING_STEP2
                │                              │
                │               ┌── click tag ──┴── show 10 sub-tags
                │               │
                │               └── confirm() ──→ PROFILE_GENERATED
                │
                └── cancel() ──→ IDLE

PROFILE_GENERATED ──→ save profile.json
                    ──→ enter daily loop
                    ──→ can be re-triggered manually any time
```

### 文件

`intelligence/onboarding.py`

### 函数签名

```python
class OnboardingFlow:
    """
    Stateful interaction manager for the cold-start interest discovery.
    Each API call mutates internal state (session-based).
    """

    def __init__(self, tag_tree: TagTree):
        self.tag_tree = tag_tree
        self.selected: set[TagID] = set()    # currently selected tags
        self.expanded: set[TagID] = set()    # expanded parent tags

    def get_root_tags(self) -> list[dict]:
        """Returns the 10 first-level tags with metadata."""
        ...

    def expand_tag(self, tag_id: TagID) -> list[dict]:
        """Returns children of tag_id. Marks parent as expanded."""
        ...

    def toggle_tag(self, tag_id: TagID):
        """Add/remove tag from selection. Minimum 3."""
        ...

    def confirm(self) -> Profile:
        """Generate initial profile from selected tags → save."""
        if len(self.selected) < 3:
            raise ValueError("Minimum 3 tags required")
        profile = self._generate_profile()
        save_profile(profile)
        return profile

    def _generate_profile(self) -> Profile:
        """
        1. Collect all keywords from selected tags
        2. Build path-based descriptions
        3. Encode with embedding model
        4. Construct Profile object
        """
```

### 标签树数据文件

```
intelligence/tag_tree/
├── root.json                    # 10 first-level tags
│   └── children: [
│       { id: "ai-ml",      name: "AI/ML",    keywords: ["AI","ML"], ... },
│       { id: "design",     name: "设计工具",  keywords: ["Figma","UI"], ... },
│       ...
│   ]
├── ai-ml.json                  # children of ai-ml (~8 sub-tags)
├── design.json                 # children of design (~8 sub-tags)
├── startup.json
├── academic.json
├── music.json
├── gaming.json
├── finance.json
├── tech-news.json
├── open-source.json
└── ai-art.json
```

### API 端点

```
GET  /api/intel/tags/root          → 10 root tags
GET  /api/intel/tags/{tag_id}      → children of tag_id
POST /api/intel/onboarding/toggle  → { tag_id: "ai-ml" }
POST /api/intel/onboarding/confirm → { profile: Profile }
```

---

## L6: 反馈学习层

### 职责

接收 👍/👎 反馈，更新对应 topic 的权重和 embedding。

### 文件

`intelligence/feedback.py`

### 更新公式

```
Like:   w_new = w_old × (1 + δ)     δ = 0.05
Unlike: w_new = w_old × (1 - δ)     δ = 0.05
Clip:   w_new = clamp(w_new, 0.1, 3.0)

Embedding update (soft):
  direction = +1 if like, -1 if dislike
  emb_new[i] = emb_old[i] + direction × η × (item_emb[i] - emb_old[i])
  η = 0.02 (learning rate)
```

### 函数签名

```python
FEEDBACK_DELTA = 0.05      # δ: weight adjustment per feedback
LEARNING_RATE = 0.02       # η: embedding adjustment step
WEIGHT_MIN = 0.1           # minimum weight
WEIGHT_MAX = 3.0           # maximum weight

def apply_feedback(profile: Profile, item_title: str, action: str) -> Profile:
    """
    1. Encode item_title with embedding model
    2. Find best-matching topic (highest cosine)
    3. Update topic weight: w *= (1 ± δ)
    4. Update topic embedding: emb += ±η · (item_emb - emb)
    5. Log to history
    6. Save profile.json
    """
```

### 状态转移

```
用户看到推荐 → 点 👍 → apply_feedback("like")
                      → 该 topic 权重 +5%
                      → embedding 向该内容靠近 2%
                      
用户看到推荐 → 点 👎 → apply_feedback("dislike")
                      → 该 topic 权重 -5%
                      → embedding 远离该内容 2%
```

### 收敛分析

```
Single topic, starting weight = 1.0:

Like sequence:  1.0 → 1.05 → 1.10 → 1.16 → 1.22 → 1.28 → ...
After 24 likes: 1.0 × 1.05^24 = 3.0 (hits ceiling)
After 24 dislikes: 1.0 × 0.95^24 = 0.29

Typical convergence: 100-200 feedback events (~15-30 days)
Stable weights: ±0.1 around equilibrium after ~3 months
```

---

## L7: LLM 摘要层

### 职责

将评分后的 top 推荐列表输入 LLM（DeepSeek Flash），生成结构化摘要。

### 文件

`intelligence/daily_briefing.py`（与 L8 同文件）

### Prompt 模板

```
你是一个每日科技情报编辑。用户的主要兴趣领域是：
{兴趣摘要（来自 profile JSON 中的 topics 路径列表）}

以下是今天从 {平台列表} 抓取的热搜内容，已按相关度排序。
Top 3（评分 > 0.6）：
{items[0:3]}

同领域关注（评分 0.4-0.6）：
{items[3:10]}

请生成一份简报，格式如下：

## 今日重点关注（Top 3）
每条：[标题] — [为什么用户会感兴趣，1 句话]

## 趋势分析
2-3 句话归纳今天值得注意的整体趋势

## 后续关注
1 个建议未来几天观察的方向

注意：每条内容需附 [平台: 热度分数] 标签。
```

### 成本

```
每次调用：~500 tokens input + ~200 tokens output
DeepSeek Flash 定价：$0.01/1K input, $0.01/1K output
单次成本：~$0.007
每日 2 次：~$0.014
月度：~$0.42
```

---

## L8: 推送层

### 职责

将 LLM 生成的摘要通过 Telegram 推送到 Sir 的聊天窗口。

### 文件

`intelligence/daily_briefing.py`

### 函数签名

```python
def push_telegram(summary: str, target: str = "telegram") -> bool:
    """
    Send summary text via Hermes send_message.
    target: "telegram" (Sir's home channel)
    
    Returns: True if delivered successfully
    """
    from hermes_tools import send_message  # Hermes built-in
    result = send_message(
        target=target,
        message=summary
    )
    return result.get("success", False)
```

### 推送格式

```
🌅 每日情报 | 2026-05-15 am
━━━━━━━━━━━━━━━━━━━━━━━━

🔥 今日重点关注
1. {标题} — {理由} [百度: 780万热度]
2. ...
3. ...

📊 趋势分析
{2-3 句}

👀 后续关注
{1 个方向}

━━━━━━━━━━━━━━━━━━━━━━━━
  👍 有用 | 👎 不感兴趣
```

---

## L9: 调度层 (Cron)

### 职责

按预设时间表触发每日情报管道。

### 文件

`scripts/run_daily_briefing.py`
`scripts/register_intel_cron.sh`

### 入口脚本

```python
# scripts/run_daily_briefing.py

import sys, json, time
sys.path.insert(0, "/Volumes/Lab/Aether/swarm")

from intelligence.daily_briefing import run_daily_briefing
from intelligence.predictor import radar_data, suggest_optimal_N

def main():
    time_flag = sys.argv[1] if len(sys.argv) > 1 else "am"
    print(f"[briefing] Starting {time_flag} run at {time.time():.0f}")
    
    start = time.time()
    result = run_daily_briefing()
    elapsed = time.time() - start
    
    print(f"[briefing] Done in {elapsed:.1f}s")
    print(f"[briefing] {len(result.get('items', []))} items scored")
    print(f"[briefing] Top score: {result['items'][0]['score'] if result.get('items') else 'N/A'}")

if __name__ == "__main__":
    main()
```

### Cron 注册

```bash
# 5:30am (UTC+8) — morning briefing
# 17:30 (UTC+8) — evening briefing

hermes cron create \
  --name "daily-briefing-am" \
  --schedule "30 5 * * *" \
  --prompt "Run daily briefing (AM): cd /Volumes/Lab/Aether/swarm && python3 scripts/run_daily_briefing.py --time=am" \
  --deliver local

hermes cron create \
  --name "daily-briefing-pm" \
  --schedule "30 17 * * *" \
  --prompt "Run daily briefing (PM): cd /Volumes/Lab/Aether/swarm && python3 scripts/run_daily_briefing.py --time=pm" \
  --deliver local
```

### 完整的单次运行时间线

```
t=0:00    Cron fired
t=0:01    hotlist_scraper.py: Camofox create tab
t=0:02    Camofox scroll + snapshot + parse (50 items)
t=0:03    encode_items(): 50 embeddings (batch ~250ms)
t=0:04    rank_items(): 1,500 cosine comparisons (<5ms)
t=0:05    LLM summary prompt: ~500 tokens in
t=0:06    LLM response: ~200 tokens out
t=0:07    push_telegram(): message sent
t=0:08    Complete

Total: ~8 seconds
```

---

## 附录：完整数据流追踪

### 每日推送路径

```
[L9] Cron: 5:30am fired
  → [L1] hotlist_scraper.py
    → Camofox API (4 calls)
    → 50 ContentItems (raw text)
  → [L2] encode_items()
    → sentence-transformers (batch)
    → 50 items with embeddings
  → [L3] rank_items(50 items, profile.json)
    → 1,500 cosine similarity ops
    → sorted ScoredItems
  → [L3] filter_recommendations()
    → top 20 items
  → [L7] LLM prompt generation
    → DeepSeek Flash (500 token input)
    → structured summary
  → [L8] push_telegram()
    → Hermes send_message
    → Sir's Telegram inbox
```

### 冷启动路径

```
User requests POST /api/intel/onboarding/confirm
  → [L5] OnboardingFlow.confirm()
    → collect selected tag IDs
    → collect keywords from tag_tree
    → encode profile_text → base_embedding
    → encode each topic path → topic embeddings
    → construct Profile object
    → save to profile.json
  → Response: { profile: Profile }
```

### 反馈路径

```
User clicks 👍 on a recommendation
  → POST /api/intel/feedback { item_title, action: "like" }
  → [L6] apply_feedback(profile, item_title, "like")
    → encode item_title
    → find best-matching topic
    → weight ×= 1.05
    → embedding += 0.02 × (item_emb - topic_emb)
    → append to history
    → save profile.json
  → Response: { updated_topic, new_weight, new_score_stdev }
```
