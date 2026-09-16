from core.actions import Action, ActionName
from core.risk import RiskLevel, classify, requires_confirmation
from core.state import TaskStatus
from core.task_engine import TaskEngine


def test_task_lifecycle() -> None:
    engine = TaskEngine()
    task = engine.create("build a project")
    assert task.status is TaskStatus.PENDING

    engine.set_status(task.task_id, TaskStatus.RUNNING)
    engine.set_plan(task.task_id, ["inspect", "build"])
    engine.record_action(task.task_id, "inspect")
    engine.complete_action(task.task_id, "inspect")

    current = engine.get(task.task_id)
    assert current.status is TaskStatus.RUNNING
    assert current.completed_actions == ["inspect"]


def test_action_validation_and_risk() -> None:
    action = Action(
        action=ActionName.CLICK,
        parameters={"x": 10, "y": 20},
        expected_result="button activates",
        verification="observe UI state",
    )
    action.validate()
    assert classify(action) is RiskLevel.LOW
    assert requires_confirmation(action) is False


def test_high_risk_process_stop_requires_confirmation() -> None:
    action = Action(action=ActionName.STOP_PROCESS, parameters={"pid": 1234})
    action.validate()
    assert classify(action) is RiskLevel.HIGH
    assert requires_confirmation(action) is True
