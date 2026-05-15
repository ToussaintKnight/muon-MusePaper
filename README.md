# 🎯 Muse

**A daily intelligence engine that learns what matters to you.**

Muse is a personal interest-learning engine. Every day it scrapes Chinese platform hot lists (Baidu, Weibo, Bilibili), matches content against your learned interest profile using semantic embeddings, surfaces what you'll actually care about, and pushes a curated summary to Telegram.

Unlike feed algorithms designed to maximize engagement for billions of users, Muse is built for **one user who wants signal, not noise.**

---

## The Problem

Daily intelligence tools fall into two camps:

| Camp | Example | Problem |
|------|---------|---------|
| Hot list aggregators | Baidu Hot Search, TrendRadar | You see what everyone likes, not what *you* like |
| Feed recommender systems | Twitter/X, Weibo, TikTok | Trained on 100M+ users, need a cloud GPU farm, designed to addict |

Muse is neither. It's a **third path**: local, learnable, personal.

---

## How It Works

### The 9-Layer Pipeline

```
              ╔══════════════════════════════════╗
              ║         Layer 0: Entities        ║
              ║  Profile · TagNode · ContentItem ║
              ║  ScoredItem · Recommendation     ║
              ╚══════════════════════════════════╝
                         │
╔════════════════════════╪════════════════════════╗
║  L1: Data Collection  │  hotlist_scraper.py    ║
║  (Camofox Browser)    │  50 items from Baidu   ║
╚════════════════════════╪════════════════════════╝
                         │ raw text
╔════════════════════════╪════════════════════════╗
║  L2: Vector Encoding  │  bge-small-zh-v1.5     ║
║  (sentence-transform) │  256-dim embeddings    ║
╚════════════════════════╪════════════════════════╝
                         │ vectors
╔════════════════════════╪════════════════════════╗
║  L3: Interest Scoring  │  α·cos(base,item)     ║
║  (cosine similarity)   │  + (1-α)·W·cos(t,i)   ║
╚════════════════════════╪════════════════════════╝
                         │ ranked items
╔════════════════════════╪════════════════════════╗
║  L4: Predictor         │  C(N) = 1-e^{-λN}     ║
║  (radar chart math)    │  G(N) = C·R·e^{-φN}   ║
╚════════════════════════╪════════════════════════╝
                         │ trade-off metrics
╔════════════════════════╪════════════════════════╗
║  L5: Cold Start        │  10 root tags →       ║
║  (interactive tree)    │  expand → select →    ║
║                        │  generate profile      ║
╚════════════════════════╪════════════════════════╝
                         │ initial profile
╔════════════════════════╪════════════════════════╝
║  L6: Feedback Learning │  👍 weight ×= 1.05    ║
║  (per-topic adjustment)│  👎 weight ×= 0.95    ║
║                        │  emb += ±η·Δ          ║
╚════════════════════════╪════════════════════════╝
                         │ refined profile
╔════════════════════════╪════════════════════════╗
║  L7: LLM Synthesis     │  DeepSeek Flash       ║
║  (structured summary)  │  $0.007/run            ║
╚════════════════════════╪════════════════════════╝
                         │ prose
╔════════════════════════╪════════════════════════╗
║  L8: Push (Telegram)   │  Hermes send_message  ║
╚════════════════════════╪════════════════════════╝
                         │ notification
╔════════════════════════╪════════════════════════╗
║  L9: Cron (5:30am/pm)  │  register_intel_cron  ║
╚════════════════════════╩════════════════════════╝
```

---

## Key Design Decisions

### How We Handle Cold Start

Instead of showing you a blank screen and waiting for you to click things, Muse uses a **Reddit/Pinterest-style interactive interest tree**:

```
Step 1: Show 10 general tags (AI/ML, Design, Startup, Academia, Music...)
Step 2: You pick ≥3
Step 3: Click any tag → expands 10 sub-tags
Step 4: Recursively expand or confirm
Step 5: System generates initial embedding vector from your selections
```

This converts the cold-start problem from "wait 2 weeks for the algorithm to learn you" to "tell us who you are in 30 seconds."

### How Tag Selection Works

Tags form a **3-level tree** (~500 nodes):

```
Root (10 tags)
 └── AI/ML (8 sub-tags)
      ├── LLM
      │    ├── GPT/Azure
      │    ├── Open Source LLMs
      │    └── Evaluation Benchmarks
      ├── Multimodal
      ├── Diffusion Models
      └── Agents
```

Each leaf node carries **keywords** used for initial embedding generation and as a fallback when the embedding model is unavailable.

### How We Match Content

The scoring formula:

```
score(item) = 0.3 · cos(base_embedding, item_embedding)
            + 0.7 · max_i [ weight_i · cos(topic_i, item_embedding) ]
```

- **base_embedding**: aggregated vector representing your overall interests
- **topic_i embedding**: per-tag specific vector
- **weight_i**: adjusted over time via feedback (starts at 1.0, range [0.1, 3.0])

The 0.3/0.7 split ensures both macro coverage (you might like things outside your defined tags) and micro precision (your specific interests dominate).

### How We Learn Preferences

Feedback loop:

```
Like:   w_new = w_old × 1.05      (+5% weight, 2% embedding shift toward item)
Dislike: w_new = w_old × 0.95     (-5% weight, 2% embedding shift away)
Clip:   weight ∈ [0.1, 3.0]
```

Convergence: ~100-200 feedback events (15-30 days at 2 pushes/day).

### How We Handle Diminishing Returns (Info Gain)

The info gain function has a **natural peak**:

```
G(N) = C(N) · R(N) · e^{-φN}
```
where:
- `C(N) = 1 - e^{-λN}` : coverage (more tags → more content matched)
- `R(N) = 1 - e^{-μN}` : relevance (more tags → finer matching)
- `e^{-φN}` : fatigue penalty (more tags → more repetition)

**Peak at N=18 tags.** Optimal zone: 10-18 tags.

### How We Predict Trade-offs Instantly

All predictions are pure mathematical functions — no ML, no training, no disk I/O:

| Dimension | Formula | At N=15 |
|-----------|---------|---------|
| Coverage | `C(N) = 1 - e^{-0.068N}` | 63.9% |
| Info Gain | `G(N) = C·R·e^{-0.05N}` | 0.235 bits |
| Daily Items | `I(N) = 150 × C(N)` | 95 items |
| Memory | `Mem(N) = N × 256 × 4` | 15 KB |
| Time | `T(N) = 0.004·N·150 + 2.0` | 11 ms |

These run in-browser in <1ms via JavaScript copy. The radar chart updates in real-time as you hover potential tags.

### How We Generate Summaries

Top 10 scored items → DeepSeek Flash LLM (500 token prompt, 200 token response) → structured briefing:

```
🌅 Daily Briefing | 2026-05-15
━━━━━━━━━━━━━━━━━━━━━━━━
🔥 Top 3:
  1. [title] — why you'd care [Baidu: 7.8M heat]
  2. ...
📊 Trend Analysis
  [2-3 sentence synthesis]
👀 Follow-up
  [1 suggestion]
━━━━━━━━━━━━━━━━━━━━━━━━
  👍 Useful | 👎 Not interested
```

Cost: ~$0.007/run, ~$0.42/month at 2 runs/day.

---

## Mathematical Model Summary

| Symbol | Meaning | Default | Formula |
|--------|---------|---------|---------|
| `N` | Number of interest tags | — | User-defined |
| `M` | Daily content pool size | 150 | Baidu 50 + Weibo 50 + Bilibili 50 |
| `p` | Single-tag match rate | 0.08 | Empirical |
| `α` | Tag overlap coefficient | 0.15 | Tunable |
| `λ` | Effective coverage rate | 0.068 | `λ = p(1-α)` |
| `μ` | Relevance growth rate | 0.10 | Embedding model dependent |
| `φ` | Fatigue coefficient | 0.05 | Tunable |
| `δ` | Feedback delta | 0.05 | Per 👍/👎 weight change |
| `η` | Embedding learning rate | 0.02 | Per feedback step |
| `d` | Embedding dimension | 256 | bge-small-zh-v1.5 |
| `k` | Time per item per tag | 0.004 ms | MacBook M-series |

All parameters are adjustable via `profile.json`. No recompilation or redeployment needed.

---

## Architecture

```
muse/
├── README.md                 ← This file
├── pyproject.toml
├── muse/
│   ├── __init__.py
│   ├── predictor.py          ← Pure math model (7 formulas)
│   ├── interest_engine.py    ← Embedding + scoring
│   ├── daily_briefing.py     ← Pipeline orchestrator
│   ├── feedback.py           ← Feedback learning loop
│   ├── tag_tree.py           ← Tag tree loader
│   ├── tag_tree/
│   │   ├── root.json         ← 10 root tags
│   │   ├── ai-ml.json
│   │   └── ...
│   ├── onboarding.py         ← Cold start flow
│   └── profile.json          ← Runtime interest config
├── scripts/
│   ├── run_daily_briefing.py ← Cron entry point
│   └── register_cron.sh
├── dashboard/
│   └── interests.html        ← Tag selector + radar chart
└── docs/
    ├── architecture-specification.md  ← 9-layer spec
    ├── daily-intelligence-design.md   ← Full design doc
    ├── interest-discovery-design.md   ← Cold start + radar UI
    ├── open-source-analysis.md        ← Competitor research
    └── figures/                       ← Generated plots
```

---

## Getting Started

```bash
# Clone
git clone https://github.com/ToussaintKnight/muon-muse.git
cd muon-muse

# Install (one dependency)
pip install sentence-transformers
# Downloads bge-small-zh-v1.5 (~133MB) on first run

# Run the math model (no dependencies needed — pure Python)
python3 -m muse.predictor

# Run cold start (interactive tag selection)
python3 -m muse.onboarding

# Run daily briefing (full pipeline)
python3 scripts/run_daily_briefing.py
```

---

## Comparison to Alternatives

| | Muse | Twitter/X | Coffeed News | 1202-corp Bot |
|---|---|---|---|---|
| Users | 1 | 500M+ | Multi-tenant | Multi-tenant |
| Hardware | MacBook | GPU farm | Supabase cloud | Docker 7 containers |
| Embeddings | Local model | FAISS cluster | OpenAI API | OpenAI API |
| Storage | Memory (~30KB) | Multiple DBs | pgvector | Qdrant |
| Cold start | Interactive tree | 2-week ramp | Topic selection | Follow channels |
| Feedback | 👍/👎 → weight shift | Implicit signals | None | Swipe |
| Delivery | Telegram | Feed | Email | Telegram |
| Code | ~500 lines | Classified | ~10K lines | ~3K lines |

Muse is not trying to compete with social media feeds. It's a **personal intelligence tool** for one person who wants high-signal, low-noise daily updates.

---

## License

MIT — Use it, fork it, make it yours.
