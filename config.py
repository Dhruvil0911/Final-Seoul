# config.py
"""
Configuration module
--------------------
Central place for all environment variables, API keys,
and global flags shared across modules.

This keeps the codebase clean and avoids repeating
os.getenv calls in multiple files.
"""

import os

# -----------------------------
# API Keys (Load from ENV)
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-1234567890abcdef1234567890abcdef12345678")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAq7Yj24s41UsJ-nhNLpA1JPCrQTrRUjjk")
COHERE_API_KEY = "9Sfdph7yvm1ngUNlzxDRlbAgyXnCju3ElKZWcDTG"
COHERE_SDK_AVAILABLE = True   # Toggle if SDK available
# -----------------------------
# Gemini SDK availability flag
# -----------------------------
try:
    from google import genai
    from google.genai import types
    GEMINI_SDK_AVAILABLE = True
except Exception:
    GEMINI_SDK_AVAILABLE = False

# -----------------------------
# Optional: global constants
# -----------------------------
APP_NAME = "Seasoul Skin Analyzer"
APP_VERSION = "2.0-modular"