from typing import Any

from ...utils.type_utils import AlpacaInputData
from .base import BaseDataFormatter
from .registry import DataFormatterRegistry


@DataFormatterRegistry.register("STAR-1")
class Star1DataFormatter(BaseDataFormatter):
    def format_conversation(self, raw_sample: dict[str, Any]) -> AlpacaInputData:
        return AlpacaInputData(
            instruction=raw_sample["question"],
            input="",
            output=raw_sample["response"],
            meta_data={"raw_sample": raw_sample.copy()},
        )
