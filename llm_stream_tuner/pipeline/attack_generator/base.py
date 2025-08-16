from abc import ABC, abstractmethod
from typing import Any


class BaseAttackGenerator(ABC):
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def generate_attack(
        self,
        prompt: str,
        reminder: str,
        example_prompt: str,
        example_attack_prompt: str,
    ) -> str | None: ...
