from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    RECOVERABLE_FAILURE = "RECOVERABLE_FAILURE"
    USER_INPUT_REQUIRED = "USER_INPUT_REQUIRED"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"
    FATAL_FAILURE = "FATAL_FAILURE"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"


@dataclass(slots=True)
class Observation:
    timestamp: float
    source: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskState:
    task_id: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    plan: list[str] = field(default_factory=list)
    completed_actions: list[str] = field(default_factory=list)
    current_action: str | None = None
    observations: list[Observation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    recovery_attempts: int = 0
