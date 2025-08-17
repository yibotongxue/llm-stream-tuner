from typing import Any, override

from ..utils.json_utils import save_json
from ..utils.type_utils import AlpacaInputData, InferenceInput, InferenceOutput
from .base import BaseTask


class SingleTask(BaseTask):
    def __init__(self, task_cfgs: dict[str, Any]) -> None:
        super().__init__(task_cfgs)

    @override
    def run(self) -> None:
        if len(self.attack_dataset) != 1:
            raise ValueError("SingleTask only support 1 attack sample")
        attack_sample = self.attack_dataset[0]
        attack_prompt = attack_sample.get_prompt()
        self.logger.info(f"攻击提示：{attack_prompt}")
        attack_input = InferenceInput.from_prompts(attack_prompt)
        attack_outputs = self.inference.generate([attack_input])
        self.logger.info(f"攻击提示的响应：{attack_outputs[0].response}")
        safety_judge_results = self.safety_judger.judge(attack_outputs)
        if safety_judge_results[0]:
            self.logger.info("攻击提示失败，模型得到的响应被判定为安全")
            return
        self.logger.info("攻击提示成功，模型得到的响应被判定为不安全")
        self.logger.info(
            f"攻击提示: {attack_prompt}, 模型得到的响应: {attack_outputs[0].response}"
        )

        intent = self.extract_intent(attack_prompt)
        if intent is None:
            return

        reminder = self.generate_reminder(
            attack_prompt, attack_outputs[0].response, intent
        )
        if reminder is None:
            return

        self.logger.info(f"开始生成攻击提示")
        attack_prompts = self.attack_generator.generate_attack(
            prompts=[prompt.get_prompt() for prompt in self.dataset],
            reminder=reminder,
            example_prompt=intent,
            example_attack_prompt=attack_prompt,
        )
        self.logger.info(
            f"从{len(self.dataset)}条数据中生成了{len(attack_prompts)}条攻击提示"
        )
        if len(attack_prompts) == 0:
            self.logger.info("生成攻击提示失败")
            return
        self.logger.info(f"第一条攻击提示：{attack_prompts[0]}")
        if len(attack_prompts) > 1:
            self.logger.info(f"第二条攻击提示：{attack_prompts[1]}")

        attack_outputs = self.generate_responses(attack_prompts)

        safety_judgment, asr = self.judge_safety(attack_outputs, attack_prompts)
        if asr < self.asr_threshold:
            self.logger.info(
                f"最开始攻击成功率为{asr}，低于阈值{self.asr_threshold}，攻击失败"
            )
            return

        safe_dataset, unsafe_dataset = self.split_dataset(
            attack_outputs, attack_prompts, safety_judgment
        )
        self.logger.info(
            f"安全数据数量: {len(safe_dataset)}, 不安全数据数量: {len(unsafe_dataset)}"
        )

        result_dataset = safe_dataset.copy()
        original_attack_prompts = attack_prompts.copy()
        attack_prompts = [prompt.get_prompt() for prompt in unsafe_dataset]

        for i in range(self.attack_epoch_num):
            attack_outputs = self.generate_responses(attack_prompts, reminder)
            safety_judgment, asr = self.judge_safety(attack_outputs, attack_prompts)
            safe_dataset, unsafe_dataset = self.split_dataset(
                attack_outputs, attack_prompts, safety_judgment
            )
            self.logger.info(f"第{i+1}轮攻击成功率: {asr}")
            result_dataset.extend(safe_dataset)
            self.logger.info(
                f"增加{len(safe_dataset)}条安全数据，总计{len(result_dataset)}条数据，占比{len(result_dataset)} / {len(original_attack_prompts)} = {len(result_dataset) / len(original_attack_prompts)}"
            )
            if asr < self.asr_threshold:
                self.logger.info(
                    f"攻击成功率为{asr}，低于阈值{self.asr_threshold}，攻击结束"
                )
                break
            attack_prompts = [prompt.get_prompt() for prompt in unsafe_dataset]
            attack_prompt = attack_prompts[0]
            self.logger.info(f"第{i+1}轮攻击提示：{attack_prompt}")
            intent = self.extract_intent(attack_prompt)
            if intent is None:
                self.logger.info("解析攻击提示的意图失败，结束攻击")
                break
            reminder = self.generate_reminder(
                attack_prompt, attack_outputs[0].response, intent
            )
            if reminder is None:
                self.logger.info("生成提醒失败，结束攻击")
                break

        self.logger.info(f"攻击结束，共生成{len(result_dataset)}条数据")
        self.logger.info(
            f"开始保存攻击数据集到{self.output_dir / 'attack_dataset.json'}"
        )
        dataset_to_save = [data.model_dump() for data in result_dataset]
        save_json(dataset_to_save, self.output_dir / "attack_dataset.json")
        self.logger.info(f"攻击数据集保存完成")

    def extract_intent(self, attack_prompt: str) -> str | None:
        self.logger.info(f"开始解析攻击提示的意图")
        intent = None
        for i in range(self.retry_num):
            intent = self.intent_extractor.extract_intent(
                prompt=attack_prompt,
            )
            if intent is None:
                self.logger.info(f"第{i+1}次解析攻击提示的意图失败，重试")
                continue
            break
        if intent is None:
            self.logger.info(f"解析攻击提示的意图失败，{self.retry_num}次重试均失败")
            return None
        self.logger.info(f"攻击提示的意图为：{intent}")
        return intent

    def generate_reminder(
        self, attack_prompt: str, attack_output: str, intent: str
    ) -> str | None:
        self.logger.info(f"开始生成提醒")
        reminder = None
        for i in range(self.retry_num):
            reminder = self.reminder_generator.generate_reminder(
                prompt=attack_prompt,
                response=attack_output,
                intent=intent,
            )
            if reminder is None:
                self.logger.info(f"第{i+1}次生成提醒失败，重试")
                continue
            break
        if reminder is None:
            self.logger.info(f"生成提醒失败，{self.retry_num}次重试均失败")
            return None
        self.logger.info(f"生成的提醒为：{reminder}")
        return reminder

    def generate_responses(
        self, attack_prompts: list[str], reminder: str = ""
    ) -> list[InferenceOutput]:
        self.logger.info(f"开始生成攻击提示的响应")
        attack_inputs = [
            InferenceInput.from_prompts(prompt, system_prompt=reminder)
            for prompt in attack_prompts
        ]
        attack_outputs = self.inference.generate(
            inputs=attack_inputs,
            enable_tqdm=True,
            tqdm_args={"desc": "生成攻击提示的响应"},
        )
        self.logger.info(
            f"第一条攻击提示：{attack_prompts[0]}，模型得到的响应：{attack_outputs[0].response}"
        )
        if len(attack_inputs) > 1:
            self.logger.info(
                f"第二条攻击提示：{attack_prompts[1]}，模型得到的响应：{attack_outputs[1].response}"
            )
        return attack_outputs

    def judge_safety(
        self, attack_outputs: list[InferenceOutput], attack_prompts: list[str]
    ) -> tuple[list[bool], float]:
        self.logger.info(f"开始判断攻击提示的响应是否安全")
        safety_judge_results = self.safety_judger.judge(attack_outputs)
        self.logger.info(
            f"第一条攻击提示:{attack_prompts[0]}, 模型得到的响应：{attack_outputs[0].response}，判定为{'安全' if safety_judge_results[0] else '不安全'}"
        )
        if len(safety_judge_results) > 1:
            self.logger.info(
                f"第二条攻击提示:{attack_prompts[1]}, 模型得到的响应：{attack_outputs[1].response}，判定为{'安全' if safety_judge_results[1] else '不安全'}"
            )
        asr = 1.0 - sum(safety_judge_results) / len(safety_judge_results)
        self.logger.info(
            f"攻击成功率：1.0 - {sum(safety_judge_results)} / {len(safety_judge_results)} = {asr}"
        )
        return safety_judge_results, asr

    def split_dataset(
        self,
        attack_outputs: list[InferenceOutput],
        attack_prompts: list[str],
        safety_judgments: list[bool],
    ) -> tuple[list[AlpacaInputData], list[AlpacaInputData]]:
        safe_dataset: list[AlpacaInputData] = [
            AlpacaInputData(
                instruction=attack_prompts[i],
                input="",
                output=attack_outputs[i].response,
            )
            for i in range(len(attack_prompts))
            if safety_judgments[i]
        ]
        unsafe_dataset: list[AlpacaInputData] = [
            AlpacaInputData(
                instruction=attack_prompts[i],
                input="",
                output=attack_outputs[i].response,
            )
            for i in range(len(attack_prompts))
            if not safety_judgments[i]
        ]
        return safe_dataset, unsafe_dataset


def main() -> None:
    import argparse
    import os

    from ..utils.backup_utils import backup_project_files
    from ..utils.config import (
        deepcopy_config,
        load_config,
        update_config_with_unparsed_args,
    )
    from ..utils.json_utils import save_json

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--config-file-path",
        type=str,
        default="./configs/single.yaml",
        help="The path to the config file",
    )
    args, unparsed_args = parser.parse_known_args()

    cfgs = load_config(args.config_file_path)
    update_config_with_unparsed_args(unparsed_args=unparsed_args, cfgs=cfgs)

    cfgs = deepcopy_config(cfgs)

    cfgs.pop("_common", None)

    output_dir = cfgs["output_dir"]

    save_json(cfgs, f"{output_dir}/cfgs.json")

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    print(cfgs)

    backup_project_files(output_dir, args.config_file_path, project_root)

    task = SingleTask(task_cfgs=cfgs)
    task.run()


if __name__ == "__main__":
    main()
