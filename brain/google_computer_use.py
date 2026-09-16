from __future__ import annotations

import base64
import json
from typing import Callable

from google import genai

from computer.executor import execute
from vision.screen import capture_jpeg
from config.settings import GEMINI_MODEL, MAX_STEPS


class GoogleComputerUse:
    """Gemini Computer Use loop for the real Windows desktop."""

    def __init__(self, api_key: str, on_status: Callable[[str], None] | None = None):
        self.client = genai.Client(api_key=api_key)
        self.on_status = on_status or (lambda _: None)

    @staticmethod
    def _action_to_local(name: str, args: dict) -> dict:
        # Gemini desktop Computer Use uses normalized 0..999 coordinates.
        if name in {"click", "double_click", "triple_click", "middle_click", "right_click", "move", "mouse_down", "mouse_up"}:
            import pyautogui
            width, height = pyautogui.size()
            mapped = {"x": int(args["x"] * width / 999), "y": int(args["y"] * height / 999)}
            mapping = {"click": "mouse.click", "double_click": "mouse.click", "triple_click": "mouse.click", "middle_click": "mouse.click", "right_click": "mouse.click", "move": "mouse.move", "mouse_down": "mouse.down", "mouse_up": "mouse.up"}
            mapped["clicks"] = {"double_click": 2, "triple_click": 3}.get(name, 1)
            mapped["button"] = {"middle_click": "middle", "right_click": "right"}.get(name, "left")
            return {"action": mapping[name], "parameters": mapped}
        if name == "type":
            return {"action": "keyboard.type", "parameters": {"text": args["text"]}}
        if name == "press_key":
            return {"action": "keyboard.press", "parameters": {"key": args["key"]}}
        if name == "hotkey":
            return {"action": "keyboard.hotkey", "parameters": {"keys": args["keys"]}}
        if name == "scroll":
            return {"action": "mouse.scroll", "parameters": {"amount": -int(args.get("magnitude_in_pixels", 300)) if args["direction"] == "down" else int(args.get("magnitude_in_pixels", 300))}}
        if name == "wait":
            return {"action": "wait", "parameters": {"seconds": args.get("seconds", 1)}}
        if name == "drag_and_drop":
            import pyautogui
            width, height = pyautogui.size()
            sx, sy = int(args["start_x"] * width / 999), int(args["start_y"] * height / 999)
            ex, ey = int(args["end_x"] * width / 999), int(args["end_y"] * height / 999)
            return {"action": "drag", "parameters": {"start_x": sx, "start_y": sy, "end_x": ex, "end_y": ey}}
        raise ValueError(f"Unsupported Gemini Computer Use function: {name}")

    def run(self, goal: str) -> str:
        screenshot = capture_jpeg()
        interaction = self.client.interactions.create(
            model=GEMINI_MODEL,
            input=[
                {"type": "text", "text": goal},
                {"type": "image", "data": base64.b64encode(screenshot).decode(), "mime_type": "image/jpeg"},
            ],
            tools=[{
                "type": "computer_use",
                "environment": "desktop",
                "enable_prompt_injection_detection": True,
            }],
        )

        for _ in range(MAX_STEPS):
            calls = [step for step in interaction.steps if step.type == "function_call"]
            if not calls:
                return getattr(interaction, "output_text", None) or "Task finished."

            results = []
            for call in calls:
                args = call.arguments if isinstance(call.arguments, dict) else json.loads(call.arguments)
                safety = args.get("safety_decision") if isinstance(args, dict) else None
                if safety and safety.get("decision") == "require_confirmation":
                    raise PermissionError(safety.get("explanation", "Google requested confirmation."))
                local = self._action_to_local(call.name, args)
                self.on_status(f"Executing {call.name}")
                result = execute(local)
                results.append({
                    "type": "function_result",
                    "name": call.name,
                    "call_id": call.id,
                    "result": [
                        {"type": "text", "text": json.dumps(result)},
                        {"type": "image", "data": base64.b64encode(capture_jpeg()).decode(), "mime_type": "image/jpeg"},
                    ],
                })

            interaction = self.client.interactions.create(
                model=GEMINI_MODEL,
                previous_interaction_id=interaction.id,
                input=results,
                tools=[{
                    "type": "computer_use",
                    "environment": "desktop",
                    "enable_prompt_injection_detection": True,
                }],
            )
        raise TimeoutError("JARVIS reached the maximum computer-use step budget.")
