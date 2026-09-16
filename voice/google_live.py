from __future__ import annotations

import asyncio
from google import genai
from google.genai import types
from config.settings import GEMINI_LIVE_MODEL


class GoogleLiveVoice:
    """Google Gemini Live API adapter; audio transport stays replaceable."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def speak(self, text: str) -> list[bytes]:
        audio: list[bytes] = []
        async with self.client.aio.live.connect(
            model=GEMINI_LIVE_MODEL,
            config=types.LiveConnectConfig(response_modalities=["AUDIO"]),
        ) as session:
            await session.send_realtime_input(text=text)
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if getattr(part, "inline_data", None) and part.inline_data.data:
                            audio.append(part.inline_data.data)
                if response.server_content and response.server_content.turn_complete:
                    break
        return audio

    def speak_sync(self, text: str) -> list[bytes]:
        return asyncio.run(self.speak(text))
