"""
FastAPI Server Entry Point for AI Study Companion.
Project 2 (Week 3) — AI & Generative AI Fellowship Program
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

from backend.services.chunker import extract_text_from_filepath, chunk_text, ExtractionError
from backend.services.qdrant_service import QdrantService
from backend.services.planner import generate_study_plan, PlannerError
from backend.models import (
    IngestionResponse,
    RetrievalRequest,
    RetrievalResponse,
    PlanGenerationRequest,
    StudyPlanResponse
)

load_dotenv()

app = FastAPI(
    title="AI Study Companion API",
    description="Ingestion, Qdrant Vector Search, and LLM Study Plan Generation Engine.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Qdrant Vector Database Service
qdrant_service = QdrantService()


@app.get("/api/health")
def health_check():
    """Health check endpoint returning system & Qdrant status."""
    info = qdrant_service.get_collection_info()
    return {
        "status": "online",
        "service": "AI Study Companion API",
        "version": "1.0.0",
        "qdrant_info": info
    }


@app.get("/api/demo")
def run_sample_demo():
    """
    Preloads sample_notes.txt, chunks it, stores in Qdrant,
    and returns sample retrieval & generated study plan.
    """
    sample_file = Path("data/sample_notes.txt")
    if not sample_file.exists():
        raise HTTPException(status_code=404, detail="Sample notes file not found.")

    raw_text = extract_text_from_filepath(str(sample_file))
    chunks = chunk_text(raw_text, target_chunk_size=300)
    qdrant_service.reset_collection()
    stored_count = qdrant_service.store_chunks(chunks, document_name="sample_notes.txt")

    retrieved = qdrant_service.search_relevant_chunks("Neural Networks", limit=3)
    plan = generate_study_plan("Neural Networks", retrieved)
    return {
        "status": "demo_successful",
        "sample_document": "sample_notes.txt",
        "chunks_indexed": len(chunks),
        "vectors_stored": stored_count,
        "sample_retrieved_chunks": retrieved,
        "sample_generated_plan": plan
    }


@app.post("/api/ingest", response_model=IngestionResponse)
async def ingest_document(
    file: UploadFile = File(..., description="Syllabus or study notes document (.pdf, .docx, .txt)")
):
    """
    1. Document Upload: Receives PDF, DOCX, or TXT file.
    2. Chunking: Splits text into ~200-500 token chunks.
    3. Embeddings & Qdrant: Generates vectors and stores points in Qdrant DB.
    """
    filename = file.filename or "notes.txt"
    ext = Path(filename).suffix.lower()
    
    if ext not in (".pdf", ".txt", ".docx", ".doc"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: .pdf, .docx, .doc, .txt."
        )

    upload_path = UPLOAD_DIR / f"upload_{filename}"
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Step 1: Extract Text
        raw_text = extract_text_from_filepath(str(upload_path))
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Extracted document text is empty.")

        # Step 2: Chunk Text
        chunks = chunk_text(raw_text, target_chunk_size=350, min_chunk_size=80)
        if not chunks:
            raise HTTPException(status_code=400, detail="Failed to create text chunks from document.")

        # Step 3: Embed & Store in Qdrant
        # Reset collection to store clean fresh document embeddings
        qdrant_service.reset_collection()
        stored_count = qdrant_service.store_chunks(chunks, document_name=filename)

        return IngestionResponse(
            status="success",
            filename=filename,
            total_characters=len(raw_text),
            total_chunks=len(chunks),
            stored_vectors=stored_count,
            collection_name=qdrant_service.collection_name,
            message=f"Successfully ingested '{filename}', created {len(chunks)} chunks, and stored {stored_count} vectors in Qdrant."
        )

    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=f"Text Extraction Error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion Error: {str(exc)}")
    finally:
        if upload_path.exists():
            try:
                upload_path.unlink()
            except Exception:
                pass


@app.post("/api/retrieve", response_model=RetrievalResponse)
async def retrieve_chunks(request: RetrievalRequest):
    """
    Retrieval Endpoint: Queries Qdrant for top matching chunks given a query topic.
    """
    query = request.query.strip()
    limit = request.limit or 4

    if not query:
        raise HTTPException(status_code=400, detail="Query topic cannot be empty.")

    results = qdrant_service.search_relevant_chunks(query, limit=limit)
    return RetrievalResponse(
        query=query,
        retrieved_count=len(results),
        chunks=results
    )


@app.post("/api/generate-plan", response_model=StudyPlanResponse)
async def generate_plan(request: PlanGenerationRequest):
    """
    Study Plan Generation Endpoint:
    1. Retrieves top matching context chunks from Qdrant vector DB.
    2. Sends prompt + retrieved context to Gemini Flash LLM.
    3. Returns validated, structured Study Plan JSON.
    """
    query = request.query.strip()
    limit = request.limit or 4

    if not query:
        raise HTTPException(status_code=400, detail="Target topic cannot be empty.")

    # 1. Retrieve Context from Qdrant
    retrieved_chunks = qdrant_service.search_relevant_chunks(query, limit=limit)
    if not retrieved_chunks:
        raise HTTPException(
            status_code=400,
            detail="No study material found in Qdrant collection. Please upload a study document first."
        )

    # 2. LLM Study Plan Generation
    try:
        plan_json = generate_study_plan(query, retrieved_chunks)
        plan_json["retrieved_chunks_used"] = len(retrieved_chunks)
        return plan_json
    except PlannerError as exc:
        raise HTTPException(status_code=500, detail=f"Study Plan Generation Error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(exc)}")
