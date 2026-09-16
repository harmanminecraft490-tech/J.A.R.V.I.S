from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(os.environ.get("PROGRAMDATA", Path.home())) / "JARVIS"
APP_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = os.getenv("JARVIS_MODEL", "gemini-3.8-flash")
GEMINI_LIVE_MODEL = os.getenv("JARVIS_LIVE_MODEL", "gemini-3.8-live")
MAX_STEPS = int(os.getenv("JARVIS_MAX_STEPS", "40"))
SCREEN_MAX_WIDTH = int(os.getenv("JARVIS_SCREEN_MAX_WIDTH", "1440"))
