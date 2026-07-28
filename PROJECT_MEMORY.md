# 🧠 PROJECT MEMORY & ARCHITECTURE GUIDE
**Project:** MATCH.AI — Enterprise AI Resume Screener & Structured Feedback System  
**Repository:** `majidali1256/ai-resume-screener`  
**Fellowship:** AI & Generative AI Fellowship @ Zeppelin Lab (Weeks 1 & 2 Completed)  
**Developer Mode:** Solo Developer (`@majidali1256`)

---

## 📐 Project Overview & Architecture

MATCH.AI is a full-stack, deterministic AI resume screening engine that evaluates candidate resumes (`.pdf`, `.docx`, `.doc`, `.txt`) against job description specifications using **Google Gemini Flash** with zero-temperature determinism and strict **Pydantic schema validation**.

```
                         ┌───────────────────────────────┐
                         │   Next.js 16 Frontend UI      │
                         │   http://localhost:3000       │
                         └──────────────┬────────────────┘
                                        │ (REST API / Multipart Form)
                                        ▼
                         ┌───────────────────────────────┐
                         │    FastAPI Backend Server     │
                         │   http://localhost:8001       │
                         └──────────────┬────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
│ Text Extractor     │       │ Gemini Flash Engine│       │ Evidence Grounding │
│ (pypdf/python-docx)│       │ (zero-temp JSON)   │       │ Verifier           │
└────────────────────┘       └────────────────────┘       └────────────────────┘
```

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology | Key Libraries / Frameworks |
|---|---|---|
| **Frontend** | Next.js 16 (App Router) | React 19, Tailwind CSS v4, Framer Motion (`framer-motion`), Lucide Icons (`lucide-react`) |
| **Backend** | Python 3.9–3.12 + FastAPI | Uvicorn, Pydantic v2, Python-dotenv, Tenacity |
| **AI Engine** | Google Gemini Flash | `gemini-flash-lite-latest` / `gemini-2.0-flash` (via direct REST API) |
| **Document Extractors** | Local Text Extractors | `pypdf` (PDF), `python-docx` (DOCX/DOC), UTF-8 text parser |
| **Testing** | Pytest | Automated test suite in `tests/test_screener.py` (5/5 pass) |
| **Deployment** | Multi-Platform | Hugging Face Spaces (Gradio `app.py`), GitHub Public Repo, Docker |

---

## 🚀 How to Run Locally (No Mistakes!)

### 1. Environment Setup
Make sure `.env` exists in the workspace root:
```env
GEMINI_API_KEY=AIzaSy...your_gemini_api_key...
AI_MODEL=gemini-flash-lite-latest
PORT=8000
```
> ⚠️ **Security Rule:** `.env` is ignored by `.gitignore`. Never commit API keys to git.

### 2. Start Backend Server (FastAPI)
Run from workspace root:
```bash
PYTHONPATH=$HOME/Library/Python/3.9/lib/python/site-packages /usr/bin/python3 -m uvicorn main:app --reload --port 8001
```
- **Backend API:** `http://localhost:8001`
- **Swagger Docs:** `http://localhost:8001/docs`
- **Health Check:** `http://localhost:8001/api/health`

### 3. Start Frontend Dev Server (Next.js)
Run from `frontend/` directory:
```bash
cd frontend
npm run dev -- -p 3000
```
- **Frontend Dashboard:** `http://localhost:3000`

---

## 📁 Repository Directory Structure

```
ai-resume-screener/
├── main.py                     # FastAPI server entry point (Routes: /api/scan, /api/demo, /api/health)
├── app.py                      # Gradio entry point for Hugging Face Spaces
├── resume_scanner/
│   ├── assessor.py             # Gemini Flash LLM engine with zero-temp JSON schema & retry
│   ├── extractor.py            # Local document text extractor (.pdf, .docx, .doc, .txt)
│   ├── grounding.py            # Evidence grounding verifier module
│   └── models.py               # Pydantic Assessment JSON schema definition
├── frontend/                   # Next.js 16 + React 19 + Tailwind CSS + Framer Motion UI
│   ├── src/app/
│   │   ├── page.tsx            # Main Interactive 3D Dashboard UI component
│   │   ├── layout.tsx          # Root Layout & Metadata (MATCH.AI)
│   │   └── globals.css         # Glassmorphism & custom utility styles
│   ├── next.config.ts          # Turbopack root config (`turbopack: { root: __dirname }`)
│   └── package.json            # Frontend dependencies
├── data/
│   ├── benchmark/              # Test benchmarks (resume & JD pairs)
│   ├── sample_resume.txt       # Built-in sample resume for quick demo
│   └── sample_jd.txt           # Built-in sample JD for quick demo
├── tests/
│   └── test_screener.py        # Automated Pytest suite (5/5 passing)
├── screenshots/                # Capture directory for GitHub PRs and submission PDFs
├── .gitignore                  # Excludes .env, node_modules, .venv, uploads, caches
├── README.md                   # Full documentation with architecture, setup, and roles
└── PROJECT_MEMORY.md           # This file (AI IDE & developer memory reference)
```

---

## 🔑 Critical Bug Fixes & Lessons Learned

1. **Extraction Bug Fix in `main.py` & `app.py`:**
   - *Issue:* When `jd_text` was pasted into the text box, `main.py` previously passed `resume_path` twice to `prepare_scanner_inputs(resume_path, resume_path)`.
   - *Fix:* Changed line 124 in `main.py` and line 38 in `app.py` to call `extract_text_from_file(str(resume_path), label="Resume")` directly.

2. **Port Conflict & Backend Fallback:**
   - *Issue:* Port 8000 on macOS can get locked in `CLOSED`/`TIME_WAIT` state by old processes.
   - *Fix:* Backend runs on port `8001`. `frontend/src/app/page.tsx` fetches from `http://localhost:8001/api/scan` with automatic fallback to 8000.

3. **Turbopack Workspace Root Warning in Next.js 16:**
   - *Issue:* Next.js Turbopack threw panic errors when searching parent directories for `package-lock.json`.
   - *Fix:* Configured `turbopack: { root: __dirname }` and `output: "standalone"` in `frontend/next.config.ts`.

4. **Offline Font Loading in Next.js:**
   - *Fix:* Replaced `next/font/google` in `layout.tsx` with clean system font stack so production builds compile 100% offline without sandbox network errors.

5. **Gemini API Model Quotas:**
   - *Fix:* Configured `AI_MODEL=gemini-flash-lite-latest` in `.env` to avoid free tier 429 rate limiting on `gemini-2.0-flash`.

---

## 🌿 Git & Workflow Guidelines

- **Developer Mode:** Solo developer (`@majidali1256`).
- **Branch Strategy:** `main` (Production) ← `dev` (Integration) ← `feature/*` (Feature branches).
- **Commit Pattern:** Step-by-step build order commits (e.g. `feat(step-1): ...`, `feat(step-2): ...`).
- **Merging:** Always merge feature branches into `dev`, test, then merge `dev` into `main` and push.
- **Hugging Face Remotes:**
  - `https://huggingface.co/spaces/majidali1256/AI-Resume-Screener-Studio`
  - `https://huggingface.co/majidali1256/AI_Resume_Scanner`

---

## 📋 Completed Week 1 & Week 2 Submissions

- **Week 1 PDF Report:** `Week1_Submission_Majid_Ali.pdf`
- **Week 2 PDF Report:** `Week2_Submission_Majid_Ali.pdf` (Contains live working demo screenshot showing 85% match score, matched requirements, missing keywords, and rewrite suggestions).
- **Pytest Suite Status:** 5/5 tests passing (`/Users/macbookair/Library/Python/3.9/bin/pytest tests/`).
