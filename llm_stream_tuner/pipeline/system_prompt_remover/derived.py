from typing import Any, override

from ...inference import InferenceFactory
from ...prompts import PromptBuilderRegistry
from ...utils.type_utils import InferenceInput
from .base import BaseSystemPromptRemover
from .prompts import BaseSystemPromptRemoverPromptBuilder
from .registry import SystemPromptRemoverRegistry


@SystemPromptRemoverRegistry.register("llm")
class LlmSystemPromptRemover(BaseSystemPromptRemover):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config=config)
        llm_cfgs = config["llm_cfgs"]
        model_cfgs: dict[str, Any] = llm_cfgs["model_cfgs"]
        inference_cfgs: dict[str, Any] = llm_cfgs["inference_cfgs"]
        cache_cfgs: dict[str, Any] | None = llm_cfgs.get("cache_cfgs", None)
        self.prompt_builder_cfgs = config["prompt_builder_cfgs"]
        PromptBuilderRegistry.verify_type(
            self.prompt_builder_cfgs, BaseSystemPromptRemoverPromptBuilder  # type: ignore [type-abstract]
        )
        self.inference = InferenceFactory.get_inference_instance(
            model_cfgs=model_cfgs,
            inference_cfgs=inference_cfgs,
            cache_cfgs=cache_cfgs,
        )

    @override
    def remove_system_prompt(self, responses: list[str]) -> list[str]:
        outputs = self.inference.generate(
            [InferenceInput.from_prompts(response) for response in responses],
            prompt_template=self.prompt_builder_cfgs,
            enable_tqdm=True,
            tqdm_args={"desc": "Removing System Prompt"},
        )
        new_responses = [output.parsed_output for output in outputs]
        results: list[str] = []
        for new_response in new_responses:
            if new_response is None:
                continue
            elif not isinstance(new_response, str):
                raise TypeError(
                    f"IntentExtractor output is not str, but {type(new_response).__name__}"
                )
            else:
                results.append(new_response)
        return results
