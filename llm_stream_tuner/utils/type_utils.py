from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel

from .logger import Logger, app_logger


class CustomBaseModel(BaseModel):  # type: ignore [misc]
    def to_brief_dict(self) -> dict[str, Any]:
        raw_dict = deepcopy(self.model_dump())
        if "meta_data" in raw_dict:
            raw_dict.pop("meta_data")
        return raw_dict  # type: ignore [no-any-return]


class InferenceInput(CustomBaseModel):
    conversation: list[dict[str, Any]]
    system_prompt: str
    meta_data: dict[str, Any]

    @classmethod
    def from_prompts(
        cls: type[InferenceInput], prompt: str, system_prompt: str = ""
    ) -> InferenceInput:
        return cls(
            conversation=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            system_prompt=system_prompt,
            meta_data={},
        )

    @classmethod
    def from_output(
        cls,
        output: InferenceOutput,
        logger: Logger | None = None,
        use_parsed_output: bool = False,
    ) -> InferenceInput:
        conversation = InferenceInput(**output.input).conversation.copy()
        if conversation[0]["role"] == "system":
            conversation.pop(0)
        if logger is None:
            logger = app_logger
        if conversation[-1]["role"] == "assistant":
            logger.warning(
                f"The last turn of conversation is assistant.\nThe details is {conversation[-1]}. We will remove it"
            )
            conversation.pop()
        if use_parsed_output:
            if output.parsed_output is None:
                logger.warning(
                    f"The output of {output.parsed_output} is None. We will use the raw output."
                )
                response = output.response
            if not isinstance(output.parsed_output, str):
                logger.warning(
                    f"The output of {output.parsed_output} is not str. We will use the raw output."
                )
                response = output.response
            else:
                response = output.parsed_output
        else:
            response = output.response
        conversation.append({"role": "assistant", "content": response})
        return InferenceInput(
            conversation=conversation,
            system_prompt="",
            meta_data={},
        )

    def get_last_user_message(self) -> str:
        if len(self.conversation) == 0:
            raise ValueError("The conversation is empty")
        last_turn = self.conversation[-1]
        if last_turn["role"] != "user":
            raise ValueError("The last turn is not user")
        return last_turn["content"]  # type: ignore [no-any-return]

    def with_update_prompt(self, new_prompt: str) -> InferenceInput:
        new_conversation = deepcopy(self.conversation)
        new_conversation[-1] = {"role": "user", "content": new_prompt}
        raw = {
            **self.model_dump(),
            "conversation": new_conversation,
        }
        return InferenceInput(**raw)

    def get_raw_question(self) -> str:
        if "raw_question" in self.meta_data:
            return self.meta_data["raw_question"]  # type: ignore [no-any-return]
        return self.conversation[-1]["content"]  # type: ignore [no-any-return]

    def with_meta_data(self, meta_data: dict[str, Any]) -> InferenceInput:
        new_meta_data = {
            **self.meta_data,
            **meta_data,
        }
        raw = {
            **self.model_dump(),
            "meta_data": new_meta_data,
        }
        return InferenceInput(**raw)


class InferenceOutput(CustomBaseModel):
    response: str
    parsed_output: Any | None = None
    input: dict[str, Any]
    engine: str
    meta_data: dict[str, Any]

    def with_parsed_output(self, parsed_output: Any | None) -> InferenceOutput:
        raw = {
            **self.model_dump(),
            "parsed_output": parsed_output,
        }
        return InferenceOutput(**raw)


class AlpacaInputData(CustomBaseModel):
    instruction: str
    input: str
    output: str
    meta_data: dict[str, Any] = {}


def to_dict(obj: BaseModel | dict[str, Any]) -> dict[str, Any]:

    def _to_dict(
        obj: BaseModel | dict[str, Any] | list[Any] | Any
    ) -> dict[str, Any] | list[Any] | Any:
        if isinstance(obj, BaseModel):
            return _to_dict(obj.model_dump())
        if isinstance(obj, dict):
            return {k: _to_dict(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_to_dict(e) for e in obj]
        return obj

    return _to_dict(obj)  # type: ignore [return-value]
