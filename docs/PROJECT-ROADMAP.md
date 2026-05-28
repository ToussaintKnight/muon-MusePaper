# Muse → MusePaper v3: Project Depiction & Roadmap

> Document generated: 2026-05-23
> Current stable commit: `83e210a` — feat: MusePaper v3

---

## 1. Project Overview

**Muse** is a daily intelligence engine that learns what you care about by observing your reading behavior. It fetches articles from hundreds of sources, ranks them by personal relevance using embedding-based scoring, and presents them in an ever-improving daily digest.

**MusePaper v3** is the latest evolution: a newspaper-style reading interface inspired by 1900s broadsheets. Articles are categorized into sections (Science & Industry, Commerce & Trade, Arts & Letters, etc.), laid out in a multi-page grid with visual hierarchy, and presented with thematic engravings and period-authentic typography.

### Interaction Model
- **Click-to-learn**: Click an article to expand it → records "interested"
- **Scroll-to-ignore**: Scroll past without clicking → records "not interested"
- **Batch save**: One save happens when clicking "Done for Today"
- **Daily refresh**: A new edition is composed every morning at 5:30 AM

---

## 2. Current Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MUSEPAPER V3                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  FRONTEND (React 19 + Vite 7 + Tailwind v3)                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ NewspaperComposer│→│  PretextLayout  │→│   AuditAgent    │             │
│  │                 │  │  (text measure) │  │ (coverage 55-65%)│             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│           ↓                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   ImageAgent    │→│ NewspaperRenderer│→│   ArticleCard   │             │
│  │ (engraving sel) │  │  (CSS Grid layout)│  │ (click-to-learn)│             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  Stores: Zustand contentStore — fetch, track clicks, batch save             │
│  Animation: GSAP-powered delivery sequence on first visit/day               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ HTTP
┌─────────────────────────────────────────────────────────────────────────────┐
│  BACKEND (Python 3.13 + FastAPI)                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        MORNING ROUTINE                                │ │
│  │  SourceAggregator → RankerEngine → LayoutAgent → AbstractAgent        │ │
│  │  (fetch 100+)     → (score)      → (categorize)  → (trim abstracts) │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                      ↓                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  /api/newspaper/│  │  /api/session/  │  │  /api/cron/     │             │
│  │  issue, click   │  │  save, start    │  │  status, trigger│             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  Learning: FastLoop (immediate) + SlowLoop (nightly)                        │
│  Cron: Daily 5:30 AM briefing + Telegram push                               │
│  Profile: Persistent JSON with tag tree + embedding vectors                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. What's Been Implemented

### Phase 1: Backend Draft Pipeline ✅ COMPLETE

**Files:**
- `muse/agents/layout_agent.py` — Categorizes 100 articles into newspaper sections
  - `SECTION_MAP`: 50+ tag paths → 7 newspaper sections
  - `column_span_for_rank()`: Top 3 = 3 cols, 4-8 = 2 cols, rest = 1 col
  - `abstract_budget_for_span()`: 180 / 120 / 80 words
  - `build_pages()`: Distributes into 3 pages with layout templates
  
- `muse/agents/abstract_agent.py` — Prepares article abstracts
  - Top 20: fetches original content + trims to word budget
  - Rest: title + domain teaser
  - All abstracts trimmed to exact word count

- `muse/models.py` — Added `SlotItem`, `NewspaperPage`, `NewspaperDraftIssue`

- `muse/engine.py` — `run_newspaper_issue(top_n=100)`
  - Full pipeline: fetch → layout → abstracts → create Kanban session → return draft

- `main.py` — New endpoints
  - `GET /api/newspaper/issue` — returns composed newspaper draft
  - `POST /api/newspaper/click` — records click/interest
  - `POST /api/session/save` — updated with `clicks`/`ignores`/`tools` arrays
  - Root `/` serves React frontend (falls back to old dashboard if no build)
  - `/admin` preserves old Kanban dashboard

- `tests/test_newspaper.py` — 7 tests, all passing

**Test Results:** 53/54 pass (1 pre-existing stale test)

### Phase 2: Frontend Compose Pipeline ✅ COMPLETE

**New Files:**
- `src/lib/pretextLayout.ts` — Wrapper around `@chenglou/pretext` for DOM-free text measurement
- `src/agents/auditAgent.ts` — Coverage audit (55-65% target) + 2-pass layout refinement
- `src/agents/imageAgent.ts` — Thematic engraving selection from `public/engravings/`
- `src/store/contentStore.ts` — Zustand store: fetch issue, track clicks/tools, batch save
- `src/components/NewspaperComposer.tsx` — Orchestrates client pipeline
- `src/components/NewspaperRenderer.tsx` — CSS Grid page renderer (front page + section spreads)
- `src/components/ArticleCard.tsx` — Click-to-learn card with ink-dot indicator, drop-cap, expand
- `src/components/DeliveryAnimation.tsx` — GSAP bicycle delivery intro
- `src/components/FinishOverlay.tsx` — "Done for Today" summary + save
- `src/components/Masthead.tsx` — "The London Morning Chronicle" masthead
- `src/components/Footer.tsx` — Period-authentic footer
- `src/components/Navbar.tsx` — Section navigation bar

**Deleted (superseded):**
- `src/pages/*.tsx` — All old Kanban section pages
- `src/components/ArticleBlock.tsx` — Old article component

**Built & Verified:**
- `npm install` + `npm run build` succeeds (31 files, 0 errors)
- `dist/` folder generated with assets, engravings, index.html

### Phase 3: DevOps & Polish 🔄 IN PROGRESS

**Completed:**
- Portable Node.js setup for Windows development
- Git push to GitHub (`83e210a`)

**In Progress:**
- Docker containerization (Dockerfile, docker-compose.yml)
- Cloudflare Pages deployment pipeline
- VPS backend deployment (HK CN2 GIA)

---

## 4. Data Flow (End-to-End)

```
1. CRON (5:30 AM daily)
   └── engine.run_morning_routine(top_n=100)
       ├── SourceAggregator.fetch_all() → 100+ NewsItem objects
       ├── RankerEngine.score() → embedding-based personal relevance
       ├── LayoutAgent.categorize_items() → 7 sections, column spans
       ├── LayoutAgent.build_pages() → 3 NewspaperPage objects
       ├── AbstractAgent.prepare_abstracts() → 60-180 word abstracts
       └── KanbanSession.create() → session_id for tracking

2. USER OPENS APP
   └── Frontend fetches /api/newspaper/issue
       ├── Backend runs pipeline (if not cached)
       └── Returns NewspaperIssue JSON with session_id

3. FRONTEND RENDERS
   └── NewspaperComposer
       ├── Pretext measures abstract heights
       ├── AuditAgent checks coverage (55-65%)
       ├── ImageAgent places thematic engravings
       └── NewspaperRenderer displays pages

4. USER INTERACTS
   ├── Click article → POST /api/newspaper/click → records "interested"
   ├── "Done for Today" → POST /api/session/save → batch saves all clicks
   └── Backend learning loops update profile for tomorrow

5. NEXT DAY
   └── Profile updated → better ranking → better newspaper
```

---

## 5. What's Left (Future Phases)

### Phase 3A: AIGC Images (High Priority)
- Replace thematic engraving library with AI-generated images
- Prompt engineering per section theme
- Cost control: only generate for top 10 articles, cache results

### Phase 3B: Real-Time Updates
- WebSocket or Server-Sent Events for live article injection
- "Breaking News" banner for high-heat items

### Phase 3C: User Profiles & Multi-User
- Authentication (OAuth / simple token)
- Per-user profiles and session isolation
- Admin dashboard for managing sources

### Phase 3D: Mobile Polish
- Swipe gestures for mobile reading
- Offline reading with Service Worker
- PWA install prompt

### Phase 3E: Deployment Hardening
- Environment-based API URL (not hardcoded localhost)
- Health check endpoint
- Structured logging + monitoring
- Database backend (PostgreSQL) instead of JSON files

### Phase 4: Advanced Features
- Full-text search across historical articles
- Topic clustering visualization
- Shareable article snippets (social cards)
- Email digest (daily/weekly)
- Telegram bot inline queries

---

## 6. Current Repo State

### File Structure (Key Files)

```
muon-muse/
├── main.py                          # FastAPI app, all endpoints
├── pyproject.toml                   # Python deps
├── start.bat / start.ps1            # Local startup scripts
│
├── muse/
│   ├── engine.py                    # MuseEngine orchestrator
│   ├── models.py                    # NewsItem, EngagementEvent, etc.
│   ├── agents/
│   │   ├── layout_agent.py          # Newspaper categorization + page building
│   │   └── abstract_agent.py        # Content fetch + word budget trimming
│   ├── crawler.py                   # Content fetching pipeline
│   ├── embedder.py                  # Sentence-transformers embeddings
│   ├── ranker.py                    # Relevance scoring
│   ├── sources/                     # NewsNow, RSSHub, Native APIs
│   ├── learning/                    # FastLoop + SlowLoop optimizers
│   └── ui/                          # KanbanSession, NotionSync
│
├── front-end/app/
│   ├── src/
│   │   ├── App.tsx                  # Root router (wouter)
│   │   ├── main.tsx                 # React 19 entry
│   │   ├── index.css                # Newspaper theme tokens
│   │   ├── store/contentStore.ts    # Zustand state + API
│   │   ├── lib/pretextLayout.ts     # Text measurement
│   │   ├── agents/
│   │   │   ├── auditAgent.ts        # Coverage audit
│   │   │   └── imageAgent.ts        # Engraving selection
│   │   └── components/
│   │       ├── NewspaperComposer.tsx   # Pipeline orchestrator
│   │       ├── NewspaperRenderer.tsx   # Page layout renderer
│   │       ├── ArticleCard.tsx         # Article card component
│   │       ├── DeliveryAnimation.tsx   # GSAP intro
│   │       ├── FinishOverlay.tsx       # Save overlay
│   │       ├── Masthead.tsx            # Newspaper header
│   │       ├── Navbar.tsx              # Section nav
│   │       └── Layout.tsx              # Page wrapper (Lenis scroll)
│   ├── public/                      # Engravings, SVG ornaments, textures
│   ├── dist/                        # Built frontend (gitignored)
│   ├── package.json                 # React 19, Vite 7, Tailwind v3
│   └── vite.config.ts               # Proxy /api → localhost:8000
│
├── tests/
│   ├── test_newspaper.py            # 7 tests for newspaper pipeline
│   ├── test_api.py                  # API endpoint tests
│   ├── test_ranker.py               # Ranking logic tests
│   └── ...
│
├── dashboard/                       # Old Kanban UI (preserved at /admin)
├── data/                            # profile.json, tag_tree.json
├── docs/                            # Architecture docs, this roadmap
└── tools/                           # Portable Node.js (gitignored)
```

### Dependencies

**Backend:**
- FastAPI, uvicorn, pydantic
- sentence-transformers, numpy
- httpx, aiohttp (async fetching)
- APScheduler (cron)
- python-telegram-bot

**Frontend:**
- React 19, Vite 7, TypeScript 5.9
- Tailwind CSS v3, tailwindcss-animate
- Zustand 5 (state management)
- wouter 3 (routing)
- GSAP 3 (animations)
- Lenis 1.3 (smooth scroll)
- @chenglou/pretext 0.0.7 (text measurement)

---

## 7. Known Issues & Limitations

| Issue | Severity | Status |
|-------|----------|--------|
| API URL hardcoded to `localhost:8000` | 🔴 High | Needs env var for production |
| No database — profile/session in JSON | 🟡 Medium | Fine for single-user, needs DB for multi-user |
| Newspaper issue generation takes 30-60s cold | 🟡 Medium | Needs caching / pre-generation |
| `beforeunload` save handler is empty | 🟡 Medium | Should use `navigator.sendBeacon` |
| TypeScript type mismatches (camelCase vs snake_case) | 🟢 Low | Runtime works, types need cleanup |
| No auth — single shared session | 🟡 Medium | Blocks multi-user deployment |
| Engravings are static library (not AIGC) | 🟢 Low | Phase 3A will address |
| `test_get_profile` asserts version 2 (stale) | 🟢 Low | Pre-existing, unrelated |

---

## 8. Deployment Target Architecture

```
Production (musepaper.muonlabs.ai)
├── Cloudflare Pages
│   └── React frontend (auto-deploy from `release` branch)
│
├── Cloudflare DNS + CDN
│   ├── musepaper.muonlabs.ai → Pages
│   └── api.muonlabs.ai → VPS (orange cloud)
│
└── Hong Kong VPS (Docker)
    ├── FastAPI backend (port 8000)
    ├── Cron scheduler
    └── Persistent data volume (profile.json, cache)
```

**Deployment Gate:** `release` branch (not `main`). Push to `main` = dev. Merge to `release` = production deploy.

---

## 9. Quick Start (Local Development)

```bash
# Backend
cd F:\Projects\muon-muse
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (requires Node.js)
cd front-end/app
npm install
npm run build        # production build
npm run dev          # development server (port 3000, proxies /api)
```

---

*End of document. Last updated: 2026-05-23*
