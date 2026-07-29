"""
Qdrant Vector Database Storage and Retrieval Service.
Manages collection creation, vector payload insertion, and cosine similarity vector retrieval.
Supports in-memory mode (:memory:), local storage, or remote Qdrant Docker instance.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from backend.services.embeddings import get_embedding, get_embeddings_batch

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", ":memory:")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "study_companion_chunks")
VECTOR_DIMENSION = 768  # Matches Gemini text-embedding-004 output dimension


class QdrantService:
    def __init__(self, location: Optional[str] = None, collection_name: Optional[str] = None):
        self.location = location or QDRANT_URL
        self.collection_name = collection_name or QDRANT_COLLECTION
        
        # Initialize client
        if self.location == ":memory:":
            self.client = QdrantClient(":memory:")
        elif self.location.startswith("http://") or self.location.startswith("https://"):
            self.client = QdrantClient(url=self.location)
        else:
            self.client = QdrantClient(path=self.location)
            
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Creates Qdrant collection if it does not already exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=VECTOR_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                print(f"[Qdrant Service] Created collection '{self.collection_name}' with size={VECTOR_DIMENSION}.")
        except Exception as exc:
            print(f"[Qdrant Service] Collection initialization warning: {exc}")

    def reset_collection(self):
        """Recreates the collection to clear previous vector embeddings."""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
        except Exception:
            pass
        self._ensure_collection_exists()

    def store_chunks(self, chunks: List[Dict[str, Any]], document_name: str = "notes") -> int:
        """
        Stores chunks into Qdrant collection with their vector embeddings and original text payload.
        Returns total stored vector count.
        """
        if not chunks:
            return 0
            
        texts = [c["text"] for c in chunks]
        embeddings = get_embeddings_batch(texts)
        
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            payload = {
                "chunk_id": chunk.get("chunk_id", f"chunk_{i}"),
                "text": chunk["text"],
                "token_estimate": chunk.get("token_estimate", len(chunk["text"].split())),
                "document_name": document_name,
                "chunk_index": i
            }
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return len(points)

    def search_relevant_chunks(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """
        Generates query embedding and performs vector similarity search in Qdrant.
        Returns top matching chunks with similarity score and payload metadata.
        """
        query_vector = get_embedding(query)
        
        try:
            # Execute Qdrant vector search (compatible with both legacy search and qdrant-client 1.16+ query_points)
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=limit
                )
                search_results = response.points
            else:
                search_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=limit
                )
            
            retrieved = []
            for res in search_results:
                retrieved.append({
                    "score": round(float(res.score), 4),
                    "chunk_id": res.payload.get("chunk_id"),
                    "text": res.payload.get("text"),
                    "document_name": res.payload.get("document_name"),
                    "token_estimate": res.payload.get("token_estimate")
                })
            return retrieved
        except Exception as exc:
            print(f"[Qdrant Service] Search error: {exc}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """Returns collection stats (points count, status)."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "collection_name": self.collection_name,
                "status": info.status,
                "vectors_count": info.points_count,
                "vector_dimension": VECTOR_DIMENSION
            }
        except Exception as exc:
            return {"error": str(exc)}
