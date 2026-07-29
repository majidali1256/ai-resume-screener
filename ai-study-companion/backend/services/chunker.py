"""
Document Text Extraction and Chunking Service.
Splits uploaded documents (PDF, DOCX, TXT) into meaningful semantic chunks (~200-500 tokens).
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
import docx

class ExtractionError(Exception):
    pass

def extract_text_from_filepath(file_path: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT file."""
    path = Path(file_path)
    if not path.exists():
        raise ExtractionError(f"File not found: {file_path}")
        
    ext = path.suffix.lower()
    
    if ext == ".txt":
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1")
            
    elif ext == ".pdf":
        try:
            reader = PdfReader(str(path))
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages.append(text)
            if not pages:
                raise ExtractionError("No readable text found in PDF.")
            return "\n\n".join(pages)
        except Exception as exc:
            raise ExtractionError(f"PDF extraction failed: {str(exc)}")
            
    elif ext in (".docx", ".doc"):
        try:
            doc = docx.Document(str(path))
            full_text = [p.text for p in doc.paragraphs if p.text.strip()]
            if not full_text:
                raise ExtractionError("No readable text found in Word document.")
            return "\n\n".join(full_text)
        except Exception as exc:
            raise ExtractionError(f"Docx extraction failed: {str(exc)}")
    else:
        raise ExtractionError(f"Unsupported file extension '{ext}'. Only .pdf, .docx, .doc, and .txt allowed.")

def chunk_text(
    text: str,
    target_chunk_size: int = 350,
    min_chunk_size: int = 100,
    overlap_paragraphs: int = 1
) -> List[Dict[str, Any]]:
    """
    Splits text into meaningful semantic chunks (~200-500 tokens / words).
    Returns a list of dictionaries with chunk_id, text, token_estimate, and paragraph_range.
    """
    if not text or not text.strip():
        return []
        
    # Split text into paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    
    if not paragraphs:
        paragraphs = [text.strip()]
        
    chunks = []
    current_paragraphs = []
    current_word_count = 0
    chunk_idx = 0
    
    for i, para in enumerate(paragraphs):
        words_in_para = len(para.split())
        
        if current_word_count + words_in_para > target_chunk_size and current_word_count >= min_chunk_size:
            chunk_text_content = "\n\n".join(current_paragraphs)
            chunks.append({
                "chunk_id": f"chunk_{chunk_idx + 1}",
                "text": chunk_text_content,
                "token_estimate": current_word_count,
                "paragraph_count": len(current_paragraphs)
            })
            chunk_idx += 1
            
            # Keep overlap paragraphs
            if overlap_paragraphs > 0 and len(current_paragraphs) >= overlap_paragraphs:
                current_paragraphs = current_paragraphs[-overlap_paragraphs:]
                current_word_count = sum(len(p.split()) for p in current_paragraphs)
            else:
                current_paragraphs = []
                current_word_count = 0
                
        current_paragraphs.append(para)
        current_word_count += words_in_para
        
    if current_paragraphs:
        chunk_text_content = "\n\n".join(current_paragraphs)
        chunks.append({
            "chunk_id": f"chunk_{chunk_idx + 1}",
            "text": chunk_text_content,
            "token_estimate": current_word_count,
            "paragraph_count": len(current_paragraphs)
        })
        
    return chunks
