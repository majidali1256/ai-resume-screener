"""
Embedding Generation Service.
Generates 768-dimensional vector embeddings for text chunks using Google Gemini text-embedding-004 model.
Includes a fallback pseudo-vector generator for offline/testing robustness.
"""

import os
import hashlib
import numpy as np
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _generate_fallback_embedding(text: str, dimension: int = 768) -> List[float]:
    """Generates a deterministic 768-dim normalized embedding based on sha256 hash for offline testing."""
    hash_bytes = hashlib.sha256(text.encode("utf-8")).digest()
    np.random.seed(int.from_bytes(hash_bytes[:4], "big"))
    vec = np.random.randn(dimension)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def get_embedding(text: str) -> List[float]:
    """Generates vector embedding for a single text string."""
    if not text or not text.strip():
        return [0.0] * 768

    if GEMINI_API_KEY:
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text.strip(),
                task_type="retrieval_document"
            )
            embedding = result.get("embedding", [])
            if embedding:
                return embedding
        except Exception as exc:
            print(f"[Embedding Service] Gemini API embedding error: {exc}. Using fallback embedding.")

    return _generate_fallback_embedding(text)


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generates vector embeddings for a list of text strings."""
    return [get_embedding(t) for t in texts]
