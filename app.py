# app.py (Main Entry)
"""
Main FastAPI application entry point.
Only handles routing, dependency injection, and minimal orchestration.
All heavy logic is modularized into separate service modules.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.image_encoder import encode_upload_to_base64
from services.llm_runner import run_multi_llm_analysis
from core.synthesizer import run_analysis, finalize_from_single_model
import json

app = FastAPI(title="Seasoul Skin Analyzer", version="2.0-modular")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze-skin")
async def analyze_skin(file: UploadFile = File(...)):
    """Main API endpoint.
    - Accepts image
    - Runs GPT + Gemini
    - Merges results
    - Applies synthesis and formatting
    """

    img_b64, mime_type = await encode_upload_to_base64(file)
    gpt_res, gem_res = await run_multi_llm_analysis(img_b64, mime_type)

    try:
        gpt_json = json.loads(gpt_res) if gpt_res else {}
    except:
        gpt_json = {}

    try:
        gem_json = json.loads(gem_res) if gem_res else {}
    except:
        gem_json = {}

    # Both failed
    if not gpt_json and not gem_json:
        return JSONResponse({
            "status": "error",
            "message": "Both models failed to produce a valid response"
        }, status_code=500)

    # One worked
    if gpt_json and not gem_json:
        return JSONResponse(finalize_from_single_model(gpt_json))
    if gem_json and not gpt_json:
        return JSONResponse(finalize_from_single_model(gem_json))

    # Both worked → full synthesis
    final_json = run_analysis({"details": {"gpt4o": gpt_json, "gemini": gem_json}})
    return JSONResponse(final_json)


@app.get("/")
def root():
    return {"message": "Seasoul Modular Analyzer is live!"}
