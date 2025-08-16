from typing import Any

from .base import BaseReminderGenerator
from .registry import ReminderGeneratorRegistry


def get_reminder_generator(cfgs: dict[str, Any]) -> BaseReminderGenerator:
    name = cfgs["type"]
    reminder_generator = ReminderGeneratorRegistry.get_by_name(name)(cfgs)
    return reminder_generator
