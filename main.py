"""Muse FastAPI application — localhost API server."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import numpy as np

from muse.engine import MuseEngine
from muse.models import NewsItem
from muse.ui.kanban import KanbanSession

# Global engine instance
_engine: Optional[MuseEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    global _engine
    _engine = MuseEngine()
    yield
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
    return FileResponse("dashboard/index.html")


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
    tags: list[dict]


class OnboardingConfirmRequest(BaseModel):
    selected_tag_ids: list[str]


class OnboardingConfirmResponse(BaseModel):
    success: bool
    vector_initialized: bool
    top_tags: list[tuple[float, str]]


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


@app.get("/api/search-queries", response_model=SearchQueriesResponse)
async def get_search_queries():
    """Get decoded search queries from current interest vector."""
    engine = _engine_instance()
    queries = engine.get_search_queries()
    return SearchQueriesResponse(queries=queries)


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
    tags = [
        {"id": t.id, "name": t.name, "path": t.path, "keywords": t.keywords}
        for t in engine.decoder.tags
    ]
    return OnboardingTagsResponse(tags=tags)


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
