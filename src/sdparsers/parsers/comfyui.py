from ..parser import Parser
from ..prompt_info import PromptInfo

GENERATOR_ID = "ComfyUI"


class ComfyUIParser(Parser):

    def parse(self, image):
        params_prompt = image.info.get('prompt')
        if params_prompt is None:
            return None

        prompts, processing_info = self.process(params_prompt)
        params_workflow = image.info.get('workflow')

        return PromptInfo(GENERATOR_ID, prompts, processing_info,
                          {"prompt": params_prompt,
                           "workflow": params_workflow})

    def process(self, params_prompt):
        return [], []