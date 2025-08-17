from abc import ABC, abstractmethod
from typing import Any

from ...utils.logger import Logger


class BaseSystemPromptRemover(ABC):
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.logger = Logger(f"{self.__module__}.{self.__class__.__name__}")

    @abstractmethod
    def remove_system_prompt(self, responses: list[str]) -> list[str | None]: ...
