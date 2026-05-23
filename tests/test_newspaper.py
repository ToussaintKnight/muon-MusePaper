"""Tests for MusePaper newspaper pipeline."""

import pytest
from muse.agents.layout_agent import LayoutAgent, SECTION_MAP, _column_span, _abstract_budget
from muse.agents.abstract_agent import AbstractAgent
from muse.models import NewsItem, TagNode
from muse.decoder import VectorDecoder


class TestLayoutAgent:
    def test_column_span_ranking(self):
        assert _column_span(1) == 3
        assert _column_span(3) == 3
        assert _column_span(4) == 2
        assert _column_span(8) == 2
        assert _column_span(9) == 1
        assert _column_span(100) == 1

    def test_abstract_budget(self):
        assert _abstract_budget(3) == 180
        assert _abstract_budget(2) == 120
        assert _abstract_budget(1) == 80

    def test_section_map_coverage(self):
        # All tag paths in the tree should have a mapping
        assert "AI" in SECTION_MAP
        assert "Science" in SECTION_MAP
        assert "Design" in SECTION_MAP
        assert "Startup" in SECTION_MAP

    def test_categorize_items(self):
        decoder = VectorDecoder()
        agent = LayoutAgent(decoder)

        items = [
            NewsItem(id="1", title="AI Breakthrough", url="http://a.com", source="test", source_type="test", score=0.9),
            NewsItem(id="2", title="New Startup", url="http://b.com", source="test", source_type="test", score=0.8),
            NewsItem(id="3", title="Design Tool", url="http://c.com", source="test", source_type="test", score=0.7),
            NewsItem(id="4", title="Security Alert", url="http://d.com", source="test", source_type="test", score=0.6),
            NewsItem(id="5", title="Finance News", url="http://e.com", source="test", source_type="test", score=0.5),
            NewsItem(id="6", title="Science Paper", url="http://f.com", source="test", source_type="test", score=0.4),
            NewsItem(id="7", title="Dev Tool", url="http://g.com", source="test", source_type="test", score=0.3),
            NewsItem(id="8", title="Data Pipeline", url="http://h.com", source="test", source_type="test", score=0.2),
            NewsItem(id="9", title="Product Launch", url="http://i.com", source="test", source_type="test", score=0.1),
            NewsItem(id="10", title="Hardware Review", url="http://j.com", source="test", source_type="test", score=0.05),
        ]
        slots = agent.categorize_items(items)

        assert len(slots) == 10
        assert slots[0].column_span == 3  # rank 1
        assert slots[1].column_span == 3  # rank 2
        assert slots[2].column_span == 3  # rank 3
        assert slots[3].column_span == 2  # rank 4
        assert slots[7].column_span == 2  # rank 8
        assert slots[8].column_span == 1  # rank 9
        assert slots[9].column_span == 1  # rank 10

    def test_build_pages(self):
        decoder = VectorDecoder()
        agent = LayoutAgent(decoder)

        items = [
            NewsItem(id=str(i), title=f"Article {i}", url=f"http://a{i}.com", source="test", source_type="test", score=0.9 - i * 0.01)
            for i in range(20)
        ]
        slots = agent.categorize_items(items)
        pages = agent.build_pages(slots)

        assert len(pages) >= 2  # at least front page + one section
        assert pages[0].layout_template == "front_page"
        assert pages[0].page_number == 1


class TestAbstractAgent:
    def test_trim_to_words(self):
        agent = AbstractAgent()
        text = "This is a test sentence. Here is another one. And a third."
        result = agent._trim_to_words(text, 6)
        assert len(result.split()) <= 8  # slightly over is OK if we end at sentence boundary
        assert result.endswith(".")

    def test_make_teaser(self):
        agent = AbstractAgent()
        article = {
            "headline": "Big News Today",
            "source": "newsnow_test",
        }
        teaser = agent._make_teaser(article, 50)
        assert "Big News Today" in teaser
