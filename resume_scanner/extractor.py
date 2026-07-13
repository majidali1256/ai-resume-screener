"""
Local text extraction and document safety checks for AI Resume Scanner.
Ensures files exist, valid extension (.pdf / .txt), rejects empty/overly large files,
and extracts clean text locally before sending to Gemini API.
"""

import os
from pathlib import Path
from typing import Tuple

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class ExtractionError(Exception):
    """Raised when document extraction or validation fails."""
    pass


def validate_file(file_path: str, label: str = "File") -> Path:
    """
    Validates existence, extension (.pdf/.txt), and size of a file path.
    """
    path = Path(file_path)

    if not path.exists():
        raise ExtractionError(f"{label} not found: '{file_path}'")

    if not path.is_file():
        raise ExtractionError(f"{label} is not a valid file: '{file_path}'")

    ext = path.suffix.lower()
    if ext not in (".pdf", ".txt"):
        raise ExtractionError(
            f"{label} has unsupported extension '{ext}'. Only .pdf and .txt are allowed."
        )

    file_size = path.stat().st_size
    if file_size == 0:
        raise ExtractionError(f"{label} is empty: '{file_path}'")

    if file_size > MAX_FILE_SIZE_BYTES:
        raise ExtractionError(
            f"{label} exceeds maximum allowed size of 10MB ({file_size} bytes): '{file_path}'"
        )

    return path


def extract_text_from_pdf(path: Path) -> str:
    """Extracts text content from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ExtractionError("pypdf is not installed. Run `pip install pypdf`.")

    try:
        reader = PdfReader(str(path))
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- Page {i + 1} ---\n{text.strip()}")
        extracted = "\n\n".join(pages_text).strip()
        if not extracted:
            raise ExtractionError(f"No readable text could be extracted from PDF: '{path.name}'")
        return extracted
    except Exception as exc:
        raise ExtractionError(f"Failed to parse PDF '{path.name}': {exc}") from exc


def extract_text_from_file(file_path: str, label: str = "Document") -> str:
    """
    Validates and extracts raw text from either a .pdf or .txt file.
    """
    path = validate_file(file_path, label=label)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(path)
    else:
        try:
            content = path.read_text(encoding="utf-8", errors="replace").strip()
            if not content:
                raise ExtractionError(f"{label} text file is empty: '{path.name}'")
            return content
        except Exception as exc:
            raise ExtractionError(f"Failed to read TXT file '{path.name}': {exc}") from exc


def prepare_scanner_inputs(resume_path: str, jd_path: str) -> Tuple[str, str]:
    """
    Extracts and validates both resume and job description text locally.
    Returns (resume_text, jd_text).
    """
    resume_text = extract_text_from_file(resume_path, label="Resume")
    jd_text = extract_text_from_file(jd_path, label="Job Description")
    return resume_text, jd_text
