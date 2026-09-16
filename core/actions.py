from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionName(str, Enum):
    OBSERVE = "observe"
    MOVE = "mouse.move"
    CLICK = "mouse.click"
    TYPE = "keyboard.type"
    PRESS = "keyboard.press"
    HOTKEY = "keyboard.hotkey"
    EXECUTE = "terminal.execute"
    CREATE_FILE = "filesystem.create_file"
    WRITE_FILE = "filesystem.write_file"
    START_PROCESS = "process.start"
    STOP_PROCESS = "process.stop"
    FOCUS_WINDOW = "window.focus"


@dataclass(slots=True)
class Action:
    action: ActionName
    target: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    expected_result: str = ""
    verification: str = ""

    def validate(self) -> None:
        if not self.action:
            raise ValueError("action is required")
        if not isinstance(self.parameters, dict):
            raise TypeError("parameters must be an object")
        if len(self.reason) > 2000:
            raise ValueError("reason is too long")
        if len(self.expected_result) > 2000:
            raise ValueError("expected_result is too long")
        if len(self.verification) > 2000:
            raise ValueError("verification is too long")
