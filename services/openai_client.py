# services/openai_client.py
"""
Module: openai_client
---------------------
Handles GPT-4o image analysis request.
Encapsulates:
- OpenAI API call
- Error handling
- Returning raw JSON string

Keeps main app clean.
"""

import asyncio
import base64
from openai import OpenAI
from config import OPENAI_API_KEY


async def analyze_with_openai(img_b64: str, mime_type: str, prompt: str):
    """Send image + prompt to GPT-4o and return raw JSON string.
    If API fails → returns None.
    """

    client = OpenAI(api_key=OPENAI_API_KEY)

    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}}
    ]

    try:
        # Run sync API in thread
        resp = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
        )

        return resp.choices[0].message.content

    except Exception as e:
        print(f"❌ GPT Error: {e}")
        return None