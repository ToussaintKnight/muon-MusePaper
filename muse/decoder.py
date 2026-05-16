"""Vector decoder — translates interest vector into search queries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np

from muse.embedder import encode, get_dim
from muse.models import TagNode, cosine_similarity


class VectorDecoder:
    """Decodes interest vector into search queries via tag tree matching."""

    def __init__(self, tag_tree_path: Optional[Path] = None):
        self.tag_tree_path = tag_tree_path or Path(__file__).parent.parent / "data" / "tag_tree.json"
        self.tags: list[TagNode] = []
        self._loaded = False

    def _load(self) -> None:
        """Load and flatten tag tree, precompute embeddings."""
        if self._loaded:
            return
        
        if not self.tag_tree_path.exists():
            # Use minimal default tree
            self.tags = _default_tags()
        else:
            data = json.loads(self.tag_tree_path.read_text(encoding="utf-8"))
            roots = [TagNode.from_dict(node) for node in data.get("roots", [])]
            self.tags = []
            for root in roots:
                self.tags.extend(root.flatten())
        
        # Precompute embeddings
        for tag in self.tags:
            text = f"{tag.path}. {' '.join(tag.keywords)}."
            tag.embedding = encode(text)
        
        self._loaded = True

    def vector_to_queries(
        self,
        vector: np.ndarray,
        top_k: int = 5,
        queries_per_tag: int = 2,
    ) -> list[dict]:
        """
        Convert interest vector into search queries.
        
        Returns list of {"query": str, "tag": str, "confidence": float}
        """
        self._load()
        if len(self.tags) == 0:
            return []
        
        # Cosine similarity against all tags
        scored = [
            (cosine_similarity(vector, tag.embedding), tag)
            for tag in self.tags
            if tag.embedding is not None
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        
        queries: list[dict] = []
        for sim, tag in scored[:top_k]:
            base = tag.name
            kws = tag.keywords[:3]
            for _ in range(queries_per_tag):
                q = f"{base} {' '.join(kws)} 最新".strip()
                queries.append({
                    "query": q,
                    "tag": tag.path,
                    "confidence": round(float(sim), 3),
                })
        
        return queries

    def get_top_tags(self, vector: np.ndarray, k: int = 5) -> list[tuple[float, str]]:
        """Return top-k matching tag paths with confidence."""
        self._load()
        scored = [
            (cosine_similarity(vector, tag.embedding), tag.path)
            for tag in self.tags
            if tag.embedding is not None
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(round(float(s), 3), path) for s, path in scored[:k]]


def _default_tags() -> list[TagNode]:
    """Minimal default tag tree for bootstrapping."""
    return [
        TagNode(id="ai-ml", name="AI/ML", path="AI/ML", keywords=["AI", "ML", "deep learning"]),
        TagNode(id="tools", name="Tools", path="Tools", keywords=["tool", "IDE", "framework"]),
        TagNode(id="design", name="Design", path="Design", keywords=["design", "UI", "UX"]),
        TagNode(id="startup", name="Startup", path="Startup", keywords=["startup", "SaaS", "融资"]),
        TagNode(id="academic", name="Academic", path="Academic", keywords=["paper", "research", "CVPR"]),
    ]
