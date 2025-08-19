中文 | [English](README_en.md)

# LLM Stream Tuner

动态增量开放学习的大语言模型框架

*注意：本中文 README 和英文 README 均由 Qwen Code 自动生成。*

## 描述

LLM Stream Tuner 是一个为大语言模型设计的动态增量开放学习框架。它提供了持续训练和微调LLM的工具，使模型能够适应新信息而不遗忘已学知识。

该框架支持各种任务，包括安全性评估、对抗性攻击生成和增量学习策略。它特别专注于生成对抗性样本来提高模型的鲁棒性和安全性。

## 环境设置

本项目使用 `uv` 进行依赖管理。设置环境的步骤如下：

1. 如果尚未安装 `uv`，请先安装：
   ```bash
   pip3 install uv
   ```

2. 同步依赖：
   ```bash
   uv sync
   ```

3. 激活虚拟环境：
   ```bash
   source .venv/bin/activate
   ```

4. 安装 pre-commit 钩子：
   ```bash
   pre-commit install
   ```

关于 `uv` 的更多信息，请参考[文档](https://docs.astral.sh/uv/)或[中文文档](https://uv.doczh.com/)。

## 使用方法

本项目的主要使用方式是通过单任务模块：

```bash
uv run -m llm_stream_tuner.task.single --config-file-path ./configs/single.yaml
```

您也可以传递额外参数来覆盖配置值：

```bash
uv run -m llm_stream_tuner.task.single --config-file-path ./configs/single.yaml --model_cfgs.model_name_or_path Qwen/Qwen3-8B
```

### 配置

框架使用 YAML 配置文件来定义实验设置。主配置文件是 `configs/single.yaml`，包括：

- 数据加载配置
- 模型配置
- 推理设置
- 安全性判断配置
- 意图提取设置
- 提醒生成设置
- 攻击生成设置
- 系统提示移除设置

## 设计

框架采用模块化设计，包含以下关键组件：

1. **任务模块**：定义不同类型的任务（目前仅实现了 SingleTask）
2. **数据模块**：处理数据加载和预处理
3. **推理模块**：管理模型推理，支持多种后端（vLLM、基于API）
4. **管道模块**：包含不同阶段的专用组件：
   - 安全判断器：评估响应安全性
   - 意图提取器：从提示中提取意图
   - 提醒生成器：创建安全提醒
   - 攻击生成器：生成对抗性样本
   - 系统提示移除器：移除系统提示
5. **缓存管理器**：处理推理结果的缓存
6. **工具模块**：提供日志、配置和文件处理的实用函数

SingleTask 工作流程：
1. 加载初始数据和攻击数据
2. 对模型执行初始攻击
3. 评估攻击成功率
4. 从成功攻击中提取意图
5. 生成安全提醒
6. 生成新的对抗性样本
7. 在指定的轮数内迭代优化攻击
8. 保存生成的安全数据集

## 测试

项目在 `tests` 目录中包含了单元测试。运行测试：

```bash
uv run pytest
```

测试覆盖：
- 每个模块的核心功能
- 配置加载和解析
- 数据处理管道
- 实用函数

## 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。
