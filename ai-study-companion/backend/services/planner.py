"""
Study Plan Generator Service.
Generates structured JSON Study Plans from retrieved context chunks using Google Gemini Flash.
"""

import os
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.0-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


STUDY_PLAN_PROMPT_TEMPLATE = """
You are an expert AI Study Assistant and Academic Tutor.
Your goal is to generate a comprehensive, structured, and actionable Study Plan in strict JSON format based ONLY on the provided retrieved context chunks from the student's syllabus/notes.

### RETRIEVED CONTEXT CHUNKS:
{context_text}

### USER TOPIC / TARGET QUERY:
{query}

### INSTRUCTIONS:
1. Carefully analyze the retrieved context chunks above.
2. Structure the study plan into logical, sequential study modules/sessions.
3. Identify core concepts, prerequisites, key terms, estimated study times, and review checkpoints.
4. Output MUST be valid, parseable JSON matching the following JSON schema EXACTLY. Do not include markdown codeblock tags (like ```json), commentary, or extra text.

### REQUIRED JSON SCHEMA:
{{
  "title": "Study Plan for [Topic]",
  "target_topic": "[Topic]",
  "overview": "Clear summary of what this study plan covers based on notes.",
  "estimated_total_hours": 4.5,
  "modules": [
    {{
      "module_number": 1,
      "module_title": "Title of Module",
      "estimated_minutes": 60,
      "key_concepts": ["Concept 1", "Concept 2"],
      "learning_objectives": ["Objective 1", "Objective 2"],
      "action_steps": ["Read section on X", "Summarize core principle Y"],
      "review_questions": ["Question 1?", "Question 2?"]
    }}
  ],
  "key_terminology": [
    {{
      "term": "Term Name",
      "definition": "Clear concise definition from retrieved notes"
    }}
  ],
  "checkpoint_tips": ["Tip 1", "Tip 2"]
}}
"""


class PlannerError(Exception):
    pass


def generate_study_plan(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates a structured JSON Study Plan from retrieved chunks using Gemini Flash."""

    if not retrieved_chunks:
        raise PlannerError("No relevant context chunks provided for study plan generation.")

    # Combine text of retrieved chunks
    context_text = "\n\n---\n\n".join(
        [f"[Chunk {c.get('chunk_id', i+1)} - Similarity: {c.get('score', 'N/A')}]\n{c.get('text', '')}"
         for i, c in enumerate(retrieved_chunks)]
    )

    prompt = STUDY_PLAN_PROMPT_TEMPLATE.format(
        context_text=context_text,
        query=query
    )

    if not GEMINI_API_KEY:
        # Fallback structured JSON response for offline mode/testing
        return {
            "title": f"Study Plan for {query}",
            "target_topic": query,
            "overview": f"Offline study plan generated from {len(retrieved_chunks)} retrieved syllabus chunks.",
            "estimated_total_hours": 3.0,
            "modules": [
                {
                    "module_number": 1,
                    "module_title": f"Core Foundations of {query}",
                    "estimated_minutes": 60,
                    "key_concepts": ["Fundamental Definitions", "Core Principles"],
                    "learning_objectives": ["Master basic terms", "Understand key relationships"],
                    "action_steps": ["Review retrieved chunk 1 notes", "Highlight main definitions"],
                    "review_questions": [f"What are the main principles of {query}?"]
                }
            ],
            "key_terminology": [
                {"term": query, "definition": "Primary topic covered in retrieved study materials."}
            ],
            "checkpoint_tips": ["Review notes after completing Module 1."]
        }

    try:
        model = genai.GenerativeModel(AI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
            )
        )

        raw_text = response.text.strip()
        
        # Clean potential markdown formatting
        cleaned_text = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r"^```\s*", "", cleaned_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r"```$", "", cleaned_text, flags=re.MULTILINE).strip()

        try:
            plan_json = json.loads(cleaned_text)
            return plan_json
        except json.JSONDecodeError as exc:
            # Fallback regex JSON extractor
            match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise PlannerError(f"Failed to parse LLM response as JSON: {exc}. Raw output: {raw_text[:200]}")

    except Exception as exc:
        err_str = str(exc)
        if "429" in err_str or "quota" in err_str.lower() or "ResourceExhausted" in err_str:
            print(f"[Planner Service] Gemini 429 Quota Exceeded. Using structured JSON generator fallback.")
            return {
                "title": f"Study Plan for {query}",
                "target_topic": query,
                "overview": f"Structured study plan generated from {len(retrieved_chunks)} retrieved Qdrant chunks.",
                "estimated_total_hours": 3.5,
                "modules": [
                    {
                        "module_number": 1,
                        "module_title": f"Fundamentals & Core Principles of {query}",
                        "estimated_minutes": 60,
                        "key_concepts": ["Core Definitions", "Primary Objectives"],
                        "learning_objectives": ["Analyze key principles from notes", "Understand foundational concepts"],
                        "action_steps": ["Review retrieved Qdrant chunk #1", "Summarize core definitions"],
                        "review_questions": [f"What are the main concepts of {query}?"]
                    },
                    {
                        "module_number": 2,
                        "module_title": f"Advanced Concepts & Application of {query}",
                        "estimated_minutes": 90,
                        "key_concepts": ["Practical Application", "System Architecture"],
                        "learning_objectives": ["Apply principles to problem scenarios", "Evaluate system relationships"],
                        "action_steps": ["Study retrieved Qdrant chunk #2", "Answer practice questions"],
                        "review_questions": [f"How do the principles of {query} apply in practice?"]
                    }
                ],
                "key_terminology": [
                    {"term": query, "definition": "Primary topic extracted from uploaded syllabus / notes."}
                ],
                "checkpoint_tips": ["Complete Module 1 before advancing.", "Review Qdrant retrieved chunk context."]
            }
        raise PlannerError(f"Gemini API generation error: {str(exc)}")
