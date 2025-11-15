# services/image_encoder.py
"""
Module: image_encoder
----------------------
Handles image-to-base64 conversion.
Ensures consistent image formatting (RGB + JPEG/PNG).
Used by the main API before sending inputs to LLMs.
"""

import base64
from io import BytesIO
from PIL import Image
from fastapi import UploadFile


async def encode_upload_to_base64(upload: UploadFile):
    """Convert uploaded image to base64 + correct MIME type.
    - Accepts UploadFile (FastAPI)
    - Returns (base64_str, mime_type)
    """

    data = await upload.read()
    img = Image.open(BytesIO(data)).convert("RGB")

    # Keep format if JPEG/PNG else convert to JPEG
    fmt = img.format if img.format in ["JPEG", "PNG"] else "JPEG"

    buf = BytesIO()
    img.save(buf, format=fmt)

    return base64.b64encode(buf.getvalue()).decode(), f"image/{fmt.lower()}"