"""
Evidence-Grounding Verification Module for AI Resume Screener.
Verifies that claims made by the AI model in `matched_requirements`
are genuinely supported by text snippets in the candidate's resume.
Prevents ungrounded claims or hallucinated qualifications.
"""

import re
from typing import List, Dict, Any


class GroundingVerifier:
    """
    Verifies matched requirements against candidate resume text.
    Uses keyword/phrase overlap analysis to categorize claims into:
    - verified: strongly supported by resume text
    - unverified: insufficient textual evidence found in resume
    """

    def __init__(self, min_overlap_ratio: float = 0.35):
        self.min_overlap_ratio = min_overlap_ratio

    def _tokenize(self, text: str) -> set:
        """Extracts normalized alphanumeric word tokens (>2 chars)."""
        words = re.findall(r"\b[a-zA-Z0-9+#]{2,}\b", text.lower())
        stop_words = {
            "and", "the", "for", "with", "from", "that", "this", "have", "has",
            "are", "was", "were", "will", "would", "can", "could", "should",
            "experience", "years", "year", "working", "strong", "knowledge",
            "ability", "skills", "skill", "must", "plus", "preferred",
        }
        return {w for w in words if w not in stop_words}

    def verify_claims(self, matched_claims: List[str], resume_text: str) -> Dict[str, Any]:
        """
        Verifies each claimed match against resume text.
        Returns a dict with 'verified', 'unverified' lists, and 'grounding_score'.
        """
        resume_tokens = self._tokenize(resume_text)
        verified = []
        unverified = []

        for claim in matched_claims:
            claim_tokens = self._tokenize(claim)
            if not claim_tokens:
                verified.append(claim)
                continue

            overlap = claim_tokens.intersection(resume_tokens)
            overlap_ratio = len(overlap) / len(claim_tokens)

            if overlap_ratio >= self.min_overlap_ratio:
                verified.append(claim)
            else:
                unverified.append(claim)

        grounding_score = round((len(verified) / max(len(matched_claims), 1)) * 100, 1)
        return {
            "verified": verified,
            "unverified": unverified,
            "grounding_score": grounding_score,
        }
