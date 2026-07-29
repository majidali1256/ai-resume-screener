"""
Automated Pytest Suite for AI Study Companion.
Tests chunking, embedding generation, Qdrant vector storage & retrieval, and FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.chunker import chunk_text
from backend.services.embeddings import get_embedding, _generate_fallback_embedding
from backend.services.qdrant_service import QdrantService
from backend.services.planner import generate_study_plan

client = TestClient(app)


def test_chunking_logic():
    """Verifies text chunking divides long text into ~200-500 word chunks."""
    sample_text = "\n\n".join([f"Paragraph {i}: " + "word " * 100 for i in range(10)])
    chunks = chunk_text(sample_text, target_chunk_size=300, min_chunk_size=50)
    assert len(chunks) > 1
    assert "chunk_id" in chunks[0]
    assert "text" in chunks[0]


def test_embedding_dimensions():
    """Verifies vector embedding produces 768 dimensions."""
    vec = get_embedding("Machine Learning and Neural Networks")
    assert isinstance(vec, list)
    assert len(vec) == 768


def test_qdrant_service_storage_and_search():
    """Verifies Qdrant collection creation, vector upsert, and similarity search."""
    q_service = QdrantService(location=":memory:", collection_name="test_collection")
    chunks = [
        {"chunk_id": "c1", "text": "Linear algebra is the study of vectors and matrices.", "token_estimate": 10},
        {"chunk_id": "c2", "text": "Photosynthesis is the process used by plants to convert light into energy.", "token_estimate": 12}
    ]
    stored = q_service.store_chunks(chunks, document_name="test.txt")
    assert stored == 2

    # Query Qdrant
    results = q_service.search_relevant_chunks("matrices and vectors", limit=1)
    assert len(results) == 1
    assert "Linear algebra" in results[0]["text"]


def test_health_check_endpoint():
    """Verifies GET /api/health endpoint status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "qdrant_info" in data


def test_study_plan_generation_fallback():
    """Verifies structured study plan JSON generation format."""
    chunks = [
        {"chunk_id": "c1", "score": 0.95, "text": "Artificial Intelligence involves machine learning, deep learning, and neural networks."}
    ]
    plan = generate_study_plan("Artificial Intelligence", chunks)
    assert "title" in plan
    assert "modules" in plan
    assert len(plan["modules"]) >= 1
    assert "key_terminology" in plan
