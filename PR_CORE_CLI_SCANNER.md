# Pull Request: Core AI Resume Scanner CLI & Pydantic Schema (`feature/core-cli-scanner` → `dev`)

### 🚀 Summary of Changes
- Implements core `resume_scanner` Python package (`cli.py`, `extractor.py`, `assessor.py`, `models.py`).
- Enforces strict Pydantic `Assessment` schema (`match_score`, `score_rationale`, `matched_requirements`, `missing_requirements`, `suggestions`, `limitations`).
- Integrates Google Gemini Flash structured JSON output with `temperature=0.0` and `tenacity` exponential backoff retry.
- Adds local document safety validation (accepts `.pdf`/`.txt`, enforces 10MB limit, isolates user uploads in `data/uploads/`).
- Includes sample candidate resume and job description (`data/sample_resume.txt`, `data/sample_jd.txt`) for immediate CLI testing.

### 🎯 Related Issue / Task
- Resolves Week 1 Core Architecture & Pydantic Schema specification.

### 🧪 Verification Performed
- [x] Ran `python3 -m resume_scanner.cli data/sample_resume.txt data/sample_jd.txt` successfully.
- [x] Verified `.gitignore` blocks `.env`, `__pycache__`, macOS `.DS_Store`, and `data/uploads/*`.
- [x] Verified zero syntax or runtime errors.
