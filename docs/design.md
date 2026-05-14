# 🎯 Muse

**The feedback loop that learns what you care about.**

Every day Muse presents you with 50 trending items across 5 areas. You drag them into three Kanban columns. When you press Save, Muse learns from your choices and searches better next time.

That's it. No cold start onboarding, no tag trees, no LLM summaries. Just drag, save, learn.

---

## One Loop

```
                     ┌─── Tools (→ stored to Notion) ───┐
                     │                                   │
                     │                                   ▼
[兴趣向量] → [搜索5领域] → [50条] → 你拖到 ──┤  ←─ [ Notion 工具库 ]
                     │                                   ▲
                     ├─── Interested ─────────────────────┤
                     │                                   │
                     └─── Not Interested ─────────────────┘
                                │
                                ▼
                         按 Save → 更新 embedding
                                │
                                ▼
                    下一轮用新向量搜索
```

No 9 layers. No cold start. No LLM calls. One loop.

---

## How It Works

### Step 1: Search 5 Areas

Your interest vector is decoded into 5 search queries that cover your current interest profile:

```python
# 50 = 5 areas × 10 items each
areas = decode_vector_to_areas(interest_vector, n=5)
for area in areas:
    items = search(f"{area.keywords} trending 2026")
    results[area.name] = top_10(items)
```

The 5 areas adjust as your vector drifts.

### Step 2: You Drag

Each item is a card with:
- Title
- Source + heat score (if available)
- 1-line summary

Three columns:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 🛠️ Tools     │  │ 👀 Interested│  │ ❌ Not Int.  │
│──────────────│  │──────────────│  │──────────────│
│              │  │              │  │              │
│  Card A      │  │  Card B      │  │  Card D      │
│  Card C      │  │              │  │              │
│              │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Step 3: Save

When you press **Save**, two things happen synchronously:

#### A) Tools → Notion Toolbox

```python
for item in tools_column:
    notion.pages.create(
        parent={"database_id": NOTION_TOOLBOX_DB},
        properties={
            "Name": {"title": [{"text": {"content": item.title}}]},
            "URL": {"url": item.url},
            "Source": {"select": {"name": item.platform}},
            "Status": {"select": {"name": "To Evaluate"}},
            "Added": {"date": {"start": today}},
            "Tags": {"multi_select": [{"name": area} for area in item.matched_areas]},
        }
    )
```

This is the **persistent business value** — your system architecture monitoring becomes a side effect of your daily reading.

#### B) Embedding Update

```
For Tools:      weight ×= 1.15  (+15%, strong positive signal)
                emb += 0.05 × (item_emb - emb)

For Interested: weight ×= 1.05  (+5%, mild positive)
                emb += 0.02 × (item_emb - emb)

For Not Int.:   weight ×= 0.90  (-10%, negative)
                emb -= 0.03 × (item_emb - emb)

For Unmoved:    weight ×= 0.995 (-0.5%, ignored items drift down)
```

The update happens once on Save, not per-card. The batch update is more stable than incremental.

---

## The Math

### Signal Weights

| Bucket | Signal | Weight change | Embedding step | Interpretation |
|--------|--------|---------------|----------------|----------------|
| 🛠️ Tools | Strong positive | ×1.15 (+15%) | +0.05·Δ | "This is actionable — surface more like it" |
| 👀 Interested | Mild positive | ×1.05 (+5%) | +0.02·Δ | "I want to see more of this" |
| ❌ Not Int. | Negative | ×0.90 (-10%) | -0.03·Δ | "Stop showing this" |
| (Not moved) | Weak negative | ×0.995 (-0.5%) | None | "Ignored = marginally less interesting" |

### Update Rule

After each Save session:

```python
for item in session_items:
    if item in tools_column:
        w_new = clamp(w_old × 1.15, 0.1, 3.0)
        e_new = e_old + 0.05 × (item_emb - e_old)
    elif item in interested_column:
        w_new = clamp(w_old × 1.05, 0.1, 3.0)
        e_new = e_old + 0.02 × (item_emb - e_old)
    elif item in not_interested_column:
        w_new = clamp(w_old × 0.90, 0.1, 3.0)
        e_new = e_old - 0.03 × (item_emb - e_old)
    else:
        w_new = clamp(w_old × 0.995, 0.1, 3.0)
        e_new = e_old  # untouched items = slightly decayed weight
```

### Cold Start — Solved

There is no cold start. First run shows random trending items from the general hot list. Your first drag session generates the initial interest vector.

```
Session 1: Show 50 hot → you drag 3 to "Interested" → Save → vector born
Session 2: Vector searches 5 areas → you drag 10 → Save → vector refines
Session 5: Vector converges → 70%+ of items match your real interests
```

---

## Session Flow

```
5:30 am — Muse runs
  ↓
Interest vector → decode 5 areas → search each → 50 items
  ↓
Push to Telegram / open web dashboard
  ↓
09:00 — You open the Kanban
  ↓
Drag items: 3 to 🛠️ Tools, 8 to 👀 Interested, 5 to ❌ Not Int.
  ↓
Press Save
  ↓
┌──────────────────────────────────────────┐
│  ① Tools → written to Notion Toolbox DB  │
│  ② Embedding → updated (batch)           │
│  ③ Next search → uses new vector         │
│  ④ Report → "Your interests shifted:"    │
└──────────────────────────────────────────┘
```

Total user time: ~3 minutes/day.

---

## Files

```
muse/
├── muse/
│   ├── __init__.py
│   ├── engine.py           ← Core: search → score → learn
│   ├── embedding.py        ← Vector ops: encode, decode, update
│   ├── kanban.py           ← Session state: columns, drag, save
│   ├── notion_sync.py      ← Tools → Notion API
│   ├── profile.py          ← Load/save profile.json
│   └── profile.json        ← { vector, topics, history }
├── dashboard/
│   └── index.html          ← Single-page Kanban UI
├── scripts/
│   ├── run.py              ← Morning cron entry
│   └── register.sh
├── docs/
│   └── design.md           ← This file
└── README.md               ← Public facing
```

---

## What About...

| Question | Answer |
|----------|--------|
| What if no items match? | Show hot list fallback — you'll drag something |
| What if user's taste changes? | Stop dragging → old topics decay at 0.5%/session |
| What if 50 is too many? | Drag what catches your eye, ignore the rest |
| Who pays for Notion API? | Already have it (Notion Toolbox DB exists) |
| When does vector converge? | ~5 sessions (5 days) to useful, ~15 to stable |
| How many tools per week? | Realistically 1-3. Quality over quantity. |

---

## Comparison to the Old Design

| Dimension | V1 (9 layers) | ⊙ Kanban Loop |
|-----------|---------------|---------------|
| Cold start | Tag tree / 30s interactive | 0 — just start dragging |
| Feedback | 👍/👎 per item | Drag to column + Save |
| Learn rate | +5% per feedback | +15% for Tools |
| Persistence | profile.json only | Tools → Notion Toolbox |
| User time | Read summary | 3 min drag + Save |
| LLM cost | $0.42/month | $0 (no LLM needed) |
| Complexity | 500+ lines, 9 layers | ~200 lines, 1 loop |

The Kanban loop is simpler, faster to build, cheaper to run, and delivers immediate business value (Notion Toolbox feeds directly into system architecture decisions).
