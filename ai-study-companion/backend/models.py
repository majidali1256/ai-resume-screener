"""
Pydantic Request & Response Data Models for AI Study Companion API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class IngestionResponse(BaseModel):
    status: str = "success"
    filename: str
    total_characters: int
    total_chunks: int
    stored_vectors: int
    collection_name: str
    message: str


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Topic or question to search in study notes")
    limit: Optional[int] = Field(4, ge=1, le=20, description="Top matching chunks to retrieve")


class ChunkMetadata(BaseModel):
    score: float
    chunk_id: str
    text: str
    document_name: Optional[str] = None
    token_estimate: Optional[int] = None


class RetrievalResponse(BaseModel):
    query: str
    retrieved_count: int
    chunks: List[ChunkMetadata]


class PlanGenerationRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Target topic for study plan")
    limit: Optional[int] = Field(4, ge=1, le=10, description="Number of context chunks to retrieve from Qdrant")


class Module(BaseModel):
    module_number: int
    module_title: str
    estimated_minutes: int
    key_concepts: List[str]
    learning_objectives: List[str]
    action_steps: List[str]
    review_questions: List[str]


class Terminology(BaseModel):
    term: str
    definition: str


class StudyPlanResponse(BaseModel):
    title: str
    target_topic: str
    overview: str
    estimated_total_hours: float
    modules: List[Module]
    key_terminology: List[Terminology]
    checkpoint_tips: List[str]
    retrieved_chunks_used: int
