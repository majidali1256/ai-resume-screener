"""
Enterprise Automated Test Suite for AI Resume Screener & Grounding Engine.
Tests structured schema boundaries, grounding verification, and document validation.
"""

import pytest
from resume_scanner.grounding import GroundingVerifier
from resume_scanner.models import Assessment
from resume_scanner.extractor import validate_file, ExtractionError


def test_grounding_verifier_valid_claims():
    verifier = GroundingVerifier(min_overlap_ratio=0.3)
    resume_text = "Experienced Senior Python Engineer proficient in FastAPI, Docker, and Google Gemini APIs."
    claims = [
        "Python Engineer proficient in FastAPI",
        "Docker containerization experience",
        "Expertise in Quantum String Theory"
    ]

    result = verifier.verify_claims(claims, resume_text)

    assert "Python Engineer proficient in FastAPI" in result["verified"]
    assert "Docker containerization experience" in result["verified"]
    assert "Expertise in Quantum String Theory" in result["unverified"]
    assert result["grounding_score"] > 50.0


def test_grounding_verifier_empty_claims():
    verifier = GroundingVerifier()
    result = verifier.verify_claims([], "Any resume text here")
    assert result["verified"] == []
    assert result["unverified"] == []
    assert result["grounding_score"] == 0.0


def test_assessment_response_schema():
    payload = {
        "match_score": 88,
        "score_rationale": "Strong alignment with AI engineering requirements.",
        "matched_requirements": ["Python", "FastAPI"],
        "missing_requirements": ["Kubernetes"],
        "suggestions": ["Add links to deployed projects."]
    }
    response = Assessment(**payload)
    assert response.match_score == 88
    assert len(response.matched_requirements) == 2
    assert "Kubernetes" in response.missing_requirements


def test_assessment_score_bounds():
    with pytest.raises(ValueError):
        Assessment(
            match_score=150,
            score_rationale="Invalid score over 100",
            matched_requirements=[],
            missing_requirements=[],
            suggestions=[]
        )


def test_validate_file_extensions(tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy content")
    docx_file = tmp_path / "test.docx"
    docx_file.write_text("dummy content")
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("dummy content")

    assert validate_file(str(pdf_file)) is not None
    assert validate_file(str(docx_file)) is not None
    assert validate_file(str(txt_file)) is not None

    exe_file = tmp_path / "test.exe"
    exe_file.write_text("dummy content")
    with pytest.raises(ExtractionError):
        validate_file(str(exe_file))
