"""Embedding model wrapper — bge-small-zh singleton."""

from __future__ import annotations

from typing import Optional

import numpy as np

_model: Optional[object] = None
_model_name: str = "BAAI/bge-small-zh-v1.5"
_dim: int = 256


def get_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(_model_name)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load embedding model {_model_name}. "
                "Install with: pip install sentence-transformers"
            ) from exc
    return _model


def encode(text: str) -> np.ndarray:
    """Encode a single text string to a 256-dim vector."""
    model = get_model()
    emb = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
    return np.array(emb, dtype=np.float32)


def encode_batch(texts: list[str], batch_size: int = 32) -> list[np.ndarray]:
    """Batch encode texts."""
    if not texts:
        return []
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return [np.array(e, dtype=np.float32) for e in embeddings]


def get_dim() -> int:
    """Return embedding dimension."""
    return _dim
