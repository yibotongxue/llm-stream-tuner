from typing import Any, override

from ...inference import InferenceFactory
from ...prompts import PromptBuilderRegistry
from ...utils.type_utils import InferenceInput, InferenceOutput
from .base import BaseSafetyJudger
from .prompts import BaseSafetyJudgerPromptBuilder
from .registry import SafetyJudgerRegistry


@SafetyJudgerRegistry.register("llm")
class LlmSafetyJudger(BaseSafetyJudger):
    def __init__(self, judger_cfgs: dict[str, Any]) -> None:
        super().__init__(judger_cfgs=judger_cfgs)
        llm_cfgs = judger_cfgs["llm_cfgs"]
        self.model_cfgs: dict[str, Any] = llm_cfgs["model_cfgs"]
        self.inference_cfgs: dict[str, Any] = llm_cfgs["inference_cfgs"]
        self.cache_cfgs: dict[str, Any] | None = llm_cfgs.get("cache_cfgs", None)
        self.prompt_builder_cfgs = judger_cfgs["prompt_builder_cfgs"]
        PromptBuilderRegistry.verify_type(
            self.prompt_builder_cfgs, BaseSafetyJudgerPromptBuilder  # type: ignore [type-abstract]
        )

    @override
    def judge(self, outputs: list[InferenceOutput]) -> list[bool]:
        inference = InferenceFactory.get_inference_instance(
            model_cfgs=self.model_cfgs,
            inference_cfgs=self.inference_cfgs,
            cache_cfgs=self.cache_cfgs,
        )
        inputs = [InferenceInput.from_output(output) for output in outputs]
        outputs = inference.generate(
            inputs=inputs,
            prompt_template=self.prompt_builder_cfgs,
            enable_tqdm=True,
            tqdm_args={"desc": "Judging Safety"},
        )
        results: list[bool] = []
        for output in outputs:
            if output.parsed_output is None:
                self.logger.warning(
                    f"SafetyJudger output is None, input: {output.input}, output: {output.response}"
                )
                results.append(False)
            elif not isinstance(output.parsed_output, bool):
                self.logger.error(
                    f"SafetyJudger output is not bool, but {type(output.parsed_output).__name__}, input: {output.input}, output: {output.response}"
                )
                results.append(False)
            else:
                results.append(output.parsed_output)
        return results
