from __future__ import annotations

from dataclasses import replace
from threading import RLock
from uuid import uuid4

from .state import TaskState, TaskStatus


class TaskEngine:
    """Thread-safe task registry for the agent control loop."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskState] = {}
        self._lock = RLock()

    def create(self, goal: str) -> TaskState:
        goal = goal.strip()
        if not goal:
            raise ValueError("goal cannot be empty")
        task = TaskState(task_id=str(uuid4()), goal=goal)
        with self._lock:
            self._tasks[task.task_id] = task
        return replace(task)

    def get(self, task_id: str) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            return replace(task)

    def set_status(self, task_id: str, status: TaskStatus) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.status = status
            return replace(task)

    def set_plan(self, task_id: str, plan: list[str]) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.plan = list(plan)
            return replace(task)

    def record_action(self, task_id: str, action: str) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.current_action = action
            return replace(task)

    def complete_action(self, task_id: str, action: str) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.completed_actions.append(action)
            task.current_action = None
            return replace(task)

    def record_error(self, task_id: str, message: str) -> TaskState:
        with self._lock:
            task = self._tasks[task_id]
            task.errors.append(message)
            task.recovery_attempts += 1
            return replace(task)

    def cancel(self, task_id: str) -> TaskState:
        return self.set_status(task_id, TaskStatus.CANCELLED)

    def pause(self, task_id: str) -> TaskState:
        return self.set_status(task_id, TaskStatus.PAUSED)

    def resume(self, task_id: str) -> TaskState:
        return self.set_status(task_id, TaskStatus.RUNNING)
