from abc import ABC, abstractmethod
from typing import Any


class BaseSystemPromptRemover(ABC):
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def remove_system_prompt(self, responses: list[str]) -> list[str]: ...
