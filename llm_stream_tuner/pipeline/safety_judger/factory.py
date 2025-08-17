from typing import Any

from .base import BaseSafetyJudger
from .registry import SafetyJudgerRegistry


def get_safety_judger(judger_cfgs: dict[str, Any]) -> BaseSafetyJudger:
    judger_type = judger_cfgs.pop("type")
    judger = SafetyJudgerRegistry.get_by_name(judger_type)(judger_cfgs)
    return judger
