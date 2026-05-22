"""Muse FastAPI application — localhost API server."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import numpy as np

# Resolve project root so static paths work regardless of CWD
PROJECT_ROOT = Path(__file__).resolve().parent

from muse.engine import MuseEngine
from muse.models import NewsItem
from muse.ui.kanban import KanbanSession
from muse.cron import MuseCron
from muse.telegram_bot import MuseTelegramBot

# Global instances
_engine: Optional[MuseEngine] = None
_cron: Optional[MuseCron] = None
_bot: Optional[MuseTelegramBot] = None


async def _run_daily_briefing():
    """Callback for the cron scheduler: run morning routine + Telegram push."""
    global _engine, _bot
    if _engine is None:
        return
    try:
        items = await _engine.run_morning_routine(top_n=50)
        if _bot and _bot.is_configured():
            item_dicts = [
                {"title": i.title, "url": i.url, "score": i.score}
                for i in items[:10]
            ]
            await _bot.send_daily_briefing(item_dicts)
    except Exception as exc:
        print(f"[Cron] daily briefing failed: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    global _engine, _cron, _bot
    _engine = MuseEngine()
    _cron = MuseCron(run_callback=_run_daily_briefing)
    _bot = MuseTelegramBot()
    # Eager-load embedding model so first request isn't slow
    from muse.embedder import get_model
    try:
        get_model()
    except Exception:
        pass
    # Auto-schedule daily run if not already scheduled
    _cron.schedule_daily(hour=5, minute=30)
    _cron.start()
    yield
    if _cron:
        _cron.stop()
    if _engine:
        await _engine.close()


app = FastAPI(
    title="Muse",
    description="Daily intelligence engine that learns what you care about.",
    version="2.0.0",
    lifespan=lifespan,
)

# ── Dashboard ──────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve the Kanban dashboard."""
    return FileResponse(PROJECT_ROOT / "dashboard" / "index.html")


# ── Request/Response Models ────────────────────────────────────────────

class ItemResponse(BaseModel):
    id: str
    title: str
    url: str
    source: str
    score: Optional[float] = None
    pub_date: Optional[str] = None


class MoveRequest(BaseModel):
    item_id: str
    to_bucket: str  # "tools" | "interested" | "not_interested"


class SaveRequest(BaseModel):
    session_id: str


class SaveResponse(BaseModel):
    vector_delta: float
    notion_synced: int
    new_top_tags: list[str]
    effectiveness_score: Optional[float] = None


class ProfileResponse(BaseModel):
    version: int
    embedding_model: str
    save_count: int
    top_tags: list[tuple[float, str]]
    keyword_weights: dict[str, float]
    created_at: str
    updated_at: str


class SearchQueriesResponse(BaseModel):
    queries: list[str]


class HealthResponse(BaseModel):
    profile_exists: bool
    save_count: int
    sources: dict[str, bool]
    notion_configured: bool


class MetricsResponse(BaseModel):
    daily_metrics: list[dict]


class OnboardingTagsResponse(BaseModel):
    roots: list[dict]


class OnboardingConfirmRequest(BaseModel):
    selected_tag_ids: list[str]


class OnboardingConfirmResponse(BaseModel):
    success: bool
    vector_initialized: bool
    top_tags: list[tuple[float, str]]


class ReadingItemResponse(BaseModel):
    id: str
    title: str
    url: str
    source: str
    status: str
    added_at: str
    read_at: Optional[str] = None
    summary: Optional[str] = None
    score: Optional[float] = None


class SummarizeRequest(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = "https://api.openai.com/v1"
    model: Optional[str] = "gpt-4o-mini"


class ContentFetchRequest(BaseModel):
    url: str


class ContentFetchResponse(BaseModel):
    title: str
    text: str
    url: str
    ok: bool
    error: Optional[str] = None


# ── Helper ─────────────────────────────────────────────────────────────

def _engine_instance() -> MuseEngine:
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return _engine


def _item_to_response(item: NewsItem) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        title=item.title,
        url=item.url,
        source=item.source,
        score=item.score,
        pub_date=item.pub_date.isoformat() if item.pub_date else None,
    )


# ── API Endpoints ──────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"name": "Muse", "version": "2.0.0", "status": "running"}


@app.get("/api/items/today", response_model=list[ItemResponse])
async def get_today_items():
    """Fetch and rank today's top items."""
    engine = _engine_instance()
    items = await engine.run_morning_routine(top_n=50)
    return [_item_to_response(item) for item in items]


@app.get("/api/profile", response_model=ProfileResponse)
async def get_profile():
    """Get current user profile."""
    engine = _engine_instance()
    p = engine.profile
    return ProfileResponse(
        version=p.version,
        embedding_model=p.embedding_model,
        save_count=p.save_count,
        top_tags=engine.get_top_tags(k=5),
        keyword_weights=p.keyword_weights,
        created_at=p.created_at.isoformat(),
        updated_at=p.updated_at.isoformat(),
    )


@app.post("/api/profile/reset")
async def reset_profile():
    """Delete profile.json and reinitialize engine to force cold-start onboarding."""
    global _engine
    engine = _engine_instance()
    profile_path = engine.profile_path
    if profile_path.exists():
        profile_path.unlink()
    # Reinitialize engine so next request sees a fresh profile
    _engine = MuseEngine()
    return {"success": True, "message": "Profile reset. Refresh to start onboarding."}


# ── Reading Queue Endpoints ────────────────────────────────────────────

@app.get("/api/reading/queue", response_model=list[ReadingItemResponse])
async def get_reading_queue():
    """Return the user's reading queue (unread + read)."""
    engine = _engine_instance()
    queue = engine.profile.reading_queue
    return [
        ReadingItemResponse(
            id=r.id,
            title=r.title,
            url=r.url,
            source=r.source,
            status=r.status,
            added_at=r.added_at.isoformat(),
            read_at=r.read_at.isoformat() if r.read_at else None,
            summary=r.summary,
            score=r.score,
        )
        for r in reversed(queue)
    ]


@app.post("/api/reading/{item_id}/read")
async def mark_item_read(item_id: str):
    """Mark a reading item as read."""
    engine = _engine_instance()
    for item in engine.profile.reading_queue:
        if item.id == item_id:
            item.status = "read"
            item.read_at = datetime.now()
            engine.profile.save(engine.profile_path)
            return {"success": True}
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/api/reading/{item_id}")
async def delete_reading_item(item_id: str):
    """Remove an item from the reading queue."""
    engine = _engine_instance()
    engine.profile.reading_queue = [
        r for r in engine.profile.reading_queue if r.id != item_id
    ]
    engine.profile.save(engine.profile_path)
    return {"success": True}


@app.post("/api/reading/{item_id}/summarize")
async def summarize_item(item_id: str, req: SummarizeRequest):
    """Generate LLM summary for a reading item. Returns cached summary if exists."""
    engine = _engine_instance()
    item = next((r for r in engine.profile.reading_queue if r.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.summary:
        return {"success": True, "summary": item.summary, "cached": True}
    
    # If content not fetched yet, fetch it first
    if not item.content:
        from muse.content_fetcher import fetch_article
        fetched = await fetch_article(item.url)
        if fetched["ok"]:
            item.content = fetched["text"]
            item.title = fetched["title"] or item.title
        else:
            item.content = f"Could not fetch content: {fetched['error']}"
    
    # Call LLM if API key provided, otherwise placeholder
    if req.api_key:
        from muse.llm import distill_article
        item.summary = await distill_article(
            title=item.title,
            content=item.content,
            api_key=req.api_key,
            base_url=req.base_url,
            model=req.model,
        )
    else:
        item.summary = f"## {item.title}\n\n*AI summary requires an API key. Add one in settings to enable distillation.*\n\n---\n\n{item.content[:800]}..." if item.content else "*Content not available.*"
    
    engine.profile.save(engine.profile_path)
    return {"success": True, "summary": item.summary, "cached": False}


@app.post("/api/content/fetch", response_model=ContentFetchResponse)
async def fetch_content(req: ContentFetchRequest):
    """Fetch and extract article text from a URL."""
    from muse.content_fetcher import fetch_article
    result = await fetch_article(req.url)
    return ContentFetchResponse(**result)


@app.get("/api/search-queries", response_model=SearchQueriesResponse)
async def get_search_queries():
    """Get decoded search queries from current interest vector."""
    engine = _engine_instance()
    queries = engine.get_search_queries()
    return SearchQueriesResponse(queries=queries)


# ── Cron Endpoints ─────────────────────────────────────────────────────

@app.post("/api/cron/trigger")
async def trigger_cron():
    """Manually trigger the daily briefing run."""
    await _run_daily_briefing()
    return {"success": True, "message": "Daily briefing triggered"}


@app.get("/api/cron/status")
async def get_cron_status():
    """Get cron scheduler status."""
    global _cron
    next_run = _cron.get_next_run() if _cron else None
    return {
        "scheduled": _cron.is_scheduled() if _cron else False,
        "next_run": next_run.isoformat() if next_run else None,
    }


@app.get("/api/health", response_model=HealthResponse)
async def get_health():
    """Health check for all sources."""
    engine = _engine_instance()
    health = await engine.health_check()
    return HealthResponse(**health)


@app.get("/api/metrics/daily", response_model=MetricsResponse)
async def get_daily_metrics():
    """Get daily effectiveness metrics history."""
    engine = _engine_instance()
    return MetricsResponse(
        daily_metrics=engine.profile.daily_metrics_history[-30:]  # last 30 days
    )


# ── Onboarding Endpoints ───────────────────────────────────────────────

@app.get("/api/onboarding/tags", response_model=OnboardingTagsResponse)
async def get_onboarding_tags():
    """Return the interest tag tree for cold-start selection."""
    engine = _engine_instance()
    engine.decoder._load()

    def node_to_dict(node):
        return {
            "id": node.id,
            "name": node.name,
            "path": node.path,
            "keywords": node.keywords,
            "children": [node_to_dict(c) for c in node.children],
        }

    roots = [node_to_dict(r) for r in engine.decoder.roots]
    return OnboardingTagsResponse(roots=roots)


@app.post("/api/onboarding/confirm", response_model=OnboardingConfirmResponse)
async def confirm_onboarding(req: OnboardingConfirmRequest):
    """Initialize interest vector from selected tags."""
    engine = _engine_instance()
    engine.decoder._load()
    
    # Find selected tags
    selected = [t for t in engine.decoder.tags if t.id in req.selected_tag_ids]
    if not selected:
        raise HTTPException(status_code=400, detail="No valid tags selected")
    
    # Encode each selected tag and average them
    from muse.embedder import encode
    import numpy as np
    embeddings = [encode(f"{t.path}. {' '.join(t.keywords)}.") for t in selected]
    avg_vector = np.mean(embeddings, axis=0)
    avg_vector = avg_vector / (np.linalg.norm(avg_vector) + 1e-10)
    
    engine.profile.set_vector(avg_vector)
    engine.profile.save(engine.profile_path)
    
    top = engine.get_top_tags(k=5)
    return OnboardingConfirmResponse(
        success=True,
        vector_initialized=True,
        top_tags=top,
    )


# ── Session Endpoints ──────────────────────────────────────────────────

# In-memory session store (sufficient for single-user localhost)
_sessions: dict[str, KanbanSession] = {}


@app.post("/api/session/start")
async def start_session():
    """Start a new Kanban session with today's items."""
    engine = _engine_instance()
    items = await engine.run_morning_routine(top_n=50)
    session = KanbanSession.create(items, engine.profile)
    _sessions[session.session_id] = session
    return {
        "session_id": session.session_id,
        "items": [_item_to_response(item) for item in session.items],
    }


@app.post("/api/session/move")
async def move_item(req: MoveRequest):
    """Move an item to a bucket."""
    # Find session containing this item
    session = None
    for s in _sessions.values():
        if any(item.id == req.item_id for item in s.items):
            session = s
            break
    
    if session is None:
        raise HTTPException(status_code=404, detail="Item not found in any session")
    
    session.move_item(req.item_id, req.to_bucket)
    return {"success": True, "session_id": session.session_id}


@app.post("/api/session/save", response_model=SaveResponse)
async def save_session(req: SaveRequest):
    """Save a session: update vector, sync Notion, compute metrics."""
    session = _sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = _engine_instance()
    result = await engine.handle_save(session)
    
    # Clean up session
    del _sessions[req.session_id]
    
    return SaveResponse(
        vector_delta=result.vector_delta,
        notion_synced=result.notion_synced,
        new_top_tags=result.new_top_tags,
        effectiveness_score=result.effectiveness_score,
    )


@app.post("/api/run")
async def run_pipeline():
    """Manually trigger the morning routine."""
    engine = _engine_instance()
    items = await engine.run_morning_routine(top_n=50)
    return {
        "count": len(items),
        "items": [_item_to_response(item) for item in items],
    }


# ── Entry Point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
