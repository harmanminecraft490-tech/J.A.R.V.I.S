from __future__ import annotations

import os
import subprocess
import time
from typing import Any

import pyautogui

pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True


def execute(action: dict[str, Any]) -> dict[str, Any]:
    name = action["action"]
    p = action.get("parameters", {})
    if name == "mouse.move":
        pyautogui.moveTo(float(p["x"]), float(p["y"]), duration=float(p.get("duration", 0.08)))
    elif name == "mouse.click":
        pyautogui.click(float(p["x"]), float(p["y"]), clicks=int(p.get("clicks", 1)), button=p.get("button", "left"))
    elif name == "mouse.down":
        pyautogui.moveTo(float(p["x"]), float(p["y"]), duration=0.03); pyautogui.mouseDown(button=p.get("button", "left"))
    elif name == "mouse.up":
        pyautogui.moveTo(float(p["x"]), float(p["y"]), duration=0.03); pyautogui.mouseUp(button=p.get("button", "left"))
    elif name == "mouse.scroll":
        pyautogui.scroll(int(p["amount"]))
    elif name == "drag":
        pyautogui.moveTo(p["start_x"], p["start_y"], duration=0.03); pyautogui.dragTo(p["end_x"], p["end_y"], duration=0.12, button="left")
    elif name == "keyboard.type":
        pyautogui.write(str(p["text"]), interval=float(p.get("interval", 0)))
    elif name == "keyboard.press":
        pyautogui.press(p["key"])
    elif name == "keyboard.hotkey":
        pyautogui.hotkey(*p["keys"])
    elif name == "terminal.execute":
        completed = subprocess.run(p["command"], shell=True, capture_output=True, text=True, timeout=float(p.get("timeout", 120)))
        return {"ok": completed.returncode == 0, "stdout": completed.stdout[-8000:], "stderr": completed.stderr[-8000:], "code": completed.returncode}
    elif name == "process.start":
        subprocess.Popen(p["command"], shell=True, cwd=p.get("cwd") or None)
    elif name == "filesystem.create_file":
        path = os.path.abspath(p["path"]); os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "a", encoding="utf-8").close()
    elif name == "filesystem.write_file":
        path = os.path.abspath(p["path"]); os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f: f.write(p["content"])
    elif name == "wait":
        time.sleep(float(p.get("seconds", 0.5)))
    else:
        raise ValueError(f"Unsupported computer action: {name}")
    return {"ok": True}
