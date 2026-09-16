from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .actions import Action
from .state import Observation, TaskState, TaskStatus
from .task_engine import TaskEngine


class Brain(Protocol):
    def plan(self, task: TaskState, observation: Observation) -> list[Action]: ...


class Observer(Protocol):
    def observe(self) -> Observation: ...


class Executor(Protocol):
    def execute(self, action: Action) -> None: ...


@dataclass
class Agent:
    brain: Brain
    observer: Observer
    executor: Executor
    tasks: TaskEngine

    def run_once(self, task_id: str) -> TaskState:
        task = self.tasks.set_status(task_id, TaskStatus.RUNNING)
        observation = self.observer.observe()
        actions = self.brain.plan(task, observation)
        self.tasks.set_plan(task_id, [a.action.value for a in actions])

        for action in actions:
            action.validate()
            self.tasks.record_action(task_id, action.action.value)
            self.executor.execute(action)
            self.tasks.complete_action(task_id, action.action.value)

        return self.tasks.set_status(task_id, TaskStatus.SUCCESS)
