# AI Study Companion — Week 3 (Part 1)

> **Fellowship:** AI & Generative AI Fellowship @ Zeppelin Lab  
> **Project 2 (Week 3 Scope):** RAG Ingestion, Qdrant Vector Storage, Retrieval, and LLM JSON Study Plan Generation.  
> **Developer:** Solo Developer Mode (`@majidali1256` — Working 100% Alone)

---

## 🎯 Architecture Overview

AI Study Companion builds the ingestion and retrieval (RAG) foundation for study notes & syllabus documents.

```
                         ┌───────────────────────────────┐
                         │   Next.js 16 Frontend UI      │
                         │   http://localhost:3000       │
                         └──────────────┬────────────────┘
                                        │ (REST API / Multipart Form)
                                        ▼
                         ┌───────────────────────────────┐
                         │    FastAPI Backend Server     │
                         │   http://localhost:8000       │
                         └──────────────┬────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
│ Text Chunker       │       │ Qdrant Vector DB   │       │ Gemini Flash LLM   │
│ (~200–500 tokens)  │       │ (Cosine Vectors)   │       │ (JSON Study Plan)  │
└────────────────────┘       └────────────────────┘       └────────────────────┘
```

---

## ✨ Key Features & Pipeline Steps

1. **Document Upload Endpoint (`POST /api/ingest`)**:
   - Supports `.pdf`, `.docx`, `.doc`, and `.txt` study materials.
2. **Chunking Logic (`backend/services/chunker.py`)**:
   - Splits document into semantic chunks (~200–500 tokens / paragraph splitting with overlap).
3. **Embedding Generation (`backend/services/embeddings.py`)**:
   - Generates 768-dimensional normalized vector embeddings using Google Gemini embeddings.
4. **Qdrant Vector Database (`backend/services/qdrant_service.py`)**:
   - Stores vectors with raw text payloads in Qdrant DB. Supports `:memory:` mode for zero-setup execution as well as Qdrant Docker or Qdrant Cloud.
5. **Semantic Retrieval (`POST /api/retrieve`)**:
   - Performs cosine vector similarity search in Qdrant for any user topic or question.
6. **LLM Study Plan Generation (`POST /api/generate-plan`)**:
   - Passes retrieved Qdrant chunks + structured prompt to **Gemini Flash** to output a validated, structured JSON study plan.

---

## 🚀 How to Run Locally

### 1. Backend Setup (FastAPI)

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables (`.env`)**:
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   AI_MODEL=gemini-flash-lite-latest
   EMBEDDING_MODEL=models/embedding-001
   QDRANT_URL=:memory:
   QDRANT_COLLECTION=study_companion_chunks
   PORT=8000
   ```

3. **Start the FastAPI Backend Server**:
   ```bash
   PYTHONPATH=. /usr/bin/python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8002
   ```
   - API Documentation: `http://127.0.0.1:8002/docs`
   - System Health Check: `http://127.0.0.1:8002/api/health`

### 2. Frontend Setup (Next.js 16)

1. Navigate to the `frontend/` folder:
   ```bash
   cd frontend
   npm install
   ```

2. Start Next.js Development Server:
   ```bash
   npm run dev
   ```
   - Open browser at `http://localhost:3050`

---

## 🧪 Running Automated Tests

Run the Pytest suite to verify document chunking, vector dimension match, Qdrant search, and API endpoints:
```bash
PYTHONPATH=. /usr/bin/python3 -m pytest backend/tests/test_companion.py
```

---

## 🐋 Optional: Qdrant Setup with Docker

If you prefer running a dedicated Qdrant Docker container instead of the built-in in-memory mode:

1. **Run Qdrant via Docker**:
   ```bash
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```
2. Update `.env`:
   ```env
   QDRANT_URL=http://localhost:6333
   ```
