"""
Gemini Flash Assessment Service for AI Resume Scanner.
Implements structured Pydantic output (`Assessment`), temperature=0 for consistency,
and exponential backoff retry for transient API / rate-limit (429) errors.
"""

import json
import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .models import Assessment


SYSTEM_PROMPT = """You are an expert AI Resume Assessor and Career Feedback Advisor.
Your purpose is to objectively evaluate how well a candidate's resume aligns with a specific job description.

CRITICAL ASSESSMENT RULES:
1. Assess ONLY job-relevant professional qualifications, technical skills, achievements, and experience.
2. Rely strictly on evidence provided in the resume text. Do NOT assume, fabricate, or speculate about unmentioned skills.
3. Be constructive, truthful, and objective. Provide clear evidence for matched requirements and specific gaps.
4. Output MUST conform strictly to the requested Assessment JSON schema.
"""


class AssessorError(Exception):
    """Raised when AI assessment or structured schema parsing fails."""
    pass


class ResumeAssessor:
    """
    Executes structured resume vs job description screening using Gemini Flash.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        from dotenv import load_dotenv
        from pathlib import Path
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path, override=True)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("AI_MODEL", model_name)

    def _build_prompt(self, resume_text: str, jd_text: str) -> str:
        return f"""Evaluate the candidate resume against the provided job description.

=== [START JOB DESCRIPTION TEXT] ===
{jd_text}
=== [END JOB DESCRIPTION TEXT] ===

=== [START RESUME TEXT] ===
{resume_text}
=== [END RESUME TEXT] ===

Provide your structured evaluation matching the Assessment JSON schema."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def assess(self, resume_text: str, jd_text: str) -> Assessment:
        """
        Sends extracted texts to Gemini Flash and returns validated Pydantic Assessment.
        Automatically retries on temporary API errors / rate limits.
        If no API key is provided, falls back to a deterministic simulation for offline testing.
        """
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return self._simulate_assessment(resume_text, jd_text)

        prompt = self._build_prompt(resume_text, jd_text)

        # Direct REST API invocation using Python standard library (robust across all Python envs)
        import urllib.request
        import json

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.0
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return Assessment.model_validate_json(raw_text)
        except Exception as exc:
            raise AssessorError(f"Gemini API assessment failed: {exc}") from exc

    def _simulate_assessment(self, resume_text: str, jd_text: str) -> Assessment:
        """
        Offline simulation mode so the CLI can be tested immediately even without an active API key.
        """
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()

        # Basic keyword heuristics for realistic offline demo
        keywords = ["python", "fastapi", "next.js", "react", "git", "sql", "ai", "gemini", "docker", "pydantic"]
        matched = [kw.upper() for kw in keywords if kw in resume_lower and kw in jd_lower]
        missing = [kw.upper() for kw in keywords if kw in jd_lower and kw not in resume_lower]

        score = min(95, max(45, 50 + len(matched) * 8 - len(missing) * 5))

        return Assessment(
            match_score=score,
            score_rationale=f"Simulated local assessment: Candidate matched {len(matched)} key technologies and missing {len(missing)} requirements.",
            matched_requirements=[f"Demonstrated proficiency in {kw} within resume projects." for kw in matched]
            or ["General software engineering experience demonstrated."],
            missing_requirements=[f"No direct evidence found for {kw} in resume text." for kw in missing]
            or ["None identified in offline simulation."],
            suggestions=[
                "Quantify your accomplishments with specific metrics and key performance indicators.",
                "Ensure every technical skill listed in your summary appears in at least one project or work experience bullet.",
            ],
            limitations=[
                "Assessment generated in local offline simulation mode (GEMINI_API_KEY not set). Set API key in .env for live Gemini Flash screening."
            ],
        )
