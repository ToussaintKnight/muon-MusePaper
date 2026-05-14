# 🎯 Muse

**Drag. Save. Learn.**

Muse is a daily intelligence engine that fits in 3 minutes of your morning.

Every day it finds 50 trending items across 5 areas you care about. You drag them into three Kanban columns — **Tools, Interested, Not Interested** — and press Save. That's it.

- 🛠️ Tools are written to your Notion Toolbox (actionable)
- 👀 Interested trains the model to show more like this
- ❌ Not Interested trains the model to stop
- The updated interest vector drives tomorrow's search

No cold start. No LLM calls. No setup. Just drag, save, and your system gets smarter.

---

## One Loop

```
   兴趣向量 → 搜索5个领域 → 展示50条 → 拖到Kanban → 按Save → 更新向量
                       ↑                                   │
                       └─────────── 下一轮用新向量 ──────────┘
```

---

## How It Works

### Session Flow

```
5:30 am — 50 items fetched across 5 interest areas
   ↓
09:00 — You open the Kanban (web or Telegram)
   ↓
You drag:
  🛠️ Tools      → 3 items → written to Notion Toolbox
  👀 Interested  → 8 items → strengthens these interests
  ❌ Not Int.    → 5 items → weakens these interests
  (rest)         → ignored → slight decay
   ↓
Press Save → embedding updates → next search uses new vector
```

### Signal Strength

| Bucket | Weight change | Embedding step | Meaning |
|--------|--------------|----------------|---------|
| 🛠️ Tools | ×1.15 | +0.05·Δ | "Actionable — surface more like this" |
| 👀 Interested | ×1.05 | +0.02·Δ | "Want to see more" |
| ❌ Not Int. | ×0.90 | -0.03·Δ | "Stop showing this" |
| (ignored) | ×0.995 | — | "Marginally less interesting" |

### Cold Start

Session 1 starts with general trending. Your first drag-save cycle creates the interest vector.
Convergence: ~5 sessions (days) to useful, ~15 to stable.

---

## Why Kanban?

Because reading the news and curating your system architecture watchlist are the same activity. Every item you drag to 🛠️ Tools is a potential upgrade to your stack — preserved in Notion, actionable this sprint.

---

## Quick Start

```bash
git clone https://github.com/ToussaintKnight/muon-muse.git
cd muon-muse
python3 -m muse.engine
```

Requires: `sentence-transformers` (one-time ~133MB model download).

---

## Tech Stack

| Component | What |
|-----------|------|
| Embedding | BAAI/bge-small-zh-v1.5 (256-dim, local) |
| Search | Camofox browser API |
| Storage | SQLite (sessions) + Notion API (tools) |
| UI | Single HTML file — Kanban with drag & drop |
| Schedule | Hermes cron — 5:30am/pm |
