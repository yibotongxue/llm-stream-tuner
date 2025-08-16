from abc import ABC, abstractmethod
from typing import Any


class BaseIntentExtractor(ABC):
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def extract_intent(self, prompt: str) -> str | None: ...
