from abc import ABC, abstractmethod
from typing import Any

from ..data.data_loader import TrainDataLoader
from ..pipeline.attack_generator import get_attack_generator
from ..pipeline.intent_extractor import get_intent_extractor
from ..pipeline.reminder_generator import get_reminder_generator
from ..pipeline.safety_judger import get_safety_judger
from ..pipeline.system_prompt_remover import get_system_prompt_remover
from ..utils.logger import Logger


class BaseTask(ABC):
    def __init__(self, task_cfgs: dict[str, Any]) -> None:
        self.task_cfgs = task_cfgs

        # 初始化日志
        self.logger = Logger(f"{self.__module__}.{self.__class__.__name__}")

        # 加载数据
        self.logger.info("开始加载数据")
        data_cfgs: dict[str, Any] = self.task_cfgs["data_cfgs"]
        self.dataset = TrainDataLoader(data_cfgs).load_dataset()
        self.logger.info(f"数据加载完成，样本数：{len(self.dataset)}")
        self.logger.info(f"第一条数据：{self.dataset[0]}")

        # 加载攻击数据
        self.logger.info("开始加载攻击数据")
        attack_data_cfgs: dict[str, Any] = self.task_cfgs["attack_data_cfgs"]
        self.attack_dataset = TrainDataLoader(attack_data_cfgs).load_dataset()
        self.logger.info(f"攻击数据加载完成，样本数：{len(self.attack_dataset)}")
        self.logger.info(f"第一条攻击数据：{self.attack_dataset[0]}")

        # 加载模型
        self.logger.info("开始加载模型")
        self.target_model_cfgs: dict[str, Any] = self.task_cfgs["target_model_cfgs"]
        self.generate_model_cfgs: dict[str, Any] = self.target_model_cfgs[
            "generate_model_cfgs"
        ]
        self.logger.info("模型加载完成")

        # 加载安全判断器
        self.logger.info("开始加载安全判断器")
        safety_judger_cfgs: dict[str, Any] = self.task_cfgs["safety_judger_cfgs"]
        self.safety_judger = get_safety_judger(safety_judger_cfgs)
        self.logger.info("安全判断器加载完成")

        # 加载意图识别器
        self.logger.info("开始加载意图识别器")
        intent_extractor_cfgs: dict[str, Any] = self.task_cfgs["intent_extractor_cfgs"]
        self.intent_extractor = get_intent_extractor(intent_extractor_cfgs)
        self.logger.info("意图识别器加载完成")

        # 加载提醒生成器
        self.logger.info("开始加载提醒生成器")
        reminder_generator_cfgs: dict[str, Any] = self.task_cfgs[
            "reminder_generator_cfgs"
        ]
        self.reminder_generator = get_reminder_generator(reminder_generator_cfgs)
        self.logger.info("提醒生成器加载完成")

        # 加载攻击生成器
        self.logger.info("开始加载攻击生成器")
        attack_generator_cfgs: dict[str, Any] = self.task_cfgs["attack_generator_cfgs"]
        self.attack_generator = get_attack_generator(attack_generator_cfgs)
        self.logger.info("攻击生成器加载完成")

        # 加载系统提示移除器
        self.logger.info("开始加载系统提示移除器")
        system_prompt_remover_cfgs: dict[str, Any] = self.task_cfgs[
            "system_prompt_remover_cfgs"
        ]
        self.system_prompt_remover = get_system_prompt_remover(
            system_prompt_remover_cfgs
        )
        self.logger.info("系统提示移除器加载完成")

        self.output_dir = self.task_cfgs["output_dir"]
        self.logger.info(f"输出目录：{self.output_dir}")

        self.asr_threshold = self.task_cfgs["asr_threshold"]
        self.logger.info(f"攻击成功率阈值：{self.asr_threshold}")

        self.attack_epoch_num = self.task_cfgs["attack_epoch_num"]
        self.logger.info(f"攻击轮数：{self.attack_epoch_num}")

        self.retry_num = self.task_cfgs["retry_num"]
        self.logger.info(f"重试次数：{self.retry_num}")

        self.logger.info("任务初始化完成")

    @abstractmethod
    def run(self) -> None:
        pass
