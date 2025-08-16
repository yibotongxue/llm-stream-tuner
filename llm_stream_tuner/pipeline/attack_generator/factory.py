from typing import Any

from .base import BaseAttackGenerator
from .registry import AttackGeneratorRegistry


def get_attack_generator(config: dict[str, Any]) -> BaseAttackGenerator:
    name = config["type"]
    return AttackGeneratorRegistry.get_by_name(name)(config)
