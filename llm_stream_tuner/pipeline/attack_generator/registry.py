from ...utils.registry import BaseRegistry
from .base import BaseAttackGenerator


class AttackGeneratorRegistry(BaseRegistry[BaseAttackGenerator]):
    pass
