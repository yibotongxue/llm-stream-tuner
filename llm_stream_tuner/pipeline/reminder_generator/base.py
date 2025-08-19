from abc import ABC, abstractmethod
from typing import Any


class BaseReminderGenerator(ABC):
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def generate_reminder(
        self,
        prompt: str,
        response: str,
        intent: str | None,
        prev_reminder: str | None = None,
    ) -> str | None: ...
