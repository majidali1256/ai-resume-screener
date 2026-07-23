"""
FastAPI Server Entry Point for AI Resume Scanner & Feedback Dashboard.
Project 1 — AI & Generative AI Fellowship Program
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from resume_scanner.assessor import ResumeAssessor, AssessorError
from resume_scanner.extractor import extract_text_from_file, prepare_scanner_inputs, ExtractionError
from resume_scanner.models import Assessment

load_dotenv()

app = FastAPI(
    title="AI Resume Scanner API",
    description="Automated resume vs job description screening and feedback engine powered by Gemini Flash.",
    version="1.0.0",
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static frontend directory
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the interactive web UI dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>AI Resume Scanner API is running. Please add static/index.html</h1>")


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "AI Resume Scanner API",
        "version": "1.0.0",
    }


@app.get("/api/sample", response_model=Assessment)
@app.get("/api/demo")
def run_sample_assessment():
    """
    Runs an assessment using the preloaded sample resume and sample JD for quick UI demo.
    """
    sample_resume = Path("data/sample_resume.txt")
    sample_jd = Path("data/sample_jd.txt")

    if not sample_resume.exists() or not sample_jd.exists():
        raise HTTPException(
            status_code=404,
            detail="Sample files not found in data/ directory.",
        )

    try:
        resume_text, jd_text = prepare_scanner_inputs(str(sample_resume), str(sample_jd))
        assessor = ResumeAssessor()
        return assessor.assess(resume_text, jd_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/scan", response_model=Assessment)
async def scan_resume(
    resume_file: UploadFile = File(..., description="Candidate resume (.pdf or .txt)"),
    jd_file: Optional[UploadFile] = File(None, description="Job description file (.pdf or .txt)"),
    jd_text: Optional[str] = Form(None, description="Raw job description text"),
):
    """
    Accepts candidate resume and job description (file or raw text),
    extracts text safely, and returns validated Pydantic Assessment JSON.
    """
    # Save resume file safely
    resume_ext = Path(resume_file.filename or "").suffix.lower()
    if resume_ext not in (".pdf", ".txt", ".docx", ".doc"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported resume file extension '{resume_ext}'. Only .pdf, .txt, .docx, and .doc allowed.",
        )

    resume_path = UPLOAD_DIR / f"resume_{resume_file.filename}"
    with open(resume_path, "wb") as buffer:
        shutil.copyfileobj(resume_file.file, buffer)

    try:
        # Determine JD text
        if jd_file and jd_file.filename:
            jd_ext = Path(jd_file.filename).suffix.lower()
            if jd_ext not in (".pdf", ".txt", ".docx", ".doc"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported job description file extension '{jd_ext}'. Only .pdf, .txt, .docx, and .doc allowed.",
                )
            jd_path = UPLOAD_DIR / f"jd_{jd_file.filename}"
            with open(jd_path, "wb") as buffer:
                shutil.copyfileobj(jd_file.file, buffer)
            resume_extracted, jd_extracted = prepare_scanner_inputs(str(resume_path), str(jd_path))
        elif jd_text and jd_text.strip():
            resume_extracted = extract_text_from_file(str(resume_path), label="Resume")
            jd_extracted = jd_text.strip()
        else:
            raise HTTPException(
                status_code=400,
                detail="Please provide either a job description file or paste job description text.",
            )

        assessor = ResumeAssessor()
        assessment = assessor.assess(resume_extracted, jd_extracted)
        return assessment

    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=f"Extraction Error: {exc}")
    except AssessorError as exc:
        raise HTTPException(status_code=500, detail=f"AI Assessment Error: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        # Clean up temporary uploaded files to maintain clean storage
        if resume_path.exists():
            try:
                resume_path.unlink()
            except Exception:
                pass