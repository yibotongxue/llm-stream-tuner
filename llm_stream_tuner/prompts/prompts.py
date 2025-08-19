from ..utils.type_utils import InferenceInput, InferenceOutput
from .base import BasePromptBuilder
from .registry import PromptBuilderRegistry


@PromptBuilderRegistry.register("ThinkTag")
class ThinkTagPromptBuilder(BasePromptBuilder):
    def process_input(self, raw_input: InferenceInput) -> InferenceInput:
        return raw_input

    def parse_output(self, raw_output: InferenceOutput) -> InferenceOutput:
        response = raw_output.response
        raw_output_meta_data = raw_output.meta_data
        if (
            "choices" in raw_output_meta_data
            and isinstance(raw_output_meta_data["choices"], list)
            and len(raw_output_meta_data["choices"]) > 0
        ):
            choice_0 = raw_output_meta_data["choices"][0]
            if (
                isinstance(choice_0, dict)
                and "message" in choice_0
                and isinstance(choice_0["message"], dict)
            ):
                message = choice_0["message"]
                if "reasoning_content" in message and isinstance(
                    message["reasoning_content"], str
                ):
                    reasoning = message["reasoning_content"]
                    parsed_output = f"<think>\n{reasoning}\n</think>{response}"
                    return raw_output.with_parsed_output(parsed_output)
        return raw_output.with_parsed_output(response)
