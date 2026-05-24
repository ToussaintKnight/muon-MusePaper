# 🎯 MusePaper | Progress: 3/5

**The feedback loop that learns what you care about.**

Muse is a daily intelligence engine built for solopreneurs and high-pace builders. Every morning it fetches trending content from 40+ platforms (Chinese + global), ranks it against your personal interest vector, and presents 50 cards in a Kanban board. You drag them into three columns — **Tools**, **Interested**, **Not Interested** — and press Save. Muse learns. Tomorrow's content improves.

No cold start friction. No LLM costs. No SaaS lock-in. Just drag, save, and your system gets smarter.

---

## One Loop

```
Interest Vector → Multi-Source Fetch → Embed → Rank → Kanban → Save → Updated Vector
        ↑                                                                      │
        └──────────────────────────────────────────────────────────────────────┘
```

**3 minutes a day.** That's it.

---

## What Makes Muse Different

| Dimension | Muse | Typical RSS Aggregator |
|-----------|------|------------------------|
| **Learning** | Interest vector evolves from your drags | Static keyword filters |
| **Sources** | 4-source fusion (NewsNow + RSSHub + Native APIs + optional Camofox) | Single RSS feed |
| **Signal** | 4-bucket drag (Tools / Interested / Not-Int / Ignored) | Binary read/unread |
| **Output** | Tools → Notion Toolbox (actionable) | Infinite scroll |
| **Cost** | $0 (local embedding model) | Often paid SaaS |
| **Setup** | `pip install` + `uvicorn main:app` | Account + onboarding |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ToussaintKnight/muon-muse.git
cd muon-muse

# 2. Dependencies (already installed in most Python environments)
pip install fastapi uvicorn numpy sentence-transformers httpx pydantic

# 3. Optional: RSSHub for international sources
docker run -d --name rsshub -p 1200:1200 diygod/rsshub

# 4. Optional: Notion sync
export NOTION_API_KEY="your_key"
export NOTION_TOOLBOX_DB_ID="your_db_id"

# 5. Run
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for interactive API documentation.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health + version |
| `/api/items/today` | GET | Fetch & rank today's top 50 items |
| `/api/profile` | GET | Current interest vector & top tags |
| `/api/search-queries` | GET | Decode vector into search queries |
| `/api/health` | GET | Source health check |
| `/api/metrics/daily` | GET | Daily effectiveness metrics history |
| `/api/session/start` | POST | Start a new Kanban session |
| `/api/session/move` | POST | Move item to bucket |
| `/api/session/save` | POST | Save session → update vector + sync Notion |
| `/api/run` | POST | Manually trigger morning routine |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  SOURCE LAYER                                               │
│  ├── NewsNow API    (44 Chinese platforms)                  │
│  ├── RSSHub Docker  (1000+ global routes)                   │
│  ├── Native APIs    (Reddit, Hacker News — zero auth)       │
│  └── Camofox        (optional fallback search)              │
├─────────────────────────────────────────────────────────────┤
│  PROCESSING LAYER                                           │
│  ├── SourceAggregator  (merge + deduplicate)                │
│  ├── Embedder          (bge-small-zh, 256-dim, local)       │
│  └── RankerEngine      (cosine + diversity + freshness)     │
├─────────────────────────────────────────────────────────────┤
│  LEARNING LAYER                                             │
│  ├── Fast Loop  (EMA vector update, per-save)               │
│  ├── Slow Loop  (BCE keyword optimization, weekly)          │
│  └── Human Loop (dashboard override, ad-hoc)                │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT LAYER                                               │
│  ├── Kanban UI    (drag & drop)                             │
│  ├── Notion Sync  (Tools → Toolbox DB)                      │
│  └── Daily Metrics (OPC effectiveness tracking)             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Math

### Vector Update (Fast Loop)

```python
# Exponential moving average
vector += eta * (item_embedding - vector)
vector = normalize(vector)

# Bucket learning rates:
#   Tools:          eta = 0.05   (strong positive)
#   Interested:     eta = 0.02   (mild positive)
#   Not Interested: eta = -0.03  (negative)
#   Ignored:        eta = 0.0    (slight decay via keyword weights)
```

### Ranking Formula

```python
score = cosine(interest_vector, item_embedding)
        × keyword_boost
        × freshness_boost
```

### Daily Effectiveness Score (Solopreneur Metrics)

| Metric | Formula | Target |
|--------|---------|--------|
| Decision Velocity | cards / session_min | > 10/min |
| Actionability Index | Tools / (Tools + Interested) | > 0.3 |
| Signal-to-Noise | (Tools + Interested) / NotInterested | > 3 |
| Stack Velocity | New Notion tools / week | > 2 |
| Interest Stability | cosine(yesterday_vec, today_vec) | ~0.85 |

Composite score: 0–100, updated daily.

---

## File Structure

```
muon-muse/
├── main.py                  # FastAPI application
├── muse/
│   ├── models.py            # NewsItem, UserProfile, EngagementEvent, TagNode
│   ├── embedder.py          # bge-small-zh wrapper
│   ├── engine.py            # MuseEngine orchestrator
│   ├── ranker.py            # Scoring + diversity filter
│   ├── decoder.py           # Vector → search queries
│   ├── predictor.py         # Cold-start radar model
│   ├── effectiveness.py     # Daily OPC metrics
│   ├── sources/
│   │   ├── base.py          # SourceClient abstract class
│   │   ├── newsnow.py       # Chinese platform aggregator
│   │   ├── rsshub.py        # International RSS aggregator
│   │   ├── native.py        # Reddit, HN zero-auth APIs
│   │   └── aggregator.py    # Merge + deduplicate
│   ├── learning/
│   │   ├── fast_loop.py     # EMA vector update
│   │   ├── slow_loop.py     # BCE keyword optimization
│   │   └── logger.py        # Engagement logging
│   └── ui/
│       ├── kanban.py        # Session state
│       └── notion_sync.py   # Notion Toolbox API
├── data/
│   ├── tag_tree.json        # Interest tag tree (~20 nodes)
│   └── profile.json         # Runtime user profile (auto-created)
├── tests/                   # 47 pytest cases
├── docs/
│   ├── blueprint-v2.md      # Full architecture spec
│   └── diagrams-v2.mmd      # Mermaid visual diagrams
└── README.md                # This file
```

---

## Target Audience

Muse is designed for:
- **Solopreneurs / OPCers** who need to stay on top of tech trends without drowning in feeds
- **Open-source community** — localhost-first, API-ready for Hermes / Notion / Obsidian integration
- **High-pace builders** who value actionable signal over passive consumption

Mobile apps and multi-device sync are on the roadmap for v3.

---

## Tech Stack

| Component | Choice |
|-----------|--------|
| API Framework | FastAPI |
| Embedding | BAAI/bge-small-zh-v1.5 (256-dim, local, ~133MB) |
| Sources | NewsNow API + RSSHub + Native APIs + optional Camofox |
| Storage | JSON files (profile.json, tag_tree.json) |
| Sync | Notion API (optional) |
| Schedule | Hermes cron or system cron |
| Tests | pytest (47 cases) |

---

## Convergence Estimate

| Day | Saves | Match Quality |
|-----|-------|---------------|
| 1 | 1 | Broad trending |
| 3 | 3 | Noticeable focus |
| 5 | 5 | Good relevance |
| 10 | 10 | Strong personalization |
| 15 | 15 | Stable preferences |

---

## License

MIT — open source, localhost-first, build your own.
