"""Layout Agent — categorizes and slots articles into newspaper pages."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from muse.decoder import VectorDecoder
from muse.models import NewsItem


# ── Tag path → newspaper section mapping ───────────────────────────────

SECTION_MAP: dict[str, str] = {
    # AI branches → Science & Industry
    "AI": "science",
    "AI / LLM": "science",
    "AI / LLM / Proprietary": "science",
    "AI / LLM / Open Source": "science",
    "AI / Vision": "science",
    "AI / Vision / Image Gen": "science",
    "AI / Vision / Video Gen": "science",
    "AI / Agents": "science",
    "AI / Agents / RAG": "science",
    "AI / Agents / Coding": "science",
    "AI / Infrastructure": "science",
    "AI / Infra / Training": "science",
    "AI / Infra / Deployment": "science",
    # Science branches → Science & Industry
    "Science": "science",
    "Science / CS": "science",
    "Science / CS / Distributed": "science",
    "Science / Biology": "science",
    "Science / Biology / Longevity": "science",
    "Science / Biology / CRISPR": "science",
    "Science / Biology / Neuro": "science",
    "Science / Space": "science",
    "Science / Space / SpaceX": "science",
    "Science / Space / Mars": "science",
    "Science / Space / Physics": "science",
    "Science / Climate": "science",
    "Science / Climate / Fusion": "science",
    "Science / Climate / Batteries": "science",
    "Science / Climate / Carbon": "science",
    # Hardware → Science & Industry
    "Hardware": "science",
    "Hardware / Robotics": "science",
    "Hardware / Robotics / Drones": "science",
    "Hardware / Robotics / Humanoid": "science",
    "Hardware / Robotics / Industrial": "science",
    "Hardware / Chips": "science",
    "Hardware / Chips / Edge AI": "science",
    "Hardware / Chips / GPUs": "science",
    "Hardware / Chips / RISC-V": "science",
    "Hardware / Wearables": "science",
    "Hardware / Wearables / AR": "science",
    "Hardware / Wearables / Health": "science",
    # DevTools → Science & Industry
    "DevTools": "science",
    "DevTools / Languages": "science",
    "DevTools / Lang / Python": "science",
    "DevTools / Lang / Rust": "science",
    "DevTools / Lang / TypeScript": "science",
    "DevTools / DevOps": "science",
    "DevTools / DevOps / K8s": "science",
    "DevTools / DevOps / Serverless": "science",
    "DevTools / API": "science",
    "DevTools / API / AI SDKs": "science",
    "DevTools / API / GraphQL": "science",
    "DevTools / API / Webhooks": "science",
    # Data → Commerce & Trade
    "Data": "commerce",
    "Data / Databases": "commerce",
    "Data / DB / Vector": "commerce",
    "Data / DB / Graph": "commerce",
    "Data / Pipelines": "commerce",
    "Data / Pipeline / Spark": "commerce",
    "Data / Pipeline / dbt": "commerce",
    "Data / Pipeline / Airflow": "commerce",
    "Data / Visualization": "commerce",
    "Data / Viz / Tableau": "commerce",
    "Data / Viz / Observable": "commerce",
    "Data / Viz / Grafana": "commerce",
    # Design → Arts & Letters
    "Design": "arts",
    "Design / UI/UX": "arts",
    "Design / UI/UX / Systems": "arts",
    "Design / UI/UX / Mobile": "arts",
    "Design / Generative": "arts",
    "Design / Gen / Web": "arts",
    "Design / Gen / Code": "arts",
    "Design / Gen / Procedural": "arts",
    "Design / 3D": "arts",
    "Design / 3D / Blender": "arts",
    "Design / 3D / Three.js": "arts",
    "Design / 3D / Motion": "arts",
    # Product → Commerce & Trade
    "Product": "commerce",
    "Product / PM": "commerce",
    "Product / PM / Discovery": "commerce",
    "Product / Growth": "commerce",
    "Product / Growth / SEO": "commerce",
    "Product / Growth / Content": "commerce",
    "Product / Analytics": "commerce",
    "Product / Analytics / Mixpanel": "commerce",
    "Product / Analytics / PostHog": "commerce",
    "Product / Analytics / Amplitude": "commerce",
    # Startup → Commerce & Trade
    "Startup": "commerce",
    "Startup / Fundraising": "commerce",
    "Startup / Funding / VC": "commerce",
    "Startup / SaaS": "commerce",
    "Startup / SaaS / Indie": "commerce",
    "Startup / Operations": "commerce",
    "Startup / Ops / Remote": "commerce",
    "Startup / Ops / Stack": "commerce",
    "Startup / Ops / Legal": "commerce",
    # Finance → Commerce & Trade
    "Finance": "commerce",
    "Finance / DeFi": "commerce",
    "Finance / DeFi / DEX": "commerce",
    "Finance / Trading": "commerce",
    "Finance / Trading / Quant": "commerce",
    "Finance / Trading / Crypto": "commerce",
    "Finance / Macro": "commerce",
    "Finance / Macro / Fed": "commerce",
    "Finance / Macro / China": "commerce",
    # Security → Society & Fashion (security news)
    "Security": "society",
    "Security / AppSec": "society",
    "Security / AppSec / Bug Bounty": "society",
    "Security / Privacy": "society",
    "Security / Privacy / E2EE": "society",
    "Security / Privacy / Anon": "society",
    "Security / Compliance": "society",
    "Security / Compliance / SOC2": "society",
    "Security / Compliance / GDPR": "society",
}

# ── Column span by score rank ──────────────────────────────────────────

def _column_span(rank: int) -> int:
    if rank <= 3:
        return 3
    if rank <= 8:
        return 2
    return 1


# ── Abstract word budget by column span ────────────────────────────────

def _abstract_budget(column_span: int) -> int:
    if column_span == 3:
        return 180  # ~150-200 words
    if column_span == 2:
        return 120  # ~100-150 words
    return 80     # ~60-100 words


# ── Page templates ─────────────────────────────────────────────────────

PAGE_TEMPLATES: dict[str, dict] = {
    "front_page": {
        "sections": ["front"],
        "max_articles": 8,
    },
    "section_spread": {
        "sections": [],  # filled dynamically
        "max_articles": 12,
    },
    "classifieds": {
        "sections": ["classifieds"],
        "max_articles": 20,
    },
}

# Section → page group mapping
SECTION_PAGE_GROUPS: list[list[str]] = [
    ["front"],
    ["science"],
    ["commerce"],
    ["arts"],
    ["society", "foreign"],
    ["classifieds"],
]


# ── Models ─────────────────────────────────────────────────────────────

@dataclass
class SlotItem:
    """An article positioned in the newspaper layout."""

    # From NewsItem
    id: str
    headline: str
    url: str
    source: str
    score: Optional[float]
    pub_date: Optional[str]
    embedding: Optional[list[float]]
    top_tag: str

    # Layout
    section: str
    column_span: int
    abstract_budget: int
    page_number: int
    position_index: int

    # Generated metadata
    subheadline: str = ""
    byline: str = ""
    dateline: str = ""
    abstract: str = ""
    image_theme: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "headline": self.headline,
            "url": self.url,
            "source": self.source,
            "score": self.score,
            "pub_date": self.pub_date,
            "top_tag": self.top_tag,
            "section": self.section,
            "column_span": self.column_span,
            "abstract_budget": self.abstract_budget,
            "page_number": self.page_number,
            "position_index": self.position_index,
            "subheadline": self.subheadline,
            "byline": self.byline,
            "dateline": self.dateline,
            "abstract": self.abstract,
            "image_theme": self.image_theme,
        }


@dataclass
class NewspaperPage:
    """One page of the newspaper."""

    page_number: int
    layout_template: str
    sections: list[dict]  # [{"section": str, "articles": [SlotItem.to_dict()]}]

    def to_dict(self) -> dict:
        return {
            "page_number": self.page_number,
            "layout_template": self.layout_template,
            "sections": self.sections,
        }


@dataclass
class NewspaperDraftIssue:
    """A complete draft newspaper issue, ready for client refinement."""

    issue_date: str
    issue_number: int
    pages: list[NewspaperPage]
    session_id: str

    def to_dict(self) -> dict:
        return {
            "issue_date": self.issue_date,
            "issue_number": self.issue_number,
            "pages": [p.to_dict() for p in self.pages],
            "session_id": self.session_id,
        }


# ── Layout Agent ───────────────────────────────────────────────────────

class LayoutAgent:
    """Categorizes and slots articles into newspaper layout."""

    def __init__(self, decoder: VectorDecoder):
        self.decoder = decoder
        self.decoder._load()  # ensure tags are loaded

    def _guess_top_tag_path(self, item: NewsItem) -> str:
        """Get the best matching tag path for an item."""
        if item.embedding is None:
            return ""
        top_tags = self.decoder.get_top_tags(item.embedding, k=1)
        return top_tags[0][1] if top_tags else ""

    def _map_to_section(self, tag_path: str) -> str:
        """Map a tag path to a newspaper section."""
        # Exact match
        if tag_path in SECTION_MAP:
            return SECTION_MAP[tag_path]
        # Partial match (try parent paths)
        parts = tag_path.split(" / ")
        for i in range(len(parts), 0, -1):
            candidate = " / ".join(parts[:i])
            if candidate in SECTION_MAP:
                return SECTION_MAP[candidate]
        # Fallback by keyword heuristics
        lowered = tag_path.lower()
        if any(k in lowered for k in ["art", "design", "creat", "music", "visual"]):
            return "arts"
        if any(k in lowered for k in ["sci", "research", "paper", "biolog", "space", "climate"]):
            return "science"
        if any(k in lowered for k in ["startup", "business", "saas", "fund", "product", "growth", "market", "financ", "crypto", "trade", "defi"]):
            return "commerce"
        if any(k in lowered for k in ["game", "lifestyle", "social", "secur", "privac"]):
            return "society"
        return "classifieds"

    def _generate_subheadline(self, item: NewsItem) -> str:
        """Generate a subheadline from the title."""
        title = item.title
        if " — " in title:
            return title.split(" — ", 1)[1].strip()
        if " | " in title:
            return title.split(" | ", 1)[1].strip()
        if ": " in title:
            return title.split(": ", 1)[1].strip()
        # Truncate title to ~60 chars as subheadline
        if len(title) > 60:
            return title[:60] + "..."
        return ""

    def _generate_byline(self, source: str, section: str) -> str:
        """Generate a byline from source and section."""
        section_correspondent = {
            "front": "Special",
            "science": "Scientific",
            "commerce": "Commercial",
            "arts": "Arts",
            "society": "Society",
            "foreign": "Foreign",
            "classifieds": "Advertising",
        }
        corr = section_correspondent.get(section, "Special")
        return f"By Our {corr} Correspondent"

    def _generate_dateline(self, item: NewsItem) -> str:
        """Generate a dateline from pub_date and source."""
        date_str = ""
        if item.pub_date:
            date_str = item.pub_date.strftime("%B %d") if hasattr(item.pub_date, "strftime") else str(item.pub_date)
        source = item.source or "our Correspondent"
        return f"From {source}, {date_str}".strip(", ")

    def categorize_items(self, items: list[NewsItem]) -> list[SlotItem]:
        """Map each item to a newspaper section + column span + budget."""
        slots: list[SlotItem] = []
        for rank, item in enumerate(items, start=1):
            tag_path = self._guess_top_tag_path(item)
            section = self._map_to_section(tag_path)
            col_span = _column_span(rank)
            budget = _abstract_budget(col_span)

            slot = SlotItem(
                id=item.id,
                headline=item.title,
                url=item.url,
                source=item.source,
                score=item.score,
                pub_date=item.pub_date.isoformat() if item.pub_date else None,
                embedding=item.embedding.tolist() if item.embedding is not None else None,
                top_tag=tag_path,
                section=section,
                column_span=col_span,
                abstract_budget=budget,
                page_number=0,  # filled later
                position_index=0,  # filled later
                subheadline=self._generate_subheadline(item),
                byline=self._generate_byline(item.source, section),
                dateline=self._generate_dateline(item),
                image_theme=section,
            )
            slots.append(slot)
        return slots

    def build_pages(self, slots: list[SlotItem]) -> list[NewspaperPage]:
        """Distribute slots across pages with templates."""
        # Group slots by section
        by_section: dict[str, list[SlotItem]] = {}
        for slot in slots:
            by_section.setdefault(slot.section, []).append(slot)

        # Promote top-scored items to front page (regardless of section)
        sorted_by_score = sorted(slots, key=lambda s: s.score or 0, reverse=True)
        front_slots = sorted_by_score[:8]
        front_ids = {s.id for s in front_slots}

        # Remove front items from their original sections
        for slot in front_slots:
            slot.section = "front"
            by_section[slot.section] = [s for s in by_section.get(slot.section, []) if s.id not in front_ids]
            # Also remove from original section
            for sec, sec_slots in by_section.items():
                if sec != "front":
                    by_section[sec] = [s for s in sec_slots if s.id not in front_ids]

        pages: list[NewspaperPage] = []
        page_num = 1

        # Page 1: Front Page
        front_slots.sort(key=lambda s: s.score or 0, reverse=True)
        for i, slot in enumerate(front_slots):
            slot.page_number = page_num
            slot.position_index = i
        pages.append(NewspaperPage(
            page_number=page_num,
            layout_template="front_page",
            sections=[{"section": "front", "articles": [s.to_dict() for s in front_slots]}],
        ))
        page_num += 1

        # Remaining sections distributed across page groups
        remaining_sections = [sec for sec in by_section if sec != "front" and by_section[sec]]
        for sec in remaining_sections:
            sec_slots = by_section[sec]
            sec_slots.sort(key=lambda s: s.score or 0, reverse=True)
            for i, slot in enumerate(sec_slots):
                slot.page_number = page_num
                slot.position_index = i
            pages.append(NewspaperPage(
                page_number=page_num,
                layout_template="section_spread",
                sections=[{"section": sec, "articles": [s.to_dict() for s in sec_slots]}],
            ))
            page_num += 1

        # Last page: classifieds (lowest scored items not yet placed)
        unplaced = [s for s in slots if s.page_number == 0]
        if unplaced:
            unplaced.sort(key=lambda s: s.score or 0, reverse=True)
            for i, slot in enumerate(unplaced):
                slot.section = "classifieds"
                slot.page_number = page_num
                slot.position_index = i
                slot.column_span = 1
                slot.abstract_budget = 40
            pages.append(NewspaperPage(
                page_number=page_num,
                layout_template="classifieds",
                sections=[{"section": "classifieds", "articles": [s.to_dict() for s in unplaced]}],
            ))

        return pages
