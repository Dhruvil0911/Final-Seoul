# services/llm_runner.py
"""
Module: llm_runner
------------------
Responsible for running BOTH LLMs (GPT‑4o and Gemini) in parallel.
Returns raw JSON strings from both models.
No merging or synthesis happens here.
"""

import asyncio
from services.openai_client import analyze_with_openai
from services.gemini_client import analyze_with_gemini
from core.prompts import GPT_PROMPT, GEMINI_PROMPT


async def run_multi_llm_analysis(img_b64: str, mime_type: str):
    """Run GPT‑4o + Gemini 2.0 Flash in parallel.
    Returns a tuple: (gpt_response, gemini_response)
    """

    gpt_task = analyze_with_openai(img_b64, mime_type, GPT_PROMPT)
    gem_task = analyze_with_gemini(img_b64, mime_type, GEMINI_PROMPT)

    return await asyncio.gather(gpt_task, gem_task)
