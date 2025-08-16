from typing import Any

from .base import BaseSystemPromptRemover
from .registry import SystemPromptRemoverRegistry


def get_system_prompt_remover(config: dict[str, Any]) -> BaseSystemPromptRemover:
    name = config["type"]
    system_prompt_remover = SystemPromptRemoverRegistry.get_by_name(name)(config=config)
    return system_prompt_remover
