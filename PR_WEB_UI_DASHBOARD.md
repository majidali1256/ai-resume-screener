# Pull Request: Interactive Web UI & PDF Upload Dashboard (`feature/web-ui-dashboard` → `dev`)

### 🚀 Summary of Changes
- Implements **AI Resume Scanner Studio Web UI** (`static/index.html`) featuring a rich dark-mode glassmorphism interface.
- Adds interactive drag-and-drop file uploaders for candidate resume (`.pdf` or `.txt`) and Job Description input (file upload or text paste).
- Implements visual circular **Match Score Gauge (0–100)** with dynamic color coding, score rationale, and interactive requirements checklists (`matched_requirements`, `missing_requirements`, `suggestions`).
- Updates `main.py` with FastAPI endpoints:
  - `GET /` — Serves the interactive Web Dashboard.
  - `POST /api/scan` — Accepts multipart file upload, isolates files safely in `data/uploads/`, runs Pydantic-validated screening via `ResumeAssessor`, and returns structured JSON.
  - `GET /api/sample` — 1-Click Demo endpoint running instant screening on sample files.

### 🎯 Related Issue / Task
- Resolves **Task #3** (*"Add a user-friendly PDF upload screen and result card/dashboard"*) from Project 1 specification Page 3.

### 🧪 Verification Performed
- [x] Verified zero syntax compilation errors on `main.py`.
- [x] Verified UI responsiveness and drag-and-drop file upload interaction.
- [x] Verified sample demo endpoint returns valid Pydantic Assessment JSON.
