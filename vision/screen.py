from __future__ import annotations

import base64
import io
from PIL import Image, ImageGrab


def capture_jpeg(max_width: int = 1440, quality: int = 72) -> bytes:
    image = ImageGrab.grab(all_screens=False)
    if image.width > max_width:
        height = round(image.height * max_width / image.width)
        image = image.resize((max_width, height), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    image.convert("RGB").save(out, format="JPEG", quality=quality, optimize=True)
    return out.getvalue()


def capture_data_url(max_width: int = 1440) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(capture_jpeg(max_width)).decode("ascii")
