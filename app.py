"""
MATCH.AI — AI Resume Screener & Feedback System
Hugging Face Gradio Space Entry Point
"""

import os
import gradio as gr
try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(fn):
            return fn

from resume_scanner.assessor import ResumeAssessor
from resume_scanner.extractor import prepare_scanner_inputs

@spaces.GPU
def scan_resume_gradio(resume_file, jd_file, jd_text) -> tuple:
    if not resume_file:
        return (
            "⚠️ Error: Please upload a candidate resume file (.pdf, .docx, or .txt).",
            0,
            "No evaluation rationale.",
            "",
            "",
            "",
        )

    try:
        resume_path = resume_file.name
        jd_path = jd_file.name if jd_file else resume_path

        if jd_file:
            resume_extracted, jd_extracted = prepare_scanner_inputs(resume_path, jd_path)
        elif jd_text and jd_text.strip():
            resume_extracted, _ = prepare_scanner_inputs(resume_path, resume_path)
            jd_extracted = jd_text.strip()
        else:
            return (
                "⚠️ Error: Please provide either a Job Description file or paste Job Description text.",
                0,
                "",
                "",
                "",
                "",
            )

        assessor = ResumeAssessor()
        result = assessor.assess(resume_extracted, jd_extracted)

        score = result.match_score
        rationale = result.score_rationale
        matched = "\n".join([f"✅ {item}" for item in result.matched_requirements]) or "None"
        missing = "\n".join([f"⚠️ {item}" for item in result.missing_requirements]) or "None"
        suggestions = "\n".join([f"💡 {item}" for item in result.suggestions]) or "None"

        status_msg = f"🎉 Scan Complete! Match Score: {score}/100"
        return status_msg, score, rationale, matched, missing, suggestions
    except Exception as exc:
        return f"❌ Error during assessment: {str(exc)}", 0, str(exc), "", "", ""


def run_demo_gradio() -> tuple:
    try:
        sample_resume = "data/sample_resume.txt"
        sample_jd = "data/sample_jd.txt"
        resume_extracted, jd_extracted = prepare_scanner_inputs(sample_resume, sample_jd)
        assessor = ResumeAssessor()
        result = assessor.assess(resume_extracted, jd_extracted)

        score = result.match_score
        rationale = result.score_rationale
        matched = "\n".join([f"✅ {item}" for item in result.matched_requirements]) or "None"
        missing = "\n".join([f"⚠️ {item}" for item in result.missing_requirements]) or "None"
        suggestions = "\n".join([f"💡 {item}" for item in result.suggestions]) or "None"

        return (
            f"⚡ 1-Click Demo Assessment Complete! Score: {score}/100",
            score,
            rationale,
            matched,
            missing,
            suggestions,
        )
    except Exception as exc:
        return f"❌ Demo error: {str(exc)}", 0, str(exc), "", "", ""


CUSTOM_CSS = """
.gradio-container {
    background: radial-gradient(circle at 10% 20%, rgb(11, 15, 25) 0%, rgb(17, 24, 39) 90%) !important;
    color: #f3f4f6 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.hero-banner {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    backdrop-filter: blur(12px);
}
.hero-title {
    background: linear-gradient(135deg, #22d3ee 0%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 8px;
}
button.primary {
    background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 0 15px rgba(6, 182, 212, 0.4) !important;
    transition: all 0.3s ease !important;
}
button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 25px rgba(139, 92, 246, 0.7) !important;
}
"""

with gr.Blocks(
    title="MATCH.AI — Executive AI Resume Screener Studio",
    theme=gr.themes.Base(
        primary_hue="cyan",
        secondary_hue="purple",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"],
    ),
    css=CUSTOM_CSS,
) as demo:
    gr.HTML('''
    <div class="hero-banner">
        <div class="hero-title">🚀 MATCH.AI — Executive AI Resume Screener Studio</div>
        <p style="color: #cbd5e1; font-size: 1.05rem; margin: 0;">
            Enterprise deterministic AI screening powered by <b>Google Gemini Flash</b> & <b>Pydantic AI</b>.
            Equipped with Hallucination Grounding Verification & Zero-Bias Structured Analysis.
        </p>
    </div>
    ''')

    with gr.Row():
        with gr.Column(scale=5):
            gr.Markdown("### 📄 Candidate Documents")
            resume_input = gr.File(
                label="Upload Candidate Resume (.pdf, .docx, .doc, .txt)",
                file_types=[".pdf", ".docx", ".doc", ".txt"],
            )
            jd_input = gr.File(
                label="Upload Job Description (.pdf, .docx, .doc, .txt) [Optional if pasting text below]",
                file_types=[".pdf", ".docx", ".doc", ".txt"],
            )
            jd_text_input = gr.Textbox(
                label="Or Paste Job Description Text",
                lines=5,
                placeholder="Paste job requirements here...",
            )

            with gr.Row():
                scan_btn = gr.Button("⚡ Run AI Scan", variant="primary")
                demo_btn = gr.Button("🚀 1-Click Sample Demo", variant="secondary")

        with gr.Column(scale=6):
            gr.Markdown("### 📊 AI Executive Assessment Results")
            status_output = gr.Textbox(label="Status", interactive=False)
            score_output = gr.Number(label="Match Score (0 - 100)", interactive=False)
            rationale_output = gr.Textbox(
                label="Executive Evaluation Rationale", lines=4, interactive=False
            )

            with gr.Row():
                matched_output = gr.Textbox(
                    label="✅ Matched Qualifications", lines=5, interactive=False
                )
                missing_output = gr.Textbox(
                    label="⚠️ Identified Skill Gaps", lines=5, interactive=False
                )

            suggestions_output = gr.Textbox(
                label="💡 Actionable Presentation Suggestions", lines=4, interactive=False
            )

    scan_btn.click(
        fn=scan_resume_gradio,
        inputs=[resume_input, jd_input, jd_text_input],
        outputs=[
            status_output,
            score_output,
            rationale_output,
            matched_output,
            missing_output,
            suggestions_output,
        ],
        show_api=False,
    )

    demo_btn.click(
        fn=run_demo_gradio,
        inputs=[],
        outputs=[
            status_output,
            score_output,
            rationale_output,
            matched_output,
            missing_output,
            suggestions_output,
        ],
        show_api=False,
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)
