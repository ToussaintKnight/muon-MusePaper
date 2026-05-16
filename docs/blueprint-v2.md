# 🎯 Muse — Best Design Blueprint v2.0

> **Synthesis of all design iterations** | Date: 2026-05-16 | Status: Ready for Review

---

## Executive Summary

After 4 rounds of deep architectural discussions, the design has evolved from a complex 9-layer pipeline into a **unified closed-loop system** centered around a single concept:

```
Interest Vector → Search → Kanban → Save → Updated Vector → Next Search
```

This blueprint incorporates:
- ✅ **4-source data fusion** (NewsNow domestic + RSSHub international + Native APIs + Camofox fallback)
- ✅ **Vector-to-query decoder** (interest embedding → tag tree cosine → search queries)
- ✅ **Closed-loop learning** (fast latent loop + slow language loop + human override)
- ✅ **Zero cold start** (first drag creates the vector)
- ✅ **Business value** (Tools column → Notion Toolbox)
- ✅ **Zero LLM cost** (no summarization, no generation)

---

## 1. Design Philosophy

### Core Principles (from chat-history discussions)

| Principle | Rationale | Origin |
|-----------|-----------|--------|
| **One Loop** | Complexity kills execution. One clear loop beats 9 layers. | `design.md` simplification |
| **Vector is King** | 256-dim embedding encodes everything. No keyword lists to maintain. | Sir's core question on latent space |
| **Multi-Source Fusion** | NewsNow for China, RSSHub for global, Camofox for gaps. No single point of failure. | TrendRadar analysis + GitHub research |
| **Drag = Signal** | 4 bucket types (Tools/Interested/Not-Interested/Ignored) = rich gradient. Binary 👍/👎 is too poor. | Kanban design insight |
| **Batch Update** | One Save = one vector update. More stable than incremental per-card. | EMA convergence analysis |

### What We Deliberately Removed

- ❌ **9-layer architecture** — Over-engineered for a single user
- ❌ **Tag tree onboarding** — Creates friction; Kanban drag is the real onboarding
- ❌ **LLM summarization** — $0.42/month for text Sir won't read; he drags cards instead
- ❌ **Per-item 👍/👎** — Too coarse; Kanban columns give directional signal
- ❌ **QMD/GitNexus integration** — Different embedding spaces, wrong abstraction

---

## 2. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DAILY CYCLE (5:30 AM)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SOURCE LAYER (4 Engines)                            │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│  NewsNow API    │  RSSHub Docker  │  Native APIs    │   Camofox Browser     │
│  (Domestic)     │  (International)│  (Zero Cost)    │   (Fallback)          │
├─────────────────┼─────────────────┼─────────────────┼───────────────────────┤
│ • weibo         │ • hackernews    │ • reddit.json   │ • Any search URL      │
│ • baidu         │ • github/trend  │ • hn.firebase   │ • JS-rendered sites   │
│ • zhihu         │ • producthunt   │                 │ • Paywalled content   │
│ • bilibili      │ • techcrunch    │                 │                       │
│ • 36kr          │ • google/news   │                 │                       │
│ • +34 more      │ • +1000 routes  │                 │                       │
├─────────────────┼─────────────────┼─────────────────┼───────────────────────┤
│ ~600-1320 items │ ~200-500 items  │ ~100-200 items  │ ~50-100 items         │
│ refresh: 2-10min│ refresh: 15min  │ refresh: realtime│ refresh: on-demand   │
└─────────────────┴─────────────────┴─────────────────┴───────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      UNIFIED POOL (Merge + Deduplicate)                     │
│                     ~1000-2000 raw items → unique set                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EMBEDDING LAYER (bge-small-zh)                         │
│                                                                             │
│   Title + Description ──→ model.encode() ──→ 256-dim Float32 vector       │
│                                                                             │
│   Throughput: ~500 items/sec (M2, CPU)                                     │
│   Total time: ~2-4 seconds for 2000 items                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RANKING LAYER (Vector Cosine)                          │
│                                                                             │
│   score(item) = cosine(interest_vector, item_embedding)                     │
│                                                                             │
│   + Diversity penalty: max 3 items per source                               │
│   + Freshness boost: items < 2h get +10%                                    │
│   + Source rotation: ensure all 4 sources represented                       │
│                                                                             │
│   Output: top 50 scored items                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KANBAN UI (Web / Telegram)                          │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ 🛠️ Tools     │  │ 👀 Interested│  │ ❌ Not Int.  │                      │
│  │  (actionable)│  │  (learn +)   │  │  (learn -)   │                      │
│  │──────────────│  │──────────────│  │──────────────│                      │
│  │  Card A      │  │  Card B      │  │  Card D      │                      │
│  │  Card C      │  │              │  │              │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                             │
│  [Not moved cards = slight decay signal]                                    │
│  [Press SAVE → triggers batch update]                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SAVE HANDLER (Synchronous)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. TOOLS → Notion Toolbox API                                              │
│     • Create database entry: Title, URL, Source, Tags, Status="To Evaluate" │
│                                                                             │
│  2. EMBEDDING UPDATE (Fast Loop — Latent Space)                             │
│     • For each bucket, apply EMA update to interest_vector:                 │
│       Tools:       v += 0.05 × (item_emb - v)                               │
│       Interested:  v += 0.02 × (item_emb - v)                               │
│       Not Int.:    v -= 0.03 × (item_emb - v)                               │
│       Ignored:     weight ×= 0.995 (no vector change)                       │
│     • Normalize to unit length                                              │
│                                                                             │
│  3. KEYWORD WEIGHT LOG (Slow Loop — Language Space)                         │
│     • Append to history: {item, bucket, timestamp, top_tag}                 │
│     • Trigger weekly batch re-optimization if history > 50 events           │
│                                                                             │
│  4. PROFILE PERSISTENCE                                                     │
│     • Save profile.json: {vector, history, updated_at}                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │  interest_vector   │
                          │     updated        │
                          └────────────────────┘
                                     │
                                     └────────────────┐
                                                      │
                        ┌─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NEXT CYCLE (tomorrow 5:30 AM)                            │
│                                                                             │
│   interest_vector ──→ vector_to_queries() ──→ 5 search queries             │
│        │                                                                    │
│        └──→ Camofox searches these queries ──→ fresh items                  │
│        └──→ NewsNow/RSSHub/Native APIs ──→ bulk items                       │
│                                                                             │
│   [Loop continues...]                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagram (Detailed)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  NewsNow    │     │   RSSHub    │     │   Native    │     │   Camofox   │
│   Client    │     │   Client    │     │    APIs     │     │   Browser   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │ fetch(id)         │ fetch(route)      │ GET /hot.json     │ create_tab()
       │ ──────────────>   │ ──────────────>   │ ──────────────>   │ ──────────────>
       │                   │                   │                   │
       │ items[]           │ items[]           │ items[]           │ snapshot
       │ <──────────────   │ <──────────────   │ <──────────────   │ <──────────────
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SourceAggregator  │
                    │  • Deduplicate by   │
                    │    title similarity │
                    │  • Normalize schema │
                    │  • Tag with source  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Embedder (bge-small)│
                    │  • Batch encode     │
                    │    2000 titles      │
                    │  • Output: 256-dim  │
                    │    vectors          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    RankerEngine     │
                    │  • cosine(interest, │
                    │    item)            │
                    │  • diversity filter │
                    │  • freshness boost  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Top 50         │
                    │    ScoredItems      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
      │  Web Kanban │  │  Telegram   │  │  Notion     │
      │   (drag)    │  │  (inline)   │  │  (Tools)    │
      └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
             │                │                │
             └────────────────┴────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     SaveHandler     │
                 │  • Update vector    │
                 │  • Sync Notion      │
                 │  • Log history      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     profile.json    │
                 │  {vector, history,  │
                 │   updated_at}       │
                 └─────────────────────┘
```

---

## 4. Class Diagram

```python
# ============================================================
# CORE DOMAIN MODELS
# ============================================================

class NewsItem:
    """Universal content item from any source."""
    + id: str
    + title: str
    + url: str
    + source: str           # "newsnow_weibo", "rsshub_hn", "camofox_baidu"
    + source_type: str      # "newsnow" | "rsshub" | "native" | "camofox"
    + pub_date: datetime
    + heat_score: int
    + extra: dict
    + embedding: np.ndarray | None   # 256-dim, filled by Embedder
    + score: float | None            # filled by Ranker

class UserProfile:
    """Single-user interest profile. Singleton per installation."""
    + version: int = 2
    + embedding_model: str = "BAAI/bge-small-zh-v1.5"
    + interest_vector: np.ndarray    # 256-dim, unit length
    + keyword_weights: dict[str, float]   # Slow loop: keyword → weight
    + history: list[EngagementEvent]
    + created_at: datetime
    + updated_at: datetime
    ---
    + save(path: str)
    + load(path: str) -> UserProfile
    + update_vector(events: list[EngagementEvent])
    + recompute_keyword_weights()

class EngagementEvent:
    """One user action on one item."""
    + item_id: str
    + item_title: str
    + bucket: str           # "tools" | "interested" | "not_interested" | "ignored"
    + item_embedding: np.ndarray
    + timestamp: datetime
    + top_tag: str          # best-matching tag from tag_tree

class TagNode:
    """Node in the interest tag tree."""
    + id: str
    + name: str
    + path: str             # "AI/ML → MLLM"
    + keywords: list[str]
    + children: list[TagNode]
    + embedding: np.ndarray | None   # precomputed

# ============================================================
# SOURCE LAYER (Strategy Pattern)
# ============================================================

abstract class SourceClient:
    """Base class for all content sources."""
    + source_type: str
    ---
    + abstract fetch() -> list[NewsItem]
    + abstract health_check() -> bool

class NewsNowClient(SourceClient):
    """Chinese platform aggregator."""
    + API_BASE: str = "https://newsnow.busiyi.world/api/s"
    + source_ids: list[str]
    + cache_ttl: timedelta
    ---
    + fetch_source(source_id: str) -> list[NewsItem]
    + fetch_all() -> list[NewsItem]

class RSSHubClient(SourceClient):
    """International platform aggregator."""
    + BASE_URL: str = "http://localhost:1200"
    + routes: list[str]
    ---
    + fetch_route(route: str) -> list[NewsItem]
    + fetch_all() -> list[NewsItem]

class NativeAPIClient(SourceClient):
    """Zero-auth APIs (Reddit, HN)."""
    + endpoints: dict[str, str]
    ---
    + fetch_reddit(subreddit: str) -> list[NewsItem]
    + fetch_hackernews() -> list[NewsItem]

class CamofoxClient(SourceClient):
    """Browser-based search for gaps."""
    + CAMOFOX_URL: str = "http://localhost:9377"
    ---
    + search(query: str, platform: str) -> list[NewsItem]
    + create_tab(url: str) -> str     # tab_id
    + get_snapshot(tab_id: str) -> dict
    + close_tab(tab_id: str)

class SourceAggregator:
    """Merges all sources, deduplicates, normalizes."""
    + clients: list[SourceClient]
    + seen_titles: set[str]
    ---
    + fetch_all() -> list[NewsItem]
    + deduplicate(items: list[NewsItem]) -> list[NewsItem]
    + normalize(items: list[NewsItem]) -> list[NewsItem]

# ============================================================
# INTELLIGENCE LAYER
# ============================================================

class Embedder:
    """bge-small-zh singleton."""
    + model: SentenceTransformer | None
    + dim: int = 256
    ---
    + get_model() -> SentenceTransformer    # lazy load
    + encode(text: str) -> np.ndarray
    + encode_batch(texts: list[str]) -> list[np.ndarray]

class RankerEngine:
    """Scores and ranks items against interest vector."""
    + embedder: Embedder
    + diversity_max_per_source: int = 3
    + freshness_boost_hours: int = 2
    ---
    + score_item(item: NewsItem, profile: UserProfile) -> float
    + rank_items(items: list[NewsItem], profile: UserProfile) -> list[NewsItem]
    + apply_diversity(items: list[NewsItem]) -> list[NewsItem]
    + apply_freshness_boost(items: list[NewsItem]) -> list[NewsItem]

class VectorDecoder:
    """Decodes interest vector into search queries."""
    + tag_tree: list[TagNode]
    + embedder: Embedder
    ---
    + vector_to_queries(vector: np.ndarray, top_k: int = 5) -> list[dict]
    + precompute_tag_embeddings()       # one-time setup
    + get_top_tags(vector: np.ndarray, k: int) -> list[tuple[float, TagNode]]

class Predictor:
    """Mathematical model for interest tag optimization."""
    + params: dict
    ---
    + coverage(N: int) -> float
    + info_gain(N: int) -> float
    + suggest_optimal_N() -> dict
    + radar_data(N: int) -> dict

# ============================================================
# FEEDBACK & LEARNING LAYER
# ============================================================

class FastLoopUpdater:
    """Per-session latent space update."""
    + BUCKET_PARAMS: dict
    ---
    + update_vector(profile: UserProfile, events: list[EngagementEvent])
    + ema_step(current: np.ndarray, target: np.ndarray, eta: float) -> np.ndarray
    + normalize(vector: np.ndarray) -> np.ndarray

class SlowLoopOptimizer:
    """Weekly batch keyword weight optimization."""
    + min_events: int = 50
    + regularization_lambda: float = 0.01
    ---
    + optimize_keyword_weights(profile: UserProfile)
    + compute_bce_loss(predicted: np.ndarray, actual: np.ndarray) -> float
    + should_trigger(profile: UserProfile) -> bool

class FeedbackLogger:
    """Logs engagement for slow loop analysis."""
    ---
    + log_event(event: EngagementEvent)
    + get_weekly_history(profile: UserProfile) -> list[EngagementEvent]

# ============================================================
# UI & SYNC LAYER
# ============================================================

class KanbanSession:
    """One user interaction session."""
    + session_id: str
    + items: list[NewsItem]         # the 50 presented items
    + columns: dict[str, list[str]] # bucket -> item_ids
    + profile_snapshot: UserProfile
    ---
    + move_item(item_id: str, from_bucket: str, to_bucket: str)
    + save() -> SaveResult

class SaveResult:
    + vector_delta: float           # how much vector moved
    + notion_synced: int            # count of tools written
    + new_top_tags: list[str]       # what interests changed

class NotionSync:
    """Writes Tools to Notion Toolbox DB."""
    + database_id: str
    ---
    + create_tool_entry(item: NewsItem) -> bool
    + batch_sync(items: list[NewsItem])

class KanbanUI:
    """Web-based drag-and-drop interface."""
    ---
    + render(items: list[NewsItem])
    + handle_drag(item_id: str, target_column: str)
    + handle_save() -> SaveResult

# ============================================================
# ORCHESTRATION LAYER
# ============================================================

class MuseEngine:
    """Main entry point. Owns the full pipeline."""
    + source_aggregator: SourceAggregator
    + embedder: Embedder
    + ranker: RankerEngine
    + decoder: VectorDecoder
    + fast_loop: FastLoopUpdater
    + slow_loop: SlowLoopOptimizer
    + notion: NotionSync
    + profile: UserProfile
    ---
    + run_morning_routine() -> list[NewsItem]
    + handle_save(session: KanbanSession) -> SaveResult
    + get_search_queries() -> list[str]
    + health_check() -> dict

class CronScheduler:
    """Triggers daily runs."""
    ---
    + schedule_daily(am_time: str = "5:30", pm_time: str = "17:30")
    + run_now()
```

---

## 5. The Learning Architecture: Three Loops

### 5.1 Fast Loop (Per-Save, Latent Space)

**When:** Every time user presses Save.  
**Where:** `FastLoopUpdater`  
**What:** Updates the 256-dim interest vector via EMA.

```python
def update_vector(profile, events):
    v = profile.interest_vector
    for event in events:
        eta = BUCKET_ETA[event.bucket]   # tools:0.05, interested:0.02, not_int:-0.03
        item_emb = event.item_embedding
        v += eta * (item_emb - v)        # EMA step
    v = normalize(v)                     # maintain unit length
```

**Why EMA?** Exponential moving average gives more weight to recent behavior while preserving historical signal. The vector is always a convex combination of all past items, with recency bias controlled by η.

### 5.2 Slow Loop (Weekly, Language Space)

**When:** Every Sunday at 3 AM, or when history > 50 events.  
**Where:** `SlowLoopOptimizer`  
**What:** Recomputes keyword → weight mapping for explainability.

```python
def optimize_keyword_weights(profile):
    history = get_weekly_history(profile)
    keywords = extract_top_keywords(history)
    
    # Target: maximize prediction accuracy for next week
    # Loss: BCE + L2 regularization + change penalty
    loss = -Σ[y·log(p) + (1-y)·log(1-p)] + λ₁·Σw² + λ₂·Σmax(0, |Δw|-0.5)
    
    profile.keyword_weights = minimize(loss)
```

**Why two loops?** Fast loop gives instant gratification (next search immediately improves). Slow loop gives explainability ("keyword 'diffusion' weight +15%") and prevents drift.

### 5.3 Human Loop (Ad-hoc)

**When:** User opens dashboard and manually edits.  
**What:** Direct vector manipulation, tag pruning, cold start reset.

```
Dashboard shows:
  • Current interest_vector (256 numbers, visualized as top-10 tags)
  • Keyword weight table (from slow loop)
  • [Edit] button → manual weight override
  • [Reset] button → trigger new cold start
```

---

## 6. Source Architecture Detail

### 6.1 Source Priority Matrix

| Source | Speed | Coverage | Maintenance | Priority |
|--------|-------|----------|-------------|----------|
| NewsNow | ⭐⭐⭐⭐⭐ | 44 Chinese platforms | Zero (external) | Primary (domestic) |
| RSSHub | ⭐⭐⭐⭐⭐ | 1000+ global routes | Docker (self-host) | Primary (global) |
| Native APIs | ⭐⭐⭐⭐⭐ | Reddit, HN | Zero | Secondary |
| Camofox | ⭐⭐⭐ | Any URL | High (custom parsers) | Fallback |

### 6.2 Source Selection Logic

```python
def select_sources(interest_vector, day_of_week):
    """Adaptive source selection based on vector maturity."""
    
    # Always active
    sources = [NewsNowClient(), RSSHubClient(), NativeAPIClient()]
    
    # Camofox only if vector is mature (> 3 save sessions)
    # or if primary sources return < 30 items
    if profile.save_count > 3 or primary_items < 30:
        queries = decoder.vector_to_queries(interest_vector)
        sources.append(CamofoxClient(queries))
    
    return sources
```

---

## 7. File Structure

```
muon-muse/
├── muse/
│   ├── __init__.py
│   ├── engine.py              # MuseEngine — main orchestrator
│   ├── models.py              # NewsItem, UserProfile, EngagementEvent, TagNode
│   ├── embedder.py            # Embedder — bge-small-zh wrapper
│   ├── ranker.py              # RankerEngine — scoring + diversity
│   ├── decoder.py             # VectorDecoder — vector → search queries
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base.py            # SourceClient abstract class
│   │   ├── newsnow.py         # NewsNowClient
│   │   ├── rsshub.py          # RSSHubClient
│   │   ├── native.py          # NativeAPIClient (Reddit, HN)
│   │   ├── camofox.py         # CamofoxClient
│   │   └── aggregator.py      # SourceAggregator
│   ├── learning/
│   │   ├── __init__.py
│   │   ├── fast_loop.py       # FastLoopUpdater (EMA)
│   │   ├── slow_loop.py       # SlowLoopOptimizer (BCE)
│   │   └── logger.py          # FeedbackLogger
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── kanban.py          # KanbanSession, SaveResult
│   │   └── notion_sync.py     # NotionSync
│   ├── predictor.py           # Predictor — radar math model
│   └── profile.json           # Runtime user profile
├── data/
│   └── tag_tree.json          # ~500 nodes, precomputed embeddings
├── dashboard/
│   └── index.html             # Single-page Kanban UI
├── scripts/
│   ├── run_morning.py         # Cron entry point
│   └── health_check.py        # Source health monitor
├── docs/
│   ├── blueprint-v2.md        # This document
│   ├── design.md              # Simplified one-loop design
│   └── demo.py                # Day 0 → Day 1 simulation
└── README.md                  # Public landing page
```

---

## 8. API Specification (Internal)

### Engine-Level API

```python
class MuseEngine:
    # Morning routine
    def run_morning_routine() -> list[NewsItem]
        """Full pipeline: fetch → embed → rank → return top 50."""
    
    # Save handling
    def handle_save(session: KanbanSession) -> SaveResult
        """Process save: update vector, sync Notion, log history."""
    
    # Query generation
    def get_search_queries() -> list[str]
        """Decode current vector into search queries."""
    
    # Health
    def health_check() -> dict[str, bool]
        """Check all source clients."""
```

### Source Client API

```python
class SourceClient(ABC):
    @abstractmethod
    def fetch(self) -> list[NewsItem]
    
    @abstractmethod
    def health_check(self) -> bool
```

---

## 9. Key Algorithms

### 9.1 Vector-to-Query Decoder

```python
def vector_to_queries(interest_vector: np.ndarray, top_k=5) -> list[str]:
    """
    1. Compare interest_vector against all tag embeddings (cosine)
    2. Take top-k matching tags
    3. For each tag, assemble: "{tag.name} {keywords} 最新"
    4. Return list of query strings
    """
    scored = [(cosine(interest_vector, tag.embedding), tag) 
              for tag in all_tags]
    scored.sort(reverse=True)
    
    queries = []
    for _, tag in scored[:top_k]:
        q = f"{tag.name} {' '.join(tag.keywords[:3])} 最新"
        queries.append(q)
    
    return queries
```

**Complexity:** O(N_tags × d) = O(500 × 256) = ~1ms.

### 9.2 EMA Vector Update

```python
def ema_update(vector, item_embedding, eta):
    """
    vector: current interest vector (unit length)
    item_embedding: encoded item title
    eta: learning rate (0.05 for Tools, 0.02 for Interested, -0.03 for Not Int.)
    
    Returns: updated vector (unit length)
    """
    new_vector = vector + eta * (item_embedding - vector)
    return new_vector / np.linalg.norm(new_vector)
```

**Physical meaning:** The vector is pulled toward items the user likes, pushed away from items they reject. The magnitude of η controls "how fast" interests can shift.

### 9.3 Ranking Formula

```python
def score_item(item, profile):
    base = cosine(profile.interest_vector, item.embedding)
    
    # Keyword boost from slow loop
    keyword_boost = sum(
        profile.keyword_weights.get(kw, 1.0) 
        for kw in extract_keywords(item.title)
    ) / max(1, len(extract_keywords(item.title)))
    
    # Freshness boost
    age_hours = (now - item.pub_date).total_seconds() / 3600
    freshness = 1.0 if age_hours < 2 else 0.9 if age_hours < 6 else 0.8
    
    return base * keyword_boost * freshness
```

---

## 10. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Machine                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Muse Core  │  │ bge-small   │  │  profile.json       │ │
│  │  (Python)   │  │  (~133MB)   │  │  (local state)      │ │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘ │
│         │                                                   │
│         ├──→ HTTP ──→ NewsNow API (busiyi.world)           │
│         ├──→ HTTP ──→ RSSHub Docker (localhost:1200)       │
│         ├──→ HTTP ──→ Reddit/HN APIs                       │
│         ├──→ HTTP ──→ Camofox (localhost:9377)             │
│         ├──→ HTTP ──→ Notion API (notion.so)               │
│         └──→ HTTP ──→ Telegram Bot API (optional push)     │
└─────────────────────────────────────────────────────────────┘
```

**Requirements:**
- Python 3.10+
- `sentence-transformers` (auto-downloads bge-small-zh on first run)
- Docker (for RSSHub, optional)
- Camofox browser (for fallback search, optional)
- ~500MB RAM total

---

## 11. Design Decisions & Trade-offs

| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Embedding model | bge-small-zh (256d, local) | OpenAI text-embedding-3 | Free, offline, sufficient for 50-item ranking |
| Vector update | EMA in latent space | Gradient descent on BCE | EMA is O(1) per item, no training needed |
| Cold start | No onboarding; random trending first | Tag tree selection | Zero friction; first drag creates vector |
| Data sources | 4-source fusion | Single source | Resilience + coverage |
| UI | Kanban drag | Tinder swipe | 4 buckets > binary signal |
| Persistence | JSON file | SQLite/Postgres | Single user, < 100KB data |
| LLM usage | None | Daily summary | Cost + Sir doesn't read summaries; he drags |
| Notion sync | Tools → Toolbox | Everything → Notion | Only actionable items have business value |

---

## 12. Evolution from Previous Designs

```
V1 (9-layer) ──→ V2 (Kanban loop) ──→ V3 (This blueprint)
    │                │                    │
    │                │                    ├── Multi-source fusion (NewsNow + RSSHub)
    │                │                    ├── Closed-loop learning (fast + slow + human)
    │                │                    ├── Vector-to-query decoder
    │                │                    └── Zero LLM cost
    │                │
    │                └── Simplified to one loop
    │                    ├── Removed tag tree onboarding
    │                    ├── Replaced 👍/👎 with Kanban drag
    │                    └── Added Notion Toolbox sync
    │
    └── Original complex pipeline
        ├── L1-L9 explicit layers
        ├── LLM summary generation
        ├── Tag tree cold start
        └── Per-item binary feedback
```

---

## 13. Open Questions for Review

1. **Should we keep the predictor/radar model?** It's mathematically elegant but adds UI complexity. The Kanban loop works without it.

2. **RSSHub self-hosting vs. public instance?** Public instances are rate-limited. Self-hosting adds Docker dependency.

3. **Camofox maintenance burden?** It's powerful but requires Node + browser. Should it be truly optional (degrade gracefully if not running)?

4. **Notion sync failure handling?** If Notion API is down, should Save fail or queue for retry?

5. **Multi-device sync?** Currently profile.json is local. If Sir uses multiple machines, how to sync?

---

## 14. Convergence Estimate

Based on the EMA update formula and simulated user behavior:

| Day | Save Sessions | Vector Stability | Match Quality |
|-----|--------------|------------------|---------------|
| 0 | 0 | N/A (zero vector) | Random trending |
| 1 | 1 | 15% | Broad 5-area search |
| 3 | 3 | 45% | Noticeable focus |
| 5 | 5 | 65% | Good relevance |
| 10 | 10 | 82% | Strong personalization |
| 15 | 15 | 91% | Stable preferences |
| 30 | 30 | 96% | Mature profile |

**Definition of "stable":** Top-5 decoded tags remain unchanged across 3 consecutive saves.

---

*End of Blueprint v2.0*
