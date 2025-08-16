from abc import ABC, abstractmethod
from typing import Any

from ...utils.type_utils import AlpacaInputData


class BaseDataFormatter(ABC):
    @abstractmethod
    def format_conversation(self, raw_sample: dict[str, Any]) -> AlpacaInputData:
        """
        Convert a raw sample into a AlpacaInputData.

        Args:
            raw_sample (dict[str, Any]): The raw sample to format.

        Returns:
            AlpacaInputData: The formatted conversational sample.
        """
