# services/gemini_client.py
"""
Module: gemini_client
---------------------
Handles Gemini 2.0 Flash image analysis request.
Supports both:
 - Official Gemini Python SDK (if installed)
 - REST API fallback

Returns raw JSON string or None if request fails.
"""

import asyncio
import aiohttp
import base64

from config import GOOGLE_API_KEY, GEMINI_SDK_AVAILABLE

# Gemini SDK imports (optional)
if GEMINI_SDK_AVAILABLE:
    from google import genai
    from google.genai import types


async def analyze_with_gemini(img_b64: str, mime_type: str, prompt: str):
    """Send image + prompt to Gemini 2.0 Flash.
    Auto-fallback to REST if SDK is unavailable.
    """

    # =========================
    # 🌟 OFFICIAL SDK MODE
    # =========================
    if GEMINI_SDK_AVAILABLE:
        try:
            client = genai.Client(api_key=GOOGLE_API_KEY)
            config = types.GenerateContentConfig(response_mime_type="application/json")

            # Build prompt part
            try:
                prompt_part = types.Part.from_text(prompt)
            except TypeError:
                prompt_part = types.Part(text=prompt)

            # Build image part
            try:
                image_part = types.Part.from_bytes(
                    data=base64.b64decode(img_b64), mime_type=mime_type
                )
            except TypeError:
                image_part = types.Part(data=base64.b64decode(img_b64), mime_type=mime_type)

            result = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.0-flash",
                contents=[prompt_part, image_part],
                config=config,
            )

            return result.text

        except Exception as e:
            print(f"❌ Gemini SDK Error: {e}")
            return None

    # =========================
    # 🌐 REST API MODE (Fallback)
    # =========================
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": img_b64}}
            ]
        }],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as r:
                data = await r.json()
                return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    except Exception as e:
        print(f"❌ Gemini REST API Error: {e}")
        return None