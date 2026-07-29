# 🧠 PROJECT MEMORY & ARCHITECTURE GUIDE

**Project:** AI Study Companion — Ingestion & Retrieval Pipeline (Part 1)  
**Repository:** `Zeppelin Lab / AI Study Companion`  
**Fellowship:** AI & Generative AI Fellowship @ Zeppelin Lab (Week 3 Task)  
**Developer Mode:** Solo Developer (`@majidali1256` — Working 100% Alone / No Team Members)

---

## 📐 Project Overview & Architecture

AI Study Companion is a RAG (Retrieval-Augmented Generation) system that ingests syllabus and study notes documents, chunks them into semantic pieces, generates vector embeddings, indexes them in a **Qdrant Vector Database**, and performs semantic retrieval to generate structured **JSON Study Plans** using **Google Gemini Flash**.

```
                          ┌───────────────────────────────┐
                          │    Next.js 16 Frontend UI     │
                          │    http://localhost:3050      │
                          └──────────────┬────────────────┘
                                         │ (REST API / Multipart Form)
                                         ▼
                          ┌───────────────────────────────┐
                          │    FastAPI Backend Server     │
                          │    http://localhost:8000      │
                          └──────────────┬────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            ▼                            ▼                            ▼
 ┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
 │ Document Chunker   │       │ Qdrant Vector DB   │       │ Gemini Flash LLM   │
 │ (200-500 tokens)   │       │ (qdrant-client)    │       │ (Structured JSON)  │
 └────────────────────┘       └────────────────────┘       └────────────────────┘
```

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology | Key Libraries / Frameworks |
|---|---|---|
| **Frontend** | Next.js 16 (App Router) | React 19, Tailwind CSS v4, Framer Motion, Lucide Icons |
| **Backend** | Python 3.9–3.12 + FastAPI | Uvicorn, Pydantic v2, Python-dotenv, Tenacity |
| **Vector DB** | Qdrant | `qdrant-client` (Supports local memory mode & Qdrant server) |
| **Embeddings** | Gemini Embeddings | `text-embedding-004` (768 dimensions) |
| **LLM Engine** | Google Gemini Flash | `gemini-2.0-flash` / `gemini-flash-lite-latest` |
| **Testing** | Pytest | Automated test suite in `backend/tests/` |

---

## 📋 Build Order (One Step at a Time)

1. Document upload endpoint (`/api/ingest`)
2. Chunking logic (200–500 tokens / paragraph splitting)
3. Embedding generation (`text-embedding-004`)
4. Qdrant collection creation + vector storage
5. Retrieval endpoint (`/api/retrieve`)
6. Study plan generation (LLM + retrieved chunks → JSON)
7. Frontend rendering + polish + README update

---

## 📁 Repository Directory Structure

```
AI Study Companion/
├── backend/
│   ├── main.py                 # FastAPI server entry point
│   ├── services/
│   │   ├── chunker.py          # Text chunker (~200-500 tokens)
│   │   ├── embeddings.py       # Gemini text-embedding-004 service
│   │   ├── qdrant_service.py   # Qdrant collection & vector search manager
│   │   └── planner.py          # Gemini LLM study plan generator
│   └── tests/
│       └── test_companion.py   # Pytest test suite
├── frontend/                   # Next.js 16 + React 19 + Tailwind UI
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide & Qdrant documentation
└── MEMORY.md                   # Single source of truth (this file)
```
