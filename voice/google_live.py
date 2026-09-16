from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from google import genai
from google.genai import types

from config.settings import GEMINI_LIVE_MODEL


class GoogleLiveVoice:
    """Google Gemini Live API adapter. Audio transport is intentionally replaceable."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def session(self) -> AsyncIterator[object]:
        config = types.LiveConnectConfig(response_modalities=["AUDIO"])
        async with self.client.aio.live.connect(model=GEMINI_LIVE_MODEL, config=config) as session:
            yield session

    async def send_text(self, text: str) -> None:
        async with self.client.aio.live.connect(
            model=GEMINI_LIVE_MODEL,
            config=types.LiveConnectConfig(response_modalities=["AUDIO"]),
        ) as session:
            await session.send_realtime_input(text=text)
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    return

    def send_text_sync(self, text: str) -> None:
        asyncio.run(self.send_text(text))
