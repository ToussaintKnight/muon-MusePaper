"""Abstract Agent — fetches and prepares article abstracts to fit word budgets."""

from __future__ import annotations

import re
from typing import Optional

from muse.agents.layout_agent import NewspaperPage, SlotItem
from muse.content_fetcher import fetch_article


# ── Abstract Agent ─────────────────────────────────────────────────────

class AbstractAgent:
    """Fetches and prepares article abstracts to fit word budgets."""

    # How many top articles get full content fetch
    FULL_FETCH_LIMIT = 20

    # How many sentences to extract as fallback abstract
    FALLBACK_SENTENCES = 3

    async def prepare_abstracts(self, pages: list[NewspaperPage]) -> list[NewspaperPage]:
        """
        Prepare abstracts for all articles across all pages.

        For top articles by score: fetch original content, truncate to budget.
        For rest: use title + source teaser.
        """
        # Collect all slots across pages
        all_slots: list[tuple[NewspaperPage, dict, dict]] = []
        for page in pages:
            for sec in page.sections:
                for article in sec["articles"]:
                    all_slots.append((page, sec, article))

        # Sort by score descending to prioritize full fetch for top articles
        all_slots.sort(key=lambda x: x[2].get("score") or 0, reverse=True)

        for idx, (page, sec, article) in enumerate(all_slots):
            budget = article.get("abstract_budget", 80)
            if idx < self.FULL_FETCH_LIMIT:
                abstract = await self._fetch_and_trim(
                    article["url"],
                    article["headline"],
                    budget,
                )
            else:
                abstract = self._make_teaser(article, budget)
            article["abstract"] = abstract

        return pages

    async def _fetch_and_trim(self, url: str, title: str, word_budget: int) -> str:
        """Fetch article content and trim to word budget."""
        try:
            fetched = await fetch_article(url)
            if fetched["ok"] and fetched["text"]:
                text = fetched["text"]
                # If we got a title different from the headline, note it
                if fetched["title"] and fetched["title"] != title:
                    text = f"{fetched['title']}. {text}"
                return self._trim_to_words(text, word_budget)
        except Exception:
            pass
        # Fallback: title-only teaser
        return self._trim_to_words(title, word_budget)

    def _trim_to_words(self, text: str, word_budget: int) -> str:
        """Trim text to approximately word_budget words, ending at sentence boundary."""
        words = text.split()
        if len(words) <= word_budget:
            return text

        # Take word_budget words, then extend to next sentence end
        trimmed = " ".join(words[:word_budget])
        # Find last sentence-ending punctuation
        for punct in ".!?":
            last = trimmed.rfind(punct)
            if last > len(trimmed) * 0.7:  # only if we have substantial text
                trimmed = trimmed[: last + 1]
                break
        return trimmed.strip()

    def _make_teaser(self, article: dict, word_budget: int) -> str:
        """Create a teaser abstract from title and source when content fetch is skipped."""
        title = article.get("headline", "")
        source = article.get("source", "")
        # Clean up source name
        source_clean = re.sub(r"^newsnow_|^rsshub_|^native_", "", source, flags=re.I)
        source_clean = source_clean.replace("_", " ").title()

        teaser = f"{title}"
        if source_clean:
            teaser += f" — Reports from {source_clean} indicate continued developments in this area."
        return self._trim_to_words(teaser, word_budget)
