from typing import Any

from .base import BaseIntentExtractor
from .registry import IntentExtractorRegistry


def get_intent_extractor(cfgs: dict[str, Any]) -> BaseIntentExtractor:
    intent_extractor_type = cfgs["type"]
    intent_extractor = IntentExtractorRegistry.get_by_name(intent_extractor_type)(cfgs)
    return intent_extractor
