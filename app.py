"""
MATCH.AI — AI Resume Screener & Feedback System
Hugging Face Gradio Space Entry Point
"""

import os
import gradio as gr
from resume_scanner.assessor import ResumeAssessor
from resume_scanner.extractor import prepare_scanner_inputs

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


with gr.Blocks(
    title="MATCH.AI — AI Resume Screener Studio",
    theme=gr.themes.Soft(primary_hue="cyan"),
) as demo:
    gr.Markdown("# 🚀 MATCH.AI — Executive AI Resume Screener Studio")
    gr.Markdown(
        "An enterprise-grade, deterministic AI screening engine powered by **Google Gemini Flash** & **Pydantic AI**."
    )

    with gr.Row():
        with gr.Column(scale=5):
            gr.Markdown("### 📄 Candidate Documents")
            resume_input = gr.File(label="Upload Candidate Resume (.pdf, .docx, .txt)")
            jd_input = gr.File(
                label="Upload Job Description (.pdf, .docx, .txt) [Optional if pasting text below]"
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
