from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

import pyautogui

from computer.executor import execute
from vision.screen import capture_jpeg


class LocalAgent:
    """No-key local agent. Uses deterministic Windows actions first and Ollama vision when available."""

    def __init__(self, on_status: Callable[[str], None] | None = None):
        self.on_status = on_status or (lambda _: None)
        self.model = os.getenv("JARVIS_LOCAL_MODEL", "qwen3-vl:8b")
        self.ollama_url = os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
        self.stop_requested = False

    def stop(self) -> None:
        self.stop_requested = True
        pyautogui.keyUp("ctrl")
        pyautogui.keyUp("shift")
        pyautogui.keyUp("alt")
        pyautogui.keyUp("win")
        pyautogui.mouseUp()

    def _log(self, text: str) -> None:
        self.on_status(text)

    def _deterministic(self, goal: str) -> str | None:
        g = goal.lower().strip()
        apps = {
            "chrome": "start chrome", "google chrome": "start chrome",
            "notepad": "start notepad", "calculator": "start calc",
            "file explorer": "start explorer", "explorer": "start explorer",
            "terminal": "start wt", "powershell": "start powershell",
            "vscode": "code", "visual studio code": "code",
        }
        for name, command in apps.items():
            if re.search(rf"\b(open|launch|start)\s+{re.escape(name)}\b", g):
                execute({"action": "process.start", "parameters": {"command": command}})
                self._log(f"Opened {name}")
                return f"Opened {name}."
        m = re.search(r"(?:create|make) (?:a )?(?:folder|directory) (?:called |named )?[\"']?(.+?)[\"']?$", goal, re.I)
        if m:
            p = Path(m.group(1).strip()).expanduser()
            p.mkdir(parents=True, exist_ok=True)
            self._log(f"Created folder: {p}")
            return f"Created folder {p}."
        if re.fullmatch(r"(take )?(a )?screenshot", g):
            Path("runtime").mkdir(exist_ok=True)
            target = Path("runtime") / "jarvis-screenshot.png"
            pyautogui.screenshot(str(target))
            self._log(f"Saved screenshot: {target}")
            return f"Screenshot saved to {target}."
        return None

    def _ollama(self, goal: str) -> dict | None:
        image = base64.b64encode(capture_jpeg(max_width=1280, quality=65)).decode("ascii")
        prompt = f'''You are JARVIS, a Windows desktop agent. Execute the user's objective through safe computer actions.\n\nUSER OBJECTIVE: {goal}\n\nReturn ONLY valid JSON with this shape: {{"done":false,"message":"short status","actions":[{{"action":"...","parameters":{{}}}}]}}.\nAllowed actions: mouse.move(x,y), mouse.click(x,y,button,clicks), mouse.scroll(amount), keyboard.type(text), keyboard.press(key), keyboard.hotkey(keys array), process.start(command), terminal.execute(command,timeout), filesystem.create_file(path), filesystem.write_file(path,content), wait(seconds).\nCoordinates are actual screen pixels. Prefer direct filesystem/process actions over GUI when reliable. Never delete data, send messages, buy things, change security settings, or expose secrets. Use at most 3 actions per response.''' 
        payload = {"model": self.model, "stream": False, "format": "json", "messages": [{"role": "user", "content": prompt, "images": [image]}]}
        req = urllib.request.Request(self.ollama_url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                body = json.loads(r.read().decode())
            return json.loads(body.get("message", {}).get("content", "{}"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            self._log(f"Local vision brain unavailable: {exc}")
            return None

    def run(self, goal: str, max_steps: int = 24) -> str:
        self.stop_requested = False
        quick = self._deterministic(goal)
        if quick:
            return quick
        for step in range(max_steps):
            if self.stop_requested:
                return "Task cancelled."
            self._log(f"Observing desktop • step {step + 1}")
            plan = self._ollama(goal)
            if not plan:
                return "I need a local vision model. Start Ollama with a vision model (for example qwen3-vl:8b), then retry."
            if plan.get("message"):
                self._log(plan["message"])
            if plan.get("done"):
                return plan.get("message") or "Task complete."
            actions = plan.get("actions") or []
            if not actions:
                return plan.get("message") or "The local brain did not produce an action."
            for action in actions[:3]:
                if self.stop_requested:
                    return "Task cancelled."
                name = action.get("action", "")
                self._log(f"Executing {name}")
                result = execute({"action": name, "parameters": action.get("parameters", {})})
                if not result.get("ok", True):
                    self._log(f"Action failed • {result.get('stderr', '')[-160:]}")
            self._log("Verifying desktop state")
        return "Task reached the local reasoning budget without a verified completion."
