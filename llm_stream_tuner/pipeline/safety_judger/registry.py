from ...utils.registry import BaseRegistry
from .base import BaseSafetyJudger


class SafetyJudgerRegistry(BaseRegistry[BaseSafetyJudger]):
    pass
