from ...prompts import BasePromptBuilder, PromptBuilderRegistry
from ...utils.extract_tools import extract_last_tag_content
from ...utils.type_utils import InferenceInput, InferenceOutput


class BaseSystemPromptRemoverPromptBuilder(BasePromptBuilder):
    pass


@PromptBuilderRegistry.register("SimpleSystemPromptRemove")
class SimpleSystemPromptRemovePromptBuilder(BaseSystemPromptRemoverPromptBuilder):
    def process_input(self, raw_input: InferenceInput) -> InferenceInput:
        raw_prompt = raw_input.get_last_user_message()
        raw_prompt = raw_prompt.replace("<think>", "START_THINKING")
        raw_prompt = raw_prompt.replace("</think>", "END_THINKING")
        raw_prompt = f"""我们正在进行一个语言模型的上下文蒸馏训练，我们在系统提示词中加入了一些提示，得到了模型对应的输出，你现在需要修改这个响应，保留它的思考过程等，但删除一些直接提及系统提示词（不一定是直接提到system）的内容。也就是说，对于那些引用系统提示的，你应该删除引用的部分，但不删除引用的内容，比如删除"as mentioned in system prompt"这些，但不删除这些被mention的内容。模型响应是：
{raw_prompt}
，你需要先分析模型响应中所有对系统提示的提及，然后逐一考虑修改，最后输出修改后的结果，注意在保持句子流畅的前提下，你的修改应该尽量少，绝大多数内容应该被保留而非修改。注意保留START_THINKING和END_THINKING这些标签。**最终将你修改的结果包围在<removed></removed>中。"""
        return raw_input.with_update_prompt(raw_prompt)

    def parse_output(self, raw_output: InferenceOutput) -> InferenceOutput:
        response = extract_last_tag_content(raw_output.response, "removed")
        if response is None:
            return raw_output
        response = response.replace("START_THINKING", "<think>")
        response = response.replace("END_THINKING", "</think>")
        return raw_output.with_parsed_output(response)
