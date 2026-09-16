from __future__ import annotations

from enum import Enum

from .actions import Action, ActionName


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


HIGH_RISK: set[ActionName] = {
    ActionName.STOP_PROCESS,
}

MEDIUM_RISK: set[ActionName] = {
    ActionName.EXECUTE,
    ActionName.CREATE_FILE,
    ActionName.WRITE_FILE,
    ActionName.START_PROCESS,
}


def classify(action: Action) -> RiskLevel:
    if action.action in HIGH_RISK:
        return RiskLevel.HIGH
    if action.action in MEDIUM_RISK:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def requires_confirmation(action: Action, *, allow_high_risk: bool = False) -> bool:
    level = classify(action)
    return level is RiskLevel.HIGH and not allow_high_risk
