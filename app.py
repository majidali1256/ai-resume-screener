"""
Hugging Face Spaces (Gradio SDK - 100% Free Tier) Entry Point.
Serves both our custom Google Stitch MCP 3D Executive Studio frontend at `/`
and a Gradio interface at `/gradio` on port 7860.
"""

import os
import uvicorn
import gradio as gr
from main import app as fastapi_app

# Create a minimal Gradio demo that links to our 3D Executive Studio
with gr.Blocks(title="MATCH.AI Executive Studio") as demo:
    gr.Markdown("# 🚀 MATCH.AI — AI Resume Screener Studio")
    gr.Markdown("### [👉 Click here to open the 3D Executive Studio Dashboard](/ )")

# Mount Gradio app onto our existing FastAPI application
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
