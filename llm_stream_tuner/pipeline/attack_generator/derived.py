from typing import Any, override

from ...inference import InferenceFactory
from ...prompts import PromptBuilderRegistry
from ...utils.type_utils import InferenceInput
from .base import BaseAttackGenerator
from .prompts import BaseAttackGeneratePromptBuilder
from .registry import AttackGeneratorRegistry


@AttackGeneratorRegistry.register("llm")
class LlmAttackGenerator(BaseAttackGenerator):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config=config)
        llm_cfgs = config["llm_cfgs"]
        model_cfgs: dict[str, Any] = llm_cfgs["model_cfgs"]
        inference_cfgs: dict[str, Any] = llm_cfgs["inference_cfgs"]
        cache_cfgs: dict[str, Any] | None = llm_cfgs.get("cache_cfgs", None)
        self.prompt_builder_cfgs = config["prompt_builder_cfgs"]
        PromptBuilderRegistry.verify_type(
            self.prompt_builder_cfgs, BaseAttackGeneratePromptBuilder  # type: ignore [type-abstract]
        )
        self.inference = InferenceFactory.get_inference_instance(
            model_cfgs=model_cfgs,
            inference_cfgs=inference_cfgs,
            cache_cfgs=cache_cfgs,
        )

    @override
    def generate_attack(
        self,
        prompts: list[str],
        reminder: str,
        example_prompt: str,
        example_attack_prompt: str,
    ) -> list[str]:
        outputs = self.inference.generate(
            [
                InferenceInput.from_prompts(prompt).with_meta_data(
                    {
                        "reminder": reminder,
                        "example_prompt": example_prompt,
                        "example_attack_prompt": example_attack_prompt,
                    }
                )
                for prompt in prompts
            ],
            prompt_template=self.prompt_builder_cfgs,
            enable_tqdm=True,
            tqdm_args={"desc": "Generating Attacks"},
        )
        attacks = [output.parsed_output for output in outputs]
        results: list[str] = []
        for attack in attacks:
            if attack is None:
                continue
            elif not isinstance(attack, str):
                raise TypeError(
                    f"IntentExtractor output is not str, but {type(attack).__name__}"
                )
            else:
                results.append(attack)
        return results
