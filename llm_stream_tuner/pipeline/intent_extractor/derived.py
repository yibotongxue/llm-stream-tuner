from typing import Any, override

from ...inference import InferenceFactory
from ...prompts import PromptBuilderRegistry
from ...utils.type_utils import InferenceInput
from .base import BaseIntentExtractor
from .prompts import BaseIntentExtractPromptBuilder
from .registry import IntentExtractorRegistry


@IntentExtractorRegistry.register("llm")
class LlmIntentExtractor(BaseIntentExtractor):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config=config)
        llm_cfgs = config["llm_cfgs"]
        model_cfgs: dict[str, Any] = llm_cfgs["model_cfgs"]
        inference_cfgs: dict[str, Any] = llm_cfgs["inference_cfgs"]
        cache_cfgs: dict[str, Any] | None = llm_cfgs.get("cache_cfgs", None)
        self.prompt_builder_cfgs = config["prompt_builder_cfgs"]
        PromptBuilderRegistry.verify_type(
            self.prompt_builder_cfgs, BaseIntentExtractPromptBuilder  # type: ignore [type-abstract]
        )
        self.inference = InferenceFactory.get_inference_instance(
            model_cfgs=model_cfgs,
            inference_cfgs=inference_cfgs,
            cache_cfgs=cache_cfgs,
        )

    @override
    def extract_intent(self, prompt: str) -> str | None:
        output = self.inference.generate(
            [InferenceInput.from_prompts(prompt)],
            prompt_template=self.prompt_builder_cfgs,
        )
        intent = output[0].parsed_output
        if intent is None:
            return None
        if not isinstance(intent, str):
            raise TypeError(
                f"IntentExtractor output is not str, but {type(intent).__name__}"
            )
        return intent
