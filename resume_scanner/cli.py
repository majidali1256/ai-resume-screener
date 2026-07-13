"""
Command Line Interface (CLI) for AI Resume Scanner.
Usage:
    python -m resume_scanner.cli <resume_path> <jd_path>
"""

import argparse
import sys
from dotenv import load_dotenv

from .extractor import prepare_scanner_inputs, ExtractionError
from .assessor import ResumeAssessor, AssessorError


def print_assessment_card(assessment, resume_path: str, jd_path: str):
    """Prints a clean, beautifully formatted assessment card to terminal."""
    print("\n" + "=" * 68)
    print("                 📄 AI RESUME SCANNER REPORT                 ")
    print("=" * 68)
    print(f"  Resume File         : {resume_path}")
    print(f"  Job Description     : {jd_path}")
    print("-" * 68)
    print(f"  🎯 ALIGNMENT SCORE  :  {assessment.match_score} / 100")
    print("-" * 68)
    print(f"  💡 RATIONALE:\n     {assessment.score_rationale}\n")

    print("  ✅ MATCHED REQUIREMENTS:")
    for item in assessment.matched_requirements:
        print(f"     • {item}")

    print("\n  ⚠️  MISSING REQUIREMENTS (GAPS):")
    for item in assessment.missing_requirements:
        print(f"     • {item}")

    print("\n  🚀 ACTIONABLE SUGGESTIONS:")
    for item in assessment.suggestions:
        print(f"     • {item}")

    if assessment.limitations:
        print("\n  ℹ️  LIMITATIONS & DOCUMENT UNCERTAINTY:")
        for item in assessment.limitations:
            print(f"     • {item}")
    print("=" * 68 + "\n")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="AI Resume Scanner — AI & Generative AI Fellowship Project 1"
    )
    parser.add_argument(
        "resume_path",
        help="Path to the candidate's resume (.pdf or .txt)",
    )
    parser.add_argument(
        "jd_path",
        help="Path to the job description (.pdf or .txt)",
    )

    args = parser.parse_args()

    print(f"🔍 Loading and extracting local documents...")
    try:
        resume_text, jd_text = prepare_scanner_inputs(args.resume_path, args.jd_path)
    except ExtractionError as exc:
        print(f"\n❌ Document Extraction Error:\n   {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"🤖 Sending extracted text to Gemini Flash Assessment Engine...")
    assessor = ResumeAssessor()

    try:
        assessment = assessor.assess(resume_text, jd_text)
        print_assessment_card(assessment, args.resume_path, args.jd_path)
    except AssessorError as exc:
        print(f"\n❌ Assessment Failed:\n   {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
