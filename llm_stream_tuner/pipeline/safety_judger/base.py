from abc import ABC, abstractmethod
from typing import Any

from ...utils.logger import Logger
from ...utils.type_utils import InferenceOutput


class BaseSafetyJudger(ABC):
    def __init__(self, judger_cfgs: dict[str, Any]) -> None:
        self.judger_cfgs = judger_cfgs
        self.logger = Logger(f"{self.__module__}.{self.__class__.__name__}")

    @abstractmethod
    def judge(self, outputs: list[InferenceOutput]) -> list[bool]: ...
