from abc import abstractmethod
from typing import override

from ...prompts.base import BasePromptBuilder
from ...prompts.registry import PromptBuilderRegistry
from ...utils.type_utils import InferenceInput, InferenceOutput


class BaseSafetyJudgerPromptBuilder(BasePromptBuilder):
    @override
    def parse_output(self, raw_output: InferenceOutput) -> InferenceOutput:
        return raw_output.with_parsed_output(self._extract_answer(raw_output.response))

    @abstractmethod
    def _extract_answer(self, raw_output: str) -> bool:
        pass


@PromptBuilderRegistry.register("LlamaGuard")
class LlamaGuardPromptBuilder(BaseSafetyJudgerPromptBuilder):
    @override
    def process_input(self, raw_prompt: InferenceInput) -> InferenceInput:
        return raw_prompt

    @override
    def _extract_answer(self, raw_output: str) -> bool:
        return "unsafe" not in raw_output.lower()
