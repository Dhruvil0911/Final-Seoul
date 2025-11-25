import base64
import asyncio
from config import COHERE_API_KEY, COHERE_SDK_AVAILABLE

if COHERE_SDK_AVAILABLE:
    import cohere

async def analyze_with_cohere(img_b64: str, mime_type: str, prompt: str):
    # SDK mode
    if COHERE_SDK_AVAILABLE:
        try:
            # Use correct client version
            client = cohere.ClientV2(COHERE_API_KEY)  # If V2 exists
            model = "c4ai-aya-vision-32b"

            # Build base64 data URL
            data_url = f"data:{mime_type};base64,{img_b64}"

            # Prepare messages
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]

            # Call chat
            response = await asyncio.to_thread(
                client.chat,
                model=model,
                messages=messages
            )

            # Extract result
            return response.message.content[0].text

        except Exception as e:
            print(f"❌ Cohere SDK Error: {e}")
            return None

    # REST fallback (similar to earlier)
    ...
