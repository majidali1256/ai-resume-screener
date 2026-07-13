"""
Pydantic schemas for AI Resume Scanner structured output validation.
Enforces the exact Assessment schema specified in Project 1 specification.
"""

from typing import List
from pydantic import BaseModel, Field


class Assessment(BaseModel):
    """
    Structured Assessment schema returned by Gemini Flash.
    Invalid or malformed output is rejected by Pydantic validation.
    """

    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="0 to 100 alignment score indicating how well the candidate matches the job requirements.",
    )
    score_rationale: str = Field(
        ...,
        description="Short, objective explanation summarizing why this match score was assigned.",
    )
    matched_requirements: List[str] = Field(
        default_factory=list,
        description="List of job description requirements evidenced by specific experience or achievements in the resume.",
    )
    missing_requirements: List[str] = Field(
        default_factory=list,
        description="List of core job description requirements that are not evidenced in the resume.",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Truthful, actionable recommendations for improving candidate presentation without fabrication.",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Any uncertainties, missing sections, or ambiguous information in the supplied documents.",
    )
