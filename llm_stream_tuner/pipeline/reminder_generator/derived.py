from typing import Any, override

from ...inference import InferenceFactory
from ...prompts import PromptBuilderRegistry
from ...utils.type_utils import InferenceInput
from .base import BaseReminderGenerator
from .prompts import BaseReminderGeneratePromptBuilder
from .registry import ReminderGeneratorRegistry


@ReminderGeneratorRegistry.register("llm")
class LlmReminderGenerator(BaseReminderGenerator):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config=config)
        llm_cfgs = config["llm_cfgs"]
        self.model_cfgs: dict[str, Any] = llm_cfgs["model_cfgs"]
        self.inference_cfgs: dict[str, Any] = llm_cfgs["inference_cfgs"]
        self.cache_cfgs: dict[str, Any] | None = llm_cfgs.get("cache_cfgs", None)
        self.prompt_builder_cfgs = config["prompt_builder_cfgs"]
        PromptBuilderRegistry.verify_type(
            self.prompt_builder_cfgs, BaseReminderGeneratePromptBuilder  # type: ignore [type-abstract]
        )

    @override
    def generate_reminder(
        self,
        prompt: str,
        response: str,
        intent: str | None,
        prev_reminder: str | None = None,
    ) -> str | None:
        inference = InferenceFactory.get_inference_instance(
            model_cfgs=self.model_cfgs,
            inference_cfgs=self.inference_cfgs,
            cache_cfgs=self.cache_cfgs,
        )
        output = inference.generate(
            [
                InferenceInput.from_prompts(prompt).with_meta_data(
                    {
                        "response": response,
                        "intent": intent,
                        "prev_reminder": prev_reminder,
                    }
                )
            ],
            prompt_template=self.prompt_builder_cfgs,
        )
        reminder = output[0].parsed_output
        if reminder is None:
            return None
        if not isinstance(reminder, str):
            raise TypeError(
                f"ReminderGenerate output is not str, but {type(reminder).__name__}"
            )
        return reminder
